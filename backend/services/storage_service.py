# Storage Service Module for RT KAYIT
# Supports: Local, S3, Google Drive, FTP, OneDrive

import os
import logging
import asyncio
from typing import Optional, Tuple, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import aiofiles
import uuid

logger = logging.getLogger(__name__)

# Environment variables for storage providers
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'eu-central-1')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

GOOGLE_DRIVE_CREDENTIALS = os.environ.get('GOOGLE_DRIVE_CREDENTIALS')
GOOGLE_DRIVE_FOLDER_ID = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')

FTP_HOST = os.environ.get('FTP_HOST')
FTP_USER = os.environ.get('FTP_USER')
FTP_PASSWORD = os.environ.get('FTP_PASSWORD')
FTP_PATH = os.environ.get('FTP_PATH', '/uploads')

ONEDRIVE_CLIENT_ID = os.environ.get('ONEDRIVE_CLIENT_ID')
ONEDRIVE_CLIENT_SECRET = os.environ.get('ONEDRIVE_CLIENT_SECRET')
ONEDRIVE_FOLDER_PATH = os.environ.get('ONEDRIVE_FOLDER_PATH', '/RTKayit')


class StorageProvider(ABC):
    """Abstract base class for storage providers"""
    
    @abstractmethod
    async def upload_file(self, file_path: str, destination: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload a file. Returns (success, url, error)"""
        pass
    
    @abstractmethod
    async def download_file(self, file_key: str, destination: str) -> Tuple[bool, Optional[str]]:
        """Download a file. Returns (success, error)"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_key: str) -> Tuple[bool, Optional[str]]:
        """Delete a file. Returns (success, error)"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
        """Get a URL to access the file"""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if this provider is properly configured"""
        pass


class LocalStorageProvider(StorageProvider):
    """Local file system storage"""
    
    def __init__(self, base_path: str = "/app/uploads"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def is_configured(self) -> bool:
        return True
    
    async def upload_file(self, file_path: str, destination: str) -> Tuple[bool, Optional[str], Optional[str]]:
        try:
            dest_path = os.path.join(self.base_path, destination)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            async with aiofiles.open(file_path, 'rb') as src:
                content = await src.read()
            async with aiofiles.open(dest_path, 'wb') as dst:
                await dst.write(content)
            
            return True, f"/uploads/{destination}", None
        except Exception as e:
            logger.error(f"Local upload error: {e}")
            return False, None, str(e)
    
    async def download_file(self, file_key: str, destination: str) -> Tuple[bool, Optional[str]]:
        try:
            src_path = os.path.join(self.base_path, file_key)
            async with aiofiles.open(src_path, 'rb') as src:
                content = await src.read()
            async with aiofiles.open(destination, 'wb') as dst:
                await dst.write(content)
            return True, None
        except Exception as e:
            logger.error(f"Local download error: {e}")
            return False, str(e)
    
    async def delete_file(self, file_key: str) -> Tuple[bool, Optional[str]]:
        try:
            file_path = os.path.join(self.base_path, file_key)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True, None
        except Exception as e:
            logger.error(f"Local delete error: {e}")
            return False, str(e)
    
    async def get_file_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
        return f"/uploads/{file_key}"


class S3StorageProvider(StorageProvider):
    """AWS S3 storage provider"""
    
    def __init__(self):
        self.client = None
        if self.is_configured():
            try:
                import boto3
                self.client = boto3.client(
                    's3',
                    region_name=AWS_REGION,
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                )
            except Exception as e:
                logger.error(f"S3 client init error: {e}")
    
    def is_configured(self) -> bool:
        return all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME])
    
    async def upload_file(self, file_path: str, destination: str) -> Tuple[bool, Optional[str], Optional[str]]:
        if not self.client:
            return False, None, "S3 not configured"
        try:
            self.client.upload_file(
                file_path,
                S3_BUCKET_NAME,
                destination,
                ExtraArgs={'ServerSideEncryption': 'AES256'}
            )
            url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{destination}"
            return True, url, None
        except Exception as e:
            logger.error(f"S3 upload error: {e}")
            return False, None, str(e)
    
    async def download_file(self, file_key: str, destination: str) -> Tuple[bool, Optional[str]]:
        if not self.client:
            return False, "S3 not configured"
        try:
            self.client.download_file(S3_BUCKET_NAME, file_key, destination)
            return True, None
        except Exception as e:
            logger.error(f"S3 download error: {e}")
            return False, str(e)
    
    async def delete_file(self, file_key: str) -> Tuple[bool, Optional[str]]:
        if not self.client:
            return False, "S3 not configured"
        try:
            self.client.delete_object(Bucket=S3_BUCKET_NAME, Key=file_key)
            return True, None
        except Exception as e:
            logger.error(f"S3 delete error: {e}")
            return False, str(e)
    
    async def get_file_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
        if not self.client:
            return None
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': file_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"S3 presigned URL error: {e}")
            return None


