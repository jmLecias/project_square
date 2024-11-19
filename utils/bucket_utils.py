import boto3
from botocore.exceptions import NoCredentialsError
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME, FOLDER_NAME


s3 = boto3.client(
    's3', 
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name = AWS_REGION
)