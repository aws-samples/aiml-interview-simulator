import os
import subprocess
import shlex
import boto3

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3")


def lambda_handler(event, context):
    data = event["Records"][0]["s3"]
    bucket = data["bucket"]["name"]
    video = data["object"]["key"]

    video_basename = os.path.splitext(os.path.basename(video))[0]
    convertion_filename = video_basename + ".mov"

    s3_source_signed_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": video}, ExpiresIn=60
    )

    ffmpeg_cmd = f"/opt/bin/ffmpeg -i {s3_source_signed_url} -vcodec h264 -f mov -an /tmp/{convertion_filename}"
    run_cmd = subprocess.run(shlex.split(ffmpeg_cmd))
    print(run_cmd)

    response = s3.upload_file(
        f"/tmp/{convertion_filename}",
        BUCKET,
        "converted/" + convertion_filename,
    )

    return {
        "statusCode": 200,
        "body": {
            "bucket": BUCKET,
            "video": "converted/" + convertion_filename,
        },
    }
