import os
import boto3

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3")


def lambda_handler(event, context):
    """
    Versão temporária que pula a conversão de vídeo
    até que o layer do FFmpeg seja configurado corretamente
    """
    data = event["Records"][0]["s3"]
    bucket = data["bucket"]["name"]
    video = data["object"]["key"]

    video_basename = os.path.splitext(os.path.basename(video))[0]
    
    print(f"⚠️  AVISO: Conversão de vídeo pulada para {video}")
    print(f"📁 Arquivo original mantido: {video}")
    
    # Simular sucesso da conversão copiando o arquivo original
    # para o diretório "converted" com extensão .mov
    convertion_filename = video_basename + ".mov"
    
    try:
        # Copiar arquivo original para pasta converted
        copy_source = {'Bucket': bucket, 'Key': video}
        s3.copy_object(
            CopySource=copy_source,
            Bucket=BUCKET,
            Key="converted/" + convertion_filename
        )
        
        print(f"✅ Arquivo copiado para: converted/{convertion_filename}")
        
    except Exception as e:
        print(f"❌ Erro ao copiar arquivo: {str(e)}")
        # Retornar o arquivo original como fallback
        convertion_filename = video

    return {
        "statusCode": 200,
        "body": {
            "bucket": BUCKET,
            "video": "converted/" + convertion_filename,
            "note": "Video conversion skipped - FFmpeg layer not available"
        },
    }
