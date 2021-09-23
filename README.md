# staircase-aws-assessment
Lambda function python code

This code is implementing the following:
  - Trigger lambda function when object is uploaded to s3 bucket.
  - Lamda function gets the object (image) from s3 using get_object()
  - Lamda function uses Amazon Rekognition API detect_labels to do image recognition on the image.
  - Then stores the result from image recognition inside a DynamoDb table using put_item()
