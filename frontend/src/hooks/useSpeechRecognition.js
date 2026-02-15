import { useState, useRef, useCallback } from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const useSpeechRecognition = () => {
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState(null);
  const [source, setSource] = useState('browser'); // 'browser' or 'server'
  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const isSupported = !!SpeechRecognition;

  // Browser-based speech recognition (Web Speech API)
  const startListening = useCallback((language = 'tr-TR') => {
    if (!isSupported) {
      setError('Tarayıcınız ses tanımayı desteklemiyor');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;

      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = language;

      recognition.onstart = () => {
        setIsListening(true);
        setSource('browser');
        setError(null);
      };

      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += result;
          } else {
            interimTranscript += result;
          }
        }

        setTranscript(prev => prev + finalTranscript + interimTranscript);
      };

      recognition.onerror = (event) => {
        setError(event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } catch (err) {
      setError(err.message);
    }
  }, [isSupported, SpeechRecognition]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  }, []);

  // Server-based speech recognition (OpenAI Whisper via backend)
  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.start(100);
      setIsRecording(true);
      setError(null);
    } catch (err) {
      setError('Mikrofon erişimi başarısız: ' + err.message);
    }
  }, []);

  const stopRecordingAndTranscribe = useCallback(async (language = 'tr', provider = 'openai') => {
    if (!mediaRecorderRef.current) return;

    return new Promise((resolve) => {
      const mediaRecorder = mediaRecorderRef.current;
      
      mediaRecorder.onstop = async () => {
        setIsRecording(false);
        setIsTranscribing(true);
        
        try {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('file', audioBlob, 'audio.webm');
          formData.append('language', language);
          formData.append('provider', provider);
          
          const response = await axios.post(`${API}/voice/transcribe`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 30000
          });
          
          if (response.data.success) {
            setTranscript(prev => prev + (prev ? ' ' : '') + response.data.text);
            setSource('server');
            resolve({ success: true, text: response.data.text });
          } else if (response.data.use_browser) {
            setError('Sunucu transkripsiyonu yapılandırılmamış, tarayıcı kullanın');
            resolve({ success: false, useBrowser: true });
          } else {
            setError(response.data.error || 'Transkripsiyon başarısız');
            resolve({ success: false, error: response.data.error });
          }
        } catch (err) {
          setError('Transkripsiyon hatası: ' + err.message);
          resolve({ success: false, error: err.message });
        } finally {
          setIsTranscribing(false);
          // Stop all tracks
          mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.stop();
    });
  }, []);

  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      mediaRecorderRef.current = null;
      audioChunksRef.current = [];
      setIsRecording(false);
    }
  }, [isRecording]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
  }, []);

  return {
    transcript,
    isListening,
    isRecording,
    isTranscribing,
    error,
    isSupported,
    source,
    startListening,
    stopListening,
    startRecording,
    stopRecordingAndTranscribe,
    cancelRecording,
    resetTranscript,
    setTranscript
  };
};
