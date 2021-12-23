import os
import uuid
import mimetypes
import re
from io import BytesIO
from flask import (
    Flask,
    request,
    jsonify,
    Blueprint,
    send_file,
    Response,
)
import boto3
from botocore.client import Config
from app.authentication import token_required

MINIO_URL = os.getenv('MINIO_URL')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
ACCEPTED_FILE_TYPES = [
    'application/pdf',
    'image/png',
    'image/jpeg',
    'audio/mpeg',
    'audio/wav',
    'video/mp4',
]
FILE_TYPE_ERROR = 'File type not allowed. Supported file types: png, jpg/jpeg, pdf, mp3, wav, mp4'
FILE_NAME_ERROR = 'File already exists. Please choose another file/rename current file'
BUCKET_NAME = 'damnation'

s3 = boto3.resource(
    's3',
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4')
)
damnation_bucket = s3.Bucket(BUCKET_NAME)

files = Blueprint('files', __name__)

@files.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

@files.route('/files', methods=['POST'])
@token_required
def save_file(decoded_token):
    file = request.files['File']
    objs = list(damnation_bucket.objects.filter(Prefix=file.filename))
    if any([w.key == file.filename for w in objs]):
        return jsonify({'message': FILE_NAME_ERROR}), 403
    if file.content_type not in ACCEPTED_FILE_TYPES:
        return jsonify({'message': FILE_TYPE_ERROR}), 415
    damnation_bucket.Object(file.filename).put(Body=file.read())
    return jsonify(
        status=True,
        filename=file.filename,
    ), 201


@files.route('/files', methods=['PUT'])
@token_required
def edit_file(decoded_token):
    new_file = request.files.get('NewFile', None)
    file_to_delete = request.form.get('FileToDelete', None)
    filename = None
    if new_file:
        objs = list(damnation_bucket.objects.filter(Prefix=new_file.filename))
        if any([w.key == new_file.filename for w in objs]):
            return jsonify({'message': FILE_NAME_ERROR}), 403
        if new_file.content_type not in ACCEPTED_FILE_TYPES:
            return jsonify({'message': FILE_TYPE_ERROR}), 415
    if file_to_delete:
        damnation_bucket.delete_objects(
            Delete={
                'Objects': [
                    {
                        'Key': file_to_delete,
                    },
                ],
            },
        )
    if new_file:
        damnation_bucket.Object(new_file.filename).put(Body=new_file.read())
        filename = new_file.filename
    return jsonify(
        status=True,
        filename=filename,
    ), 201


@files.route('/files/<filename>')
def get_file(filename):
    file = BytesIO()
    s3_object = s3.Object(BUCKET_NAME, filename)
    s3_object.download_fileobj(file)
    range_header = request.headers.get('Range', None)

    if not range_header: 
        file.seek(0)
        return send_file(
            file, 
            mimetype=s3_object.content_type,
        )

    size = file.getbuffer().nbytes  
    
    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()
    
    byte1 = int(g[0]) if g[0] else 0
    byte2 = int(g[1]) if g[1] else None

    length = size - byte1
    if byte2 is not None:
        length = byte2 + 1 - byte1
    
    file_chunk = None
    file.seek(byte1)
    file_chunk = file.read(length)

    res = Response(
        file_chunk, 
        206,
        mimetype=s3_object.content_type, 
        direct_passthrough=True
    )
    res.headers.add(
        'Content-Range', 
        f'bytes {byte1}-{byte1 + length - 1}/{size}'
    )
    return res


@files.route('/files/<filename>', methods=['DELETE'])
@token_required
def delete_file(decoded_token, filename):
    damnation_bucket.delete_objects(
        Delete={
            'Objects': [
                {
                    'Key': filename,
                },
            ],
        },
    )
    return jsonify(
        status=True,
        message='Article deleted successfully!'
    ), 204