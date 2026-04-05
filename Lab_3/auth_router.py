from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
import models, security, repository, service
from jose import jwt, JWTError

router = APIRouter(prefix="/api/auth", tags=["Security"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    repo = repository.UserRepository(db)
    serv = service.UserService(repo)
    if repo.get_by_username(username):
        raise HTTPException(status_code=400, detail="User already exists")
    return serv.register_user(username, password)

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    repo = repository.UserRepository(db)
    user = repo.get_by_username(username)
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    roles = [r.name for r in user.roles]
    token = security.create_access_token({"sub": user.username, "roles": roles})
    return {"access_token": token, "token_type": "bearer"}


def RoleChecker(allowed_roles: list):
    def checker(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
            user_roles = payload.get("roles", [])
            if not any(role in user_roles for role in allowed_roles):
                raise HTTPException(status_code=403, detail="Forbidden: Not enough roles")
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return checker

def get_current_user(token: str, db: Session):
    try:
        
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Имя пользователя не найдено в токене")
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    
    repo = repository.UserRepository(db)
    user = repo.get_by_username(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден в БД")
    return user