import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { 
  Truck, Shield, Camera, FileText, Smartphone, 
  Building2, Clock, CheckCircle, ArrowRight, 
  Globe, Moon, Sun
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { APP_VERSION } from '../config/version';

const LandingPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'tr' ? 'en' : 'tr';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  const features = [
    {
      icon: Camera,
      title: i18n.language === 'tr' ? 'Fotoğraf & Video Kayıt' : 'Photo & Video Recording',
      description: i18n.language === 'tr' 
        ? 'Garanti işlemleri için fotoğraf, video ve PDF belgelerini kolayca kaydedin.'
        : 'Easily record photos, videos and PDF documents for warranty processes.'
    },
    {
      icon: Shield,
      title: i18n.language === 'tr' ? 'Güvenli Depolama' : 'Secure Storage',
      description: i18n.language === 'tr'
        ? 'Tüm verileriniz güvenli sunucularda şifrelenmiş olarak saklanır.'
        : 'All your data is stored encrypted on secure servers.'
    },
    {
      icon: Building2,
      title: i18n.language === 'tr' ? 'Şube Bazlı Yönetim' : 'Branch-Based Management',
      description: i18n.language === 'tr'
        ? 'Her şube kendi verilerini yönetir, merkezi kontrol ile.'
        : 'Each branch manages its own data with central control.'
    },
    {
      icon: Smartphone,
      title: i18n.language === 'tr' ? 'Mobil Uyumlu' : 'Mobile Compatible',
      description: i18n.language === 'tr'
        ? 'Her cihazdan erişim sağlayın, sahada bile çalışın.'
        : 'Access from any device, work even in the field.'
    },
    {
      icon: Clock,
      title: i18n.language === 'tr' ? 'Hızlı İşlem' : 'Fast Processing',
      description: i18n.language === 'tr'
        ? 'Garanti taleplerini hızlıca oluşturun ve takip edin.'
        : 'Quickly create and track warranty claims.'
    },
    {
      icon: FileText,
      title: i18n.language === 'tr' ? 'Otomatik Raporlama' : 'Automatic Reporting',
      description: i18n.language === 'tr'
        ? 'Detaylı raporlar ve istatistikler ile işlerinizi analiz edin.'
        : 'Analyze your operations with detailed reports and statistics.'
    }
  ];

  const branches = [
    { name: 'Bursa', city: 'Bursa' },
    { name: 'İzmit', city: 'Kocaeli' },
    { name: 'Orhanlı', city: 'İstanbul' },
    { name: 'Hadımköy', city: 'İstanbul' },
    { name: 'Keşan', city: 'Edirne' }
  ];

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      theme === 'dark' ? 'bg-[#09090b]' : 'bg-gray-50'
    }`}>
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-colors duration-300 ${
        theme === 'dark' 
          ? 'bg-[#09090b]/90 backdrop-blur-xl border-b border-[#27272a]' 
          : 'bg-white/90 backdrop-blur-xl border-b border-gray-200'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#FACC15] rounded-xl flex items-center justify-center">
                <Truck className="w-5 h-5 text-black" />
              </div>
              <div>
                <h1 className={`font-bold tracking-wide ${
                  theme === 'dark' ? 'text-white' : 'text-gray-900'
                }`}>RT KAYIT</h1>
                <p className={`text-xs ${theme === 'dark' ? 'text-zinc-500' : 'text-gray-500'}`}>
                  Garanti Kayıt Sistemi
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              {/* Language toggle */}
              <button
                onClick={toggleLanguage}
                className={`p-2 rounded-lg transition-colors ${
                  theme === 'dark'
                    ? 'text-zinc-400 hover:text-white hover:bg-[#27272a]'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
                data-testid="landing-language-toggle"
              >
                <Globe className="w-5 h-5" />
              </button>

              {/* Theme toggle */}
              <button
                onClick={toggleTheme}
                className={`p-2 rounded-lg transition-colors ${
                  theme === 'dark'
                    ? 'text-zinc-400 hover:text-white hover:bg-[#27272a]'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
                data-testid="theme-toggle"
              >
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {/* Login button */}
              <button
                onClick={() => navigate('/login')}
                className="ml-2 px-5 py-2 bg-[#FACC15] text-black font-bold rounded-lg hover:bg-yellow-400 active:scale-95 transition-all"
                data-testid="landing-login-button"
              >
                {i18n.language === 'tr' ? 'Giriş Yap' : 'Login'}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#FACC15]/10 border border-[#FACC15]/20 rounded-full mb-6">
              <span className="text-[#FACC15] text-sm font-medium">v{APP_VERSION}</span>
              <span className={`text-sm ${theme === 'dark' ? 'text-zinc-400' : 'text-gray-600'}`}>
                {i18n.language === 'tr' ? 'Yeni Sürüm' : 'New Version'}
              </span>
            </div>

            <h1 className={`text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 leading-tight ${
              theme === 'dark' ? 'text-white' : 'text-gray-900'
            }`}>
              {i18n.language === 'tr' 
                ? 'Renault Trucks Garanti Kayıt Sistemi' 
                : 'Renault Trucks Warranty Record System'}
            </h1>

            <p className={`text-lg sm:text-xl mb-10 max-w-2xl mx-auto ${
              theme === 'dark' ? 'text-zinc-400' : 'text-gray-600'
            }`}>
              {i18n.language === 'tr'
                ? 'Garanti işlemlerinizi dijitalleştirin. Fotoğraf, video ve belgelerinizi güvenle saklayın, şubelerinizi kolayca yönetin.'
                : 'Digitize your warranty processes. Securely store your photos, videos and documents, easily manage your branches.'}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/login')}
                className="px-8 py-4 bg-[#FACC15] text-black font-bold rounded-xl hover:bg-yellow-400 active:scale-95 transition-all flex items-center justify-center gap-2 text-lg"
                data-testid="hero-login-button"
              >
                {i18n.language === 'tr' ? 'Hemen Başla' : 'Get Started'}
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className={`py-20 px-4 ${theme === 'dark' ? 'bg-[#18181b]' : 'bg-white'}`}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className={`text-3xl sm:text-4xl font-bold mb-4 ${
              theme === 'dark' ? 'text-white' : 'text-gray-900'
            }`}>
              {i18n.language === 'tr' ? 'Özellikler' : 'Features'}
            </h2>
            <p className={theme === 'dark' ? 'text-zinc-400' : 'text-gray-600'}>
              {i18n.language === 'tr' 
                ? 'İş süreçlerinizi kolaylaştıran güçlü özellikler'
                : 'Powerful features that simplify your workflows'}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className={`p-6 rounded-2xl border transition-all hover:scale-[1.02] ${
                    theme === 'dark'
                      ? 'bg-[#09090b] border-[#27272a] hover:border-[#FACC15]/50'
                      : 'bg-gray-50 border-gray-200 hover:border-[#FACC15]'
                  }`}
                >
                  <div className="w-12 h-12 bg-[#FACC15]/10 rounded-xl flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-[#FACC15]" />
                  </div>
                  <h3 className={`text-xl font-bold mb-2 ${
                    theme === 'dark' ? 'text-white' : 'text-gray-900'
                  }`}>
                    {feature.title}
                  </h3>
                  <p className={theme === 'dark' ? 'text-zinc-400' : 'text-gray-600'}>
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Branches Section */}
      <section className={`py-20 px-4 ${theme === 'dark' ? 'bg-[#09090b]' : 'bg-gray-50'}`}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className={`text-3xl sm:text-4xl font-bold mb-4 ${
              theme === 'dark' ? 'text-white' : 'text-gray-900'
            }`}>
              {i18n.language === 'tr' ? 'Şubelerimiz' : 'Our Branches'}
            </h2>
            <p className={theme === 'dark' ? 'text-zinc-400' : 'text-gray-600'}>
              {i18n.language === 'tr' 
                ? 'Türkiye genelinde 5 şubemizle hizmetinizdeyiz'
                : 'At your service with 5 branches across Turkey'}
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-4">
            {branches.map((branch, index) => (
              <div
                key={index}
                className={`px-6 py-4 rounded-xl border ${
                  theme === 'dark'
                    ? 'bg-[#18181b] border-[#27272a]'
                    : 'bg-white border-gray-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#71010D]/20 rounded-lg flex items-center justify-center">
                    <Building2 className="w-5 h-5 text-[#FACC15]" />
                  </div>
                  <div>
                    <h4 className={`font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                      {branch.name}
                    </h4>
                    <p className={`text-sm ${theme === 'dark' ? 'text-zinc-500' : 'text-gray-500'}`}>
                      {branch.city}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-br from-[#71010D] to-[#3d0007]">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            {i18n.language === 'tr' 
              ? 'Hemen Başlayın' 
              : 'Get Started Today'}
          </h2>
          <p className="text-lg text-white/80 mb-8 max-w-2xl mx-auto">
            {i18n.language === 'tr'
              ? 'Garanti süreçlerinizi dijitalleştirin, zamandan ve kağıttan tasarruf edin.'
              : 'Digitize your warranty processes, save time and paper.'}
          </p>
          <button
            onClick={() => navigate('/login')}
            className="px-8 py-4 bg-[#FACC15] text-black font-bold rounded-xl hover:bg-yellow-400 active:scale-95 transition-all text-lg"
            data-testid="cta-login-button"
          >
            {i18n.language === 'tr' ? 'Giriş Yap' : 'Login'}
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className={`py-8 px-4 border-t ${
        theme === 'dark' 
          ? 'bg-[#09090b] border-[#27272a]' 
          : 'bg-white border-gray-200'
      }`}>
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Truck className="w-5 h-5 text-[#FACC15]" />
            <span className={`font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
              RT KAYIT
            </span>
          </div>
          <p className={`text-sm ${theme === 'dark' ? 'text-zinc-500' : 'text-gray-500'}`}>
            © 2025 Renault Trucks. {i18n.language === 'tr' ? 'Tüm hakları saklıdır.' : 'All rights reserved.'}
          </p>
          <p className={`text-sm ${theme === 'dark' ? 'text-zinc-600' : 'text-gray-400'}`}>
            v{APP_VERSION}
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
