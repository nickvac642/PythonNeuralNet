import os
import time
import requests
from typing import Any, Dict
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt  # PyJWT


bearer = HTTPBearer(auto_error=False)
_JWKS_CACHE: Dict[str, Any] = {"keys": None, "ts": 0.0}


def _enabled() -> bool:
    return os.environ.get("MDM_AUTH_MODE", "api_key").lower() == "oidc"


def _settings() -> Dict[str, str]:
    issuer = os.environ.get("OIDC_ISSUER", "").rstrip("/") + "/"
    audience = os.environ.get("OIDC_AUDIENCE", "")
    if not issuer or not audience:
        raise HTTPException(status_code=500, detail="OIDC not configured")
    return {"issuer": issuer, "audience": audience, "jwks": f"{issuer}.well-known/jwks.json"}


def _get_jwks() -> Dict[str, Any]:
    now = time.time()
    if not _JWKS_CACHE["keys"] or (now - _JWKS_CACHE["ts"]) > 3600:
        s = _settings()
        resp = requests.get(s["jwks"], timeout=5)
        resp.raise_for_status()
        _JWKS_CACHE["keys"] = resp.json()
        _JWKS_CACHE["ts"] = now
    return _JWKS_CACHE["keys"]


def _select_key(token: str) -> Dict[str, Any]:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    jwks = _get_jwks()
    keys = jwks.get("keys", [])
    for k in keys:
        if k.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(k)
    raise HTTPException(status_code=401, detail="Invalid token key")


def verify_bearer(credentials = Depends(bearer)) -> Dict[str, Any]:
    if not _enabled():
        # OIDC disabled → bypass
        return {"mode": "disabled"}
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    s = _settings()
    token = credentials.credentials
    key = _select_key(token)
    try:
        claims = jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            audience=s["audience"],
            issuer=s["issuer"],
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    return claims


def require_scope(required_scope: str):
    def dep(claims: Dict[str, Any] = Depends(verify_bearer)):
        if not _enabled():
            return {"mode": "disabled"}
        scopes = claims.get("scope", "").split()
        if required_scope not in scopes:
            raise HTTPException(status_code=403, detail="Forbidden")
        return claims
    return dep


