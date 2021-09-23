import json
import urllib.parse
import boto3
import json

s3 = boto3.client('s3')


def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response_image = s3.get_object(Bucket=bucket, Key=key)

        client = boto3.client('rekognition')
        response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}}, MaxLabels=10)

        db_client = boto3.client('dynamodb')

        str_response = json.dumps(response['Labels'])

        data = db_client.put_item(
            TableName='images_table',
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
        print(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                key, bucket))
        raise e
