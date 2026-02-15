# Renault Trucks Garanti Kayıt Sistemi - PRD

## Proje Özeti
Renault Trucks için WhatsApp benzeri arayüze sahip Garanti Görsel/Video/PDF Kayıt Sistemi.

## Tarih
- İlk Oluşturulma: 2026-02-15
- Son Güncelleme: 2026-02-15

## Kullanıcı Profilleri
1. **Saha Teknisyeni**: Mobil cihazdan kayıt oluşturan, fotoğraf/video yükleyen kullanıcı
2. **Admin**: Kayıtları yöneten, ayarları yapılandıran sistem yöneticisi

## Temel Gereksinimler
### Kayıt Türleri
- **Standard**: Garanti/standart servis (Plaka + İş Emri zorunlu)
- **RoadAssist**: Yol yardım (Plaka zorunlu)
- **Damaged**: Hasarlı araç (Referans No zorunlu)
- **PDI**: Sıfır araç teslim öncesi (VIN zorunlu)

### Özellikler
- WhatsApp benzeri sohbet arayüzü
- Fotoğraf, video, PDF yükleme
- Plaka OCR (Tesseract.js)
- Sesli not alma (Web Speech API)
- Offline queue desteği (IndexedDB)
- Türkçe/İngilizce çoklu dil
- Admin paneli (Dashboard, Kayıtlar, Ayarlar)

## Uygulanan Özellikler

### Backend (FastAPI + MongoDB)
- [x] JWT kimlik doğrulama
- [x] 4 kayıt türü için CRUD API'ları
- [x] Dosya yükleme (fotoğraf, video, PDF)
- [x] Dosya boyutu ve format doğrulama
- [x] Ayarlar API'ı (OCR, depolama, dil)
- [x] Dashboard istatistikleri
- [x] Varsayılan admin kullanıcı (admin/admin123)

### Frontend (React + Tailwind)
- [x] Koyu tema tasarım (Renault Trucks kurumsal)
- [x] Login sayfası
- [x] Ana sayfa (kayıt listesi, arama, filtreleme)
- [x] Yeni kayıt oluşturma (4 tip seçimi)
- [x] Kayıt detay sayfası (WhatsApp benzeri)
- [x] Plaka OCR modal (Tesseract.js)
- [x] Sesli not alma (Web Speech API)
- [x] Admin dashboard
- [x] Admin kayıt tablosu
- [x] Admin ayarlar sayfası
- [x] Çevrimiçi/çevrimdışı göstergesi
- [x] Offline queue sistemi

### Admin Ayarları
- [x] OCR Sağlayıcı: Tarayıcı (Tesseract.js), Vision API
- [x] Depolama: Yerel, FTP, AWS S3, Google Drive, OneDrive
- [x] Dil: Türkçe, İngilizce

## Öncelikli Backlog

### P0 (Kritik)
- [x] Temel kayıt oluşturma ve görüntüleme ✅
- [x] Dosya yükleme ✅
- [x] Admin paneli ✅

### P1 (Yüksek)
- [ ] Bulut depolama entegrasyonları (FTP, S3, Google Drive, OneDrive)
- [ ] Google Vision API entegrasyonu
- [ ] Rol bazlı erişim kontrolü (şube bazlı)

### P2 (Orta)
- [ ] Gelişmiş raporlama ve export
- [ ] Bildirim sistemi
- [ ] Native mobil uygulama

## Sonraki Adımlar
1. Bulut depolama seçeneklerinin aktif hale getirilmesi
2. Vision API entegrasyonu
3. Raporlama özellikleri
4. Mobil uygulama geliştirme

## Teknik Mimari
- **Frontend**: React 19, Tailwind CSS, Radix UI
- **Backend**: FastAPI, Motor (async MongoDB)
- **Veritabanı**: MongoDB
- **Dosya Depolama**: Yerel (uploads klasörü)
- **Auth**: JWT
- **OCR**: Tesseract.js (tarayıcı içi)
- **Ses**: Web Speech API
