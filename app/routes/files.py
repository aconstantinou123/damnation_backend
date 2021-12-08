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
    )


@files.route('/files/<filename>')
def get_file(filename):
    a_file = BytesIO()
    s3_object = s3.Object('damnation', filename)
    s3_object.download_fileobj(a_file)
    a_file.seek(0)
    return send_file(a_file, mimetype=s3_object.content_type)