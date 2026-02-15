// Application Version Configuration
// Update these values when releasing new versions

export const APP_VERSION = '1.2.0';
export const VERSION_DATE = '2025-12-15';
export const BUILD_NUMBER = '2025121501';

export const CHANGELOG = [
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
  fullVersion: `v${APP_VERSION} (${BUILD_NUMBER})`
});
