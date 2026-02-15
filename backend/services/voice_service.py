# Voice-to-Text Service using OpenAI Whisper via Emergent Integration
# Also supports Gemini for speech recognition

import os
import logging
import tempfile
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Emergent LLM Key (Universal Key for OpenAI/Gemini/Claude)
EMERGENT_LLM_KEY = os.environ.get('LLM_API_KEY')


class VoiceToTextService:
    """Voice to text transcription service using OpenAI Whisper"""
    
    def __init__(self):
        self.api_key = EMERGENT_LLM_KEY
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def transcribe_audio(self, audio_content: bytes, language: str = "tr") -> Dict[str, Any]:
        """Transcribe audio to text using OpenAI Whisper"""
        if not self.is_configured():
            return {"success": False, "error": "Voice service not configured", "use_browser": True}
        
        try:
            from emergentintegrations.llm.openai import transcribe_audio as emergent_transcribe
            
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
                f.write(audio_content)
                temp_path = f.name
            
            try:
                result = await emergent_transcribe(
                    api_key=self.api_key,
                    audio_file_path=temp_path,
                    language=language
                )
                
                return {
                    "success": True,
                    "text": result.get("text", ""),
                    "language": language,
                    "duration": result.get("duration")
                }
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except ImportError:
            logger.warning("emergentintegrations not available, falling back to direct API")
            return await self._transcribe_direct(audio_content, language)
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _transcribe_direct(self, audio_content: bytes, language: str = "tr") -> Dict[str, Any]:
        """Direct API call to OpenAI Whisper"""
        try:
            import aiohttp
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
                f.write(audio_content)
                temp_path = f.name
            
            try:
                data = aiohttp.FormData()
                data.add_field('file', open(temp_path, 'rb'), filename='audio.webm')
                data.add_field('model', 'whisper-1')
                data.add_field('language', language)
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        'https://api.openai.com/v1/audio/transcriptions',
                        headers={'Authorization': f'Bearer {self.api_key}'},
                        data=data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return {
                                "success": True,
                                "text": result.get("text", ""),
                                "language": language
                            }
                        else:
                            error = await response.text()
                            return {"success": False, "error": error}
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"Direct Whisper API error: {e}")
            return {"success": False, "error": str(e)}
    
    async def transcribe_from_url(self, audio_url: str, language: str = "tr") -> Dict[str, Any]:
        """Transcribe audio from URL"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_url) as response:
                    if response.status == 200:
                        audio_content = await response.read()
                        return await self.transcribe_audio(audio_content, language)
                    return {"success": False, "error": f"Failed to download audio: {response.status}"}
        except Exception as e:
            logger.error(f"Audio download error: {e}")
            return {"success": False, "error": str(e)}


class GeminiVoiceService:
    """Voice to text using Gemini (alternative provider)"""
    
    def __init__(self):
        self.api_key = EMERGENT_LLM_KEY
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def transcribe_audio(self, audio_content: bytes, language: str = "tr") -> Dict[str, Any]:
        """Transcribe using Gemini's audio understanding"""
        if not self.is_configured():
            return {"success": False, "error": "Gemini not configured", "use_browser": True}
        
        try:
            from emergentintegrations.llm.gemini import generate_with_audio
            
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
                f.write(audio_content)
                temp_path = f.name
            
            try:
                prompt = f"Bu ses kaydını Türkçe olarak yazıya dök. Sadece konuşma metnini ver, başka bir şey ekleme."
                if language != "tr":
                    prompt = f"Transcribe this audio recording. Only provide the spoken text, nothing else."
                
                result = await generate_with_audio(
                    api_key=self.api_key,
                    prompt=prompt,
                    audio_file_path=temp_path
                )
                
                return {
                    "success": True,
                    "text": result.get("text", ""),
                    "language": language
                }
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except ImportError:
            logger.warning("emergentintegrations Gemini not available")
            return {"success": False, "error": "Gemini integration not available", "use_browser": True}
        except Exception as e:
            logger.error(f"Gemini transcription error: {e}")
            return {"success": False, "error": str(e)}


# Singleton instances
whisper_service = VoiceToTextService()
gemini_voice_service = GeminiVoiceService()


def get_voice_service(provider: str = "openai"):
    """Get voice service by provider"""
    if provider == "gemini":
        return gemini_voice_service if gemini_voice_service.is_configured() else None
    return whisper_service if whisper_service.is_configured() else None
