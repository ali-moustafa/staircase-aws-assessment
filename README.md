# staircase-aws-assessment

serverless.yml
  - creating S3 bucket
  - creating DynamoDB Table
  - creating lambda function

app.py
  - AWS_ACCESS_KEY="" and AWS_SECRET_ACCESS_KEY="" of the user need to be added in app.py file to be able to connect to aws services using boto3.
  - verify the file type before uploading to S3.
  - creating two API endpoints using FLask to upload image to S3 and get data from dynamoDb table.
  - creating lambda function that will be triggered when object is uploaded to the s3 bucket.
  - the lambda function will call amazon rekognition API to do image processing on the image.
  - lambda function then call dynamoDB API to put the results in the images table.
  
  
