from fastapi import FastAPI
from pydantic import BaseModel

from core.intent_parser import parse
from core.dispatcher import dispatch

app = FastAPI()

class Command(BaseModel):
    text: str

@app.post("/command")
def command(cmd: Command):
    intent = parse(cmd.text)
    response = dispatch(intent)

    return {
        "intent": intent.get("intent"),
        "domain": intent.get("domain"),
        "response": response
    }
