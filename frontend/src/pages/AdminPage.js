import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { 
  LayoutDashboard, FileText, Settings, LogOut, Menu, X,
  Truck, Wrench, AlertTriangle, ClipboardCheck, ChevronRight,
  Image, Video, Search, Filter
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AdminPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [records, setRecords] = useState([]);
  const [settings, setSettings] = useState(null);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== 'admin') {
      navigate('/');
      return;
    }
    fetchData();
  }, [user, activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboard') {
        const response = await axios.get(`${API}/stats`);
        setStats(response.data);
      } else if (activeTab === 'records') {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (filterType) params.append('record_type', filterType);
        params.append('limit', '50');
        const response = await axios.get(`${API}/records?${params}`);
        setRecords(response.data);
      } else if (activeTab === 'settings') {
        const response = await axios.get(`${API}/settings`);
        setSettings(response.data);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSettingsChange = (field, value) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  const saveSettings = async () => {
    try {
      await axios.put(`${API}/settings`, settings);
      alert(t('msg.settingsSaved'));
    } catch (error) {
      alert('Hata oluştu');
    }
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === 'tr' ? 'en' : 'tr';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  const RECORD_TYPE_ICONS = {
    standard: Wrench,
    roadassist: Truck,
    damaged: AlertTriangle,
    pdi: ClipboardCheck
  };

  const RECORD_TYPE_COLORS = {
    standard: 'bg-blue-500/10 text-blue-400',
    roadassist: 'bg-yellow-500/10 text-yellow-400',
    damaged: 'bg-red-900/20 text-red-400',
    pdi: 'bg-green-500/10 text-green-400'
  };

  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: t('admin.dashboard') },
    { id: 'records', icon: FileText, label: t('admin.records') },
    { id: 'settings', icon: Settings, label: t('admin.settings') }
  ];

  return (
    <div className="min-h-screen bg-[#09090b] flex">
      {/* Sidebar */}
      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-[#18181b] border-r border-[#27272a] transform transition-transform lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="p-4 border-b border-[#27272a]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#FACC15] rounded-xl flex items-center justify-center">
              <Truck className="w-5 h-5 text-black" />
            </div>
            <div>
              <h1 className="text-white font-bold">RT ADMIN</h1>
              <p className="text-xs text-zinc-500">{user?.full_name}</p>
            </div>
          </div>
        </div>

        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => { setActiveTab(item.id); setSidebarOpen(false); }}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
                  activeTab === item.id
                    ? 'bg-[#FACC15] text-black'
                    : 'text-zinc-400 hover:text-white hover:bg-[#27272a]'
                }`}
                data-testid={`menu-${item.id}`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-[#27272a]">
          <button
            onClick={toggleLanguage}
            className="w-full px-4 py-2 mb-2 text-sm bg-[#27272a] text-zinc-300 rounded-lg hover:bg-[#3f3f46] transition-colors"
          >
            {i18n.language === 'tr' ? 'English' : 'Türkçe'}
          </button>
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:bg-red-500/10 rounded-xl transition-colors"
            data-testid="logout-button"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">{t('nav.logout')}</span>
          </button>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <main className="flex-1 min-w-0">
        {/* Header */}
        <header className="glass-header sticky top-0 z-30 px-4 py-4 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden w-10 h-10 bg-[#27272a] rounded-xl flex items-center justify-center"
          >
            <Menu className="w-5 h-5 text-white" />
          </button>
          <h2 className="text-xl font-bold text-white">
            {menuItems.find(m => m.id === activeTab)?.label}
          </h2>
        </header>

        <div className="p-4 lg:p-6">
          {/* Dashboard */}
          {activeTab === 'dashboard' && stats && (
            <div className="space-y-6">
              {/* Stats grid */}
              <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="record-card p-4">
                  <p className="text-zinc-500 text-sm mb-1">{t('admin.totalRecords')}</p>
                  <p className="text-3xl font-bold text-white">{stats.total}</p>
                </div>
                {Object.entries(stats.by_type).map(([type, count]) => {
                  const Icon = RECORD_TYPE_ICONS[type];
                  const colorClass = RECORD_TYPE_COLORS[type];
                  return (
                    <div key={type} className="record-card p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${colorClass}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <span className="text-zinc-500 text-sm">{t(`record.${type}`)}</span>
                      </div>
                      <p className="text-2xl font-bold text-white">{count}</p>
                    </div>
                  );
                })}
              </div>

              {/* Recent records */}
              <div className="record-card p-4">
                <h3 className="text-lg font-bold text-white mb-4">{t('admin.recentRecords')}</h3>
                <div className="space-y-3">
                  {stats.recent.map((record) => {
                    const Icon = RECORD_TYPE_ICONS[record.record_type];
                    const colorClass = RECORD_TYPE_COLORS[record.record_type];
                    return (
                      <div 
                        key={record.id}
                        onClick={() => navigate(`/record/${record.id}`)}
                        className="flex items-center gap-3 p-3 bg-[#09090b] rounded-xl cursor-pointer hover:bg-[#27272a] transition-colors"
                      >
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${colorClass}`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-medium truncate">
                            {record.plate || record.vin || record.reference_no || record.case_key}
                          </p>
                          <p className="text-zinc-500 text-sm">
                            {new Date(record.created_at).toLocaleString('tr-TR')}
                          </p>
                        </div>
                        <ChevronRight className="w-5 h-5 text-zinc-600" />
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Records */}
          {activeTab === 'records' && (
            <div className="space-y-4">
              {/* Search and filter */}
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && fetchData()}
                    placeholder={`${t('action.search')}...`}
                    className="w-full h-11 pl-10 pr-4 bg-[#18181b] border border-[#27272a] rounded-xl text-white placeholder-zinc-500"
                  />
                </div>
                <select
                  value={filterType}
                  onChange={(e) => { setFilterType(e.target.value); setTimeout(fetchData, 100); }}
                  className="h-11 px-4 bg-[#18181b] border border-[#27272a] rounded-xl text-white"
                >
                  <option value="">{t('misc.all')}</option>
                  <option value="standard">{t('record.standard')}</option>
                  <option value="roadassist">{t('record.roadassist')}</option>
                  <option value="damaged">{t('record.damaged')}</option>
                  <option value="pdi">{t('record.pdi')}</option>
                </select>
              </div>

              {/* Records table */}
              <div className="record-card overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-[#27272a]">
                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase">Tür</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase">Plaka/VIN/Ref</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase">İş Emri</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase">Dosyalar</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase">Tarih</th>
                        <th className="px-4 py-3"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#27272a]">
                      {records.map((record) => {
                        const Icon = RECORD_TYPE_ICONS[record.record_type];
                        const colorClass = RECORD_TYPE_COLORS[record.record_type];
                        const fileCount = (record.files_json || []).length;
                        
                        return (
                          <tr 
                            key={record.id}
                            onClick={() => navigate(`/record/${record.id}`)}
                            className="hover:bg-[#27272a]/50 cursor-pointer"
                          >
                            <td className="px-4 py-3">
                              <div className={`inline-flex items-center gap-2 px-2 py-1 rounded-lg ${colorClass}`}>
                                <Icon className="w-4 h-4" />
                                <span className="text-xs font-medium">{t(`record.${record.record_type}`)}</span>
                              </div>
                            </td>
                            <td className="px-4 py-3">
                              <span className="text-white font-medium">
                                {record.plate || (record.vin ? `...${record.vin.slice(-5)}` : record.reference_no || '-')}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-zinc-400">
                              {record.work_order || '-'}
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                {fileCount > 0 ? (
                                  <>
                                    <Image className="w-4 h-4 text-zinc-500" />
                                    <span className="text-zinc-400">{fileCount}</span>
                                  </>
                                ) : (
                                  <span className="text-zinc-600">-</span>
                                )}
                              </div>
                            </td>
                            <td className="px-4 py-3 text-zinc-400 text-sm">
                              {new Date(record.created_at).toLocaleDateString('tr-TR')}
                            </td>
                            <td className="px-4 py-3">
                              <ChevronRight className="w-5 h-5 text-zinc-600" />
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Settings */}
          {activeTab === 'settings' && settings && (
            <div className="max-w-2xl space-y-6">
              {/* OCR Settings */}
              <div className="record-card p-6">
                <h3 className="text-lg font-bold text-white mb-4">{t('settings.ocr')}</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      {t('settings.ocrProvider')}
                    </label>
                    <select
                      value={settings.ocr_provider}
                      onChange={(e) => handleSettingsChange('ocr_provider', e.target.value)}
                      className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                    >
                      <option value="browser">{t('settings.browserOcr')}</option>
                      <option value="vision">{t('settings.visionApi')}</option>
                    </select>
                  </div>
                  
                  {settings.ocr_provider === 'vision' && (
                    <div>
                      <label className="block text-sm font-medium text-zinc-400 mb-2">
                        {t('settings.visionApiKey')}
                      </label>
                      <input
                        type="password"
                        value={settings.vision_api_key || ''}
                        onChange={(e) => handleSettingsChange('vision_api_key', e.target.value)}
                        placeholder="AIza..."
                        className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Storage Settings */}
              <div className="record-card p-6">
                <h3 className="text-lg font-bold text-white mb-4">{t('settings.storage')}</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      {t('settings.storageType')}
                    </label>
                    <select
                      value={settings.storage_type}
                      onChange={(e) => handleSettingsChange('storage_type', e.target.value)}
                      className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                    >
                      <option value="local">{t('settings.localStorage')}</option>
                      <option value="ftp">{t('settings.ftp')}</option>
                      <option value="s3">{t('settings.awsS3')}</option>
                      <option value="gdrive">{t('settings.googleDrive')}</option>
                      <option value="onedrive">{t('settings.oneDrive')}</option>
                    </select>
                  </div>

                  {/* FTP Settings */}
                  {settings.storage_type === 'ftp' && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-[#27272a]">
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          {t('settings.ftpHost')}
                        </label>
                        <input
                          type="text"
                          value={settings.ftp_host || ''}
                          onChange={(e) => handleSettingsChange('ftp_host', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          {t('settings.ftpUser')}
                        </label>
                        <input
                          type="text"
                          value={settings.ftp_user || ''}
                          onChange={(e) => handleSettingsChange('ftp_user', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                      <div className="sm:col-span-2">
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          {t('settings.ftpPassword')}
                        </label>
                        <input
                          type="password"
                          value={settings.ftp_password || ''}
                          onChange={(e) => handleSettingsChange('ftp_password', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                    </div>
                  )}

                  {/* AWS S3 Settings */}
                  {settings.storage_type === 's3' && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-[#27272a]">
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          {t('settings.awsAccessKey')}
                        </label>
                        <input
                          type="text"
                          value={settings.aws_access_key || ''}
                          onChange={(e) => handleSettingsChange('aws_access_key', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          {t('settings.awsSecretKey')}
                        </label>
                        <input
                          type="password"
                          value={settings.aws_secret_key || ''}
                          onChange={(e) => handleSettingsChange('aws_secret_key', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          {t('settings.awsBucket')}
                        </label>
                        <input
                          type="text"
                          value={settings.aws_bucket || ''}
                          onChange={(e) => handleSettingsChange('aws_bucket', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          {t('settings.awsRegion')}
                        </label>
                        <input
                          type="text"
                          value={settings.aws_region || ''}
                          onChange={(e) => handleSettingsChange('aws_region', e.target.value)}
                          placeholder="eu-west-1"
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                    </div>
                  )}

                  {/* Google Drive Settings */}
                  {settings.storage_type === 'gdrive' && (
                    <div className="grid grid-cols-1 gap-4 pt-4 border-t border-[#27272a]">
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          Google Drive Client ID
                        </label>
                        <input
                          type="text"
                          value={settings.google_drive_client_id || ''}
                          onChange={(e) => handleSettingsChange('google_drive_client_id', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          Google Drive Client Secret
                        </label>
                        <input
                          type="password"
                          value={settings.google_drive_client_secret || ''}
                          onChange={(e) => handleSettingsChange('google_drive_client_secret', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                    </div>
                  )}

                  {/* OneDrive Settings */}
                  {settings.storage_type === 'onedrive' && (
                    <div className="grid grid-cols-1 gap-4 pt-4 border-t border-[#27272a]">
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          OneDrive Client ID
                        </label>
                        <input
                          type="text"
                          value={settings.onedrive_client_id || ''}
                          onChange={(e) => handleSettingsChange('onedrive_client_id', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          OneDrive Client Secret
                        </label>
                        <input
                          type="password"
                          value={settings.onedrive_client_secret || ''}
                          onChange={(e) => handleSettingsChange('onedrive_client_secret', e.target.value)}
                          className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Language Settings */}
              <div className="record-card p-6">
                <h3 className="text-lg font-bold text-white mb-4">{t('settings.language')}</h3>
                <select
                  value={settings.language}
                  onChange={(e) => handleSettingsChange('language', e.target.value)}
                  className="w-full h-11 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white"
                >
                  <option value="tr">Türkçe</option>
                  <option value="en">English</option>
                </select>
              </div>

              {/* Save button */}
              <button
                onClick={saveSettings}
                className="w-full h-12 bg-[#FACC15] text-black font-bold rounded-xl hover:bg-yellow-400 active:scale-[0.98] transition-all"
                data-testid="save-settings-button"
              >
                {t('action.save')}
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default AdminPage;
