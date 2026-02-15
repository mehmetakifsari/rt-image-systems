// Application Version Configuration
// Update these values when releasing new versions

export const APP_VERSION = '1.3.0';
export const VERSION_DATE = '2025-12-15';
export const BUILD_NUMBER = '2025121502';
export const API_VERSION = 'v1';

export const CHANGELOG = [
  {
    version: '1.3.0',
    date: '2025-12-15',
    changes: [
      'AWS S3, Google Drive, FTP, OneDrive depolama entegrasyonları',
      'Google Vision API (OCR) entegrasyonu',
      'OpenAI Whisper Voice-to-Text entegrasyonu',
      'API versiyonlama (v1)',
      'Yıla göre kayıt filtreleme (aynı iş emri sorunu çözümü)'
    ]
  },
  {
    version: '1.2.0',
    date: '2025-12-15',
    changes: [
      'Landing page eklendi',
      'Dark/Light mode desteği eklendi',
      'Versiyon sistemi eklendi',
      'Stajyer hesap sistemi eklendi',
      'Bildirim sistemi eklendi'
    ]
  },
  {
    version: '1.1.0',
    date: '2025-02-15',
    changes: [
      'Şube bazlı personel yönetimi',
      'Admin dashboard',
      'İş emrinden şube algılama'
    ]
  },
  {
    version: '1.0.0',
    date: '2025-02-01',
    changes: [
      'İlk sürüm',
      'Temel garanti kayıt sistemi',
      'JWT kimlik doğrulama'
    ]
  }
];

export const getVersionInfo = () => ({
  version: APP_VERSION,
  date: VERSION_DATE,
  build: BUILD_NUMBER,
  apiVersion: API_VERSION,
  fullVersion: `v${APP_VERSION} (${BUILD_NUMBER})`
});
