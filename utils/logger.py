import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

# ============================================================
# CONFIGURACAO DE LOGGING
# ============================================================

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Estrategia de rotacao de logs
# Opcao 1: Por tamanho (RotatingFileHandler)
# Opcao 2: Por tempo (TimedRotatingFileHandler)
USE_TIME_ROTATION = True  # True para rotacao diaria, False para rotacao por tamanho

# Configuracoes de rotacao por tamanho
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB por arquivo
MAX_LOG_FILES = 7  # Manter ultimos 7 arquivos

# Configuracoes de rotacao por tempo
LOG_ROTATION_WHEN = "midnight"  # midnight, H, D, W0-W6
LOG_ROTATION_INTERVAL = 1  # A cada 1 dia
LOG_RETENTION_DAYS = 30  # Manter logs dos ultimos 30 dias

LOG_FILE = LOG_DIR / "friday.log"

# Formato de log limpo e estruturado
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str, level=logging.INFO):
    """
    Cria logger configurado com output para arquivo (com rotacao) e console
    
    Rotacao de logs:
    - Por padrao: Rotacao diaria a meia-noite, mantendo 30 dias
    - Alternativa: Rotacao por tamanho (10MB), mantendo 7 arquivos
    
    Args:
        name: Nome do logger (geralmente __name__ do modulo)
        level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado com rotacao automatica
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evita duplicacao de handlers
    if logger.handlers:
        return logger
    
    # Handler para arquivo com rotacao
    if USE_TIME_ROTATION:
        # Rotacao por tempo (diaria, semanal, etc)
        file_handler = TimedRotatingFileHandler(
            LOG_FILE,
            when=LOG_ROTATION_WHEN,
            interval=LOG_ROTATION_INTERVAL,
            backupCount=LOG_RETENTION_DAYS,
            encoding="utf-8"
        )
        # Formato do arquivo rotacionado: friday.log.2026-01-02
        file_handler.suffix = "%Y-%m-%d"
    else:
        # Rotacao por tamanho
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=MAX_LOG_FILES,
            encoding="utf-8"
        )
        # Formato do arquivo rotacionado: friday.log.1, friday.log.2, etc
    
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ============================================================
# HELPERS PARA LOGS ESTRUTURADOS
# ============================================================

def log_api_call(logger, method: str, url: str, status: int = None, error: str = None):
    """Log estruturado para chamadas de API"""
    if error:
        logger.error(f"API [{method}] {url} ** ERRO: {error}")
    else:
        logger.info(f"API [{method}] {url} -> Status {status}")


def log_command(logger, text: str, intent: str = None, domain: str = None):
    """Log estruturado para comandos recebidos"""
    if intent and domain:
        logger.info(f"COMANDO: '{text}' >> Intent: {intent} | Domain: {domain}")
    else:
        logger.info(f"COMANDO: '{text}'")


def log_action(logger, domain: str, action: str, target: str = None):
    """Log estruturado para acoes executadas"""
    if target:
        logger.info(f"ACAO [{domain}] {action} -> {target}")
    else:
        logger.info(f"ACAO [{domain}] {action}")


def log_separator(logger):
    """Separador visual para logs"""
    logger.info("=" * 70)
