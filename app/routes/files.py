import os
from io import BytesIO
from flask import (
    Flask,
    request,
    jsonify,
    Blueprint,
    send_file
)
import boto3
from botocore.client import Config
from app.authentication import token_required

MINIO_URL = os.getenv('MINIO_URL')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')

s3 = boto3.resource(
    's3',
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4')
)
damnation_bucket = s3.Bucket('damnation')

files = Blueprint('files', __name__)
    
@files.route('/files', methods=['POST'])
def save_file():
    file = request.files['File']
    damnation_bucket.Object(file.filename).put(Body=file.read())
    return jsonify(
        status=True,
        filename=file.filename,
    ), 201

@files.route('/files', methods=['PUT'])
def edit_file():
    new_file = request.files.get('NewFile', None)
    file_to_delete = request.form.get('FileToDelete', None)
    filename = None
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
    print('filename', filename)
    return jsonify(
        status=True,
        filename=filename,
    ), 201


@files.route('/files/<filename>')
def get_file(filename):
    a_file = BytesIO()
    s3_object = s3.Object('damnation', filename)
    s3_object.download_fileobj(a_file)
    a_file.seek(0)
    return send_file(a_file, mimetype=s3_object.content_type)


@files.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
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