#!/usr/bin/env python3
"""
Sistema de Verificação Visual Automatizada
Interface Streamlit - Versão Funcional Corrigida
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import tempfile
import os
import json
from typing import Dict, List, Optional, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos do sistema
try:
    from video_processor import VideoProcessor
    from radar_detector import RadarEquipmentDetector
    from checklist_generator import ChecklistGenerator
    from data_storage import DataStorage
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="Sistema de Verificação Visual",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para interface limpa
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .status-approved {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        font-weight: bold;
        font-size: 1.2em;
        text-align: center;
        margin: 1rem 0;
    }
    
    .status-review {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        font-weight: bold;
        font-size: 1.2em;
        text-align: center;
        margin: 1rem 0;
    }
    
    .component-critical {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 4px;
        border-left: 3px solid #ffc107;
        margin: 0.2rem 0;
    }
    
    .component-optional {
        background-color: #e2e3e5;
        padding: 0.5rem;
        border-radius: 4px;
        border-left: 3px solid #6c757d;
        margin: 0.2rem 0;
    }
    
    .upload-success {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%);
        border: none;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Inicializa variáveis de sessão"""
    if 'video_processor' not in st.session_state:
        st.session_state.video_processor = VideoProcessor()
    
    if 'radar_detector' not in st.session_state:
        st.session_state.radar_detector = RadarEquipmentDetector()
    
    if 'checklist_generator' not in st.session_state:
        st.session_state.checklist_generator = ChecklistGenerator()
    
    if 'data_storage' not in st.session_state:
        st.session_state.data_storage = DataStorage()
    
    if 'current_video' not in st.session_state:
        st.session_state.current_video = None
    
    if 'extracted_frames' not in st.session_state:
        st.session_state.extracted_frames = []
    
    if 'frame_analyses' not in st.session_state:
        st.session_state.frame_analyses = []
    
    if 'consolidated_checklist' not in st.session_state:
        st.session_state.consolidated_checklist = None
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

