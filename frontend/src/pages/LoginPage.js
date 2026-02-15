import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { Truck, Eye, EyeOff, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const LoginPage = () => {
  const { t, i18n } = useTranslation();
  const { login } = useAuth();
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
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      <div className="relative w-full max-w-md">
        {/* Language toggle */}
        <button
          onClick={toggleLanguage}
          className="absolute -top-12 right-0 px-3 py-1.5 text-sm bg-zinc-800 text-zinc-300 rounded-full hover:bg-zinc-700 transition-colors"
          data-testid="language-toggle"
        >
          {i18n.language === 'tr' ? 'EN' : 'TR'}
        </button>

        {/* Login card */}
        <div className="bg-[#18181b] border border-[#27272a] rounded-2xl p-8 shadow-2xl">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-[#FACC15] rounded-2xl mb-4">
              <Truck className="w-8 h-8 text-black" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-wide">
              {t('auth.loginTitle')}
            </h1>
            <p className="text-zinc-400 text-sm mt-1">{t('auth.loginSubtitle')}</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">
                {t('auth.username')}
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full h-12 px-4 bg-[#09090b] border border-[#27272a] rounded-lg text-white placeholder-zinc-500 focus:border-[#FACC15] focus:ring-1 focus:ring-[#FACC15] transition-colors"
                placeholder={t('auth.username')}
                data-testid="username-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">
                {t('auth.password')}
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-12 px-4 pr-12 bg-[#09090b] border border-[#27272a] rounded-lg text-white placeholder-zinc-500 focus:border-[#FACC15] focus:ring-1 focus:ring-[#FACC15] transition-colors"
                  placeholder="••••••••"
                  data-testid="password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
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
          <div className="mt-6 p-3 bg-zinc-900/50 rounded-lg border border-zinc-800">
            <p className="text-xs text-zinc-500 text-center">
              Demo: admin / admin123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
