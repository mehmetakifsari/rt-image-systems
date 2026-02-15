# Renault Trucks Garanti Kayıt Sistemi - PRD

## Proje Özeti
Renault Trucks için WhatsApp benzeri arayüze sahip Garanti Görsel/Video/PDF Kayıt Sistemi.

## Versiyon: 1.4.0
- İlk Oluşturulma: 2026-02-15
- Son Güncelleme: 2026-02-15
- API Version: v1

## Kullanıcı Profilleri
1. **Admin**: Tüm şubeleri ve personeli yöneten sistem yöneticisi
2. **Garanti Danışmanı (Staff)**: Şube bazlı garanti kayıtları oluşturan personel
3. **Hasar Danışmanı (Staff)**: Şube bazlı hasar kayıtları oluşturan personel
4. **Müşteri Kabul Personeli (Staff)**: Şube bazlı müşteri kabul işlemleri yapan personel
5. **Stajyer/Çırak (Apprentice)**: Kayıt oluşturan, danışman onayı bekleyen saha çalışanı

## Şube Yapısı
| Kod | Şube | Şehir |
|-----|------|-------|
| 1 | Bursa | Bursa |
| 2 | İzmit | Kocaeli |
| 3 | Orhanlı | İstanbul |
| 4 | Hadımköy | İstanbul |
| 5 | Keşan | Edirne |

## ✅ Tamamlanan Özellikler v1.4.0

### v1.4.0 Yeni Özellikler (P0 Backlog - Frontend Entegrasyonu)
- [x] **OCR Frontend Entegrasyonu** - Plaka alanına "Tara" butonu, server (Google Vision) veya browser (Tesseract.js) fallback
- [x] **Voice-to-Text Frontend Entegrasyonu** - Not alanına 2 mikrofon butonu:
  - Gri mikrofon: Browser Web Speech API (ücretsiz, anlık)
  - Sarı mikrofon: Server OpenAI Whisper (daha doğru, API key gerekli)
- [x] **Admin Settings - Voice Provider** - Transkripsiyon sağlayıcı seçimi eklendi
- [x] **Graceful Degradation** - Server servisleri yapılandırılmamışsa otomatik browser fallback

### v1.3.0 Özellikler (Backend Entegrasyonu)
- [x] **AWS S3 Depolama** - Dosya yükleme/indirme (API key gerekli)
- [x] **Google Drive Depolama** - Bulut depolama (OAuth gerekli)
- [x] **FTP Depolama** - Harici FTP sunucu desteği
- [x] **OneDrive Depolama** - Microsoft bulut desteği
- [x] **Google Vision OCR** - Plaka ve metin tanıma (API key gerekli)
- [x] **OpenAI Whisper Voice-to-Text** - Ses transkripsiyonu (Emergent LLM Key)
- [x] **API Versiyonlama** - /api/version endpoint'i api_version döndürür
- [x] **Yıla Göre Filtreleme** - Aynı iş emri numarası farklı yıllarda
- [x] **Gelişmiş Sıralama** - sort_by ve sort_order parametreleri
- [x] **Servis Durumu API** - /api/services/status endpoint'i

### v1.2.0 Özellikler
- [x] **Landing Page** - Herkese açık tanıtım sayfası (/welcome)
- [x] **Dark/Light Mode** - Tema değiştirme
- [x] **Versiyon Sistemi** - Uygulama versiyonu gösterimi
- [x] **Stajyer/Çırak Hesapları** - Yeni kullanıcı rolü
- [x] **Onay İş Akışı** - pending_review durumu
- [x] **Bildirim Sistemi** - Kayıt bildirimleri

### Temel Sistem (v1.0-1.1)
- [x] JWT kimlik doğrulama
- [x] Şube sistemi (5 şube)
- [x] Personel yönetimi
- [x] Şube bazlı veri filtreleme
- [x] İş emrinden şube algılama
- [x] 4 kayıt türü (Standard, RoadAssist, Damaged, PDI)
- [x] Dosya yükleme (fotoğraf, video, PDF)

