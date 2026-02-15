import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Plus, Search, Filter, Truck, AlertTriangle, 
  Wrench, ClipboardCheck, ChevronRight, Loader2,
  Image, Video, FileText, User, LogOut, Settings, Building2, Moon, Sun
} from 'lucide-react';
import { useOffline } from '../contexts/OfflineContext';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { toast } from 'sonner';
import { APP_VERSION } from '../config/version';

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
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);

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

  const handleLogout = async () => {
    await logout();
    toast.success(t('msg.logoutSuccess'));
    navigate('/login');
  };

  const getRecordSubtitle = (record) => {
    const parts = [];
    if (record.work_order) parts.push(`İş Emri: ${record.work_order}`);
    if (record.branch_name) parts.push(record.branch_name);
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
    <div className={`min-h-screen pb-24 transition-colors ${
      theme === 'dark' ? 'bg-[#09090b]' : 'bg-gray-50'
    }`}>
      {/* Header */}
      <header className={`sticky top-0 z-40 px-4 py-4 backdrop-blur-xl border-b ${
        theme === 'dark' 
          ? 'bg-[#09090b]/90 border-[#27272a]' 
          : 'bg-white/90 border-gray-200'
      }`}>
        <div className="max-w-lg mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className={`text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                RT KAYIT
              </h1>
              <p className={`text-xs ${theme === 'dark' ? 'text-zinc-500' : 'text-gray-500'}`}>
                {user?.branch_name ? `${user.branch_name} - ${user.job_title_display}` : 'Garanti Kayıt Sistemi'}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Online/Offline status */}
              <div className={`px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-1.5 ${
                isOnline 
                  ? 'bg-green-500/10 text-green-500 border border-green-500/20' 
                  : 'bg-red-500/10 text-red-500 border border-red-500/20'
              }`}>
                <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
                {isOnline ? t('status.online') : t('status.offline')}
                {isSyncing && <Loader2 className="w-3 h-3 animate-spin" />}
              </div>

              {/* Theme toggle */}
              <button
                onClick={toggleTheme}
                className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
                  theme === 'dark'
                    ? 'bg-[#18181b] border border-[#27272a] text-zinc-400 hover:bg-[#27272a]'
                    : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-100'
                }`}
                data-testid="home-theme-toggle"
              >
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {/* User menu */}
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
                    theme === 'dark'
                      ? 'bg-[#18181b] border border-[#27272a] hover:bg-[#27272a]'
                      : 'bg-white border border-gray-200 hover:bg-gray-100'
                  }`}
                  data-testid="user-menu-button"
                >
                  <User className={`w-5 h-5 ${theme === 'dark' ? 'text-zinc-400' : 'text-gray-600'}`} />
                </button>

                {showUserMenu && (
                  <>
                    <div 
                      className="fixed inset-0 z-40" 
                      onClick={() => setShowUserMenu(false)}
                    />
                    <div className={`absolute right-0 top-12 w-56 rounded-xl shadow-xl z-50 overflow-hidden border ${
                      theme === 'dark'
                        ? 'bg-[#18181b] border-[#27272a]'
                        : 'bg-white border-gray-200'
                    }`}>
                      {/* User info */}
                      <div className={`p-3 border-b ${theme === 'dark' ? 'border-[#27272a]' : 'border-gray-200'}`}>
                        <p className={`font-medium truncate ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                          {user?.full_name}
                        </p>
                        <p className={`text-xs truncate ${theme === 'dark' ? 'text-zinc-500' : 'text-gray-500'}`}>
                          {user?.username}
                        </p>
                        {user?.branch_name && (
                          <p className={`text-xs flex items-center gap-1 mt-1 ${
                            theme === 'dark' ? 'text-zinc-500' : 'text-gray-500'
                          }`}>
                            <Building2 className="w-3 h-3" />
                            {user.branch_name}
                          </p>
                        )}
                      </div>

                      {/* Menu items */}
                      <div className="p-1">
                        {user?.role === 'admin' && (
                          <button
                            onClick={() => { setShowUserMenu(false); navigate('/admin'); }}
                            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                              theme === 'dark'
                                ? 'text-zinc-300 hover:bg-[#27272a]'
                                : 'text-gray-700 hover:bg-gray-100'
                            }`}
                            data-testid="admin-menu-item"
                          >
                            <Settings className="w-4 h-4" />
                            <span className="text-sm">{t('nav.admin')}</span>
                          </button>
                        )}
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center gap-3 px-3 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                          data-testid="logout-menu-item"
                        >
                          <LogOut className="w-4 h-4" />
                          <span className="text-sm">{t('nav.logout')}</span>
                        </button>
                      </div>

                      {/* Version */}
                      <div className={`px-3 py-2 border-t ${theme === 'dark' ? 'border-[#27272a]' : 'border-gray-200'}`}>
                        <p className={`text-xs ${theme === 'dark' ? 'text-zinc-600' : 'text-gray-400'}`}>
                          v{APP_VERSION}
                        </p>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className={`absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 ${
              theme === 'dark' ? 'text-zinc-500' : 'text-gray-400'
            }`} />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={`${t('action.search')}...`}
              className={`w-full h-11 pl-10 pr-4 rounded-xl border ${
                theme === 'dark'
                  ? 'bg-[#18181b] border-[#27272a] text-white placeholder-zinc-500'
                  : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'
              }`}
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
                  : theme === 'dark'
                    ? 'bg-[#27272a] text-zinc-400 hover:text-white'
                    : 'bg-gray-200 text-gray-600 hover:text-gray-900'
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
                    : theme === 'dark'
                      ? 'bg-[#27272a] text-zinc-400 hover:text-white'
                      : 'bg-gray-200 text-gray-600 hover:text-gray-900'
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
        className="fixed bottom-20 right-6 w-14 h-14 bg-[#FACC15] rounded-full shadow-lg flex items-center justify-center hover:bg-yellow-400 active:scale-95 transition-all z-50"
        data-testid="new-record-fab"
      >
        <Plus className="w-6 h-6 text-black" />
      </button>
    </div>
  );
};

export default HomePage;
