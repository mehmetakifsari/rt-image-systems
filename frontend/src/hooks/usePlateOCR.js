import { useRef, useCallback, useState } from 'react';
import Tesseract from 'tesseract.js';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Turkish plate regex pattern
const TURKISH_PLATE_REGEX = /^\d{2}\s?[A-ZÇĞİÖŞÜ]{1,3}\s?\d{2,4}$/;

export const usePlateOCR = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [useServerOCR, setUseServerOCR] = useState(false);
  const workerRef = useRef(null);

  // Try server-side OCR first (Google Vision API), fallback to browser
  const processImage = useCallback(async (imageSource) => {
    setIsProcessing(true);
    setProgress(0);
    setError(null);

    // First try server-side OCR if available
    try {
      setProgress(20);
      const formData = new FormData();
      
      // Convert base64 to blob if needed
      if (imageSource.startsWith('data:')) {
        const response = await fetch(imageSource);
        const blob = await response.blob();
        formData.append('file', blob, 'plate.jpg');
      } else {
        formData.append('file', imageSource);
      }
      
      setProgress(40);
      const serverResult = await axios.post(`${API}/ocr/detect-plate`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 10000
      });
      
      if (serverResult.data.success && serverResult.data.plate) {
        setProgress(100);
        setIsProcessing(false);
        setUseServerOCR(true);
        return {
          success: true,
          plate: serverResult.data.plate,
          confidence: serverResult.data.confidence || 0.9,
          rawText: serverResult.data.raw_text,
          source: 'server'
        };
      }
      
      // Server returned no plate, or told us to use browser
      if (serverResult.data.use_browser) {
        throw new Error('Server OCR not configured');
      }
    } catch (serverError) {
      console.log('Server OCR not available, falling back to browser:', serverError.message);
    }

    // Fallback to browser-based Tesseract
    setProgress(50);
    try {
      const result = await Tesseract.recognize(
        imageSource,
        'tur+eng',
        {
          logger: (m) => {
            if (m.status === 'recognizing text') {
              setProgress(50 + Math.round(m.progress * 50));
            }
          }
        }
      );

      const text = result.data.text;
      
      // Extract potential plate numbers
      const lines = text.split('\n').map(line => line.trim().toUpperCase());
      let detectedPlate = null;
      let confidence = 0;

      for (const line of lines) {
        // Clean up the line
        const cleaned = line
          .replace(/[^0-9A-ZÇĞİÖŞÜ\s]/g, '')
          .replace(/\s+/g, ' ')
          .trim();

        // Check if it matches Turkish plate format
        if (TURKISH_PLATE_REGEX.test(cleaned)) {
          detectedPlate = cleaned;
          confidence = result.data.confidence;
          break;
        }

        // Try to find plate-like patterns
        const plateMatch = cleaned.match(/\d{2}\s?[A-ZÇĞİÖŞÜ]{1,3}\s?\d{2,4}/);
        if (plateMatch) {
          detectedPlate = plateMatch[0];
          confidence = result.data.confidence;
          break;
        }
      }

      setIsProcessing(false);
      setUseServerOCR(false);
      
      return {
        success: !!detectedPlate,
        plate: detectedPlate,
        confidence,
        rawText: text,
        source: 'browser'
      };
    } catch (err) {
      setError(err.message);
      setIsProcessing(false);
      return {
        success: false,
        plate: null,
        confidence: 0,
        error: err.message
      };
    }
  }, []);

  const validatePlate = useCallback((plate) => {
    if (!plate) return false;
    const cleaned = plate.toUpperCase().replace(/\s+/g, ' ').trim();
    return TURKISH_PLATE_REGEX.test(cleaned);
  }, []);

  const formatPlate = useCallback((plate) => {
    if (!plate) return '';
    // Format as: 34 ABC 123
    const cleaned = plate.toUpperCase().replace(/\s+/g, '');
    const match = cleaned.match(/^(\d{2})([A-ZÇĞİÖŞÜ]{1,3})(\d{2,4})$/);
    if (match) {
      return `${match[1]} ${match[2]} ${match[3]}`;
    }
    return plate;
  }, []);

  return {
    processImage,
    validatePlate,
    formatPlate,
    isProcessing,
    progress,
    error,
    useServerOCR
  };
};
