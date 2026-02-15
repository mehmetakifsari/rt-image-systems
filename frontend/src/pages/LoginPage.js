import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { Truck, Eye, EyeOff, Loader2, Moon, Sun } from 'lucide-react';
import { toast } from 'sonner';
import { APP_VERSION } from '../config/version';

const LoginPage = () => {
  const { t, i18n } = useTranslation();
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      toast.error(t('msg.loginError'));
      return;
    }

    setLoading(true);
    try {
      await login(username, password);
      toast.success(t('msg.loginSuccess'));
    } catch (error) {
      toast.error(error.response?.data?.detail || t('msg.loginError'));
    } finally {
      setLoading(false);
    }
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === 'tr' ? 'en' : 'tr';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 transition-colors ${
      theme === 'dark' ? 'bg-[#09090b]' : 'bg-gray-100'
    }`}>
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      <div className="relative w-full max-w-md">
        {/* Top controls */}
        <div className="absolute -top-12 right-0 flex items-center gap-2">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className={`p-2 rounded-full transition-colors ${
              theme === 'dark'
                ? 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                : 'bg-white text-gray-600 hover:bg-gray-100 shadow'
            }`}
            data-testid="login-theme-toggle"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
          
          {/* Language toggle */}
          <button
            onClick={toggleLanguage}
            className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
              theme === 'dark'
                ? 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                : 'bg-white text-gray-600 hover:bg-gray-100 shadow'
            }`}
            data-testid="language-toggle"
          >
            {i18n.language === 'tr' ? 'EN' : 'TR'}
          </button>
        </div>

        {/* Login card */}
        <div className={`rounded-2xl p-8 shadow-2xl border transition-colors ${
          theme === 'dark' 
            ? 'bg-[#18181b] border-[#27272a]' 
            : 'bg-white border-gray-200'
        }`}>
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-[#FACC15] rounded-2xl mb-4">
              <Truck className="w-8 h-8 text-black" />
            </div>
            <h1 className={`text-2xl font-bold tracking-wide ${
              theme === 'dark' ? 'text-white' : 'text-gray-900'
            }`}>
              {t('auth.loginTitle')}
            </h1>
            <p className={`text-sm mt-1 ${theme === 'dark' ? 'text-zinc-400' : 'text-gray-500'}`}>
              {t('auth.loginSubtitle')}
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className={`block text-sm font-medium mb-2 ${
                theme === 'dark' ? 'text-zinc-400' : 'text-gray-600'
              }`}>
                {t('auth.username')}
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={`w-full h-12 px-4 border rounded-lg transition-colors ${
                  theme === 'dark'
                    ? 'bg-[#09090b] border-[#27272a] text-white placeholder-zinc-500'
                    : 'bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-400'
                } focus:border-[#FACC15] focus:ring-1 focus:ring-[#FACC15]`}
                placeholder={t('auth.username')}
                data-testid="username-input"
              />
            </div>

            <div>
              <label className={`block text-sm font-medium mb-2 ${
                theme === 'dark' ? 'text-zinc-400' : 'text-gray-600'
              }`}>
                {t('auth.password')}
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`w-full h-12 px-4 pr-12 border rounded-lg transition-colors ${
                    theme === 'dark'
                      ? 'bg-[#09090b] border-[#27272a] text-white placeholder-zinc-500'
                      : 'bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-400'
                  } focus:border-[#FACC15] focus:ring-1 focus:ring-[#FACC15]`}
                  placeholder="••••••••"
                  data-testid="password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className={`absolute right-3 top-1/2 -translate-y-1/2 ${
                    theme === 'dark' ? 'text-zinc-500 hover:text-zinc-300' : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-[#FACC15] text-black font-bold rounded-lg hover:bg-yellow-400 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              data-testid="login-button"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {t('misc.loading')}
                </>
              ) : (
                t('auth.login')
              )}
            </button>
          </form>

          {/* Demo credentials hint */}
          <div className={`mt-6 p-3 rounded-lg border ${
            theme === 'dark' 
              ? 'bg-zinc-900/50 border-zinc-800' 
              : 'bg-gray-50 border-gray-200'
          }`}>
            <p className={`text-xs text-center ${theme === 'dark' ? 'text-zinc-500' : 'text-gray-500'}`}>
              Demo: admin / admin123
            </p>
          </div>

          {/* Version */}
          <p className={`text-center text-xs mt-4 ${theme === 'dark' ? 'text-zinc-600' : 'text-gray-400'}`}>
            v{APP_VERSION}
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
