from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
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

# Şube tanımlamaları
BRANCHES = {
    "1": {"code": "1", "name": "Bursa", "city": "Bursa"},
    "2": {"code": "2", "name": "İzmit", "city": "Kocaeli"},
    "3": {"code": "3", "name": "Orhanlı", "city": "İstanbul"},
    "4": {"code": "4", "name": "Hadımköy", "city": "İstanbul"},
    "5": {"code": "5", "name": "Keşan", "city": "Edirne"}
}

# Görev tanımları
JOB_TITLES = {
    "garanti_danisman": "Garanti Danışmanı",
    "hasar_danisman": "Hasar Danışmanı",
    "musteri_kabul": "Müşteri Kabul Personeli"
}

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

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"  # Alt hesaplar (danışmanlar)
    APPRENTICE = "apprentice"  # Stajyer/Çırak

# Record Status for Apprentice workflow
class RecordStatus(str, Enum):
    ACTIVE = "active"
    PENDING_REVIEW = "pending_review"  # Stajyer tarafından oluşturuldu, danışman onayı bekliyor
    APPROVED = "approved"
    REJECTED = "rejected"
    DELETED = "deleted"

# Application Version
APP_VERSION = "1.2.0"
VERSION_DATE = "2025-12-15"
BUILD_NUMBER = "2025121501"

# Models
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "staff"
    branch_code: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    branch_code: Optional[str] = None
    job_title: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    username: str
    full_name: str
    role: str
    branch_code: Optional[str] = None
    branch_name: Optional[str] = None
    job_title: Optional[str] = None
    job_title_display: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    is_online: bool = False
    last_seen: Optional[str] = None
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
    branch_code: Optional[str] = None  # PDI, Hasarlı, Yol yardım için

class RecordUpdate(BaseModel):
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
    branch_code: str
    branch_name: Optional[str] = None
    created_at: str
    updated_at: str
    status: str = "active"
    created_by_name: Optional[str] = None
    created_by_role: Optional[str] = None

# Notification Models
class NotificationType(str, Enum):
    MISSING_DOCUMENT = "missing_document"
    RETAKE_PHOTO = "retake_photo"
    RECORD_APPROVED = "record_approved"
    RECORD_REJECTED = "record_rejected"
    NEW_RECORD = "new_record"

class NotificationCreate(BaseModel):
    record_id: str
    recipient_id: str
    notification_type: NotificationType
    message: str

class NotificationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    record_id: str
    sender_id: str
    sender_name: str
    recipient_id: str
    recipient_name: str
    notification_type: str
    message: str
    is_read: bool = False
    created_at: str

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

def create_token(user_id: str, username: str, role: str, branch_code: str = None) -> str:
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'branch_code': branch_code,
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
        # Update last seen
        await db.users.update_one(
            {"id": user['id']},
            {"$set": {"last_seen": datetime.now(timezone.utc).isoformat(), "is_online": True}}
        )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token süresi dolmuş")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Geçersiz token")

def get_branch_name(branch_code: str) -> str:
    return BRANCHES.get(branch_code, {}).get("name", "Bilinmiyor")

def get_job_title_display(job_title: str) -> str:
    return JOB_TITLES.get(job_title, job_title)

# İş emri numarasından şube kodunu çıkar
def extract_branch_from_work_order(work_order: str) -> str:
    """
    İş emri formatı: 40216001
    İlk rakam şube kodudur: 4 = Hadımköy
    """
    if work_order and len(work_order) >= 1:
        first_char = work_order[0]
        if first_char in BRANCHES:
            return first_char
    return None

# Generate case_key based on record type
def generate_case_key(record_type: str, plate: str = None, work_order: str = None, 
                      vin: str = None, reference_no: str = None, branch_code: str = None) -> str:
    year = datetime.now().year
    branch_prefix = branch_code or "0"
    if record_type == RecordType.STANDARD:
        return f"{year}-STD-{branch_prefix}-{work_order or 'NOORDER'}-{plate or 'NOPLATE'}"
    elif record_type == RecordType.ROADASSIST:
        return f"{year}-RA-{branch_prefix}-{plate or 'NOPLATE'}"
    elif record_type == RecordType.DAMAGED:
        return f"{year}-DMG-{branch_prefix}-{reference_no or 'NOREF'}"
    elif record_type == RecordType.PDI:
        return f"{year}-PDI-{branch_prefix}-{vin or 'NOVIN'}"
    return f"{year}-UNK-{uuid.uuid4().hex[:8]}"

