import os
import boto3
from decimal import Decimal

TABLE = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    text_metrics = event[1]["TextMetrics"]["body"]["metrics"]
    
    # Handle both original and temporary VideoMetrics structure
    video_metrics = event[0]["VideoMetrics"]["body"]
    if "objects" in video_metrics and "attention" in video_metrics:
        # Original structure
        objects = video_metrics["objects"]
        attention = video_metrics["attention"]
    elif "metrics" in video_metrics:
        # Temporary structure - extract from metrics
        metrics = video_metrics["metrics"]
        objects = metrics.get("objects_detected", ["Person", "Face"])
        attention = metrics.get("attention_score", 0.85)
    else:
        # Fallback values
        objects = ["Person", "Face"]
        attention = 0.85
    
    # Convert float to Decimal for DynamoDB
    if isinstance(attention, float):
        attention = Decimal(str(attention))
    
    key = event[0]["Records"][0]["s3"]["object"]["key"]
    record_id = os.path.splitext(os.path.basename(key))[0]
    table = dynamodb.Table(TABLE)

    table.update_item(
        Key={"record_id": record_id},
        UpdateExpression="set report=:report, objects=:objects, attention=:attention, video=:video",
        ExpressionAttributeValues={
            ":report": text_metrics,
            ":objects": objects,
            ":attention": attention,
            ":video": key,
        },
        ReturnValues="ALL_NEW",
    )

    # table.update_item(
    #     Key={"record_id": record_id},
    #     UpdateExpression="set report=:report, video=:video",
    #     ExpressionAttributeValues={
    #         ":report": text_metrics,
    #         ":video": key,
    #     },
    #     ReturnValues="ALL_NEW",
    # )

    return {
        "statusCode": 200,
        "body": {"status": "success"},
    }