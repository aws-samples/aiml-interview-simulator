import os
import json
import boto3

TABLE = os.environ["TABLE_NAME"]
INDEX = os.environ["INDEX_NAME"]
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE)

    response = table.query(
        IndexName=INDEX,
        KeyConditionExpression="email = :email",
        ExpressionAttributeValues={
            ":email": event["queryStringParameters"]["email"],
        },
    )

    if not response["Items"]:
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
            },
            "body": json.dumps(
                {
                    "results": [],
                }
            ),
        }

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": json.dumps(
            {
                "results": response["Items"],
            }
        ),
    }
