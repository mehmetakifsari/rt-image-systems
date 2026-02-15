from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import aiofiles
import shutil
from enum import Enum
import bcrypt
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'renault-trucks-secret-key-2024')
JWT_ALGORITHM = 'HS256'
security = HTTPBearer(auto_error=False)

# Upload directories
UPLOAD_DIR = ROOT_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)
for subdir in ['standard', 'roadassist', 'damaged', 'pdi']:
    (UPLOAD_DIR / subdir).mkdir(exist_ok=True)

# File size limits (bytes)
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 120 * 1024 * 1024  # 120MB
MAX_PDF_SIZE = 30 * 1024 * 1024  # 30MB

# Allowed extensions
ALLOWED_PHOTO_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_VIDEO_EXT = {'.mp4', '.mov', '.avi', '.webm'}
ALLOWED_PDF_EXT = {'.pdf'}

app = FastAPI(title="Renault Trucks Garanti Kayıt Sistemi")
api_router = APIRouter(prefix="/api")

# Enums
class RecordType(str, Enum):
    STANDARD = "standard"
    ROADASSIST = "roadassist"
    DAMAGED = "damaged"
    PDI = "pdi"

class MediaType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"
    PDF = "pdf"

# Models
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "user"
    branch: str = ""

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    username: str
    full_name: str
    role: str
    branch: str
    created_at: str

class FileItem(BaseModel):
    id: str
    filename: str
    original_name: str
    media_type: str
    path: str
    size: int
    thumb: Optional[str] = None
    uploaded_at: str

class RecordCreate(BaseModel):
    record_type: RecordType
    plate: Optional[str] = None
    work_order: Optional[str] = None
    vin: Optional[str] = None
    reference_no: Optional[str] = None
    note_text: Optional[str] = None

class RecordResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    record_type: str
    plate: Optional[str] = None
    work_order: Optional[str] = None
    vin: Optional[str] = None
    vin_last5: Optional[str] = None
    reference_no: Optional[str] = None
    case_key: str
    note_text: Optional[str] = None
    files_json: List[Dict[str, Any]] = []
    user_id: str
    branch: str
    created_at: str
    updated_at: str
    status: str = "active"

class SettingsUpdate(BaseModel):
    vision_api_key: Optional[str] = None
    ocr_provider: Optional[str] = "browser"
    storage_type: Optional[str] = "local"
    ftp_host: Optional[str] = None
    ftp_user: Optional[str] = None
    ftp_password: Optional[str] = None
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    aws_bucket: Optional[str] = None
    aws_region: Optional[str] = None
    google_drive_client_id: Optional[str] = None
    google_drive_client_secret: Optional[str] = None
    onedrive_client_id: Optional[str] = None
    onedrive_client_secret: Optional[str] = None
    language: str = "tr"

class SettingsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    vision_api_key: Optional[str] = None
    ocr_provider: str = "browser"
    storage_type: str = "local"
    ftp_host: Optional[str] = None
    ftp_user: Optional[str] = None
    aws_bucket: Optional[str] = None
    aws_region: Optional[str] = None
    google_drive_client_id: Optional[str] = None
    onedrive_client_id: Optional[str] = None
    language: str = "tr"

# Auth helpers
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, username: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.now(timezone.utc).timestamp() + 86400 * 7  # 7 days
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Kimlik doğrulama gerekli")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload['user_id']}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token süresi dolmuş")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Geçersiz token")

# Generate case_key based on record type
def generate_case_key(record_type: str, plate: str = None, work_order: str = None, 
                      vin: str = None, reference_no: str = None) -> str:
    year = datetime.now().year
    if record_type == RecordType.STANDARD:
        return f"{year}-STD-{work_order or 'NOORDER'}-{plate or 'NOPLATE'}"
    elif record_type == RecordType.ROADASSIST:
        return f"{year}-RA-{plate or 'NOPLATE'}"
    elif record_type == RecordType.DAMAGED:
        return f"{year}-DMG-{reference_no or 'NOREF'}"
    elif record_type == RecordType.PDI:
        return f"{year}-PDI-{vin or 'NOVIN'}"
    return f"{year}-UNK-{uuid.uuid4().hex[:8]}"

# Generate filename
def generate_filename(record_type: str, identifier: str, seq: int, ext: str) -> str:
    now = datetime.now()
    date_str = now.strftime('%Y%m%d_%H%M')
    return f"{now.year}-{record_type}-{identifier}-{date_str}-{seq:03d}{ext}"

