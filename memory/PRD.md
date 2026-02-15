# Renault Trucks Garanti Kayıt Sistemi - PRD

## Proje Özeti
Renault Trucks için WhatsApp benzeri arayüze sahip Garanti Görsel/Video/PDF Kayıt Sistemi.

## Versiyon: 1.2.0
- İlk Oluşturulma: 2026-02-15
- Son Güncelleme: 2026-12-15

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

### Kayıt Durumları (Status)
- **active**: Normal/Aktif kayıt
- **pending_review**: Stajyer tarafından oluşturuldu, danışman onayı bekliyor
- **approved**: Danışman tarafından onaylandı
- **rejected**: Danışman tarafından reddedildi

## Tamamlanan Özellikler v1.2.0

### Temel Sistem
- [x] JWT kimlik doğrulama (Admin, Staff, Apprentice)
- [x] Şube sistemi (5 şube)
- [x] Personel yönetimi (staff CRUD)
- [x] Şube bazlı veri filtreleme
- [x] İş emrinden şube algılama
- [x] Rol bazlı erişim kontrolü
- [x] 4 kayıt türü için CRUD API'ları
- [x] Dosya yükleme (fotoğraf, video, PDF)

### v1.2.0 Yeni Özellikler
- [x] **Landing Page**: Herkese açık tanıtım sayfası (/welcome)
- [x] **Dark/Light Mode**: Tema değiştirme (localStorage'da saklanır)
- [x] **Versiyon Sistemi**: /api/version endpoint'i ve UI'da gösterim
- [x] **Stajyer/Çırak Hesapları**: Yeni kullanıcı rolü
- [x] **Onay İş Akışı**: Stajyer kayıtları pending_review olarak başlar
- [x] **Bildirim Sistemi**: Kayıt oluşturma/onay/ret bildirimleri
- [x] **Admin Panel Sekmeleri**: Dashboard, Kayıtlar, Bekleyen Kayıtlar, Personel, Stajyerler, Ayarlar

### Frontend (React + Tailwind)
- [x] Koyu/Açık tema tasarım
- [x] Login sayfası (tema toggle)
- [x] Landing page (özellikler, şubeler, CTA)
- [x] Ana sayfa (kayıt listesi, arama, filtreleme)
- [x] Bildirim çanı (NotificationBell)
- [x] Kullanıcı menüsü (profil, logout, versiyon)
- [x] Yeni kayıt oluşturma (4 tip seçimi + şube)
- [x] Kayıt detay sayfası (WhatsApp benzeri)
- [x] Plaka OCR modal (Tesseract.js)
- [x] Sesli not alma (Web Speech API)
- [x] Admin dashboard (şube bazlı istatistikler)
- [x] Bekleyen kayıtlar sekmesi (onay/ret)
- [x] Personel yönetimi (staff + apprentice)
- [x] Stajyer yönetimi sekmesi

### Backend API'ları
- [x] /api/version - Versiyon bilgisi
- [x] /api/auth/login - Giriş
- [x] /api/auth/register - Kayıt (Admin)
- [x] /api/records - Kayıt CRUD
- [x] /api/records/pending - Bekleyen kayıtlar
- [x] /api/records/{id}/approve - Kayıt onaylama
- [x] /api/records/{id}/reject - Kayıt reddetme
- [x] /api/notifications - Bildirimler
- [x] /api/notifications/read-all - Tümünü okundu işaretle
- [x] /api/staff - Personel listesi
- [x] /api/apprentices - Stajyer listesi
- [x] /api/stats - Dashboard istatistikleri
- [x] /api/settings - Ayarlar

## Demo Hesaplar
- **Admin**: admin / admin123
- **Staff**: hadimkoy_garanti / test123
- **Stajyer**: test_stajyer / test123

## MOCKED (Henüz Gerçek Entegrasyon Yok)
⚠️ Aşağıdaki özellikler UI'da mevcuttur ancak backend entegrasyonu yapılmamıştır:
- Google Vision API (OCR)
- AWS S3 Depolama
- FTP Depolama
- Google Drive Depolama
- OneDrive Depolama
- Gemini/OpenAI Voice-to-Text

## Öncelikli Backlog

### P0 (Kritik) ✅ TAMAMLANDI
- [x] Şube sistemi
- [x] Personel yönetimi
- [x] Şube bazlı veri filtreleme
- [x] İş emrinden şube algılama
- [x] Landing page
- [x] Dark/Light mode
- [x] Versiyon sistemi
- [x] Stajyer hesapları
- [x] Bildirim sistemi

### P1 (Yüksek)
- [ ] Yıla göre aynı iş emri numarası sorunu (tarihe göre sıralama)
- [ ] Mobil API versiyonlama (/api/v1/...)
- [ ] Bulut depolama entegrasyonları (S3, GDrive)

### P2 (Orta)
- [ ] Google Vision API entegrasyonu
- [ ] Gemini/OpenAI Voice-to-Text entegrasyonu
- [ ] Gelişmiş raporlama ve export
- [ ] Native mobil uygulama (Android/iOS)

## Teknik Mimari
- **Frontend**: React 19, Tailwind CSS, Radix UI, Shadcn/UI
- **Backend**: FastAPI, Motor (async MongoDB)
- **Veritabanı**: MongoDB
- **Dosya Depolama**: Yerel (uploads klasörü)
- **Auth**: JWT
- **OCR**: Tesseract.js (tarayıcı içi)
- **Ses**: Web Speech API

## Test Raporları
- /app/test_reports/iteration_1.json
- /app/test_reports/iteration_2.json
- /app/test_reports/iteration_3.json (v1.2.0 - Tüm testler geçti)
