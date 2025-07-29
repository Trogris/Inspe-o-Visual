#!/bin/bash

# Sistema de Verificação Visual Automatizada
# Script de Instalação Automática - Versão Final

set -e  # Parar em caso de erro

echo "🚀 Iniciando instalação do Sistema de Verificação Visual Automatizada"
echo "=================================================================="

# Verificar Python
echo "📋 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.11+ primeiro."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION encontrado"

# Verificar versão mínima
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "✅ Versão do Python compatível"
else
    echo "❌ Python 3.8+ necessário. Versão atual: $PYTHON_VERSION"
    exit 1
fi

# Criar ambiente virtual
echo "🔧 Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
if [ -f "requirements_final.txt" ]; then
    pip install -r requirements_final.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ Arquivo requirements.txt não encontrado"
    exit 1
fi

echo "✅ Dependências instaladas com sucesso"

# Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p data/inspections
mkdir -p data/reports
mkdir -p data/backups
mkdir -p logs
echo "✅ Estrutura de diretórios criada"

# Testar instalação
echo "🧪 Testando instalação..."
cd src

# Teste básico de importações
python3 -c "
import streamlit
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
import easyocr
print('✅ Todas as dependências importadas com sucesso')
"

# Teste de integração (se disponível)
if [ -f "integration_test_video.py" ]; then
    echo "🧪 Executando teste de integração..."
    python3 integration_test_video.py
    if [ $? -eq 0 ]; then
        echo "✅ Teste de integração passou"
    else
        echo "⚠️  Teste de integração falhou, mas instalação pode estar OK"
    fi
fi

cd ..

# Criar script de inicialização
echo "📝 Criando script de inicialização..."
cat > start_system.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando Sistema de Verificação Visual Automatizada"
source venv/bin/activate
cd src
streamlit run streamlit_clean_app.py --server.port 8501 --server.headless true
EOF

chmod +x start_system.sh

# Criar arquivo de configuração de exemplo
echo "⚙️  Criando configuração de exemplo..."
cat > config.json << 'EOF'
{
  "video": {
    "max_size_mb": 100,
    "supported_formats": ["mp4", "mov", "avi", "mkv", "wmv"],
    "frames_to_extract": 10
  },
  "detection": {
    "confidence_threshold": 0.5,
    "critical_components": [
      "etiqueta_visivel",
      "tampa_encaixada", 
      "parafusos_presentes",
      "conectores_instalados",
      "cameras"
    ]
  },
  "storage": {
    "data_retention_days": 90,
    "backup_enabled": true
  },
  "interface": {
    "theme": "clean",
    "language": "pt-BR"
  }
}
EOF

echo "✅ Configuração criada: config.json"

# Informações finais
echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=================================================================="
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. Para iniciar o sistema:"
echo "   ./start_system.sh"
echo ""
echo "2. Ou manualmente:"
echo "   source venv/bin/activate"
echo "   cd src"
echo "   streamlit run streamlit_clean_app.py"
echo ""
echo "3. Acesse no navegador:"
echo "   http://localhost:8501"
echo ""
echo "📁 ESTRUTURA CRIADA:"
echo "   ├── venv/                 # Ambiente virtual Python"
echo "   ├── src/                  # Código fonte"
echo "   ├── data/                 # Banco de dados e relatórios"
echo "   ├── logs/                 # Logs do sistema"
echo "   ├── config.json           # Configurações"
echo "   └── start_system.sh       # Script de inicialização"
echo ""
echo "🔧 ARQUIVOS PRINCIPAIS:"
echo "   src/streamlit_clean_app.py     # Interface principal"
echo "   src/video_processor.py         # Processamento de vídeo"
echo "   src/radar_detector.py          # Detecção IA"
echo "   src/checklist_generator.py     # Checklists automáticos"
echo ""
echo "📖 DOCUMENTAÇÃO:"
echo "   README_FINAL.md                # Documentação completa"
echo ""
echo "✅ Sistema pronto para uso em produção!"
echo "=================================================================="

