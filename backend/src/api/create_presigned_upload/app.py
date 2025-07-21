import os
import json
import boto3
from botocore.config import Config

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3", config=Config(s3={"use_accelerate_endpoint": True}))


def lambda_handler(event, context):
    # Handle OPTIONS request for CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
            },
            "body": ""
        }
    
    # Check if queryStringParameters exists
    if not event.get("queryStringParameters") or not event["queryStringParameters"].get("filename"):
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
            },
            "body": json.dumps({"error": "Missing filename parameter"})
        }
    
    response = s3.generate_presigned_post(
        Bucket=BUCKET,
        Key=event["queryStringParameters"]["filename"],
        ExpiresIn=600,
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
        "body": json.dumps(response),
    }
