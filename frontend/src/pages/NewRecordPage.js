import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft, Wrench, Truck, AlertTriangle, ClipboardCheck,
  Loader2, ScanLine, Building2, Mic, MicOff, Square
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';
import PlateOCRModal from '../components/PlateOCRModal';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const BRANCHES = [
  { code: "1", name: "Bursa" },
  { code: "2", name: "İzmit" },
  { code: "3", name: "Orhanlı" },
  { code: "4", name: "Hadımköy" },
  { code: "5", name: "Keşan" }
];

const RECORD_TYPES = [
  {
    id: 'standard',
    icon: Wrench,
    color: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    fields: { plate: true, workOrder: true, vin: false, referenceNo: false },
    needsBranch: false // Şube iş emrinden çıkarılır
  },
  {
    id: 'roadassist',
    icon: Truck,
    color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    fields: { plate: true, workOrder: false, vin: false, referenceNo: false },
    needsBranch: true
  },
  {
    id: 'damaged',
    icon: AlertTriangle,
    color: 'bg-red-900/20 text-red-400 border-red-500/30',
    fields: { plate: false, workOrder: false, vin: false, referenceNo: true },
    needsBranch: true
  },
  {
    id: 'pdi',
    icon: ClipboardCheck,
    color: 'bg-green-500/10 text-green-400 border-green-500/20',
    fields: { plate: false, workOrder: false, vin: true, referenceNo: false },
    needsBranch: true
  }
];

const NewRecordPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user, selectedBranch, changeBranch } = useAuth();
  
  const [step, setStep] = useState(1);
  const [selectedType, setSelectedType] = useState(null);
  const [formData, setFormData] = useState({
    plate: '',
    workOrder: '',
    vin: '',
    referenceNo: '',
    note: '',
    branchCode: selectedBranch || ''
  });
  const [loading, setLoading] = useState(false);
  const [showOCR, setShowOCR] = useState(false);
  
  // Voice recognition for notes
  const {
    transcript,
    isListening,
    isRecording,
    isTranscribing,
    isSupported: voiceSupported,
    startListening,
    stopListening,
    startRecording,
    stopRecordingAndTranscribe,
    cancelRecording,
    resetTranscript,
    setTranscript
  } = useSpeechRecognition();
  
  const [voiceMode, setVoiceMode] = useState('browser'); // 'browser' or 'server'

  const handleTypeSelect = (type) => {
    setSelectedType(type);
    // Staff kullanıcı ise kendi şubesini kullan
    if (user?.role === 'staff' && user?.branch_code) {
      setFormData(prev => ({ ...prev, branchCode: user.branch_code }));
    } else if (selectedBranch) {
      setFormData(prev => ({ ...prev, branchCode: selectedBranch }));
    }
    setStep(2);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleBranchChange = (branchCode) => {
    setFormData(prev => ({ ...prev, branchCode }));
    changeBranch(branchCode);
  };

  const handlePlateDetected = (plate) => {
    setFormData(prev => ({ ...prev, plate }));
    setShowOCR(false);
    toast.success(t('msg.plateDetected'));
  };

  const handleSubmit = async () => {
    const typeConfig = RECORD_TYPES.find(t => t.id === selectedType);
    
    // Validate required fields
    if (typeConfig.fields.plate && !formData.plate) {
      toast.error(`${t('field.plate')} ${t('field.required')}`);
      return;
    }
    if (typeConfig.fields.workOrder && !formData.workOrder) {
      toast.error(`${t('field.workOrder')} ${t('field.required')}`);
      return;
    }
    if (typeConfig.fields.vin && !formData.vin) {
      toast.error(`${t('field.vin')} ${t('field.required')}`);
      return;
    }
    if (typeConfig.fields.referenceNo && !formData.referenceNo) {
      toast.error(`${t('field.referenceNo')} ${t('field.required')}`);
      return;
    }
    // PDI, Hasarlı, Yol yardım için şube zorunlu
    if (typeConfig.needsBranch && !formData.branchCode && user?.role !== 'staff') {
      toast.error(t('branch.selectRequired'));
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/records`, {
        record_type: selectedType,
        plate: formData.plate || null,
        work_order: formData.workOrder || null,
        vin: formData.vin || null,
        reference_no: formData.referenceNo || null,
        note_text: formData.note || null,
        branch_code: formData.branchCode || null
      });
      
      toast.success(t('msg.recordCreated'));
      navigate(`/record/${response.data.id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const selectedTypeConfig = RECORD_TYPES.find(t => t.id === selectedType);

  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* Header */}
      <header className="glass-header sticky top-0 z-40 px-4 py-4">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <button
            onClick={() => step === 1 ? navigate('/') : setStep(1)}
            className="w-10 h-10 bg-[#18181b] rounded-xl flex items-center justify-center hover:bg-[#27272a] transition-colors"
            data-testid="back-button"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>
          <div>
            <h1 className="text-lg font-bold text-white">{t('nav.newRecord')}</h1>
            <p className="text-xs text-zinc-500">
              {step === 1 ? 'Kayıt türü seçin' : t(`record.${selectedType}`)}
            </p>
          </div>
        </div>
      </header>

      <div className="px-4 py-6 max-w-lg mx-auto">
        {/* Step 1: Select type */}
        {step === 1 && (
          <div className="space-y-3">
            {RECORD_TYPES.map((type) => {
              const Icon = type.icon;
              return (
                <button
                  key={type.id}
                  onClick={() => handleTypeSelect(type.id)}
                  className="w-full record-card p-5 text-left hover:border-[#FACC15]/50 transition-colors"
                  data-testid={`type-${type.id}`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center border ${type.color}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-white font-semibold text-lg">
                        {t(`record.${type.id}`)}
                      </h3>
                      <p className="text-zinc-500 text-sm">
                        {t(`record.${type.id}Desc`)}
                      </p>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Step 2: Form */}
        {step === 2 && selectedTypeConfig && (
          <div className="space-y-5">
            {/* Branch selector for PDI, Damaged, RoadAssist */}
            {selectedTypeConfig.needsBranch && user?.role !== 'staff' && (
              <div>
                <label className="flex items-center justify-between text-sm font-medium text-zinc-400 mb-2">
                  <span className="flex items-center gap-2">
                    <Building2 className="w-4 h-4" />
                    {t('branch.select')}
                  </span>
                  <span className="text-[#FACC15] text-xs">{t('field.required')}</span>
                </label>
                <select
                  value={formData.branchCode}
                  onChange={(e) => handleBranchChange(e.target.value)}
                  className="w-full h-12 px-4 bg-[#18181b] border border-[#27272a] rounded-lg text-white"
                  data-testid="branch-select"
                >
                  <option value="">{t('branch.select')}</option>
                  {BRANCHES.map(branch => (
                    <option key={branch.code} value={branch.code}>
                      {branch.name}
                    </option>
                  ))}
                </select>
                {selectedBranch && (
                  <p className="text-xs text-zinc-500 mt-1">
                    Son seçilen şube: {BRANCHES.find(b => b.code === selectedBranch)?.name}
                  </p>
                )}
              </div>
            )}

            {/* Plate field */}
            {(selectedTypeConfig.fields.plate || selectedType === 'damaged') && (
              <div>
                <label className="flex items-center justify-between text-sm font-medium text-zinc-400 mb-2">
                  <span>{t('field.plate')}</span>
                  {selectedTypeConfig.fields.plate && (
                    <span className="text-[#FACC15] text-xs">{t('field.required')}</span>
                  )}
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={formData.plate}
                    onChange={(e) => handleInputChange('plate', e.target.value.toUpperCase())}
                    placeholder="34 ABC 123"
                    className="flex-1 h-12 px-4 bg-[#18181b] border border-[#27272a] rounded-lg text-white placeholder-zinc-500 uppercase"
                    data-testid="plate-input"
                  />
                  <button
                    onClick={() => setShowOCR(true)}
                    className="h-12 px-4 bg-[#27272a] rounded-lg text-[#FACC15] hover:bg-[#3f3f46] transition-colors flex items-center gap-2"
                    data-testid="scan-plate-button"
                  >
                    <ScanLine className="w-5 h-5" />
                    <span className="hidden sm:inline">{t('action.scan')}</span>
                  </button>
                </div>
              </div>
            )}

            {/* Work Order field */}
            {(selectedTypeConfig.fields.workOrder || selectedType === 'damaged') && (
              <div>
                <label className="flex items-center justify-between text-sm font-medium text-zinc-400 mb-2">
                  <span>{t('field.workOrder')}</span>
                  {selectedTypeConfig.fields.workOrder && (
                    <span className="text-[#FACC15] text-xs">{t('field.required')}</span>
                  )}
                </label>
                <input
                  type="text"
                  value={formData.workOrder}
                  onChange={(e) => handleInputChange('workOrder', e.target.value)}
                  placeholder="40216001"
                  className="w-full h-12 px-4 bg-[#18181b] border border-[#27272a] rounded-lg text-white placeholder-zinc-500"
                  data-testid="work-order-input"
                />
                <p className="text-xs text-zinc-500 mt-1">
                  Format: Şube(1) + Ay(2) + Gün(2) + Sıra(3) - Örnek: 40216001
                </p>
              </div>
            )}

            {/* VIN field */}
            {selectedTypeConfig.fields.vin && (
              <div>
                <label className="flex items-center justify-between text-sm font-medium text-zinc-400 mb-2">
                  <span>{t('field.vin')}</span>
                  <span className="text-[#FACC15] text-xs">{t('field.required')}</span>
                </label>
                <input
                  type="text"
                  value={formData.vin}
                  onChange={(e) => handleInputChange('vin', e.target.value.toUpperCase())}
                  placeholder="VF1XXXXXXXXXX12345"
                  className="w-full h-12 px-4 bg-[#18181b] border border-[#27272a] rounded-lg text-white placeholder-zinc-500 uppercase"
                  maxLength={17}
                  data-testid="vin-input"
                />
              </div>
            )}

            {/* Reference No field */}
            {selectedTypeConfig.fields.referenceNo && (
              <div>
                <label className="flex items-center justify-between text-sm font-medium text-zinc-400 mb-2">
                  <span>{t('field.referenceNo')}</span>
                  <span className="text-[#FACC15] text-xs">{t('field.required')}</span>
                </label>
                <input
                  type="text"
                  value={formData.referenceNo}
                  onChange={(e) => handleInputChange('referenceNo', e.target.value)}
                  placeholder="REF-2024-001"
                  className="w-full h-12 px-4 bg-[#18181b] border border-[#27272a] rounded-lg text-white placeholder-zinc-500"
                  data-testid="reference-input"
                />
              </div>
            )}

            {/* Note field */}
            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">
                {t('field.note')} <span className="text-zinc-600">({t('field.optional')})</span>
              </label>
              <textarea
                value={formData.note}
                onChange={(e) => handleInputChange('note', e.target.value)}
                placeholder="Ek notlar..."
                rows={3}
                className="w-full px-4 py-3 bg-[#18181b] border border-[#27272a] rounded-lg text-white placeholder-zinc-500 resize-none"
                data-testid="note-input"
              />
            </div>

            {/* Submit button */}
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full h-14 bg-[#FACC15] text-black font-bold rounded-xl hover:bg-yellow-400 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-6"
              data-testid="create-record-button"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {t('misc.loading')}
                </>
              ) : (
                t('action.create')
              )}
            </button>
          </div>
        )}
      </div>

      {/* OCR Modal */}
      {showOCR && (
        <PlateOCRModal
          onClose={() => setShowOCR(false)}
          onPlateDetected={handlePlateDetected}
        />
      )}
    </div>
  );
};

export default NewRecordPage;
