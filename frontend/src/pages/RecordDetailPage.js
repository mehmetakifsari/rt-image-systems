import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft, Camera, Video, FileText, Mic, MicOff, Send, 
  Trash2, Loader2, X, Play, Pause, Download, Image as ImageIcon,
  Check, AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';
import { useOffline } from '../contexts/OfflineContext';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const RECORD_TYPE_LABELS = {
  standard: 'Standart',
  roadassist: 'Yol Yardım',
  damaged: 'Hasarlı',
  pdi: 'PDI'
};

const RecordDetailPage = () => {
  const { t, i18n } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const { isOnline, addToQueue } = useOffline();
  const { 
    transcript, isListening, isSupported, 
    startListening, stopListening, resetTranscript, setTranscript 
  } = useSpeechRecognition();
  
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [noteText, setNoteText] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchRecord();
  }, [id]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [record?.files_json]);

  useEffect(() => {
    if (transcript) {
      setNoteText(prev => prev + ' ' + transcript);
      resetTranscript();
    }
  }, [transcript]);

  const fetchRecord = async () => {
    try {
      const response = await axios.get(`${API}/records/${id}`);
      setRecord(response.data);
      setNoteText(response.data.note_text || '');
    } catch (error) {
      toast.error('Kayıt bulunamadı');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (type) => {
    fileInputRef.current.accept = type === 'photo' 
      ? 'image/jpeg,image/png,image/webp'
      : type === 'video'
      ? 'video/mp4,video/mov,video/webm'
      : 'application/pdf';
    fileInputRef.current.dataset.mediaType = type;
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const mediaType = e.target.dataset.mediaType;
    
    // Validate file size
    const maxSize = mediaType === 'photo' ? 10 : mediaType === 'video' ? 120 : 30;
    if (file.size > maxSize * 1024 * 1024) {
      toast.error(`Dosya çok büyük. Maksimum: ${maxSize}MB`);
      return;
    }

    if (!isOnline) {
      // Add to offline queue
      await addToQueue({
        recordId: id,
        file,
        mediaType,
        fileName: file.name
      });
      toast.info(t('msg.offlineQueue'));
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('media_type', mediaType);

      const response = await axios.post(
        `${API}/records/${id}/upload`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(progress);
          }
        }
      );

      toast.success(t('msg.fileUploaded'));
      fetchRecord();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Yükleme hatası');
    } finally {
      setUploading(false);
      setUploadProgress(0);
      e.target.value = '';
    }
  };

  const handleDeleteFile = async (fileId) => {
    try {
      await axios.delete(`${API}/records/${id}/files/${fileId}`);
      toast.success(t('msg.fileDeleted'));
      fetchRecord();
    } catch (error) {
      toast.error('Silme hatası');
    }
    setShowDeleteConfirm(null);
  };

  const handleSaveNote = async () => {
    try {
      const formData = new FormData();
      formData.append('note_text', noteText);
      await axios.put(`${API}/records/${id}/note`, formData);
      toast.success('Not kaydedildi');
    } catch (error) {
      toast.error('Kaydetme hatası');
    }
  };

  const toggleVoice = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening(i18n.language === 'tr' ? 'tr-TR' : 'en-US');
    }
  };

  const getRecordTitle = () => {
    if (!record) return '';
    if (record.plate) return record.plate;
    if (record.vin) return `VIN: ...${record.vin.slice(-5)}`;
    if (record.reference_no) return `Ref: ${record.reference_no}`;
    return record.case_key;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleTimeString('tr-TR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#FACC15] animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col">
      {/* Header */}
      <header className="glass-header sticky top-0 z-40 px-4 py-3">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="w-10 h-10 bg-[#18181b] rounded-xl flex items-center justify-center hover:bg-[#27272a] transition-colors"
            data-testid="back-button"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>
          <div className="flex-1 min-w-0">
            <h1 className="text-lg font-bold text-white truncate">
              {getRecordTitle()}
            </h1>
            <p className="text-xs text-zinc-500">
              {RECORD_TYPE_LABELS[record.record_type]} • {record.work_order || record.case_key}
            </p>
          </div>
        </div>
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 max-w-lg mx-auto w-full">
        {/* Record info card */}
        <div className="chat-bubble-system p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Check className="w-4 h-4 text-green-400" />
            <span className="text-green-400 text-sm font-medium">Kayıt oluşturuldu</span>
          </div>
          <div className="space-y-1 text-sm">
            {record.plate && (
              <p><span className="text-zinc-500">Plaka:</span> {record.plate}</p>
            )}
            {record.work_order && (
              <p><span className="text-zinc-500">İş Emri:</span> {record.work_order}</p>
            )}
            {record.vin && (
              <p><span className="text-zinc-500">VIN:</span> {record.vin}</p>
            )}
            {record.reference_no && (
              <p><span className="text-zinc-500">Referans:</span> {record.reference_no}</p>
            )}
          </div>
          <p className="text-zinc-600 text-xs mt-2">
            {new Date(record.created_at).toLocaleString('tr-TR')}
          </p>
        </div>

        {/* Files */}
        <div className="space-y-3">
          {(record.files_json || []).map((file, index) => (
            <div key={file.id} className="chat-bubble-user p-1 relative group">
              {/* Media preview */}
              {file.media_type === 'photo' && (
                <img
                  src={`${BACKEND_URL}${file.path}`}
                  alt={file.original_name}
                  className="w-full max-w-xs rounded-xl"
                  loading="lazy"
                />
              )}
              {file.media_type === 'video' && (
                <video
                  src={`${BACKEND_URL}${file.path}`}
                  className="w-full max-w-xs rounded-xl"
                  controls
                />
              )}
              {file.media_type === 'pdf' && (
                <a
                  href={`${BACKEND_URL}${file.path}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-3 bg-black/20 rounded-xl"
                >
                  <FileText className="w-8 h-8" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{file.original_name}</p>
                    <p className="text-xs opacity-70">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <Download className="w-5 h-5" />
                </a>
              )}
              
              {/* Delete button */}
              <button
                onClick={() => setShowDeleteConfirm(file.id)}
                className="absolute top-2 right-2 w-8 h-8 bg-black/50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <Trash2 className="w-4 h-4 text-white" />
              </button>
              
              {/* Time */}
              <p className="text-[10px] opacity-60 text-right mt-1 px-2">
                {formatDate(file.uploaded_at)}
              </p>
            </div>
          ))}
        </div>

        {/* Upload progress */}
        {uploading && (
          <div className="chat-bubble-user p-4 mt-3">
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 animate-spin" />
              <div className="flex-1">
                <p className="text-sm font-medium">{t('status.uploading')}</p>
                <div className="upload-progress h-2 mt-2">
                  <div 
                    className="upload-progress-bar" 
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
              <span className="text-sm font-bold">{uploadProgress}%</span>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Note input area */}
      <div className="border-t border-[#27272a] bg-[#09090b] p-4">
        <div className="max-w-lg mx-auto">
          {/* Note textarea */}
          <div className="flex gap-2 mb-3">
            <textarea
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              placeholder={t('field.note') + '...'}
              rows={2}
              className="flex-1 px-4 py-3 bg-[#18181b] border border-[#27272a] rounded-xl text-white placeholder-zinc-500 resize-none text-sm"
              data-testid="note-textarea"
            />
            <div className="flex flex-col gap-2">
              {isSupported && (
                <button
                  onClick={toggleVoice}
                  className={`w-11 h-11 rounded-xl flex items-center justify-center transition-colors ${
                    isListening 
                      ? 'bg-red-500 text-white recording-indicator relative' 
                      : 'bg-[#27272a] text-zinc-400 hover:text-white'
                  }`}
                  data-testid="voice-button"
                >
                  {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>
              )}
              <button
                onClick={handleSaveNote}
                className="w-11 h-11 bg-[#FACC15] rounded-xl flex items-center justify-center text-black hover:bg-yellow-400 transition-colors"
                data-testid="save-note-button"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-2">
            <button
              onClick={() => handleFileSelect('photo')}
              disabled={uploading}
              className="flex-1 h-12 bg-[#18181b] border border-[#27272a] rounded-xl text-white flex items-center justify-center gap-2 hover:bg-[#27272a] transition-colors disabled:opacity-50"
              data-testid="photo-button"
            >
              <Camera className="w-5 h-5 text-[#FACC15]" />
              <span className="text-sm">{t('misc.photo')}</span>
            </button>
            <button
              onClick={() => handleFileSelect('video')}
              disabled={uploading}
              className="flex-1 h-12 bg-[#18181b] border border-[#27272a] rounded-xl text-white flex items-center justify-center gap-2 hover:bg-[#27272a] transition-colors disabled:opacity-50"
              data-testid="video-button"
            >
              <Video className="w-5 h-5 text-blue-400" />
              <span className="text-sm">{t('misc.video')}</span>
            </button>
            <button
              onClick={() => handleFileSelect('pdf')}
              disabled={uploading}
              className="flex-1 h-12 bg-[#18181b] border border-[#27272a] rounded-xl text-white flex items-center justify-center gap-2 hover:bg-[#27272a] transition-colors disabled:opacity-50"
              data-testid="pdf-button"
            >
              <FileText className="w-5 h-5 text-red-400" />
              <span className="text-sm">{t('misc.pdf')}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-[#18181b] border border-[#27272a] rounded-2xl p-6 max-w-sm w-full">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-red-500/10 rounded-xl flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <h3 className="text-white font-semibold">{t('action.delete')}</h3>
                <p className="text-zinc-500 text-sm">{t('msg.confirmDelete')}</p>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="flex-1 h-11 bg-[#27272a] text-white rounded-lg hover:bg-[#3f3f46] transition-colors"
              >
                {t('action.cancel')}
              </button>
              <button
                onClick={() => handleDeleteFile(showDeleteConfirm)}
                className="flex-1 h-11 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                {t('action.delete')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecordDetailPage;
