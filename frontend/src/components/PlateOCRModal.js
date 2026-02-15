import React, { useState, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Camera, Loader2, Check, AlertCircle, RotateCcw } from 'lucide-react';
import { usePlateOCR } from '../hooks/usePlateOCR';

const PlateOCRModal = ({ onClose, onPlateDetected }) => {
  const { t } = useTranslation();
  const { processImage, validatePlate, formatPlate, isProcessing, progress } = usePlateOCR();
  
  const [mode, setMode] = useState('camera'); // camera, preview, result
  const [capturedImage, setCapturedImage] = useState(null);
  const [detectedPlate, setDetectedPlate] = useState(null);
  const [editedPlate, setEditedPlate] = useState('');
  const [error, setError] = useState(null);
  
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const fileInputRef = useRef(null);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      setError('Kamera erişimi başarısız');
      setMode('preview');
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, []);

  React.useEffect(() => {
    if (mode === 'camera') {
      startCamera();
    }
    return () => stopCamera();
  }, [mode, startCamera, stopCamera]);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current) return;
    
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg', 0.9);
    setCapturedImage(imageData);
    stopCamera();
    processOCR(imageData);
  }, [stopCamera]);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      setCapturedImage(event.target.result);
      stopCamera();
      processOCR(event.target.result);
    };
    reader.readAsDataURL(file);
  };

  const processOCR = async (imageData) => {
    setMode('result');
    setError(null);
    
    try {
      const result = await processImage(imageData);
      
      if (result.success && result.plate) {
        const formatted = formatPlate(result.plate);
        setDetectedPlate(formatted);
        setEditedPlate(formatted);
      } else {
        setError(t('msg.noPlateDetected'));
        setDetectedPlate(null);
        setEditedPlate('');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleConfirm = () => {
    const plate = editedPlate.trim().toUpperCase();
    if (validatePlate(plate)) {
      onPlateDetected(formatPlate(plate));
    } else {
      setError('Geçersiz plaka formatı');
    }
  };

  const handleRetry = () => {
    setCapturedImage(null);
    setDetectedPlate(null);
    setEditedPlate('');
    setError(null);
    setMode('camera');
  };

  return (
    <div className="fixed inset-0 bg-black/90 z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-zinc-800">
        <h2 className="text-lg font-bold text-white">{t('action.scanPlate')}</h2>
        <button
          onClick={onClose}
          className="w-10 h-10 bg-zinc-800 rounded-xl flex items-center justify-center hover:bg-zinc-700 transition-colors"
        >
          <X className="w-5 h-5 text-white" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        {/* Camera view */}
        {mode === 'camera' && (
          <div className="relative w-full max-w-md aspect-video bg-black rounded-2xl overflow-hidden">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover"
            />
            {/* Overlay frame */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-4/5 h-16 border-2 border-[#FACC15] rounded-lg opacity-70">
                <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[#FACC15] text-xs whitespace-nowrap">
                  Plakayı çerçeveye yerleştirin
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Processing/Result view */}
        {(mode === 'result' || mode === 'preview') && (
          <div className="w-full max-w-md">
            {/* Captured image */}
            {capturedImage && (
              <div className="relative mb-4 rounded-2xl overflow-hidden">
                <img
                  src={capturedImage}
                  alt="Captured"
                  className="w-full"
                />
              </div>
            )}

            {/* Processing state */}
            {isProcessing && (
              <div className="bg-zinc-900 rounded-xl p-6 text-center">
                <Loader2 className="w-8 h-8 text-[#FACC15] animate-spin mx-auto mb-3" />
                <p className="text-white font-medium">Plaka okunuyor...</p>
                <div className="mt-3 bg-zinc-800 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-[#FACC15] h-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Result */}
            {!isProcessing && mode === 'result' && (
              <div className="bg-zinc-900 rounded-xl p-6">
                {detectedPlate ? (
                  <>
                    <div className="flex items-center gap-2 text-green-400 mb-4">
                      <Check className="w-5 h-5" />
                      <span className="font-medium">{t('msg.plateDetected')}</span>
                    </div>
                    <input
                      type="text"
                      value={editedPlate}
                      onChange={(e) => setEditedPlate(e.target.value.toUpperCase())}
                      className="w-full h-14 px-4 bg-zinc-800 border border-zinc-700 rounded-lg text-white text-2xl font-bold text-center uppercase tracking-widest"
                      data-testid="detected-plate-input"
                    />
                    <p className="text-zinc-500 text-xs mt-2 text-center">
                      Gerekirse düzeltebilirsiniz
                    </p>
                  </>
                ) : (
                  <div className="text-center">
                    <AlertCircle className="w-10 h-10 text-yellow-400 mx-auto mb-3" />
                    <p className="text-white font-medium mb-2">{error || t('msg.noPlateDetected')}</p>
                    <p className="text-zinc-500 text-sm">
                      Manuel olarak girebilirsiniz
                    </p>
                    <input
                      type="text"
                      value={editedPlate}
                      onChange={(e) => setEditedPlate(e.target.value.toUpperCase())}
                      placeholder="34 ABC 123"
                      className="w-full h-14 px-4 mt-4 bg-zinc-800 border border-zinc-700 rounded-lg text-white text-2xl font-bold text-center uppercase tracking-widest"
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-zinc-800">
        <div className="max-w-md mx-auto flex gap-3">
          {mode === 'camera' && (
            <>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex-1 h-14 bg-zinc-800 text-white rounded-xl font-medium hover:bg-zinc-700 transition-colors"
              >
                Galeriden Seç
              </button>
              <button
                onClick={capturePhoto}
                className="flex-1 h-14 bg-[#FACC15] text-black rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-yellow-400 transition-colors"
                data-testid="capture-button"
              >
                <Camera className="w-5 h-5" />
                Çek
              </button>
            </>
          )}

          {mode === 'result' && !isProcessing && (
            <>
              <button
                onClick={handleRetry}
                className="h-14 px-6 bg-zinc-800 text-white rounded-xl font-medium hover:bg-zinc-700 transition-colors flex items-center gap-2"
              >
                <RotateCcw className="w-5 h-5" />
                Tekrar
              </button>
              <button
                onClick={handleConfirm}
                disabled={!editedPlate.trim()}
                className="flex-1 h-14 bg-[#FACC15] text-black rounded-xl font-bold hover:bg-yellow-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="confirm-plate-button"
              >
                Onayla
              </button>
            </>
          )}
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileSelect}
      />
    </div>
  );
};

export default PlateOCRModal;
