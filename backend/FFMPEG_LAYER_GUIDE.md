# Guia para Implementar Layer FFmpeg Personalizado

## Problema
As funções Lambda `ConvertVideoFunction` e `CalculateVideoMetricsFunction` dependem do FFmpeg, mas não conseguimos usar o layer do Serverless Application Repository devido a restrições de permissão.

## Solução: Layer Personalizado

### Passo 1: Criar o Layer FFmpeg

```bash
# Execute em ambiente Linux ou Docker
mkdir -p /tmp/ffmpeg-layer/bin
cd /tmp/ffmpeg-layer

# Baixar FFmpeg estático pré-compilado
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz

# Copiar binários
cp ffmpeg-*-amd64-static/ffmpeg bin/
cp ffmpeg-*-amd64-static/ffprobe bin/

# Criar ZIP do layer
zip -r ffmpeg-layer.zip bin/
```

### Passo 2: Upload para S3

```bash
# Criar bucket para layers (se não existir)
aws s3 mb s3://seu-bucket-layers --region us-east-1

# Upload do layer
aws s3 cp ffmpeg-layer.zip s3://seu-bucket-layers/layers/ffmpeg-layer.zip
```

### Passo 3: Criar Layer no Lambda

```bash
aws lambda publish-layer-version \
    --layer-name ffmpeg-layer \
    --description "FFmpeg binaries for video processing" \
    --content S3Bucket=seu-bucket-layers,S3Key=layers/ffmpeg-layer.zip \
    --compatible-runtimes python3.9 python3.8 \
    --region us-east-1
```

### Passo 4: Atualizar Template SAM

Adicionar no template.yaml:

```yaml
Resources:
  FFmpegLayer:
    Type: AWS::Lambda::LayerVersion
    Properties:
      LayerName: !Sub "${AWS::StackName}-ffmpeg-layer"
      Description: "FFmpeg binaries for video processing"
      Content:
        S3Bucket: seu-bucket-layers
        S3Key: layers/ffmpeg-layer.zip
      CompatibleRuntimes:
        - python3.9
        - python3.8

  ConvertVideoFunction:
    Type: AWS::Serverless::Function
    Properties:
      # ... outras propriedades
      Layers:
        - !Ref FFmpegLayer

  CalculateVideoMetricsFunction:
    Type: AWS::Serverless::Function
    Properties:
      # ... outras propriedades
      Layers:
        - !Ref FFmpegLayer
```

### Passo 5: Restaurar Código Original

Depois de implementar o layer, restaurar os arquivos originais:
- `src/statesmachine/convert_video/app.py`
- `src/statesmachine/calculate_video_metrics/app.py`
