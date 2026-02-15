import { useRef, useCallback, useState } from 'react';
import Tesseract from 'tesseract.js';

// Turkish plate regex pattern
const TURKISH_PLATE_REGEX = /^\d{2}\s?[A-ZÇĞİÖŞÜ]{1,3}\s?\d{2,4}$/;

export const usePlateOCR = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const workerRef = useRef(null);

  const processImage = useCallback(async (imageSource) => {
    setIsProcessing(true);
    setProgress(0);
    setError(null);

    try {
      const result = await Tesseract.recognize(
        imageSource,
        'tur+eng',
        {
          logger: (m) => {
            if (m.status === 'recognizing text') {
              setProgress(Math.round(m.progress * 100));
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
      
      return {
        success: !!detectedPlate,
        plate: detectedPlate,
        confidence,
        rawText: text
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
    error
  };
};