# Auth Routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten mevcut")
    
    user_doc = {
        "id": str(uuid.uuid4()),
        "username": user.username,
        "password": hash_password(user.password),
        "full_name": user.full_name,
        "role": user.role,
        "branch": user.branch,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    del user_doc['password']
    del user_doc['_id']
    return UserResponse(**user_doc)

@api_router.post("/auth/login")
async def login(user: UserLogin):
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user['password']):
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre")
    
    token = create_token(db_user['id'], db_user['username'], db_user['role'])
    return {
        "token": token,
        "user": {
            "id": db_user['id'],
            "username": db_user['username'],
            "full_name": db_user['full_name'],
            "role": db_user['role'],
            "branch": db_user['branch']
        }
    }

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

# Record Routes
@api_router.post("/records", response_model=RecordResponse)
async def create_record(record: RecordCreate, current_user: dict = Depends(get_current_user)):
    # Validation based on record type
    if record.record_type == RecordType.STANDARD:
        if not record.plate or not record.work_order:
            raise HTTPException(status_code=400, detail="Standart kayıt için plaka ve iş emri zorunlu")
    elif record.record_type == RecordType.ROADASSIST:
        if not record.plate:
            raise HTTPException(status_code=400, detail="Yol yardım kaydı için plaka zorunlu")
    elif record.record_type == RecordType.DAMAGED:
        if not record.reference_no:
            raise HTTPException(status_code=400, detail="Hasarlı araç kaydı için referans no zorunlu")
    elif record.record_type == RecordType.PDI:
        if not record.vin:
            raise HTTPException(status_code=400, detail="PDI kaydı için VIN/Şasi No zorunlu")
    
    now = datetime.now(timezone.utc).isoformat()
    vin_last5 = record.vin[-5:] if record.vin and len(record.vin) >= 5 else None
    
    case_key = generate_case_key(
        record.record_type, 
        record.plate, 
        record.work_order, 
        record.vin, 
        record.reference_no
    )
    
    record_doc = {
        "id": str(uuid.uuid4()),
        "record_type": record.record_type.value,
        "plate": record.plate,
        "work_order": record.work_order,
        "vin": record.vin,
        "vin_last5": vin_last5,
        "reference_no": record.reference_no,
        "case_key": case_key,
        "note_text": record.note_text,
        "files_json": [],
        "user_id": current_user['id'],
        "branch": current_user.get('branch', ''),
        "created_at": now,
        "updated_at": now,
        "status": "active"
    }
    await db.uploads.insert_one(record_doc)
    del record_doc['_id']
    return RecordResponse(**record_doc)