class GoogleDriveStorageProvider(StorageProvider):
    """Google Drive storage provider"""
    
    def __init__(self):
        self.service = None
        if self.is_configured():
            try:
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
                import json
                
                creds_dict = json.loads(GOOGLE_DRIVE_CREDENTIALS)
                creds = service_account.Credentials.from_service_account_info(
                    creds_dict,
                    scopes=['https://www.googleapis.com/auth/drive.file']
                )
                self.service = build('drive', 'v3', credentials=creds)
            except Exception as e:
                logger.error(f"Google Drive init error: {e}")
    
    def is_configured(self) -> bool:
        return bool(GOOGLE_DRIVE_CREDENTIALS)
    
    async def upload_file(self, file_path: str, destination: str) -> Tuple[bool, Optional[str], Optional[str]]:
        if not self.service:
            return False, None, "Google Drive not configured"
        try:
            from googleapiclient.http import MediaFileUpload
            
            file_metadata = {
                'name': os.path.basename(destination),
                'parents': [GOOGLE_DRIVE_FOLDER_ID] if GOOGLE_DRIVE_FOLDER_ID else []
            }
            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            return True, file.get('webViewLink'), None
        except Exception as e:
            logger.error(f"Google Drive upload error: {e}")
            return False, None, str(e)
    
    async def download_file(self, file_key: str, destination: str) -> Tuple[bool, Optional[str]]:
        if not self.service:
            return False, "Google Drive not configured"
        try:
            from googleapiclient.http import MediaIoBaseDownload
            import io
            
            request = self.service.files().get_media(fileId=file_key)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            async with aiofiles.open(destination, 'wb') as f:
                await f.write(fh.getvalue())
            return True, None
        except Exception as e:
            logger.error(f"Google Drive download error: {e}")
            return False, str(e)
    
    async def delete_file(self, file_key: str) -> Tuple[bool, Optional[str]]:
        if not self.service:
            return False, "Google Drive not configured"
        try:
            self.service.files().delete(fileId=file_key).execute()
            return True, None
        except Exception as e:
            logger.error(f"Google Drive delete error: {e}")
            return False, str(e)
    
    async def get_file_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
        if not self.service:
            return None
        try:
            file = self.service.files().get(fileId=file_key, fields='webViewLink').execute()
            return file.get('webViewLink')
        except Exception as e:
            logger.error(f"Google Drive URL error: {e}")
            return None


class FTPStorageProvider(StorageProvider):
    """FTP storage provider"""
    
    def is_configured(self) -> bool:
        return all([FTP_HOST, FTP_USER, FTP_PASSWORD])
    
    async def upload_file(self, file_path: str, destination: str) -> Tuple[bool, Optional[str], Optional[str]]:
        if not self.is_configured():
            return False, None, "FTP not configured"
        try:
            import ftplib
            
            with ftplib.FTP(FTP_HOST) as ftp:
                ftp.login(FTP_USER, FTP_PASSWORD)
                
                # Create directory if needed
                remote_dir = os.path.dirname(f"{FTP_PATH}/{destination}")
                try:
                    ftp.mkd(remote_dir)
                except:
                    pass
                
                with open(file_path, 'rb') as f:
                    ftp.storbinary(f'STOR {FTP_PATH}/{destination}', f)
            
            return True, f"ftp://{FTP_HOST}{FTP_PATH}/{destination}", None
        except Exception as e:
            logger.error(f"FTP upload error: {e}")
            return False, None, str(e)
    
    async def download_file(self, file_key: str, destination: str) -> Tuple[bool, Optional[str]]:
        if not self.is_configured():
            return False, "FTP not configured"
        try:
            import ftplib
            
            with ftplib.FTP(FTP_HOST) as ftp:
                ftp.login(FTP_USER, FTP_PASSWORD)
                with open(destination, 'wb') as f:
                    ftp.retrbinary(f'RETR {FTP_PATH}/{file_key}', f.write)
            return True, None
        except Exception as e:
            logger.error(f"FTP download error: {e}")
            return False, str(e)
    
    async def delete_file(self, file_key: str) -> Tuple[bool, Optional[str]]:
        if not self.is_configured():
            return False, "FTP not configured"
        try:
            import ftplib
            
            with ftplib.FTP(FTP_HOST) as ftp:
                ftp.login(FTP_USER, FTP_PASSWORD)
                ftp.delete(f"{FTP_PATH}/{file_key}")
            return True, None
        except Exception as e:
            logger.error(f"FTP delete error: {e}")
            return False, str(e)
    
    async def get_file_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
        return f"ftp://{FTP_HOST}{FTP_PATH}/{file_key}"


