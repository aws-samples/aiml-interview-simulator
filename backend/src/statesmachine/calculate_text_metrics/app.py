# General
import re
import os
import json
import boto3

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3")

LLM_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

metrics = {
    "transcription": "",
    "feedback": "",
}

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
)

def bedrock_feedback(perguntas, apresentacao):
    prompt_template_bedrock = f"""Use a transcrição da entrevista para auxiliar o entrevistador:
  
    <perguntas>{perguntas}</perguntas>
    <apresentação>{apresentacao}</apresentação>
    
    A resposta deve seguir o seguinte formato:
    <avaliação>Avaliação geral e de boas práticas de apresentação</avaliação>
    <correção>Correção das respostas do aluno para as perguntas</correção>
    """
    
    response = bedrock.invoke_model(
        modelId=LLM_MODEL_ID,
        body=json.dumps(
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
        ),
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
