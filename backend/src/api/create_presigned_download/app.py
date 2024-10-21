import os
import json
import boto3

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3")


def lambda_handler(event, context):
    filename = event["queryStringParameters"]["filename"]

    url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET, "Key": filename}, ExpiresIn=300
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": json.dumps(
            {
                "url": url,
            }
        ),
    }
