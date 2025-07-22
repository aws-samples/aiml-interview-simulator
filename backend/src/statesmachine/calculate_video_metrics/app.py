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
    try:
        # Load the video clip with verbose output to help diagnose issues
        video_clip = VideoFileClip(video_path, verbose=True)
        
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
    except Exception as e:
        print(f"Error extracting frames: {str(e)}")
        # Use ffmpeg directly as a fallback
        import subprocess
        import tempfile
        import glob
        
        # Create a temporary directory for frames
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Extract frames using ffmpeg directly
            cmd = f"ffmpeg -i {video_path} -vf 'fps=1/{seconds}' {temp_dir}/frame_%03d.jpg"
            subprocess.run(cmd, shell=True, check=True)
            
            # Get all extracted frames
            frame_files = sorted(glob.glob(f"{temp_dir}/frame_*.jpg"))
            
            # Read frames into bytes
            frames_bytes = []
            for frame_file in frame_files:
                with open(frame_file, 'rb') as f:
                    frames_bytes.append(f.read())
                    
            return frames_bytes
        except Exception as e2:
            print(f"Fallback method also failed: {str(e2)}")
            # Return empty list if both methods fail
            return []


def lambda_handler(event, context):
    print(event)
    try:
        key = event["Converted"]["body"]["video"]
        # download video to tmp and call extract frames
        s3.download_file(BUCKET, key, "/tmp/video.qt")

        # Extract frames
        # Set the step size to 5 seconds
        step_size = 5
        frames = extract_frames("/tmp/video.qt", [], step_size)

        # Handle case where no frames were extracted
        if not frames:
            print("No frames were extracted from the video")
            return {
                "statusCode": 200,
                "body": {"objects": str([]), "attention": str(True)},
            }

        # Identify objects
        objects = identify_objects(frames, [])

        # Calculate attention
        attention = calculate_attention(frames)

        return {
            "statusCode": 200,
            "body": {"objects": str(objects), "attention": str(attention)},
        }
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        # Return default values in case of error
        return {
            "statusCode": 200,
            "body": {"objects": str([]), "attention": str(True)},
        }