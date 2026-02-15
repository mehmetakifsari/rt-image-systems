import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Plus, Search, Filter, Truck, AlertTriangle, 
  Wrench, ClipboardCheck, ChevronRight, Loader2,
  Image, Video, FileText
} from 'lucide-react';
import { useOffline } from '../contexts/OfflineContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const RECORD_TYPE_ICONS = {
  standard: Wrench,
  roadassist: Truck,
  damaged: AlertTriangle,
  pdi: ClipboardCheck
};

const RECORD_TYPE_COLORS = {
  standard: 'badge-standard',
  roadassist: 'badge-roadassist',
  damaged: 'badge-damaged',
  pdi: 'badge-pdi'
};

const HomePage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isOnline, pendingUploads, isSyncing } = useOffline();
  
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');

  useEffect(() => {
    fetchRecords();
  }, [search, filterType]);

  const fetchRecords = async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (filterType) params.append('record_type', filterType);
      
      const response = await axios.get(`${API}/records?${params}`);
      setRecords(response.data);
    } catch (error) {
      console.error('Error fetching records:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRecordTitle = (record) => {
    if (record.plate) return record.plate;
    if (record.vin) return `VIN: ...${record.vin.slice(-5)}`;
    if (record.reference_no) return `Ref: ${record.reference_no}`;
    return record.case_key;
  };

  const getRecordSubtitle = (record) => {
    const parts = [];
    if (record.work_order) parts.push(`İş Emri: ${record.work_order}`);
    if (record.branch) parts.push(record.branch);
    return parts.join(' • ') || formatDate(record.created_at);
  };

  const getMediaCounts = (files) => {
    const counts = { photo: 0, video: 0, pdf: 0 };
    files.forEach(f => {
      if (counts[f.media_type] !== undefined) {
        counts[f.media_type]++;
      }
    });
    return counts;
  };

  return (
    <div className="min-h-screen bg-[#09090b] pb-24">
      {/* Header */}
      <header className="glass-header sticky top-0 z-40 px-4 py-4">
        <div className="max-w-lg mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-xl font-bold text-white">RT KAYIT</h1>
              <p className="text-xs text-zinc-500">Garanti Kayıt Sistemi</p>
            </div>
            
            {/* Online/Offline status */}
            <div className={`px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-1.5 ${
              isOnline ? 'online-indicator' : 'offline-indicator'
            }`}>
              <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
              {isOnline ? t('status.online') : t('status.offline')}
              {isSyncing && <Loader2 className="w-3 h-3 animate-spin" />}
            </div>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={`${t('action.search')}...`}
              className="w-full h-11 pl-10 pr-4 bg-[#18181b] border border-[#27272a] rounded-xl text-white placeholder-zinc-500"
              data-testid="search-input"
            />
          </div>

          {/* Filter tabs */}
          <div className="flex gap-2 mt-3 overflow-x-auto pb-1 scrollbar-hide">
            <button
              onClick={() => setFilterType('')}
              className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                filterType === '' 
                  ? 'bg-[#FACC15] text-black' 
                  : 'bg-[#27272a] text-zinc-400 hover:text-white'
              }`}
              data-testid="filter-all"
            >
              {t('misc.all')}
            </button>
            {['standard', 'roadassist', 'damaged', 'pdi'].map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                  filterType === type 
                    ? 'bg-[#FACC15] text-black' 
                    : 'bg-[#27272a] text-zinc-400 hover:text-white'
                }`}
                data-testid={`filter-${type}`}
              >
                {t(`record.${type}`)}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Pending uploads banner */}
      {pendingUploads.length > 0 && (
        <div className="mx-4 mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
          <p className="text-yellow-400 text-sm flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            {pendingUploads.length} {t('msg.offlineQueue')}
          </p>
        </div>
      )}

      {/* Records list */}
      <div className="px-4 py-4 max-w-lg mx-auto">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-[#FACC15] animate-spin" />
          </div>
        ) : records.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-[#18181b] rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Truck className="w-8 h-8 text-zinc-600" />
            </div>
            <p className="text-zinc-500">{t('misc.noRecords')}</p>
          </div>
        ) : (
          <div className="space-y-3">
            {records.map((record) => {
              const Icon = RECORD_TYPE_ICONS[record.record_type];
              const colorClass = RECORD_TYPE_COLORS[record.record_type];
              const mediaCounts = getMediaCounts(record.files_json || []);
              
              return (
                <button
                  key={record.id}
                  onClick={() => navigate(`/record/${record.id}`)}
                  className="w-full record-card p-4 text-left group"
                  data-testid={`record-card-${record.id}`}
                >
                  <div className="flex items-start gap-3">
                    {/* Icon */}
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${colorClass}`}>
                          {t(`record.${record.record_type}`)}
                        </span>
                      </div>
                      <h3 className="text-white font-semibold truncate">
                        {getRecordTitle(record)}
                      </h3>
                      <p className="text-zinc-500 text-sm truncate">
                        {getRecordSubtitle(record)}
                      </p>
                      
                      {/* Media counts */}
                      {(mediaCounts.photo > 0 || mediaCounts.video > 0 || mediaCounts.pdf > 0) && (
                        <div className="flex items-center gap-3 mt-2">
                          {mediaCounts.photo > 0 && (
                            <span className="flex items-center gap-1 text-xs text-zinc-500">
                              <Image className="w-3.5 h-3.5" />
                              {mediaCounts.photo}
                            </span>
                          )}
                          {mediaCounts.video > 0 && (
                            <span className="flex items-center gap-1 text-xs text-zinc-500">
                              <Video className="w-3.5 h-3.5" />
                              {mediaCounts.video}
                            </span>
                          )}
                          {mediaCounts.pdf > 0 && (
                            <span className="flex items-center gap-1 text-xs text-zinc-500">
                              <FileText className="w-3.5 h-3.5" />
                              {mediaCounts.pdf}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    
                    {/* Arrow */}
                    <ChevronRight className="w-5 h-5 text-zinc-600 group-hover:text-[#FACC15] transition-colors flex-shrink-0" />
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* FAB - New Record */}
      <button
        onClick={() => navigate('/new')}
        className="fixed bottom-6 right-6 w-14 h-14 bg-[#FACC15] rounded-full shadow-lg flex items-center justify-center hover:bg-yellow-400 active:scale-95 transition-all z-50"
        data-testid="new-record-fab"
      >
        <Plus className="w-6 h-6 text-black" />
      </button>
    </div>
  );
};

export default HomePage;
