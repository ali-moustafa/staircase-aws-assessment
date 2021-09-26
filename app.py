import boto3
from pathlib import Path
from flask import Flask, request
from werkzeug.utils import secure_filename
import json
import urllib.parse
from botocore.exceptions import ClientError
import re

app = Flask(__name__)

# S3_BUCKET = "staircase-images"
S3_BUCKET = "serverless-staircase-images"
S3_UPLOAD_KEY_NAME = "{filename}"
# DYNAMODB_TABLE = "images_table"
DYNAMODB_TABLE = "serverless_images_table"

AWS_ACCESS_KEY="AKIA37CAKO6BCT3D2K6R"
AWS_SECRET_ACCESS_KEY="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"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_FOLDER = Path(__file__).resolve().parent


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload_image():
    """Receives a request to upload an image."""
    # Check if file was uploaded
    if "file" not in request.files:
        return "No file uploaded"

    file = request.files["file"]
    # Check if file is allowed
    if not allowed_file(file.filename):
        return "File extension not allowed"

    # save file locally
    filename = secure_filename(file.filename)
    file_path = UPLOAD_FOLDER / filename
    file.save(file_path)

    file_key = S3_UPLOAD_KEY_NAME.format(filename=filename)
    upload_image_to_s3(file_path, file_key)

    return "File uploaded successfully!"


@app.route('/get_info/<image_name>', methods=["GET"])
def get_image_info(image_name):
    db_client = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    table = db_client.Table(DYNAMODB_TABLE)

    try:
        response = table.get_item(Key={'id': image_name})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Item']


def upload_image_to_s3(file_loc, s3_key):
    s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    with open(file_loc, "rb") as f:
        s3.upload_fileobj(f, S3_BUCKET, s3_key)

    print(f"Image: {s3_key} uploaded to S3")


def process_image(event, context):
    """Lambda function which receives S3 event."""

    s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response_image = s3.get_object(Bucket=bucket, Key=key)

        client = boto3.client('rekognition', aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}}, MaxLabels=10)

        db_client = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        str_response = json.dumps(response['Labels'])

        # file_name = re.sub("uploads/", "", key)

        data = db_client.put_item(
            TableName=DYNAMODB_TABLE,
            Item={
                'id': {
                    'S': key
                },
                'image_labels_info': {
                    'S': str_response
                },
                'image_labels_count': {
                    'N': str(len(response['Labels']))
                }
            })

        response = {
            'statusCode': 200,
            'body': 'successfully created item!',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
        }

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the '
              'same region as this function.'.format(key, bucket))
        raise e
