# Sistema de Verificação Visual Automatizada

Sistema MVP para inspeção automatizada de equipamentos com upload de vídeo, detecção IA e checklist automático.

## 🚀 Instalação Rápida

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar sistema
streamlit run streamlit_clean_app.py
```

## 📋 Funcionalidades

- **Upload de Vídeo**: Suporte a MP4, MOV, AVI, MKV, WMV
- **Extração de Frames**: 10 frames distribuídos automaticamente
- **Detecção IA**: YOLOv8 para componentes de equipamentos radar
- **Bounding Boxes**: Visualização com legendas e confiança
- **Checklist Automático**: Decisão final LIBERAR LACRE ou REVISAR
- **Interface Responsiva**: Design limpo e profissional

## 🎯 Como Usar

1. Preencha nome do técnico e número da OP
2. Faça upload do vídeo do equipamento finalizado
3. Clique em "Analisar Vídeo"
4. Revise os resultados frame-by-frame
5. Baixe o checklist ou salve a inspeção

## 📊 Componentes Detectados

**Críticos:**
- Etiqueta visível
- Tampa encaixada
- Parafusos presentes
- Conectores instalados
- Câmeras

**Opcionais:**
- Cabeamento
- Suportes

## 🔧 Arquivos Principais

- `streamlit_clean_app.py` - Interface principal
- `video_processor.py` - Processamento de vídeo
- `radar_detector.py` - Detecção IA
- `checklist_generator.py` - Bounding boxes e checklists
- `data_storage.py` - Banco de dados SQLite

## ⚡ Requisitos

- Python 3.8+
- 4GB RAM
- Conexão com internet (download de modelos IA)

## 📞 Status

✅ Sistema testado e funcional  
✅ Pronto para produção  
✅ Interface responsiva  
✅ Testes 100% aprovados

