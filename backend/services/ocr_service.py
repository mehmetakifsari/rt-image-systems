# OCR Service using Google Vision API
# Falls back to browser-based Tesseract.js if not configured

import os
import logging
import base64
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

GOOGLE_VISION_API_KEY = os.environ.get('GOOGLE_VISION_API_KEY')


class OCRService:
    """OCR service using Google Cloud Vision API"""
    
    def __init__(self):
        self.client = None
        if self.is_configured():
            try:
                from google.cloud import vision
                self.client = vision.ImageAnnotatorClient()
            except Exception as e:
                logger.error(f"Vision API client init error: {e}")
    
    def is_configured(self) -> bool:
        return bool(GOOGLE_VISION_API_KEY) or bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    
    async def detect_text(self, image_content: bytes) -> Dict[str, Any]:
        """Detect text from image bytes"""
        if not self.client:
            return {"success": False, "error": "Vision API not configured", "use_browser": True}
        
        try:
            from google.cloud import vision
            
            image = vision.Image(content=image_content)
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                return {"success": False, "error": response.error.message}
            
            texts = response.text_annotations
            if texts:
                return {
                    "success": True,
                    "full_text": texts[0].description,
                    "words": [{"text": t.description, "confidence": 0.9} for t in texts[1:]]
                }
            return {"success": True, "full_text": "", "words": []}
        except Exception as e:
            logger.error(f"Vision API error: {e}")
            return {"success": False, "error": str(e)}
    
    async def detect_license_plate(self, image_content: bytes) -> Dict[str, Any]:
        """Detect license plate from image"""
        if not self.client:
            return {"success": False, "error": "Vision API not configured", "use_browser": True}
        
        try:
            from google.cloud import vision
            
            image = vision.Image(content=image_content)
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                return {"success": False, "error": response.error.message}
            
            texts = response.text_annotations
            if texts:
                full_text = texts[0].description
                # Turkish license plate pattern: 34 ABC 1234 or 34ABC1234
                import re
                plate_pattern = r'\b(\d{2}\s?[A-Z]{1,3}\s?\d{2,4})\b'
                matches = re.findall(plate_pattern, full_text.upper().replace('\n', ' '))
                
                if matches:
                    # Clean up the plate
                    plate = matches[0].replace(' ', '')
                    return {
                        "success": True,
                        "plate": plate,
                        "confidence": 0.9,
                        "raw_text": full_text
                    }
                return {"success": True, "plate": None, "raw_text": full_text}
            return {"success": True, "plate": None, "raw_text": ""}
        except Exception as e:
            logger.error(f"Vision API plate detection error: {e}")
            return {"success": False, "error": str(e)}
    
    async def detect_text_from_url(self, image_url: str) -> Dict[str, Any]:
        """Detect text from image URL"""
        if not self.client:
            return {"success": False, "error": "Vision API not configured", "use_browser": True}
        
        try:
            from google.cloud import vision
            
            image = vision.Image()
            image.source.image_uri = image_url
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                return {"success": False, "error": response.error.message}
            
            texts = response.text_annotations
            if texts:
                return {
                    "success": True,
                    "full_text": texts[0].description,
                    "words": [{"text": t.description} for t in texts[1:]]
                }
            return {"success": True, "full_text": "", "words": []}
        except Exception as e:
            logger.error(f"Vision API URL error: {e}")
            return {"success": False, "error": str(e)}


# Using REST API instead of client library (alternative method)
class VisionAPIRest:
    """Google Vision API using REST (no client library needed)"""
    
    def __init__(self):
        self.api_key = GOOGLE_VISION_API_KEY
        self.base_url = "https://vision.googleapis.com/v1/images:annotate"
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def detect_text(self, image_content: bytes) -> Dict[str, Any]:
        """Detect text using REST API"""
        if not self.is_configured():
            return {"success": False, "error": "Vision API key not configured", "use_browser": True}
        
        try:
            import aiohttp
            
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            payload = {
                "requests": [{
                    "image": {"content": image_base64},
                    "features": [{"type": "TEXT_DETECTION"}]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}?key={self.api_key}",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        annotations = data.get('responses', [{}])[0].get('textAnnotations', [])
                        if annotations:
                            return {
                                "success": True,
                                "full_text": annotations[0].get('description', ''),
                                "words": [{"text": a.get('description', '')} for a in annotations[1:]]
                            }
                        return {"success": True, "full_text": "", "words": []}
                    else:
                        error_data = await response.json()
                        return {"success": False, "error": error_data.get('error', {}).get('message', 'Unknown error')}
        except Exception as e:
            logger.error(f"Vision REST API error: {e}")
            return {"success": False, "error": str(e)}
    
    async def detect_license_plate(self, image_content: bytes) -> Dict[str, Any]:
        """Detect license plate using REST API"""
        result = await self.detect_text(image_content)
        
        if not result.get('success') or not result.get('full_text'):
            return result
        
        import re
        full_text = result['full_text']
        plate_pattern = r'\b(\d{2}\s?[A-Z]{1,3}\s?\d{2,4})\b'
        matches = re.findall(plate_pattern, full_text.upper().replace('\n', ' '))
        
        if matches:
            plate = matches[0].replace(' ', '')
            return {
                "success": True,
                "plate": plate,
                "confidence": 0.9,
                "raw_text": full_text
            }
        return {"success": True, "plate": None, "raw_text": full_text}


# Singleton instances
ocr_service = OCRService()
vision_api_rest = VisionAPIRest()


def get_ocr_service():
    """Get the best available OCR service"""
    if ocr_service.is_configured():
        return ocr_service
    if vision_api_rest.is_configured():
        return vision_api_rest
    return None
