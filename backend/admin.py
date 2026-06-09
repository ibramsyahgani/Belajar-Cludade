from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from .config import load_config, save_config, get_admin_password

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_password = get_admin_password()
    if not secrets.compare_digest(credentials.password.encode(), correct_password.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password salah",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


@router.get("/config")
async def get_config(creds: HTTPBasicCredentials = Depends(verify_admin)):
    config = load_config()
    # Don't expose secrets
    return config


@router.post("/config")
async def update_config(new_config: dict, creds: HTTPBasicCredentials = Depends(verify_admin)):
    save_config(new_config)
    return {"status": "ok", "message": "Konfigurasi berhasil disimpan"}