## Backend API Endpoint'leri

### Temel
- `GET /api/` - Health check
- `GET /api/version` - Versiyon bilgisi (api_version dahil)

### Kimlik Doğrulama
- `POST /api/auth/login` - Giriş
- `POST /api/auth/register` - Kayıt (Admin)

### Kayıtlar
- `GET /api/records` - Kayıt listesi (year, sort_by, sort_order parametreleri)
- `GET /api/records/pending` - Bekleyen kayıtlar
- `POST /api/records` - Yeni kayıt
- `GET /api/records/{id}` - Kayıt detay
- `PUT /api/records/{id}` - Kayıt güncelle
- `PUT /api/records/{id}/approve` - Kayıt onayla
- `PUT /api/records/{id}/reject` - Kayıt reddet

### Bildirimler
- `GET /api/notifications` - Bildirim listesi
- `POST /api/notifications` - Bildirim gönder
- `PUT /api/notifications/read-all` - Tümünü okundu işaretle

### Servisler (v1.3.0+)
- `GET /api/services/status` - Servis durumları (Admin)
- `GET /api/storage/providers` - Depolama sağlayıcıları (Admin)
- `POST /api/storage/set-provider` - Aktif depolama değiştir (Admin)
- `POST /api/ocr/detect-text` - Metin algılama
- `POST /api/ocr/detect-plate` - Plaka algılama
- `POST /api/voice/transcribe` - Ses transkripsiyonu

## Environment Variables (Panelden Ayarlanacak)

### Depolama
```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=eu-central-1
S3_BUCKET_NAME=
GOOGLE_DRIVE_CREDENTIALS=
GOOGLE_DRIVE_FOLDER_ID=
FTP_HOST=
FTP_USER=
FTP_PASSWORD=
ONEDRIVE_CLIENT_ID=
ONEDRIVE_CLIENT_SECRET=
```

### Servisler
```
GOOGLE_VISION_API_KEY=
LLM_API_KEY=  # Emergent Universal Key (OpenAI Whisper için)
```

## Demo Hesaplar
- **Admin**: admin / admin123
- **Staff**: hadimkoy_garanti / password123
- **Stajyer**: test_stajyer / test123

## Test Raporları
- /app/test_reports/iteration_1.json
- /app/test_reports/iteration_2.json
- /app/test_reports/iteration_3.json (v1.2.0)
- /app/test_reports/iteration_4.json (v1.3.0 - 23 test geçti)
- /app/test_reports/iteration_5.json (v1.4.0 - 17 backend + frontend testler geçti)

## Backlog

### ✅ P0 TAMAMLANDI (v1.4.0)
- [x] OCR Frontend entegrasyonu
- [x] Voice-to-Text Frontend entegrasyonu
- [x] Admin Settings - API ayarları kaydetme

### P1 (Sonraki)
- [ ] **Mobil API Dokümantasyonu** - OpenAPI/Swagger veya API_DOCS.md
- [ ] **Dosya Depolama Tam Entegrasyonu** - Kayıt oluşturulduğunda S3/GDrive'a yükleme

### P2 (Gelecek)
- [ ] Native mobil uygulama (Android/iOS)
- [ ] Gelişmiş raporlama ve export (PDF/Excel)
- [ ] WhatsApp entegrasyonu (bildirimler için)
- [ ] Fotoğraf kalitesi kontrolü (AI ile)

## GitHub Repo
Projeyi GitHub'a kaydetmek için chat arayüzündeki **"Save to Github"** butonunu kullanın.

## Teknik Mimari
- **Frontend**: React 19, Tailwind CSS, Shadcn/UI
- **Backend**: FastAPI, Motor (async MongoDB)
- **Veritabanı**: MongoDB
- **Dosya Depolama**: Local / S3 / Google Drive / FTP / OneDrive
- **Auth**: JWT
- **OCR**: Tesseract.js (tarayıcı) / Google Vision API (sunucu)
- **Voice**: Web Speech API (tarayıcı) / OpenAI Whisper (sunucu)
