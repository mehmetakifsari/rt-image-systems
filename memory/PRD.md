# Renault Trucks Garanti Kayıt Sistemi - PRD

## Proje Özeti
Renault Trucks için WhatsApp benzeri arayüze sahip Garanti Görsel/Video/PDF Kayıt Sistemi.

## Tarih
- İlk Oluşturulma: 2026-02-15
- Son Güncelleme: 2026-02-15

## Kullanıcı Profilleri
1. **Admin**: Tüm şubeleri ve personeli yöneten sistem yöneticisi
2. **Garanti Danışmanı**: Şube bazlı garanti kayıtları oluşturan personel
3. **Hasar Danışmanı**: Şube bazlı hasar kayıtları oluşturan personel
4. **Müşteri Kabul Personeli**: Şube bazlı müşteri kabul işlemleri yapan personel
5. **Usta/Stajyer** (Sonraki aşama): Veri yükleyen saha çalışanı

## Şube Yapısı
| Kod | Şube | Şehir |
|-----|------|-------|
| 1 | Bursa | Bursa |
| 2 | İzmit | Kocaeli |
| 3 | Orhanlı | İstanbul |
| 4 | Hadımköy | İstanbul |
| 5 | Keşan | Edirne |

## İş Emri Formatı
`40216001` = 4(Şube) + 02(Ay) + 16(Gün) + 001(Sıra)
- İş emri numarasının ilk rakamı şube kodunu belirler
- Standart kayıtlarda iş emrinden şube otomatik algılanır

## Temel Gereksinimler
### Kayıt Türleri
- **Standard**: Garanti/standart servis (Plaka + İş Emri zorunlu)
- **RoadAssist**: Yol yardım (Plaka + Şube zorunlu)
- **Damaged**: Hasarlı araç (Referans No + Şube zorunlu)
- **PDI**: Sıfır araç teslim öncesi (VIN + Şube zorunlu)

### Özellikler
- WhatsApp benzeri sohbet arayüzü
- Fotoğraf, video, PDF yükleme
- Plaka OCR (Tesseract.js)
- Sesli not alma (Web Speech API)
- Offline queue desteği (IndexedDB)
- Türkçe/İngilizce çoklu dil
- Şube bazlı veri yönetimi
- Personel yönetimi (Admin)

## Uygulanan Özellikler

### Backend (FastAPI + MongoDB)
- [x] JWT kimlik doğrulama
- [x] Şube sistemi (5 şube)
- [x] Personel yönetimi (staff CRUD)
- [x] Şube bazlı veri filtreleme
- [x] İş emrinden şube algılama
- [x] Rol bazlı erişim kontrolü
- [x] 4 kayıt türü için CRUD API'ları
- [x] Dosya yükleme (fotoğraf, video, PDF)
- [x] Ayarlar API'ı (OCR, depolama, dil)
- [x] Dashboard istatistikleri (şube bazlı)

### Frontend (React + Tailwind)
- [x] Koyu tema tasarım (Renault Trucks kurumsal)
- [x] Login sayfası
- [x] Ana sayfa (kayıt listesi, arama, filtreleme)
- [x] Kullanıcı menüsü (profil, logout)
- [x] Yeni kayıt oluşturma (4 tip seçimi + şube)
- [x] Kayıt detay sayfası (WhatsApp benzeri)
- [x] Plaka OCR modal (Tesseract.js)
- [x] Sesli not alma (Web Speech API)
- [x] Admin dashboard (şube bazlı)
- [x] Personel yönetimi
- [x] WhatsApp kısayolu (personel kartlarında)
- [x] Logout fonksiyonu

### Admin Ayarları
- [x] OCR Sağlayıcı: Tarayıcı (Tesseract.js), Vision API
- [x] Depolama: Yerel, FTP, AWS S3, Google Drive, OneDrive
- [x] Dil: Türkçe, İngilizce

## Demo Hesaplar
- **Admin**: admin / admin123
- **Staff**: hadimkoy_garanti / test123

## Öncelikli Backlog

### P0 (Kritik) ✅
- [x] Şube sistemi
- [x] Personel yönetimi
- [x] Şube bazlı veri filtreleme
- [x] İş emrinden şube algılama

### P1 (Yüksek)
- [ ] Usta/Stajyer hesapları
- [ ] Bildirim sistemi (eksik evrak, istek)
- [ ] Bulut depolama entegrasyonları

### P2 (Orta)
- [ ] Google Vision API entegrasyonu
- [ ] Gelişmiş raporlama ve export
- [ ] Native mobil uygulama

## Sonraki Aşama (Usta/Stajyer)
1. Usta/Stajyer hesap oluşturma
2. Veri yükleme sonrası danışmana bildirim
3. Eksik evrak bildirimi
4. İstek bildirimi (ek görsel gerekli vb.)

## Teknik Mimari
- **Frontend**: React 19, Tailwind CSS, Radix UI
- **Backend**: FastAPI, Motor (async MongoDB)
- **Veritabanı**: MongoDB
- **Dosya Depolama**: Yerel (uploads klasörü)
- **Auth**: JWT
- **OCR**: Tesseract.js (tarayıcı içi)
- **Ses**: Web Speech API
