from core.context_manager import context
from core.domains import climate, light, sensor
from utils.logger import setup_logger
from utils.version import print_version_banner

logger = setup_logger(__name__)

# Exibe banner de versão na inicialização
print_version_banner()

def dispatch(intent: dict):
    domain = intent.get("domain")
    intent_type = intent.get("intent")
    
    if context.valid():
        payload = context.data.get("payload", {})
        ctx_domain = payload.get("domain")
        logger.info(f"Contexto ativo: {ctx_domain} | Roteando confirmacao")

        if ctx_domain == "light":
            return light.handle_confirmation(intent)
        if ctx_domain == "climate":
            return climate.handle_confirmation(intent)

    logger.info(f"Despachando: {domain}.{intent_type}")
    
    if domain == "light":
        return light.handle(intent)

    if domain == "climate":
        return climate.handle(intent)

    if domain == "sensor":
        return sensor.handle(intent)

    logger.warning(f"Dominio desconhecido: {domain}")
    return {"message": "Não entendi. Pode repetir?"}

