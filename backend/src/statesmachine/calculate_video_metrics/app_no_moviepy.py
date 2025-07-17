import os
import boto3

s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
BUCKET = os.environ["BUCKET"]


def lambda_handler(event, context):
    """
    Versão temporária que pula o processamento de vídeo com MoviePy
    até que o layer do FFmpeg seja configurado corretamente
    """
    print(f"⚠️  AVISO: Processamento de vídeo pulado - MoviePy/FFmpeg não disponível")
    print(f"📁 Event recebido: {event}")
    
    try:
        # Extrair informações do evento
        if "Converted" in event and "body" in event["Converted"]:
            video_key = event["Converted"]["body"]["video"]
            bucket = event["Converted"]["body"]["bucket"]
        else:
            # Fallback para estrutura alternativa
            video_key = "converted/video.mov"
            bucket = BUCKET
        
        print(f"📹 Vídeo processado: {video_key}")
        
        # Simular métricas de vídeo com valores padrão
        mock_metrics = {
            "attention_score": 0.85,  # 85% de atenção
            "objects_detected": ["Person", "Face"],
            "frames_analyzed": 10,
            "video_duration": 30.0,  # 30 segundos estimados
            "face_detection_confidence": 0.9,
            "attention_analysis": "Good attention maintained throughout the video",
            "note": "Video metrics calculation skipped - MoviePy/FFmpeg layer not available"
        }
        
        print(f"✅ Métricas simuladas geradas: {mock_metrics}")
        
        return {
            "statusCode": 200,
            "body": {
                "bucket": bucket,
                "video": video_key,
                "metrics": mock_metrics,
                "processing_status": "simulated"
            }
        }
        
    except Exception as e:
        print(f"❌ Erro ao processar evento: {str(e)}")
        
        # Retornar métricas básicas mesmo em caso de erro
        return {
            "statusCode": 200,
            "body": {
                "bucket": BUCKET,
                "video": "unknown",
                "metrics": {
                    "attention_score": 0.5,
                    "objects_detected": [],
                    "frames_analyzed": 0,
                    "video_duration": 0.0,
                    "error": str(e),
                    "note": "Video metrics calculation failed - using default values"
                },
                "processing_status": "error_fallback"
            }
        }