# Generate filename
def generate_filename(record_type: str, identifier: str, seq: int, ext: str) -> str:
    now = datetime.now()
    date_str = now.strftime('%Y%m%d_%H%M')
    return f"{now.year}-{record_type}-{identifier}-{date_str}-{seq:03d}{ext}"

# Branches endpoint
@api_router.get("/branches")
async def get_branches():
    return {"branches": list(BRANCHES.values())}

@api_router.get("/job-titles")
async def get_job_titles():
    return {"job_titles": [{"code": k, "name": v} for k, v in JOB_TITLES.items()]}

# Auth Routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, current_user: dict = Depends(get_current_user)):
    # Sadece admin kullanıcı oluşturabilir
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten mevcut")
    
    # Staff için şube ve görev zorunlu
    if user.role == 'staff':
        if not user.branch_code:
            raise HTTPException(status_code=400, detail="Şube seçimi zorunludur")
        if not user.job_title:
            raise HTTPException(status_code=400, detail="Görev tanımı zorunludur")
    
    user_doc = {
        "id": str(uuid.uuid4()),
        "username": user.username,
        "password": hash_password(user.password),
        "full_name": user.full_name,
        "role": user.role,
        "branch_code": user.branch_code,
        "branch_name": get_branch_name(user.branch_code) if user.branch_code else None,
        "job_title": user.job_title,
        "job_title_display": get_job_title_display(user.job_title) if user.job_title else None,
        "phone": user.phone,
        "whatsapp": user.whatsapp,
        "is_online": False,
        "last_seen": None,
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
    
    # Update online status
    await db.users.update_one(
        {"id": db_user['id']},
        {"$set": {"is_online": True, "last_seen": datetime.now(timezone.utc).isoformat()}}
    )
    
    token = create_token(db_user['id'], db_user['username'], db_user['role'], db_user.get('branch_code'))
    return {
        "token": token,
        "user": {
            "id": db_user['id'],
            "username": db_user['username'],
            "full_name": db_user['full_name'],
            "role": db_user['role'],
            "branch_code": db_user.get('branch_code'),
            "branch_name": db_user.get('branch_name'),
            "job_title": db_user.get('job_title'),
            "job_title_display": db_user.get('job_title_display'),
            "phone": db_user.get('phone'),
            "whatsapp": db_user.get('whatsapp')
        }
    }

@api_router.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {"is_online": False, "last_seen": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@api_router.put("/auth/profile", response_model=UserResponse)
async def update_profile(update: UserUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    
    if 'branch_code' in update_data:
        update_data['branch_name'] = get_branch_name(update_data['branch_code'])
    if 'job_title' in update_data:
        update_data['job_title_display'] = get_job_title_display(update_data['job_title'])
    
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": update_data}
    )
    
    updated_user = await db.users.find_one({"id": current_user['id']}, {"_id": 0, "password": 0})
    return UserResponse(**updated_user)

# Staff Management (Admin only)
@api_router.get("/staff", response_model=List[UserResponse])
async def get_staff(
    branch_code: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    query = {"role": "staff"}
    if branch_code:
        query["branch_code"] = branch_code
    
    staff = await db.users.find(query, {"_id": 0, "password": 0}).to_list(100)
    return [UserResponse(**s) for s in staff]

@api_router.get("/staff/{user_id}", response_model=UserResponse)
async def get_staff_member(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    staff = await db.users.find_one({"id": user_id, "role": "staff"}, {"_id": 0, "password": 0})
    if not staff:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return UserResponse(**staff)

@api_router.put("/staff/{user_id}", response_model=UserResponse)
async def update_staff(user_id: str, update: UserUpdate, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    
    if 'branch_code' in update_data:
        update_data['branch_name'] = get_branch_name(update_data['branch_code'])
    if 'job_title' in update_data:
        update_data['job_title_display'] = get_job_title_display(update_data['job_title'])
    
    result = await db.users.update_one(
        {"id": user_id, "role": "staff"},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    updated_user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    return UserResponse(**updated_user)

@api_router.delete("/staff/{user_id}")
async def delete_staff(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    result = await db.users.delete_one({"id": user_id, "role": "staff"})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return {"success": True}

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
        if not record.branch_code:
            raise HTTPException(status_code=400, detail="Yol yardım kaydı için şube seçimi zorunlu")
    elif record.record_type == RecordType.DAMAGED:
        if not record.reference_no:
            raise HTTPException(status_code=400, detail="Hasarlı araç kaydı için referans no zorunlu")
        if not record.branch_code:
            raise HTTPException(status_code=400, detail="Hasarlı araç kaydı için şube seçimi zorunlu")
    elif record.record_type == RecordType.PDI:
        if not record.vin:
            raise HTTPException(status_code=400, detail="PDI kaydı için VIN/Şasi No zorunlu")
        if not record.branch_code:
            raise HTTPException(status_code=400, detail="PDI kaydı için şube seçimi zorunlu")
    
    # Şube kodunu belirle
    branch_code = record.branch_code
    if record.record_type == RecordType.STANDARD and record.work_order:
        # İş emri numarasından şube kodunu çıkar
        extracted_branch = extract_branch_from_work_order(record.work_order)
        if extracted_branch:
            branch_code = extracted_branch
    
    # Staff ve Apprentice kullanıcılar sadece kendi şubelerine kayıt yapabilir
    if current_user.get('role') in ['staff', 'apprentice']:
        if branch_code and branch_code != current_user.get('branch_code'):
            raise HTTPException(status_code=403, detail="Sadece kendi şubenize kayıt yapabilirsiniz")
        branch_code = current_user.get('branch_code')
    
    # Stajyer oluşturduğunda pending_review olsun
    initial_status = "pending_review" if current_user.get('role') == 'apprentice' else "active"
    
    now = datetime.now(timezone.utc).isoformat()
    vin_last5 = record.vin[-5:] if record.vin and len(record.vin) >= 5 else None
    
    case_key = generate_case_key(
        record.record_type, 
        record.plate, 
        record.work_order, 
        record.vin, 
        record.reference_no,
        branch_code
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
        "created_by_name": current_user.get('full_name'),
        "created_by_role": current_user.get('role'),
        "branch_code": branch_code or "0",
        "branch_name": get_branch_name(branch_code) if branch_code else "Bilinmiyor",
        "created_at": now,
        "updated_at": now,
        "status": initial_status
    }
    await db.uploads.insert_one(record_doc)
    del record_doc['_id']
    
    # Stajyer kayıt oluşturduğunda danışmanlara bildirim gönder
    if current_user.get('role') == 'apprentice':
        staff_users = await db.users.find({
            "role": "staff",
            "branch_code": branch_code
        }, {"_id": 0}).to_list(50)
        
        for staff in staff_users:
            notification_doc = {
                "id": str(uuid.uuid4()),
                "record_id": record_doc['id'],
                "sender_id": current_user['id'],
                "sender_name": current_user.get('full_name', 'Stajyer'),
                "recipient_id": staff['id'],
                "recipient_name": staff.get('full_name', ''),
                "notification_type": "new_record",
                "message": f"{current_user.get('full_name', 'Stajyer')} yeni bir kayıt oluşturdu: {record_doc['case_key']}",
                "is_read": False,
                "created_at": now
            }
            await db.notifications.insert_one(notification_doc)
    
    return RecordResponse(**record_doc)

@api_router.get("/records", response_model=List[RecordResponse])
async def get_records(
    record_type: Optional[str] = None,
    branch_code: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    query = {"status": "active"}
    
    # Staff kullanıcılar sadece kendi şubelerinin kayıtlarını görebilir
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    elif branch_code:
        query["branch_code"] = branch_code
    
    if record_type:
        query["record_type"] = record_type
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
    query = {"id": record_id}
    
    # Staff kullanıcılar sadece kendi şubelerinin kayıtlarını görebilir
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    
    record = await db.uploads.find_one(query, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    return RecordResponse(**record)

@api_router.put("/records/{record_id}", response_model=RecordResponse)
async def update_record(record_id: str, update: RecordUpdate, current_user: dict = Depends(get_current_user)):
    query = {"id": record_id}
    
    # Staff kullanıcılar sadece kendi şubelerinin kayıtlarını düzenleyebilir
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.uploads.update_one(query, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    
    record = await db.uploads.find_one({"id": record_id}, {"_id": 0})
    return RecordResponse(**record)

@api_router.put("/records/{record_id}/note")
async def update_record_note(record_id: str, note_text: str = Form(...), current_user: dict = Depends(get_current_user)):
    query = {"id": record_id}
    
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    
    result = await db.uploads.update_one(
        query,
        {"$set": {"note_text": note_text, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    return {"success": True}

@api_router.delete("/records/{record_id}")
async def delete_record(record_id: str, current_user: dict = Depends(get_current_user)):
    query = {"id": record_id}
    
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    
    result = await db.uploads.update_one(
        query,
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
    query = {"id": record_id}
    
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    
    record = await db.uploads.find_one(query)
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
    query = {"id": record_id}
    
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    
    record = await db.uploads.find_one(query)
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

# Dashboard Stats (Admin)
@api_router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    total = await db.uploads.count_documents({"status": "active"})
    standard = await db.uploads.count_documents({"status": "active", "record_type": "standard"})
    roadassist = await db.uploads.count_documents({"status": "active", "record_type": "roadassist"})
    damaged = await db.uploads.count_documents({"status": "active", "record_type": "damaged"})
    pdi = await db.uploads.count_documents({"status": "active", "record_type": "pdi"})
    
    # Recent records
    recent = await db.uploads.find({"status": "active"}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
    
    # Branch stats
    branch_stats = []
    for code, branch in BRANCHES.items():
        branch_total = await db.uploads.count_documents({"status": "active", "branch_code": code})
        branch_staff = await db.users.find(
            {"role": "staff", "branch_code": code}, 
            {"_id": 0, "password": 0}
        ).to_list(20)
        
        online_count = sum(1 for s in branch_staff if s.get('is_online'))
        
        branch_stats.append({
            "code": code,
            "name": branch["name"],
            "city": branch["city"],
            "total_records": branch_total,
            "staff": branch_staff,
            "staff_count": len(branch_staff),
            "online_count": online_count
        })
    
    return {
        "total": total,
        "by_type": {
            "standard": standard,
            "roadassist": roadassist,
            "damaged": damaged,
            "pdi": pdi
        },
        "recent": recent,
        "branches": branch_stats
    }

# Staff dashboard (for staff users)
@api_router.get("/my-stats")
async def get_my_stats(current_user: dict = Depends(get_current_user)):
    branch_code = current_user.get('branch_code')
    
    query = {"status": {"$in": ["active", "approved"]}}
    if branch_code:
        query["branch_code"] = branch_code
    
    total = await db.uploads.count_documents(query)
    
    type_query = {**query}
    standard = await db.uploads.count_documents({**type_query, "record_type": "standard"})
    roadassist = await db.uploads.count_documents({**type_query, "record_type": "roadassist"})
    damaged = await db.uploads.count_documents({**type_query, "record_type": "damaged"})
    pdi = await db.uploads.count_documents({**type_query, "record_type": "pdi"})
    
    # Pending review count for staff
    pending_count = 0
    if current_user.get('role') == 'staff' and branch_code:
        pending_count = await db.uploads.count_documents({
            "branch_code": branch_code,
            "status": "pending_review"
        })
    
    # Recent records for this branch
    recent = await db.uploads.find(query, {"_id": 0}).sort("created_at", -1).limit(10).to_list(10)
    
    return {
        "total": total,
        "by_type": {
            "standard": standard,
            "roadassist": roadassist,
            "damaged": damaged,
            "pdi": pdi
        },
        "pending_count": pending_count,
        "recent": recent,
        "branch_name": get_branch_name(branch_code) if branch_code else None
    }

# ============ NOTIFICATION ROUTES ============

@api_router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    query = {"recipient_id": current_user['id']}
    if unread_only:
        query["is_read"] = False
    
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    unread_count = await db.notifications.count_documents({"recipient_id": current_user['id'], "is_read": False})
    
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }

@api_router.post("/notifications")
async def create_notification(
    notification: NotificationCreate,
    current_user: dict = Depends(get_current_user)
):
    # Staff ve Admin bildirim gönderebilir
    if current_user.get('role') not in ['admin', 'staff']:
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    # Kayıt var mı kontrol et
    record = await db.uploads.find_one({"id": notification.record_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    
    # Alıcı var mı kontrol et
    recipient = await db.users.find_one({"id": notification.recipient_id}, {"_id": 0})
    if not recipient:
        raise HTTPException(status_code=404, detail="Alıcı bulunamadı")
    
    now = datetime.now(timezone.utc).isoformat()
    notification_doc = {
        "id": str(uuid.uuid4()),
        "record_id": notification.record_id,
        "sender_id": current_user['id'],
        "sender_name": current_user.get('full_name', ''),
        "recipient_id": notification.recipient_id,
        "recipient_name": recipient.get('full_name', ''),
        "notification_type": notification.notification_type.value,
        "message": notification.message,
        "is_read": False,
        "created_at": now
    }
    
    await db.notifications.insert_one(notification_doc)
    del notification_doc['_id']
    
    return notification_doc

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"id": notification_id, "recipient_id": current_user['id']},
        {"$set": {"is_read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Bildirim bulunamadı")
    return {"success": True}

@api_router.put("/notifications/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    await db.notifications.update_many(
        {"recipient_id": current_user['id'], "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"success": True}

# ============ RECORD APPROVAL ROUTES (for Apprentice workflow) ============

@api_router.get("/records/pending")
async def get_pending_records(
    current_user: dict = Depends(get_current_user)
):
    """Danışmanlar için bekleyen kayıtları getir"""
    if current_user.get('role') not in ['admin', 'staff']:
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    query = {"status": "pending_review"}
    
    # Staff sadece kendi şubesini görebilir
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    
    records = await db.uploads.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return records

@api_router.put("/records/{record_id}/approve")
async def approve_record(record_id: str, current_user: dict = Depends(get_current_user)):
    """Kaydı onayla"""
    if current_user.get('role') not in ['admin', 'staff']:
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    query = {"id": record_id, "status": "pending_review"}
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    
    record = await db.uploads.find_one(query, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı veya zaten onaylanmış")
    
    now = datetime.now(timezone.utc).isoformat()
    await db.uploads.update_one(
        {"id": record_id},
        {"$set": {"status": "approved", "approved_by": current_user['id'], "approved_at": now, "updated_at": now}}
    )
    
    # Stajyere bildirim gönder
    if record.get('user_id'):
        notification_doc = {
            "id": str(uuid.uuid4()),
            "record_id": record_id,
            "sender_id": current_user['id'],
            "sender_name": current_user.get('full_name', ''),
            "recipient_id": record['user_id'],
            "recipient_name": record.get('created_by_name', ''),
            "notification_type": "record_approved",
            "message": f"Kaydınız onaylandı: {record.get('case_key', '')}",
            "is_read": False,
            "created_at": now
        }
        await db.notifications.insert_one(notification_doc)
    
    return {"success": True, "message": "Kayıt onaylandı"}

@api_router.put("/records/{record_id}/reject")
async def reject_record(
    record_id: str,
    reason: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Kaydı reddet"""
    if current_user.get('role') not in ['admin', 'staff']:
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    query = {"id": record_id, "status": "pending_review"}
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    
    record = await db.uploads.find_one(query, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    
    now = datetime.now(timezone.utc).isoformat()
    await db.uploads.update_one(
        {"id": record_id},
        {"$set": {"status": "rejected", "rejected_by": current_user['id'], "rejection_reason": reason, "updated_at": now}}
    )
    
    # Stajyere bildirim gönder
    if record.get('user_id'):
        notification_doc = {
            "id": str(uuid.uuid4()),
            "record_id": record_id,
            "sender_id": current_user['id'],
            "sender_name": current_user.get('full_name', ''),
            "recipient_id": record['user_id'],
            "recipient_name": record.get('created_by_name', ''),
            "notification_type": "record_rejected",
            "message": f"Kaydınız reddedildi: {record.get('case_key', '')}. Sebep: {reason}",
            "is_read": False,
            "created_at": now
        }
        await db.notifications.insert_one(notification_doc)
    
    return {"success": True, "message": "Kayıt reddedildi"}

# ============ APPRENTICE MANAGEMENT ============

@api_router.get("/apprentices", response_model=List[UserResponse])
async def get_apprentices(
    branch_code: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Stajyerleri listele"""
    if current_user.get('role') not in ['admin', 'staff']:
        raise HTTPException(status_code=403, detail="Yetkiniz yok")
    
    query = {"role": "apprentice"}
    
    # Staff sadece kendi şubesindeki stajyerleri görebilir
    if current_user.get('role') == 'staff':
        query["branch_code"] = current_user.get('branch_code')
    elif branch_code:
        query["branch_code"] = branch_code
    
    apprentices = await db.users.find(query, {"_id": 0, "password": 0}).to_list(100)
    return [UserResponse(**a) for a in apprentices]

# Health check
@api_router.get("/")
async def root():
    return {
        "message": "Renault Trucks Garanti Kayıt Sistemi API",
        "version": APP_VERSION,
        "date": VERSION_DATE,
        "build": BUILD_NUMBER
    }

# Version endpoint
@api_router.get("/version")
async def get_version():
    return {
        "version": APP_VERSION,
        "date": VERSION_DATE,
        "build": BUILD_NUMBER,
        "fullVersion": f"v{APP_VERSION} ({BUILD_NUMBER})"
    }

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
    await db.uploads.create_index("branch_code")
    await db.users.create_index("username", unique=True)
    await db.users.create_index("branch_code")
    
    # Create default admin if not exists
    admin = await db.users.find_one({"username": "admin"})
    if not admin:
        admin_doc = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "password": hash_password("admin123"),
            "full_name": "Sistem Yöneticisi",
            "role": "admin",
            "branch_code": None,
            "branch_name": None,
            "job_title": None,
            "job_title_display": None,
            "phone": None,
            "whatsapp": None,
            "is_online": False,
            "last_seen": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_doc)
        logger.info("Default admin user created: admin / admin123")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
