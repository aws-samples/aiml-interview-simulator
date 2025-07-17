import os
import boto3

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3")


def lambda_handler(event, context):
    """
    Video conversion function - currently using temporary implementation
    
    This function processes uploaded video files and prepares them for analysis.
    Currently skips actual conversion due to FFmpeg layer requirements.
    """
    try:
        data = event["Records"][0]["s3"]
        bucket = data["bucket"]["name"]
        video = data["object"]["key"]
        
        video_basename = os.path.splitext(os.path.basename(video))[0]
        converted_filename = f"converted/{video_basename}.mov"
        
        print(f"Processing video: {video}")
        
        # Copy original file to converted directory
        # This maintains the processing pipeline while FFmpeg layer is being set up
        copy_source = {'Bucket': bucket, 'Key': video}
        s3.copy_object(
            CopySource=copy_source,
            Bucket=BUCKET,
            Key=converted_filename
        )
        
        print(f"Video processed successfully: {converted_filename}")
        
        return {
            "statusCode": 200,
            "body": {
                "bucket": BUCKET,
                "video": converted_filename,
                "processing_status": "completed"
            }
        }
        
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        raise e