class OneDriveStorageProvider(StorageProvider):
    """OneDrive storage provider (Microsoft Graph API)"""
    
    def __init__(self):
        self.access_token = None
        if self.is_configured():
            self._get_access_token()
    
    def is_configured(self) -> bool:
        return all([ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET])
    
    def _get_access_token(self):
        try:
            import requests
            
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            data = {
                'client_id': ONEDRIVE_CLIENT_ID,
                'client_secret': ONEDRIVE_CLIENT_SECRET,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            response = requests.post(token_url, data=data)
            if response.ok:
                self.access_token = response.json().get('access_token')
        except Exception as e:
            logger.error(f"OneDrive token error: {e}")
    
    async def upload_file(self, file_path: str, destination: str) -> Tuple[bool, Optional[str], Optional[str]]:
        if not self.access_token:
            return False, None, "OneDrive not configured"
        try:
            import requests
            
            headers = {'Authorization': f'Bearer {self.access_token}'}
            upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{ONEDRIVE_FOLDER_PATH}/{destination}:/content"
            
            with open(file_path, 'rb') as f:
                response = requests.put(upload_url, headers=headers, data=f)
            
            if response.ok:
                data = response.json()
                return True, data.get('webUrl'), None
            return False, None, response.text
        except Exception as e:
            logger.error(f"OneDrive upload error: {e}")
            return False, None, str(e)
    
    async def download_file(self, file_key: str, destination: str) -> Tuple[bool, Optional[str]]:
        if not self.access_token:
            return False, "OneDrive not configured"
        try:
            import requests
            
            headers = {'Authorization': f'Bearer {self.access_token}'}
            url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_key}/content"
            response = requests.get(url, headers=headers)
            
            if response.ok:
                async with aiofiles.open(destination, 'wb') as f:
                    await f.write(response.content)
                return True, None
            return False, response.text
        except Exception as e:
            logger.error(f"OneDrive download error: {e}")
            return False, str(e)
    
    async def delete_file(self, file_key: str) -> Tuple[bool, Optional[str]]:
        if not self.access_token:
            return False, "OneDrive not configured"
        try:
            import requests
            
            headers = {'Authorization': f'Bearer {self.access_token}'}
            url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_key}"
            response = requests.delete(url, headers=headers)
            
            if response.status_code in [200, 204]:
                return True, None
            return False, response.text
        except Exception as e:
            logger.error(f"OneDrive delete error: {e}")
            return False, str(e)
    
    async def get_file_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
        return None  # OneDrive requires different approach for sharing


class StorageManager:
    """Manages multiple storage providers"""
    
    def __init__(self):
        self.providers: Dict[str, StorageProvider] = {
            'local': LocalStorageProvider(),
            's3': S3StorageProvider(),
            'gdrive': GoogleDriveStorageProvider(),
            'ftp': FTPStorageProvider(),
            'onedrive': OneDriveStorageProvider()
        }
        self.active_provider = 'local'  # Default
    
    def set_active_provider(self, provider_name: str) -> bool:
        if provider_name in self.providers:
            provider = self.providers[provider_name]
            if provider.is_configured():
                self.active_provider = provider_name
                return True
            logger.warning(f"Provider {provider_name} not configured")
        return False
    
    def get_provider(self, provider_name: str = None) -> StorageProvider:
        name = provider_name or self.active_provider
        return self.providers.get(name, self.providers['local'])
    
    def get_configured_providers(self) -> Dict[str, bool]:
        return {name: provider.is_configured() for name, provider in self.providers.items()}
    
    async def upload_file(self, file_path: str, destination: str, provider_name: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        provider = self.get_provider(provider_name)
        return await provider.upload_file(file_path, destination)
    
    async def download_file(self, file_key: str, destination: str, provider_name: str = None) -> Tuple[bool, Optional[str]]:
        provider = self.get_provider(provider_name)
        return await provider.download_file(file_key, destination)
    
    async def delete_file(self, file_key: str, provider_name: str = None) -> Tuple[bool, Optional[str]]:
        provider = self.get_provider(provider_name)
        return await provider.delete_file(file_key)
    
    async def get_file_url(self, file_key: str, provider_name: str = None, expires_in: int = 3600) -> Optional[str]:
        provider = self.get_provider(provider_name)
        return await provider.get_file_url(file_key, expires_in)


# Singleton instance
storage_manager = StorageManager()
