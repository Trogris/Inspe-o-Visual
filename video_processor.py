#!/usr/bin/env python3
"""
Módulo de Processamento de Vídeo - Sistema de Verificação Visual
Extrai frames de vídeos para análise de equipamentos radar de trânsito
"""

import cv2
import numpy as np
import os
import tempfile
from datetime import datetime
import logging
from typing import List, Tuple, Optional
import streamlit as st

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    """
    Classe para processamento de vídeos de equipamentos radar
    """
    
    def __init__(self):
        """Inicializa o processador de vídeo"""
        self.supported_formats = ['.mp4', '.mov', '.avi', '.mkv', '.wmv']
        self.target_frames = 10
        logger.info("Processador de vídeo inicializado")
    
    def validate_video_file(self, video_file) -> bool:
        """
        Valida se o arquivo de vídeo é suportado
        
        Args:
            video_file: Arquivo de vídeo carregado
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            if video_file is None:
                return False
            
            # Verificar extensão
            file_extension = os.path.splitext(video_file.name)[1].lower()
            if file_extension not in self.supported_formats:
                logger.warning(f"Formato não suportado: {file_extension}")
                return False
            
            # Verificar tamanho (máximo 100MB)
            if video_file.size > 100 * 1024 * 1024:
                logger.warning(f"Arquivo muito grande: {video_file.size} bytes")
                return False
            
            logger.info(f"Arquivo válido: {video_file.name} ({video_file.size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return False
    
    def extract_frames_from_video(self, video_file, num_frames: int = 10) -> List[np.ndarray]:
        """
        Extrai frames distribuídos uniformemente do vídeo
        
        Args:
            video_file: Arquivo de vídeo carregado
            num_frames: Número de frames a extrair (padrão: 10)
            
        Returns:
            List[np.ndarray]: Lista de frames extraídos
        """
        frames = []
        temp_path = None
        
        try:
            # Salvar vídeo temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_path = temp_file.name
                temp_file.write(video_file.read())
            
            # Abrir vídeo com OpenCV
            cap = cv2.VideoCapture(temp_path)
            
            if not cap.isOpened():
                logger.error("Não foi possível abrir o vídeo")
                return frames
            
            # Obter informações do vídeo
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Vídeo: {total_frames} frames, {fps:.2f} FPS, {duration:.2f}s")
            
            if total_frames < num_frames:
                logger.warning(f"Vídeo tem apenas {total_frames} frames, extraindo todos")
                num_frames = total_frames
            
            # Calcular posições dos frames
            frame_positions = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            
            for i, frame_pos in enumerate(frame_positions):
                # Ir para a posição do frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                
                # Ler frame
                ret, frame = cap.read()
                
                if ret:
                    # Converter BGR para RGB (OpenCV usa BGR, mas queremos RGB)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                    
                    timestamp = frame_pos / fps if fps > 0 else 0
                    logger.info(f"Frame {i+1}/{num_frames} extraído (posição: {frame_pos}, tempo: {timestamp:.2f}s)")
                else:
                    logger.warning(f"Falha ao ler frame na posição {frame_pos}")
            
            cap.release()
            
            logger.info(f"Extração concluída: {len(frames)} frames extraídos")
            
        except Exception as e:
            logger.error(f"Erro na extração de frames: {e}")
        
        finally:
            # Limpar arquivo temporário
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logger.warning(f"Erro ao remover arquivo temporário: {e}")
        
        return frames
    
    def get_video_info(self, video_file) -> dict:
        """
        Obtém informações detalhadas do vídeo
        
        Args:
            video_file: Arquivo de vídeo carregado
            
        Returns:
            dict: Informações do vídeo
        """
        info = {
            'filename': '',
            'size_mb': 0,
            'duration': 0,
            'fps': 0,
            'total_frames': 0,
            'resolution': (0, 0),
            'format': ''
        }
        
        temp_path = None
        
        try:
            # Informações básicas do arquivo
            info['filename'] = video_file.name
            info['size_mb'] = video_file.size / (1024 * 1024)
            info['format'] = os.path.splitext(video_file.name)[1].lower()
            
            # Salvar temporariamente para análise
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_path = temp_file.name
                temp_file.write(video_file.read())
            
            # Analisar com OpenCV
            cap = cv2.VideoCapture(temp_path)
            
            if cap.isOpened():
                info['total_frames'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                info['fps'] = cap.get(cv2.CAP_PROP_FPS)
                info['duration'] = info['total_frames'] / info['fps'] if info['fps'] > 0 else 0
                
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                info['resolution'] = (width, height)
                
                cap.release()
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do vídeo: {e}")
        
        finally:
            # Limpar arquivo temporário
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logger.warning(f"Erro ao remover arquivo temporário: {e}")
        
        return info
    
    def save_frames(self, frames: List[np.ndarray], output_dir: str, prefix: str = "frame") -> List[str]:
        """
        Salva frames extraídos como imagens
        
        Args:
            frames: Lista de frames
            output_dir: Diretório de saída
            prefix: Prefixo para nomes dos arquivos
            
        Returns:
            List[str]: Lista de caminhos dos arquivos salvos
        """
        saved_paths = []
        
        try:
            # Criar diretório se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, frame in enumerate(frames):
                filename = f"{prefix}_{timestamp}_{i+1:02d}.jpg"
                filepath = os.path.join(output_dir, filename)
                
                # Converter RGB para BGR para salvar com OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Salvar imagem
                success = cv2.imwrite(filepath, frame_bgr)
                
                if success:
                    saved_paths.append(filepath)
                    logger.info(f"Frame {i+1} salvo: {filepath}")
                else:
                    logger.error(f"Falha ao salvar frame {i+1}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar frames: {e}")
        
        return saved_paths
    
    def create_frame_summary(self, frames: List[np.ndarray], video_info: dict) -> dict:
        """
        Cria resumo dos frames extraídos
        
        Args:
            frames: Lista de frames extraídos
            video_info: Informações do vídeo
            
        Returns:
            dict: Resumo dos frames
        """
        summary = {
            'total_frames_extracted': len(frames),
            'extraction_timestamp': datetime.now().isoformat(),
            'video_info': video_info,
            'frame_details': []
        }
        
        try:
            duration = video_info.get('duration', 0)
            total_frames = video_info.get('total_frames', 0)
            
            for i, frame in enumerate(frames):
                # Calcular timestamp do frame
                if duration > 0 and len(frames) > 1:
                    timestamp = (duration / (len(frames) - 1)) * i
                else:
                    timestamp = 0
                
                # Calcular posição do frame
                if total_frames > 0 and len(frames) > 1:
                    frame_position = int((total_frames / (len(frames) - 1)) * i)
                else:
                    frame_position = 0
                
                frame_info = {
                    'frame_number': i + 1,
                    'timestamp_seconds': round(timestamp, 2),
                    'frame_position': frame_position,
                    'resolution': frame.shape[:2][::-1],  # (width, height)
                    'size_bytes': frame.nbytes
                }
                
                summary['frame_details'].append(frame_info)
            
        except Exception as e:
            logger.error(f"Erro ao criar resumo: {e}")
        
        return summary


def test_video_processor():
    """Função de teste do processador de vídeo"""
    processor = VideoProcessor()
    
    print("=== TESTE DO PROCESSADOR DE VÍDEO ===")
    print(f"Formatos suportados: {processor.supported_formats}")
    print(f"Frames alvo: {processor.target_frames}")
    
    # Teste com arquivo fictício
    class MockVideoFile:
        def __init__(self):
            self.name = "test_video.mp4"
            self.size = 1024 * 1024  # 1MB
        
        def read(self):
            return b"mock_video_data"
    
    mock_file = MockVideoFile()
    is_valid = processor.validate_video_file(mock_file)
    print(f"Validação de arquivo mock: {is_valid}")
    
    print("Processador de vídeo testado com sucesso!")


if __name__ == "__main__":
    test_video_processor()

