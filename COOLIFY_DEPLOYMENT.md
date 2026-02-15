# Coolify Deployment Guide - Renault Trucks Garanti Kayıt Sistemi

## Hızlı Kurulum (Coolify)

### 1. Yeni Kaynak Ekle
- Coolify Dashboard > Sources > Add New Source
- GitHub repo'nuzu bağlayın

### 2. Yeni Uygulama Oluştur
- Services > Add New Resource > **Docker Compose**
- Repository'nizi seçin

### 3. Environment Variables Ayarlayın
Coolify'da aşağıdaki ortam değişkenlerini ayarlayın:

#### Zorunlu:
```
MONGO_URL=mongodb://mongodb:27017
DB_NAME=renault_garanti
REACT_APP_BACKEND_URL=https://claims.visupanel.com
JWT_SECRET=your-super-secret-key-minimum-32-chars
```

#### Opsiyonel (Harici Servisler):
```
GOOGLE_VISION_API_KEY=  # OCR için
LLM_API_KEY=            # Voice-to-Text için
```

### 4. Domain Ayarla
- Settings > Domains
- Domain'inizi ekleyin: `claims.visupanel.com`
- SSL otomatik yapılandırılacak

### 5. Deploy
- Deploy butonuna tıklayın
- Build loglarını takip edin

---

## Alternatif: Sadece Dockerfile ile Deploy

Eğer docker-compose yerine sadece Dockerfile kullanmak isterseniz:

1. Coolify'da **Dockerfile** seçeneğini seçin
2. MongoDB'yi ayrı bir servis olarak ekleyin (Coolify > Services > MongoDB)
3. `MONGO_URL` değişkenini MongoDB servisinin URL'siyle güncelleyin

---

## Varsayılan Hesaplar

İlk kurulumdan sonra şu hesaplarla giriş yapabilirsiniz:

- **Admin**: `admin` / `admin123`

⚠️ **Önemli**: Üretim ortamında admin şifresini değiştirin!

---

## Port Yapılandırması

- **80**: Ana uygulama (Nginx)
- **8001**: Backend API (internal)
- **27017**: MongoDB (internal)

---

## Volume'lar

- `mongodb_data`: MongoDB veritabanı
- `uploads_data`: Yüklenen dosyalar (fotoğraf, video, PDF)

---

## Sağlık Kontrolü

Uygulama sağlık durumu:
```
curl https://claims.visupanel.com/api/
```

Beklenen yanıt:
```json
{
  "message": "Renault Trucks Garanti Kayıt Sistemi API",
  "version": "1.4.0"
}
```

---

## Sorun Giderme

### Build Hatası
- Node.js bağımlılıklarını kontrol edin
- `yarn.lock` dosyasının mevcut olduğundan emin olun

### MongoDB Bağlantı Hatası
- `MONGO_URL` değişkeninin doğru olduğundan emin olun
- MongoDB servisinin çalıştığını kontrol edin

### CORS Hatası
- `CORS_ORIGINS` değişkenini domain'inizi içerecek şekilde ayarlayın
- Veya `*` olarak bırakın

### Upload Hatası
- Nginx'te `client_max_body_size` 150M olarak ayarlı
- Daha büyük dosyalar için değiştirin

---

## Destek

Sorunlar için GitHub Issues kullanın.
