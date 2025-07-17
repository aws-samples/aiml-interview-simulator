import os
import boto3
from PIL import Image
from io import BytesIO
from moviepy.editor import VideoFileClip


s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
BUCKET = os.environ["BUCKET"]
NOT_ALLOWED = ["Hat", "Cap"]


def calculate_attention(frame_bytes):
    attention = True

    previous_position = ""
    for frame in frame_bytes:
        # Detect face position
        response = rekognition.detect_faces(Image={"Bytes": frame})

        if len(response["FaceDetails"]) > 0:
            actual_position = response["FaceDetails"][0]["Pose"]
            if previous_position != "":
                # Compare actual position with previous position, distância euclidiana
                delta_position = (
                    sum(
                        (actual_position[key] - previous_position[key]) ** 2
                        for key in actual_position.keys()
                    )
                    ** 0.5
                )
                if delta_position > 30:
                    attention = False

            previous_position = actual_position

    return attention


def identify_objects(frames_bytes, objects_list):
    for frame in frames_bytes:
        # Detect objects in the frame
        response = rekognition.detect_labels(Image={"Bytes": frame})

        # Extract the identified objects
        for label in response["Labels"]:
            if label["Name"] in NOT_ALLOWED:
                if label["Name"] not in objects_list:
                    objects_list.append(label["Name"])

    return objects_list


def frame_to_bytes(frame):
    # Convert NumPy array to PIL Image
    pil_image = Image.fromarray(frame)

    # Convert PIL Image to bytes
    image_stream = BytesIO()
    pil_image.save(image_stream, format="JPEG")
    image_bytes = image_stream.getvalue()
    image_stream.close()
    return image_bytes


def extract_frames(video_path, frames_list, seconds):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Get the duration of the video
    duration = video_clip.duration

    # Iterate over each frame and extract frames every 5 seconds
    for t in range(0, int(duration), seconds):
        # Get frame at current time
        frame = video_clip.get_frame(t)
        frames_list.append(frame)

    # Close the video clip
    video_clip.close()

    # Convert
    frames_bytes = []
    for frame in frames_list:
        # Convert frame to bytes
        frames_bytes.append(frame_to_bytes(frame))

    return frames_bytes


def lambda_handler(event, context):
    print(event)
    key = event["Converted"]["body"]["video"]
    # download video to tmp and call extract frames
    s3.download_file(BUCKET, key, "/tmp/video.qt")

    # Extract frames
    # Set the step size to 5 seconds
    step_size = 5
    frames = extract_frames("/tmp/video.qt", [], step_size)

    # Identify objects
    objects = identify_objects(frames, [])

    # Calculate attention
    attention = calculate_attention(frames)

    return {
        "statusCode": 200,
        "body": {"objects": str(objects), "attention": str(attention)},
    }