# Renault Trucks Garanti Kayıt Sistemi

## Versiyon: 2.0.0

WhatsApp benzeri arayüze sahip garanti görsel/video/PDF kayıt sistemi.

## Özellikler

- 📱 **Mobil Öncelikli Tasarım**: WhatsApp benzeri kullanıcı arayüzü
- 🏢 **Şube Yönetimi**: 5 şube (Bursa, İzmit, Orhanlı, Hadımköy, Keşan)
- 👥 **Rol Bazlı Erişim**: Admin, Danışman, Usta/Stajyer
- 📷 **Medya Yükleme**: Fotoğraf, Video, PDF desteği
- 🔍 **Plaka OCR**: Tesseract.js ile otomatik plaka tanıma
- 🎤 **Sesli Not**: Web Speech API desteği
- 📴 **Offline Destek**: IndexedDB ile çevrimdışı kuyruk
- 🌙 **Tema Desteği**: Gece/Gündüz modu
- 🔔 **Bildirim Sistemi**: Eksik evrak, istek bildirimleri
- 🌐 **Çoklu Dil**: Türkçe/İngilizce

## Kurulum

### Gereksinimler
- Node.js 18+
- Python 3.10+
- MongoDB 6+

### Backend
```bash
cd backend
pip install -r requirements.txt
python server.py
```

### Frontend
```bash
cd frontend
yarn install
yarn start
```

## API Dokümantasyonu

API dokümantasyonu: `/api/docs` (Swagger UI)

### Temel Endpoint'ler

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/auth/login` | POST | Kullanıcı girişi |
| `/api/auth/register` | POST | Kullanıcı kaydı (Admin) |
| `/api/records` | GET/POST | Kayıt listesi/oluşturma |
| `/api/records/{id}` | GET/PUT/DELETE | Kayıt detay/güncelleme/silme |
| `/api/records/{id}/upload` | POST | Dosya yükleme |
| `/api/notifications` | GET | Bildirimler |
| `/api/staff` | GET/POST | Personel yönetimi |

## Şube Kodları

| Kod | Şube |
|-----|------|
| 1 | Bursa |
| 2 | İzmit |
| 3 | Orhanlı |
| 4 | Hadımköy |
| 5 | Keşan |

## İş Emri Formatı

`40216001` = `4`(Şube) + `02`(Ay) + `16`(Gün) + `001`(Sıra)

## Lisans

© 2026 Renault Trucks. Tüm hakları saklıdır.
