import os
import json
import boto3
from datetime import date

TABLE = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
item = {
    "record_id": "",
    "email": "",
    "date": "",
    "duration": "",
    "avaliation": "",
    "video": "",
    "report": "",
}


def lambda_handler(event, context):
    # Handle OPTIONS request for CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
            },
            "body": ""
        }
        
    table = dynamodb.Table(TABLE)
    data = json.loads(event["body"])

    item["record_id"] = data["record_id"]
    item["email"] = data["email"]
    item["date"] = date.today().strftime("%d/%m/%Y")
    item["duration"] = data["duration"]

    table.put_item(Item=item)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
        },
        "body": json.dumps(
            {
                "message": "success",
            }
        ),
    }
