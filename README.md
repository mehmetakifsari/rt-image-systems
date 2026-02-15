# Renault Trucks Garanti Kayıt Sistemi

WhatsApp benzeri arayüze sahip Garanti Görsel/Video/PDF Kayıt Sistemi.

## Özellikler

- 🚛 4 farklı kayıt türü (Standart, Yol Yardım, Hasarlı, PDI)
- 📸 Fotoğraf, video ve PDF yükleme
- 📷 Plaka OCR tarama (Tesseract.js / Google Vision API)
- 🎤 Sesli not (Web Speech API / OpenAI Whisper)
- 👥 Çoklu kullanıcı ve şube yönetimi
- 🌙 Karanlık/Aydınlık tema
- 🌍 Türkçe/İngilizce dil desteği
- 📱 Mobil uyumlu tasarım

## Teknolojiler

- **Frontend**: React 19, Tailwind CSS, Shadcn/UI
- **Backend**: FastAPI, Python 3.11
- **Veritabanı**: MongoDB
- **Container**: Docker, Docker Compose

## Hızlı Başlangıç

### Docker ile Kurulum

```bash
# Repo'yu klonlayın
git clone https://github.com/your-repo/renault-garanti.git
cd renault-garanti

# Environment dosyasını oluşturun
cp .env.example .env
# .env dosyasını düzenleyin

# Docker ile başlatın
docker-compose up -d
```

### Coolify Deployment

Detaylı kurulum için [COOLIFY_DEPLOYMENT.md](./COOLIFY_DEPLOYMENT.md) dosyasına bakın.

## Varsayılan Hesaplar

| Rol | Kullanıcı Adı | Şifre |
|-----|---------------|-------|
| Admin | admin | admin123 |

⚠️ **Üretim ortamında şifreleri değiştirin!**

## Environment Variables

| Değişken | Açıklama | Zorunlu |
|----------|----------|---------|
| `MONGO_URL` | MongoDB bağlantı URL'i | ✅ |
| `DB_NAME` | Veritabanı adı | ✅ |
| `REACT_APP_BACKEND_URL` | Frontend API URL | ✅ |
| `JWT_SECRET` | JWT şifreleme anahtarı | ✅ |
| `GOOGLE_VISION_API_KEY` | OCR için API anahtarı | ❌ |
| `LLM_API_KEY` | Whisper için API anahtarı | ❌ |

## API Dokümantasyonu

API endpoint'leri için `/api/` adresini ziyaret edin.

Sağlık kontrolü:
```bash
curl https://your-domain.com/api/
```

## Lisans

MIT License

## Destek

Sorunlar için GitHub Issues kullanın.
