from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict
from . import __version__
from .engine import Engine

class Ticket(BaseModel):
    model_config = ConfigDict(extra='forbid')
    message: str = Field(min_length=1, max_length=12000)
    subject: str = Field(default='', max_length=200)


def create_app(engine=None):
    engine = engine or Engine()
    app = FastAPI(title='Laya INEMA — triagem', version=__version__)
    @app.get('/')
    def index(): return FileResponse(Path(__file__).with_name('index.html'))
    @app.get('/api/health')
    def health(): return {'status': 'ok', 'model_loaded': engine.router is not None, 'version': __version__}
    @app.post('/api/triage')
    def triage(ticket: Ticket):
        try: return engine.predict(ticket.message, ticket.subject)
        except ValueError as e: raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as e:
            import logging
            logging.getLogger(__name__).exception('Inferência indisponível')
            raise HTTPException(status_code=503, detail='Modelo indisponível. Consulte o terminal e execute o comando download antes de tentar novamente.') from e
    return app
