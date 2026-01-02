from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

from core.dispatcher import dispatch
from core.intent_parser import parse
from utils.logger import log_command, log_separator, setup_logger

logger = setup_logger(__name__)

app = FastAPI()

class Command(BaseModel):
    text: str

@app.post("/command")
def command(cmd: Command):
    log_separator(logger)
    log_command(logger, cmd.text)
    
    intent = parse(cmd.text)
    logger.info(f"Intent parseada: {intent.get('intent')} | Domain: {intent.get('domain')}")
    
    response = dispatch(intent)
    logger.info(f"Resposta: {response.get('message', 'N/A')}")
    log_separator(logger)

    return {
        "intent": intent.get("intent"),
        "domain": intent.get("domain"),
        "response": response
    }
