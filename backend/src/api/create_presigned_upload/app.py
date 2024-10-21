import os
import json
import boto3
from botocore.config import Config

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3", config=Config(s3={"use_accelerate_endpoint": True}))


def lambda_handler(event, context):
    response = s3.generate_presigned_post(
        Bucket=BUCKET,
        Key=event["queryStringParameters"]["filename"],
        ExpiresIn=600,
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": json.dumps(response),
    }
