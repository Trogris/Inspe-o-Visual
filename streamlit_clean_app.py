#!/usr/bin/env python3
"""
Sistema de Verificação Visual Automatizada - Interface Limpa e Responsiva
Análise frame-by-frame com bounding boxes e checklist automático
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os
import sys
from PIL import Image
import tempfile
import json

# Configuração da página
st.set_page_config(
    page_title="Sistema de Verificação Visual",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adicionar diretório src ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos do sistema
try:
    from video_processor import VideoProcessor
    from radar_detector import RadarEquipmentDetector
    from data_storage import DataStorage
    from checklist_generator import ChecklistGenerator
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# CSS customizado - Design limpo e responsivo
st.markdown("""
<style>
    /* Reset e base */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Cabeçalho principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Cards de status */
    .status-card {
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .status-approved {
        background-color: #f0f9f0;
        border-left-color: #28a745;
        color: #155724;
    }
    
    .status-rejected {
        background-color: #fdf2f2;
        border-left-color: #dc3545;
        color: #721c24;
    }
    
    .status-review {
        background-color: #fffbf0;
        border-left-color: #ffc107;
        color: #856404;
    }
    
    /* Componentes */
    .component-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #e9ecef;
    }
    
    .component-ok {
        border-left: 3px solid #28a745;
    }
    
    .component-missing {
        border-left: 3px solid #dc3545;
    }
    
    .component-warning {
        border-left: 3px solid #ffc107;
    }
    
    /* Frame container */
    .frame-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e9ecef;
    }
    
    /* Métricas */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #495057;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }
    
    /* Upload area */
    .upload-area {
        border: 2px dashed #ced4da;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #667eea;
        background: #f0f2ff;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    /* Responsivo */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .frame-container {
            padding: 1rem;
        }
    }
    
    /* Botões */
    .stButton > button {
        border-radius: 6px;
        border: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Checklist */
    .checklist-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #e9ecef;
    }
    
    .checklist-item:last-child {
        border-bottom: none;
    }
    
    .checklist-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }
    
    .confidence-bar {
        width: 100px;
        height: 8px;
        background: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização de componentes
@st.cache_resource
def init_components():
    """Inicializa componentes do sistema"""
    video_processor = VideoProcessor()
    radar_detector = RadarEquipmentDetector()
    radar_detector.load_model()
    storage = DataStorage()
    checklist_generator = ChecklistGenerator()
    return video_processor, radar_detector, storage, checklist_generator

def display_component_status(component_name, component_data):
    """Exibe status de um componente de forma limpa"""
    detected = component_data['detected']
    confidence = component_data['confidence']
    details = component_data['details']
    critical = component_data['critical']
    
    # Determinar classe CSS
    if detected:
        css_class = "component-ok"
        icon = "✓"
        status_text = "Detectado"
        status_color = "#28a745"
    else:
        css_class = "component-missing" if critical else "component-warning"
        icon = "✗" if critical else "○"
        status_text = "Não detectado" if critical else "Ausente"
        status_color = "#dc3545" if critical else "#ffc107"
    
    # Nome formatado
    display_name = component_name.replace('_', ' ').title()
    
    # HTML do componente
    component_html = f"""
    <div class="component-item {css_class}">
        <div style="display: flex; align-items: center; flex: 1;">
            <span class="checklist-icon" style="color: {status_color};">{icon}</span>
            <div>
                <strong>{display_name}</strong>
                {' <span style="color: #dc3545; font-size: 0.8rem;">(Crítico)</span>' if critical else ''}
                <br>
                <small style="color: #6c757d;">{details}</small>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="color: {status_color}; font-weight: bold; font-size: 0.9rem;">
                {status_text}
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence * 100}%;"></div>
            </div>
            <small style="color: #6c757d;">{confidence:.1%}</small>
        </div>
    </div>
    """
    
    st.markdown(component_html, unsafe_allow_html=True)

def display_frame_analysis(frame_number, frame, analysis_result, checklist_generator):
    """Exibe análise de um frame com bounding boxes"""
    
    st.markdown('<div class="frame-container">', unsafe_allow_html=True)
    
    # Cabeçalho do frame
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"Frame {frame_number}")
    
    with col2:
        score = analysis_result['overall_score']
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{score:.1%}</div>
            <div class="metric-label">Score Geral</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        status = analysis_result['status']
        if status == 'APROVADO':
            status_html = '<div class="status-card status-approved"><strong>Aprovado</strong></div>'
        elif status == 'REPROVADO':
            status_html = '<div class="status-card status-rejected"><strong>Reprovado</strong></div>'
        else:
            status_html = '<div class="status-card status-review"><strong>Revisar</strong></div>'
        
        st.markdown(status_html, unsafe_allow_html=True)
    
    # Layout principal do frame
    col_img, col_analysis = st.columns([1, 1])
    
    with col_img:
        # Desenhar bounding boxes
        annotated_frame = checklist_generator.draw_bounding_boxes(frame, analysis_result)
        st.image(annotated_frame, caption=f"Frame {frame_number} com detecções", use_container_width=True)
    
    with col_analysis:
        st.markdown("### Checklist de Componentes")
        
        # Exibir cada componente
        for component_name, component_data in analysis_result['components'].items():
            display_component_status(component_name, component_data)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_consolidated_checklist(consolidated_checklist):
    """Exibe checklist consolidado"""
    
    st.markdown("## Checklist Final Consolidado")
    
    info = consolidated_checklist['inspection_info']
    summary = consolidated_checklist['summary']
    components = consolidated_checklist['components_analysis']
    
    # Informações da inspeção
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Informações da Inspeção")
        st.markdown(f"**Operador:** {info['operator_name']}")
        st.markdown(f"**OP:** {info['op_number']}")
        st.markdown(f"**Data/Hora:** {info['inspection_date']}")
        st.markdown(f"**Arquivo:** {info['video_filename']}")
    
    with col2:
        st.markdown("### Estatísticas")
        st.markdown(f"**Duração:** {info['video_duration']}")
        st.markdown(f"**Frames Analisados:** {info['total_frames']}")
        st.markdown(f"**Score Geral:** {summary['overall_score']:.1%}")
    
    # Decisão final
    st.markdown("### Decisão Final")
    
    decision = summary['final_decision']
    if decision == 'LIBERAR_LACRE':
        st.markdown("""
        <div class="status-card status-approved">
            <h4 style="margin: 0;">✓ EQUIPAMENTO APROVADO - LIBERAR PARA LACRE</h4>
            <p style="margin: 0.5rem 0 0 0;">Todos os componentes críticos foram detectados adequadamente.</p>
        </div>
        """, unsafe_allow_html=True)
    elif decision == 'REVISAR_EQUIPAMENTO':
        st.markdown("""
        <div class="status-card status-review">
            <h4 style="margin: 0;">⚠ EQUIPAMENTO REQUER REVISÃO</h4>
            <p style="margin: 0.5rem 0 0 0;">Alguns componentes críticos não foram detectados adequadamente.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-card status-rejected">
            <h4 style="margin: 0;">✗ EQUIPAMENTO REPROVADO</h4>
            <p style="margin: 0.5rem 0 0 0;">Falhas críticas detectadas. Revisar montagem.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Análise por componente
    st.markdown("### Análise por Componente")
    
    # Separar componentes críticos e opcionais
    critical_components = [comp for comp in components.values() if comp['critical']]
    optional_components = [comp for comp in components.values() if not comp['critical']]
    
    # Componentes críticos
    if critical_components:
        st.markdown("#### Componentes Críticos")
        
        for comp in critical_components:
            detected = comp['final_status'] == 'DETECTED'
            icon = "✓" if detected else "✗"
            color = "#28a745" if detected else "#dc3545"
            
            st.markdown(f"""
            <div class="component-item {'component-ok' if detected else 'component-missing'}">
                <div style="display: flex; align-items: center; flex: 1;">
                    <span class="checklist-icon" style="color: {color};">{icon}</span>
                    <div>
                        <strong>{comp['component_name']}</strong>
                        <br>
                        <small style="color: #6c757d;">
                            Detectado em {comp['detected_in_frames']}/{comp['total_frames']} frames 
                            ({comp['detection_rate']:.1%})
                        </small>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="color: {color}; font-weight: bold; font-size: 0.9rem;">
                        {comp['final_status'].replace('_', ' ').title()}
                    </div>
                    <small style="color: #6c757d;">Conf: {comp['average_confidence']:.1%}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Componentes opcionais
    if optional_components:
        st.markdown("#### Componentes Opcionais")
        
        for comp in optional_components:
            detected = comp['final_status'] == 'DETECTED'
            icon = "✓" if detected else "○"
            color = "#28a745" if detected else "#6c757d"
            
            st.markdown(f"""
            <div class="component-item">
                <div style="display: flex; align-items: center; flex: 1;">
                    <span class="checklist-icon" style="color: {color};">{icon}</span>
                    <div>
                        <strong>{comp['component_name']}</strong>
                        <br>
                        <small style="color: #6c757d;">
                            Detectado em {comp['detected_in_frames']}/{comp['total_frames']} frames 
                            ({comp['detection_rate']:.1%})
                        </small>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="color: {color}; font-weight: bold; font-size: 0.9rem;">
                        {comp['final_status'].replace('_', ' ').title()}
                    </div>
                    <small style="color: #6c757d;">Conf: {comp['average_confidence']:.1%}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    
    # Cabeçalho principal
    st.markdown("""
    <div class="main-header">
        <h1>Sistema de Verificação Visual Automatizada</h1>
        <p>Análise inteligente de equipamentos com IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar componentes
    video_processor, radar_detector, storage, checklist_generator = init_components()
    
    # Sidebar com configurações
    with st.sidebar:
        st.markdown("### Configurações da Inspeção")
        
        operator_name = st.text_input("Nome do Técnico", placeholder="Ex: João Silva")
        op_number = st.text_input("Número da OP", placeholder="Ex: OP-2025-001")
        
        st.markdown("---")
        
        st.markdown("### Componentes Monitorados")
        
        st.markdown("""
        **Críticos:**
        - Etiqueta visível
        - Tampa encaixada
        - Parafusos presentes
        - Conectores instalados
        - Câmeras
        
        **Opcionais:**
        - Cabeamento
        - Suportes
        """)
    
    # Seção de upload de vídeo
    st.markdown("## Upload do Vídeo")
    
    uploaded_video = st.file_uploader(
        "Selecione o vídeo do equipamento finalizado",
        type=['mp4', 'mov', 'avi', 'mkv', 'wmv'],
        help="Formatos suportados: MP4, MOV, AVI, MKV, WMV (máximo 100MB)"
    )
    
    if uploaded_video is not None:
        # Validar arquivo
        if not video_processor.validate_video_file(uploaded_video):
            st.error("Arquivo de vídeo inválido ou muito grande (máximo 100MB)")
            return
        
        # Obter informações do vídeo
        video_info = video_processor.get_video_info(uploaded_video)
        
        # Exibir informações do vídeo
        st.success("Vídeo carregado com sucesso!")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{video_info['filename'][:15]}...</div>
                <div class="metric-label">Arquivo</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{video_info['size_mb']:.1f} MB</div>
                <div class="metric-label">Tamanho</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{video_info['duration']:.1f}s</div>
                <div class="metric-label">Duração</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{video_info['resolution'][0]}x{video_info['resolution'][1]}</div>
                <div class="metric-label">Resolução</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Botão para processar vídeo
        if st.button("Analisar Vídeo", type="primary", use_container_width=True):
            
            if not operator_name or not op_number:
                st.error("Preencha o nome do técnico e número da OP")
                return
            
            # Processar vídeo
            with st.spinner("Extraindo frames do vídeo..."):
                frames = video_processor.extract_frames_from_video(uploaded_video, num_frames=10)
            
            if not frames:
                st.error("Falha na extração de frames")
                return
            
            st.success(f"{len(frames)} frames extraídos com sucesso!")
            
            # Analisar cada frame
            all_analyses = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, frame in enumerate(frames):
                status_text.text(f"Analisando frame {i+1}/{len(frames)}...")
                progress_bar.progress((i + 1) / len(frames))
                
                # Analisar frame
                analysis_result = radar_detector.analyze_frame(frame)
                all_analyses.append(analysis_result)
            
            progress_bar.empty()
            status_text.empty()
            
            # Gerar checklist consolidado
            operator_info = {'operator_name': operator_name, 'op_number': op_number}
            consolidated_checklist = checklist_generator.generate_consolidated_checklist(
                all_analyses, video_info, operator_info
            )
            
            # Salvar no session state
            st.session_state.frames = frames
            st.session_state.analyses = all_analyses
            st.session_state.video_info = video_info
            st.session_state.operator_info = operator_info
            st.session_state.consolidated_checklist = consolidated_checklist
            
            st.success("Análise concluída!")
    
    # Exibir resultados se disponíveis
    if 'consolidated_checklist' in st.session_state:
        
        frames = st.session_state.frames
        analyses = st.session_state.analyses
        consolidated_checklist = st.session_state.consolidated_checklist
        
        # Exibir checklist consolidado
        display_consolidated_checklist(consolidated_checklist)
        
        # Análise frame por frame
        st.markdown("## Análise Frame por Frame")
        
        # Seletor de frame
        frame_options = [f"Frame {i+1}" for i in range(len(frames))]
        selected_frame_idx = st.selectbox("Selecione um frame para visualizar:", 
                                        range(len(frame_options)), 
                                        format_func=lambda x: frame_options[x])
        
        # Exibir frame selecionado
        if selected_frame_idx is not None:
            display_frame_analysis(selected_frame_idx + 1, 
                                 frames[selected_frame_idx], 
                                 analyses[selected_frame_idx],
                                 checklist_generator)
        
        # Ações finais
        st.markdown("## Ações")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Salvar Inspeção", type="primary"):
                try:
                    # Preparar dados para salvamento
                    inspection_data = {
                        'main': {
                            'op_number': st.session_state.operator_info['op_number'],
                            'operator_name': st.session_state.operator_info['operator_name'],
                            'equipment_code': f"EQ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            'final_status': consolidated_checklist['summary']['final_decision'],
                            'video_filename': st.session_state.video_info['filename'],
                            'total_frames': len(frames),
                            'average_score': consolidated_checklist['summary']['overall_score']
                        },
                        'consolidated_checklist': consolidated_checklist
                    }
                    
                    # Salvar primeiro frame como imagem representativa
                    inspection_id = storage.save_inspection(inspection_data, frames[0])
                    
                    if inspection_id:
                        st.success(f"Inspeção salva! ID: {inspection_id}")
                    else:
                        st.error("Falha ao salvar inspeção")
                        
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
        
        with col2:
            # Download do checklist
            checklist_text = checklist_generator.format_checklist_for_display(consolidated_checklist)
            st.download_button(
                label="Download Checklist",
                data=checklist_text,
                file_name=f"checklist_{st.session_state.operator_info['op_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        with col3:
            if st.button("Nova Análise"):
                # Limpar session state
                for key in ['frames', 'analyses', 'video_info', 'operator_info', 'consolidated_checklist']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Estatísticas históricas
    st.markdown("## Estatísticas do Sistema")
    
    try:
        stats = storage.get_statistics()
        if stats and stats.get('totals'):
            totals = stats['totals']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{totals.get('total_inspections', 0)}</div>
                    <div class="metric-label">Total de Inspeções</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{totals.get('approved_inspections', 0)}</div>
                    <div class="metric-label">Aprovadas</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{totals.get('rejected_inspections', 0)}</div>
                    <div class="metric-label">Reprovadas</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{totals.get('approval_rate', 0):.1f}%</div>
                    <div class="metric-label">Taxa de Aprovação</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma estatística disponível ainda")
    except Exception as e:
        st.warning(f"Erro ao carregar estatísticas: {e}")

if __name__ == "__main__":
    main()

