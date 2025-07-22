import os
import json
import boto3
import decimal
from boto3.dynamodb.types import TypeDeserializer

# Helper function to convert DynamoDB items to JSON-serializable format
def replace_decimals(obj):
    if isinstance(obj, list):
        return [replace_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: replace_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

TABLE = os.environ["TABLE_NAME"]
INDEX = os.environ["INDEX_NAME"]
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    # Set up CORS headers
    headers = {
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,OPTIONS",
        "Content-Type": "application/json"
    }
    
    # Simple response for debugging
    if event.get("queryStringParameters") and event["queryStringParameters"].get("debug") == "true":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"results": [{"record_id": "test", "email": "test@example.com", "date": "01/01/2023", "duration": "1:00"}]})
        }
    
    try:
        # Print event for debugging
        print(f"Event: {json.dumps(event)}")
        
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": headers,
                "body": ""
            }
        
        table = dynamodb.Table(TABLE)
        print(f"Table: {TABLE}, Index: {INDEX}")
        
        # Check if queryStringParameters exists
        if not event.get("queryStringParameters") or not event["queryStringParameters"].get("email"):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Missing email parameter"})
            }
        
        email = event["queryStringParameters"]["email"]
        print(f"Querying for email: {email}")
        
        response = table.query(
            IndexName=INDEX,
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={
                ":email": email,
            },
        )
        
        # Can't directly print response due to Decimal values
        print(f"DynamoDB response received with {len(response.get('Items', []))} items")
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }

    # Handle empty results
    if not response.get("Items"):
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"results": []})
        }

    try:
        # Convert Decimal types to standard Python types
        serializable_items = replace_decimals(response["Items"])
        
        # Try to serialize to JSON to catch any issues
        result_json = json.dumps({"results": serializable_items})
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": result_json
        }
    except Exception as e:
        print(f"Error serializing response: {str(e)}")
        # Return a simplified response as fallback
        simple_items = []
        for item in response.get("Items", []):
            simple_item = {}
            for k, v in item.items():
                try:
                    if isinstance(v, decimal.Decimal):
                        simple_item[k] = str(v)
                    else:
                        simple_item[k] = str(v)
                except:
                    simple_item[k] = "[Error serializing value]"
            simple_items.append(simple_item)
            
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"results": simple_items})
        }