@api_router.get("/records", response_model=List[RecordResponse])
async def get_records(
    record_type: Optional[str] = None,
    branch: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    query = {"status": "active"}
    
    if record_type:
        query["record_type"] = record_type
    if branch:
        query["branch"] = branch
    if search:
        query["$or"] = [
            {"plate": {"$regex": search, "$options": "i"}},
            {"work_order": {"$regex": search, "$options": "i"}},
            {"vin": {"$regex": search, "$options": "i"}},
            {"vin_last5": {"$regex": search, "$options": "i"}},
            {"reference_no": {"$regex": search, "$options": "i"}},
            {"case_key": {"$regex": search, "$options": "i"}}
        ]
    
    skip = (page - 1) * limit
    records = await db.uploads.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [RecordResponse(**r) for r in records]

@api_router.get("/records/{record_id}", response_model=RecordResponse)
async def get_record(record_id: str, current_user: dict = Depends(get_current_user)):
    record = await db.uploads.find_one({"id": record_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    return RecordResponse(**record)

@api_router.put("/records/{record_id}/note")
async def update_record_note(record_id: str, note_text: str = Form(...), current_user: dict = Depends(get_current_user)):
    result = await db.uploads.update_one(
        {"id": record_id},
        {"$set": {"note_text": note_text, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    return {"success": True}

@api_router.delete("/records/{record_id}")
async def delete_record(record_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.uploads.update_one(
        {"id": record_id},
        {"$set": {"status": "deleted", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    return {"success": True}

# File Upload Routes
@api_router.post("/records/{record_id}/upload")
async def upload_file(
    record_id: str,
    file: UploadFile = File(...),
    media_type: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    record = await db.uploads.find_one({"id": record_id})
    if not record:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    
    # Get file extension
    ext = Path(file.filename).suffix.lower()
    
    # Validate file type and size
    content = await file.read()
    file_size = len(content)
    
    if media_type == "photo":
        if ext not in ALLOWED_PHOTO_EXT:
            raise HTTPException(status_code=400, detail=f"Geçersiz fotoğraf formatı. İzin verilen: {ALLOWED_PHOTO_EXT}")
        if file_size > MAX_PHOTO_SIZE:
            raise HTTPException(status_code=400, detail=f"Fotoğraf çok büyük. Maksimum: {MAX_PHOTO_SIZE // (1024*1024)}MB")
    elif media_type == "video":
        if ext not in ALLOWED_VIDEO_EXT:
            raise HTTPException(status_code=400, detail=f"Geçersiz video formatı. İzin verilen: {ALLOWED_VIDEO_EXT}")
        if file_size > MAX_VIDEO_SIZE:
            raise HTTPException(status_code=400, detail=f"Video çok büyük. Maksimum: {MAX_VIDEO_SIZE // (1024*1024)}MB")
    elif media_type == "pdf":
        if ext not in ALLOWED_PDF_EXT:
            raise HTTPException(status_code=400, detail="Geçersiz PDF formatı")
        if file_size > MAX_PDF_SIZE:
            raise HTTPException(status_code=400, detail=f"PDF çok büyük. Maksimum: {MAX_PDF_SIZE // (1024*1024)}MB")
    else:
        raise HTTPException(status_code=400, detail="Geçersiz medya tipi")
    
    # Generate filename
    record_type = record['record_type']
    identifier = record.get('work_order') or record.get('plate') or record.get('vin') or record.get('reference_no') or 'unknown'
    files_count = len(record.get('files_json', []))
    new_filename = generate_filename(record_type, identifier, files_count + 1, ext)
    
    # Save file
    file_path = UPLOAD_DIR / record_type / new_filename
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Create file record
    file_item = {
        "id": str(uuid.uuid4()),
        "filename": new_filename,
        "original_name": file.filename,
        "media_type": media_type,
        "path": f"/uploads/{record_type}/{new_filename}",
        "size": file_size,
        "thumb": None,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update record
    await db.uploads.update_one(
        {"id": record_id},
        {
            "$push": {"files_json": file_item},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {"success": True, "file": file_item}

@api_router.delete("/records/{record_id}/files/{file_id}")
async def delete_file(record_id: str, file_id: str, current_user: dict = Depends(get_current_user)):
    record = await db.uploads.find_one({"id": record_id})
    if not record:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    
    file_to_delete = None
    for f in record.get('files_json', []):
        if f['id'] == file_id:
            file_to_delete = f
            break
    
    if not file_to_delete:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
    # Delete physical file
    file_path = ROOT_DIR / file_to_delete['path'].lstrip('/')
    if file_path.exists():
        file_path.unlink()
    
    # Update record
    await db.uploads.update_one(
        {"id": record_id},
        {
            "$pull": {"files_json": {"id": file_id}},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {"success": True}

# Settings Routes
@api_router.get("/settings", response_model=SettingsResponse)
async def get_settings(current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    settings = await db.settings.find_one({}, {"_id": 0})
    if not settings:
        # Create default settings
        settings = {
            "id": str(uuid.uuid4()),
            "ocr_provider": "browser",
            "storage_type": "local",
            "language": "tr"
        }
        await db.settings.insert_one(settings)
    
    # Mask sensitive data
    return SettingsResponse(**settings)

@api_router.put("/settings", response_model=SettingsResponse)
async def update_settings(settings: SettingsUpdate, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    existing = await db.settings.find_one({})
    if not existing:
        settings_doc = {
            "id": str(uuid.uuid4()),
            **settings.model_dump(exclude_none=True)
        }
        await db.settings.insert_one(settings_doc)
    else:
        await db.settings.update_one(
            {"id": existing['id']},
            {"$set": settings.model_dump(exclude_none=True)}
        )
    
    updated = await db.settings.find_one({}, {"_id": 0})
    return SettingsResponse(**updated)

# Dashboard Stats
@api_router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    total = await db.uploads.count_documents({"status": "active"})
    standard = await db.uploads.count_documents({"status": "active", "record_type": "standard"})
    roadassist = await db.uploads.count_documents({"status": "active", "record_type": "roadassist"})
    damaged = await db.uploads.count_documents({"status": "active", "record_type": "damaged"})
    pdi = await db.uploads.count_documents({"status": "active", "record_type": "pdi"})
    
    # Recent records
    recent = await db.uploads.find({"status": "active"}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "total": total,
        "by_type": {
            "standard": standard,
            "roadassist": roadassist,
            "damaged": damaged,
            "pdi": pdi
        },
        "recent": recent
    }

# Health check
@api_router.get("/")
async def root():
    return {"message": "Renault Trucks Garanti Kayıt Sistemi API", "version": "1.0.0"}

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    # Create indexes
    await db.uploads.create_index("case_key")
    await db.uploads.create_index("record_type")
    await db.uploads.create_index("plate")
    await db.uploads.create_index("work_order")
    await db.uploads.create_index("vin_last5")
    await db.users.create_index("username", unique=True)
    
    # Create default admin if not exists
    admin = await db.users.find_one({"username": "admin"})
    if not admin:
        admin_doc = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "password": hash_password("admin123"),
            "full_name": "Sistem Yöneticisi",
            "role": "admin",
            "branch": "Merkez",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_doc)
        logger.info("Default admin user created: admin / admin123")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
