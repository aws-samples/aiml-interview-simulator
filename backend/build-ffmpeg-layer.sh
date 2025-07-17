#!/bin/bash

# Script para criar layer personalizado do FFmpeg para Lambda
# Este script deve ser executado em um ambiente Linux (ou Docker)

set -e

echo "🔧 Criando layer personalizado do FFmpeg..."

# Criar diretório temporário
mkdir -p /tmp/ffmpeg-layer/bin

# Baixar FFmpeg estático pré-compilado
cd /tmp/ffmpeg-layer
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz

# Copiar binários para o diretório correto
cp ffmpeg-*-amd64-static/ffmpeg bin/
cp ffmpeg-*-amd64-static/ffprobe bin/

# Criar arquivo ZIP do layer
zip -r ffmpeg-layer.zip bin/

echo "✅ Layer criado: /tmp/ffmpeg-layer/ffmpeg-layer.zip"
echo "📝 Próximos passos:"
echo "1. Faça upload do arquivo ZIP para um bucket S3"
echo "2. Crie o layer no Lambda usando o arquivo S3"
echo "3. Atualize o template SAM para usar o layer personalizado"
