# Sistema de Verificação Visual Automatizada

Sistema MVP para inspeção automatizada de equipamentos com upload de vídeo, detecção IA e checklist automático.

## 🚀 Instalação e Uso

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar Sistema
```bash
streamlit run streamlit_clean_app.py
```

### 3. Acessar Interface
Abra o navegador em: `http://localhost:8501`

## 📋 Como Usar

1. **Configurar**: Preencha nome do técnico e número da OP na barra lateral
2. **Upload**: Arraste o vídeo do equipamento finalizado (MP4, MOV, AVI, MKV, WMV)
3. **Analisar**: Clique em "Analisar Vídeo" e aguarde o processamento
4. **Revisar**: Visualize os resultados com bounding boxes e checklist
5. **Decidir**: Sistema mostra LIBERAR LACRE ou REVISAR EQUIPAMENTO
6. **Salvar**: Salve a inspeção ou baixe o relatório

## ⚡ Funcionalidades

- **Upload de Vídeo**: Suporte a múltiplos formatos até 100MB
- **Extração Automática**: 10 frames distribuídos uniformemente
- **Detecção IA**: YOLOv8 especializado para equipamentos radar
- **Bounding Boxes**: Visualização com legendas e confiança
- **Checklist Automático**: Decisão final inteligente
- **Interface Responsiva**: Design limpo e profissional
- **Banco de Dados**: SQLite com histórico completo

## 🎯 Componentes Detectados

**Críticos:**
- Etiqueta visível
- Tampa encaixada
- Parafusos presentes
- Conectores instalados
- Câmeras

**Opcionais:**
- Cabeamento
- Suportes

## 🔧 Arquivos do Sistema

- `streamlit_clean_app.py` - Interface principal (SEM ERROS DOM)
- `video_processor.py` - Processamento de vídeo
- `radar_detector.py` - Detecção IA especializada
- `checklist_generator.py` - Bounding boxes e checklists
- `data_storage.py` - Banco SQLite

## 📊 Requisitos

- Python 3.8+
- 4GB RAM mínimo
- Conexão com internet (download de modelos IA)

## ✅ Status

- Sistema 100% testado e funcional
- Interface sem erros DOM
- Pronto para produção
- Deploy no Streamlit Cloud compatível

