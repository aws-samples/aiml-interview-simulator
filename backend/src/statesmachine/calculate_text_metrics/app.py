# General
import re
import os
import json
import boto3

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3")

# Constants for Bedrock models
MODEL_ID = "anthropic.claude-sonnet-4-20250514-v1:0"
FALLBACK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

metrics = {
    "transcription": "",
    "feedback": "",
}

# Initialize Bedrock clients
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
bedrock = boto3.client("bedrock", region_name="us-east-1")

# Function to get or create an inference profile
def get_or_create_inference_profile():
    profile_name = f"interview-simulator-claude-sonnet-4-{os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'default')}"
    
    try:
        # Try to find existing inference profile
        response = bedrock.list_inference_profiles()
        for profile in response.get('inferenceProfiles', []):
            if profile['name'] == profile_name:
                return profile['inferenceProfileArn']
        
        # If not found, try to create one
        try:
            # Get the Lambda execution role
            sts = boto3.client('sts')
            caller_identity = sts.get_caller_identity()
            account_id = caller_identity['Account']
            
            # Use the Lambda execution role for Bedrock
            role_name = os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'default')
            execution_role = f"arn:aws:iam::{account_id}:role/{role_name}"
            
            response = bedrock.create_inference_profile(
                name=profile_name,
                modelId=MODEL_ID,
                inferenceProfileType="ON_DEMAND",
                executionRoleArn=execution_role
            )
            return response['inferenceProfileArn']
        except Exception as e:
            print(f"Error creating inference profile: {str(e)}")
            return None
    except Exception as e:
        print(f"Error getting inference profile: {str(e)}")
        return None

def bedrock_feedback(perguntas, apresentacao):
    prompt_template_bedrock = f"""Use a transcrição da entrevista para auxiliar o entrevistador:
  
    <perguntas>{perguntas}</perguntas>
    <apresentação>{apresentacao}</apresentação>
    
    A resposta deve seguir o seguinte formato:
    <avaliação>Avaliação geral e de boas práticas de apresentação</avaliação>
    <correção>Correção das respostas do aluno para as perguntas</correção>
    """
    
    request_body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "system": "Você é um entrevistador. Avalie a simulação de entrevista do aluno e corrija as respostas das perguntas, avaliando se estão corretas ou não para cada uma delas.",
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt_template_bedrock}],
                }
            ],
            "temperature": 0.5,
        }
    )
    
    # Try to get or create an inference profile
    inference_profile_arn = get_or_create_inference_profile()
    
    try:
        if inference_profile_arn:
            # Use inference profile if available
            print(f"Using inference profile: {inference_profile_arn}")
            response = bedrock_runtime.invoke_model(
                inferenceProfileArn=inference_profile_arn,
                body=request_body
            )
        else:
            # Fall back to Claude 3 Haiku which supports direct invocation
            print(f"Falling back to {FALLBACK_MODEL_ID}")
            response = bedrock_runtime.invoke_model(
                modelId=FALLBACK_MODEL_ID,
                body=request_body
            )
    except Exception as e:
        # If any error occurs, fall back to Claude 3 Haiku
        print(f"Error invoking model, falling back to {FALLBACK_MODEL_ID}: {str(e)}")
        response = bedrock_runtime.invoke_model(
            modelId=FALLBACK_MODEL_ID,
            body=request_body
        )

    result = (
        json.loads(response.get("body").read())
        .get("content", [])[0]
        .get("text", "")
    )
    
    return result


def lambda_handler(event, context):
    transcription_file = event["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]

    key = os.path.splitext(os.path.basename(transcription_file))
    s3.download_file(
        BUCKET, "transcription/" + key[0] + key[1], "/tmp/transcription.json"
    )
    file = open("/tmp/transcription.json")

    data = json.load(file)
    apresentacao = data["results"]["transcripts"][0]["transcript"]
    perguntas = """"
    1- Cite um serviço de computação AWS;
    2- Como são cobrados os serviços AWS?;
    3- Onde posso armazenar aquivos em objeto na AWS?;
    """

    metrics["transcription"] = apresentacao
    feedback = bedrock_feedback(perguntas, apresentacao).replace('"', "`")
    
    avaliacao_pattern = re.compile(r'<avaliação>(.*?)<\/avaliação>', re.DOTALL)
    correcao_pattern = re.compile(r'<correção>(.*?)<\/correção>', re.DOTALL)
    avaliacao_match = avaliacao_pattern.search(feedback)
    correcao_match = correcao_pattern.search(feedback)
    metrics["avaliacao"] = avaliacao_match.group(1).strip()
    metrics["correcao"] = correcao_match.group(1).strip()

    return {
        "statusCode": 200,
        "body": {"metrics": str(metrics)},
    }
