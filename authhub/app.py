from fastapi import FastAPI, Response, Request
from pydantic import BaseModel
import os

COOKIE_NAME = 'ip_sso'
DOMAIN = '.' + os.getenv('DOMAIN_ROOT', 'insightpulseai.net')
app = FastAPI()

class TokenIn(BaseModel):
    jwt: str

@app.get('/health')
def health():
    return {'ok': True}

@app.post('/sso/cookie')
def stamp(tok: TokenIn, resp: Response):
    # In production, validate JWT here before stamping
    resp.set_cookie(
        COOKIE_NAME,
        tok.jwt,
        domain=DOMAIN,
        secure=True,
        samesite='none',
        httponly=True,
        path='/'
    )
    return {'ok': True}
