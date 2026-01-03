import os
from pathlib import Path

def get_version_info():
    """Lê as informações de versão do arquivo VERSION.txt"""
    version_file = Path(__file__).parent.parent / "VERSION.txt"
    
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "VERSÃO: Desconhecida"

def print_version_banner():
    """Exibe o banner de versão no log"""
    from utils.logger import setup_logger
    
    logger = setup_logger("friday.startup")
    version_info = get_version_info()
    
    logger.info("\n" + version_info + "\n")