def render_header():
    """Renderiza cabeçalho da aplicação"""
    st.markdown("""
    <div class="main-header">
        <h1>Sistema de Verificação Visual Automatizada</h1>
        <p>Análise inteligente de equipamentos com IA</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderiza barra lateral com configurações"""
    st.sidebar.header("Configuração da Inspeção")
    
    # Informações do operador
    operator_name = st.sidebar.text_input(
        "Nome do Técnico",
        value="",
        placeholder="Digite o nome do técnico"
    )
    
    op_number = st.sidebar.text_input(
        "Número da OP",
        value="",
        placeholder="Ex: OP-2025-001"
    )
    
    st.sidebar.markdown("---")
    
    # Componentes monitorados
    st.sidebar.subheader("Componentes Monitorados")
    
    st.sidebar.markdown("**Críticos:**")
    critical_components = [
        "Etiqueta visível",
        "Tampa encaixada", 
        "Parafusos presentes",
        "Conectores instalados",
        "Câmeras"
    ]
    
    for component in critical_components:
        st.sidebar.markdown(f'<div class="component-critical">{component}</div>', 
                          unsafe_allow_html=True)
    
    st.sidebar.markdown("**Opcionais:**")
    optional_components = [
        "Cabeamento",
        "Suportes"
    ]
    
    for component in optional_components:
        st.sidebar.markdown(f'<div class="component-optional">{component}</div>', 
                          unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Estatísticas
    st.sidebar.subheader("Estatísticas")
    try:
        stats = st.session_state.data_storage.get_statistics()
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total", stats.get('total_inspections', 0))
        with col2:
            approval_rate = stats.get('approval_rate', 0)
            st.metric("Aprovação", f"{approval_rate:.1f}%")
    except:
        st.sidebar.write("Estatísticas não disponíveis")
    
    return operator_name, op_number

def render_video_upload():
    """Renderiza área de upload de vídeo"""
    st.subheader("Upload do Vídeo")
    
    uploaded_file = st.file_uploader(
        "Selecione o vídeo do equipamento finalizado",
        type=['mp4', 'mov', 'avi', 'mkv', 'wmv'],
        help="Arraste o arquivo ou clique para selecionar"
    )
    
    if uploaded_file is not None:
        # Validar arquivo
        if st.session_state.video_processor.validate_video_file(uploaded_file):
            st.markdown(f"""
            <div class="upload-success">
                ✅ Vídeo carregado com sucesso: <strong>{uploaded_file.name}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            st.session_state.current_video = uploaded_file
            return uploaded_file
        else:
            st.error("Arquivo de vídeo inválido ou muito grande (máximo 200MB)")
    
    return None

def render_analysis_section(uploaded_file, operator_name, op_number):
    """Renderiza seção de análise"""
    if uploaded_file is None:
        st.info("📤 Faça upload de um vídeo para iniciar a análise")
        return
    
    if not operator_name or not op_number:
        st.warning("⚠️ Preencha o nome do técnico e número da OP na barra lateral")
        return
    
    st.subheader("Análise do Vídeo")
    
    # Botão para iniciar análise
    if st.button("🔍 Analisar Vídeo", type="primary"):
        analyze_video(uploaded_file, operator_name, op_number)
    
    # Mostrar resultados se análise foi concluída
    if st.session_state.analysis_complete:
        render_analysis_results()

def analyze_video(uploaded_file, operator_name, op_number):
    """Executa análise completa do vídeo"""
    try:
        # Container para progresso
        progress_container = st.container()
        
        with progress_container:
            # Barra de progresso (valores entre 0.0 e 1.0)
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            # Passo 1: Extrair frames
            status_text.text("🎬 Extraindo frames do vídeo...")
            progress_bar.progress(0.2)
            
            frames = st.session_state.video_processor.extract_frames_from_video(uploaded_file, num_frames=10)
            
            if not frames:
                st.error("❌ Falha na extração de frames. Verifique se o vídeo está correto.")
                progress_bar.empty()
                status_text.empty()
                return
            
            st.session_state.extracted_frames = frames
            
            # Passo 2: Carregar modelo IA
            status_text.text("🤖 Carregando modelo de IA...")
            progress_bar.progress(0.4)
            
            st.session_state.radar_detector.load_model()
            
            # Passo 3: Analisar frames
            status_text.text("🔍 Analisando frames com IA...")
            progress_bar.progress(0.6)
            
            analyses = []
            for i, frame in enumerate(frames):
                analysis = st.session_state.radar_detector.analyze_frame(frame)
                analyses.append(analysis)
                # Progresso entre 0.6 e 0.8
                current_progress = 0.6 + (i + 1) * 0.2 / len(frames)
                progress_bar.progress(current_progress)
            
            st.session_state.frame_analyses = analyses
            
            # Passo 4: Gerar checklist consolidado
            status_text.text("📋 Gerando checklist consolidado...")
            progress_bar.progress(0.9)
            
            video_info = {
                'filename': uploaded_file.name,
                'size_mb': uploaded_file.size / (1024 * 1024)
            }
            
            operator_info = {
                'operator_name': operator_name,
                'op_number': op_number
            }
            
            consolidated = st.session_state.checklist_generator.generate_consolidated_checklist(
                analyses, video_info, operator_info
            )
            
            st.session_state.consolidated_checklist = consolidated
            
            # Passo 5: Finalizar
            status_text.text("✅ Análise concluída!")
            progress_bar.progress(1.0)
            
            st.session_state.analysis_complete = True
            
            # Limpar barra de progresso
            import time
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
        
        st.success("🎉 Análise concluída com sucesso!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro durante análise: {str(e)}")
        logger.error(f"Erro na análise: {e}")

def render_analysis_results():
    """Renderiza resultados da análise"""
    if not st.session_state.consolidated_checklist:
        return
    
    checklist = st.session_state.consolidated_checklist
    
    st.subheader("Resultados da Análise")
    
    # Decisão final
    decision = checklist['summary']['final_decision']
    score = checklist['summary']['overall_score']
    
    if decision == "LIBERAR_LACRE":
        st.markdown(f"""
        <div class="status-approved">
            ✅ LIBERAR LACRE<br>
            Equipamento aprovado com score: {score:.1f}%
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-review">
            ⚠️ REVISAR EQUIPAMENTO<br>
            Equipamento precisa de revisão. Score: {score:.1f}%
        </div>
        """, unsafe_allow_html=True)
    
    # Resumo dos componentes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Componentes Críticos")
        for component, data in checklist['components_analysis'].items():
            if data.get('critical', False):
                status = "✅" if data['detected'] else "❌"
                confidence = data.get('confidence', 0)
                st.write(f"{status} **{component.replace('_', ' ').title()}**: {confidence:.1f}%")
    
    with col2:
        st.subheader("Componentes Opcionais")
        for component, data in checklist['components_analysis'].items():
            if not data.get('critical', True):
                status = "✅" if data['detected'] else "❌"
                confidence = data.get('confidence', 0)
                st.write(f"{status} **{component.replace('_', ' ').title()}**: {confidence:.1f}%")
    
    # Análise frame-by-frame
    st.subheader("Análise Frame-by-Frame")
    
    if st.session_state.extracted_frames:
        frame_options = [f"Frame {i+1}" for i in range(len(st.session_state.extracted_frames))]
        selected_frame_idx = st.selectbox("Selecione um frame:", range(len(frame_options)), 
                                        format_func=lambda x: frame_options[x])
        
        if selected_frame_idx is not None:
            frame = st.session_state.extracted_frames[selected_frame_idx]
            analysis = st.session_state.frame_analyses[selected_frame_idx]
            
            # Desenhar bounding boxes
            annotated_frame = st.session_state.checklist_generator.draw_bounding_boxes(frame, analysis)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.image(annotated_frame, caption=f"Frame {selected_frame_idx + 1} com detecções", 
                        use_column_width=True)
            
            with col2:
                st.subheader(f"Checklist Frame {selected_frame_idx + 1}")
                frame_checklist = st.session_state.checklist_generator.generate_frame_checklist(
                    selected_frame_idx + 1, analysis
                )
                
                for item in frame_checklist['items']:
                    status = "✅" if item['detected'] else "❌"
                    st.write(f"{status} **{item['component']}**: {item['confidence']:.1f}%")
    
    # Ações finais
    st.subheader("Ações")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar Inspeção"):
            save_inspection()
    
    with col2:
        if st.button("📄 Download Checklist"):
            download_checklist()
    
    with col3:
        if st.button("🔄 Nova Análise"):
            reset_analysis()

def save_inspection():
    """Salva inspeção no banco de dados"""
    try:
        if not st.session_state.consolidated_checklist:
            st.error("Nenhuma análise para salvar")
            return
        
        checklist = st.session_state.consolidated_checklist
        
        inspection_data = {
            'main': {
                'op_number': checklist['inspection_info']['op_number'],
                'operator_name': checklist['inspection_info']['operator_name'],
                'equipment_code': f"EQ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'final_status': checklist['summary']['final_decision'],
                'video_filename': checklist['inspection_info']['video_filename'],
                'total_frames': len(st.session_state.extracted_frames),
                'average_score': checklist['summary']['overall_score']
            },
            'consolidated_checklist': checklist
        }
        
        inspection_id = st.session_state.data_storage.save_inspection(inspection_data)
        
        if inspection_id:
            st.success(f"✅ Inspeção salva com ID: {inspection_id}")
        else:
            st.error("❌ Falha ao salvar inspeção")
            
    except Exception as e:
        st.error(f"❌ Erro ao salvar: {str(e)}")

def download_checklist():
    """Gera download do checklist"""
    try:
        if not st.session_state.consolidated_checklist:
            st.error("Nenhum checklist para download")
            return
        
        report_text = st.session_state.checklist_generator.format_checklist_for_display(
            st.session_state.consolidated_checklist
        )
        
        st.download_button(
            label="📥 Baixar Relatório",
            data=report_text,
            file_name=f"checklist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"❌ Erro ao gerar download: {str(e)}")

def reset_analysis():
    """Reseta análise para nova inspeção"""
    st.session_state.current_video = None
    st.session_state.extracted_frames = []
    st.session_state.frame_analyses = []
    st.session_state.consolidated_checklist = None
    st.session_state.analysis_complete = False
    st.rerun()

def main():
    """Função principal da aplicação"""
    # Inicializar estado da sessão
    initialize_session_state()
    
    # Renderizar interface
    render_header()
    
    # Barra lateral
    operator_name, op_number = render_sidebar()
    
    # Conteúdo principal
    uploaded_file = render_video_upload()
    
    # Seção de análise
    render_analysis_section(uploaded_file, operator_name, op_number)

if __name__ == "__main__":
    main()

