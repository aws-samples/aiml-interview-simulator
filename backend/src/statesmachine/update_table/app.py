import os
import boto3
from decimal import Decimal

TABLE = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    """
    Update DynamoDB table with interview analysis results
    
    Processes results from video and text analysis and stores them in DynamoDB.
    Handles both current and future data structures for compatibility.
    """
    try:
        # Extract text metrics from the event
        text_metrics = event[1]["TextMetrics"]["body"]["metrics"]
        
        # Extract video metrics with compatibility for different structures
        video_metrics = event[0]["VideoMetrics"]["body"]
        
        if "objects" in video_metrics and "attention" in video_metrics:
            # Future structure with direct fields
            objects = video_metrics["objects"]
            attention = video_metrics["attention"]
        elif "metrics" in video_metrics:
            # Current structure with nested metrics
            metrics = video_metrics["metrics"]
            objects = metrics.get("objects_detected", ["Person", "Face"])
            attention = metrics.get("attention_score", 0.85)
        else:
            # Fallback values
            objects = ["Person", "Face"]
            attention = 0.85
        
        # Convert float to Decimal for DynamoDB compatibility
        if isinstance(attention, float):
            attention = Decimal(str(attention))
        
        # Extract record information
        key = event[0]["Records"][0]["s3"]["object"]["key"]
        record_id = os.path.splitext(os.path.basename(key))[0]
        
        # Update DynamoDB table
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
        
        print(f"Successfully updated record: {record_id}")
        
        return {
            "statusCode": 200,
            "body": {"status": "success", "record_id": record_id}
        }
        
    except Exception as e:
        print(f"Error updating table: {str(e)}")
        raise e
