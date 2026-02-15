// Türkçe ve İngilizce çeviri dosyası
const translations = {
  tr: {
    translation: {
      // Navigation
      "nav.home": "Ana Sayfa",
      "nav.newRecord": "Yeni Kayıt",
      "nav.admin": "Yönetim",
      "nav.settings": "Ayarlar",
      "nav.logout": "Çıkış",
      
      // Auth
      "auth.login": "Giriş Yap",
      "auth.register": "Kayıt Ol",
      "auth.username": "Kullanıcı Adı",
      "auth.password": "Şifre",
      "auth.fullName": "Ad Soyad",
      "auth.branch": "Şube",
      "auth.loginTitle": "Garanti Kayıt Sistemi",
      "auth.loginSubtitle": "Renault Trucks",
      
      // Record Types
      "record.standard": "Standart",
      "record.roadassist": "Yol Yardım",
      "record.damaged": "Hasarlı",
      "record.pdi": "PDI",
      "record.standardDesc": "Garanti ve standart servis kayıtları",
      "record.roadassistDesc": "Yol yardım ekibi hızlı kayıt",
      "record.damagedDesc": "Hasarlı ve plakasız araçlar",
      "record.pdiDesc": "Sıfır araç teslim öncesi inceleme",
      
      // Form Fields
      "field.plate": "Plaka",
      "field.workOrder": "İş Emri No",
      "field.vin": "VIN / Şasi No",
      "field.referenceNo": "Referans No",
      "field.note": "Not",
      "field.required": "Zorunlu",
      "field.optional": "Opsiyonel",
      
      // Actions
      "action.save": "Kaydet",
      "action.cancel": "İptal",
      "action.delete": "Sil",
      "action.upload": "Yükle",
      "action.scan": "Tara",
      "action.scanPlate": "Plaka Tara",
      "action.takePhoto": "Fotoğraf Çek",
      "action.recordVideo": "Video Kaydet",
      "action.uploadPdf": "PDF Yükle",
      "action.voiceNote": "Sesli Not",
      "action.search": "Ara",
      "action.filter": "Filtrele",
      "action.create": "Oluştur",
      
      // Status
      "status.online": "Çevrimiçi",
      "status.offline": "Çevrimdışı",
      "status.syncing": "Senkronize ediliyor...",
      "status.uploading": "Yükleniyor...",
      "status.processing": "İşleniyor...",
      "status.success": "Başarılı",
      "status.error": "Hata",
      "status.pending": "Beklemede",
      
      // Messages
      "msg.recordCreated": "Kayıt oluşturuldu",
      "msg.fileUploaded": "Dosya yüklendi",
      "msg.fileDeleted": "Dosya silindi",
      "msg.recordDeleted": "Kayıt silindi",
      "msg.settingsSaved": "Ayarlar kaydedildi",
      "msg.loginSuccess": "Giriş başarılı",
      "msg.loginError": "Giriş başarısız",
      "msg.plateDetected": "Plaka algılandı",
      "msg.noPlateDetected": "Plaka algılanamadı",
      "msg.confirmDelete": "Silmek istediğinize emin misiniz?",
      "msg.offlineQueue": "Bağlantı kesik - Dosyalar kuyrukta",
      
      // Admin
      "admin.dashboard": "Dashboard",
      "admin.records": "Kayıtlar",
      "admin.settings": "Ayarlar",
      "admin.totalRecords": "Toplam Kayıt",
      "admin.todayRecords": "Bugünkü Kayıt",
      "admin.recentRecords": "Son Kayıtlar",
      
      // Settings
      "settings.ocr": "OCR Ayarları",
      "settings.ocrProvider": "OCR Sağlayıcı",
      "settings.browserOcr": "Tarayıcı (Tesseract.js)",
      "settings.visionApi": "Google Vision API",
      "settings.visionApiKey": "Vision API Anahtarı",
      "settings.storage": "Depolama Ayarları",
      "settings.storageType": "Depolama Tipi",
      "settings.localStorage": "Yerel Sunucu",
      "settings.ftp": "FTP",
      "settings.awsS3": "AWS S3",
      "settings.googleDrive": "Google Drive",
      "settings.oneDrive": "OneDrive",
      "settings.language": "Dil",
      "settings.ftpHost": "FTP Sunucu",
      "settings.ftpUser": "FTP Kullanıcı",
      "settings.ftpPassword": "FTP Şifre",
      "settings.awsAccessKey": "AWS Access Key",
      "settings.awsSecretKey": "AWS Secret Key",
      "settings.awsBucket": "AWS Bucket",
      "settings.awsRegion": "AWS Region",
      
      // Misc
      "misc.noRecords": "Kayıt bulunamadı",
      "misc.loading": "Yükleniyor...",
      "misc.all": "Tümü",
      "misc.photo": "Fotoğraf",
      "misc.video": "Video",
      "misc.pdf": "PDF",
      "misc.files": "Dosyalar"
    }
  },
  en: {
    translation: {
      // Navigation
      "nav.home": "Home",
      "nav.newRecord": "New Record",
      "nav.admin": "Admin",
      "nav.settings": "Settings",
      "nav.logout": "Logout",
      
      // Auth
      "auth.login": "Login",
      "auth.register": "Register",
      "auth.username": "Username",
      "auth.password": "Password",
      "auth.fullName": "Full Name",
      "auth.branch": "Branch",
      "auth.loginTitle": "Warranty Record System",
      "auth.loginSubtitle": "Renault Trucks",
      
      // Record Types
      "record.standard": "Standard",
      "record.roadassist": "Road Assist",
      "record.damaged": "Damaged",
      "record.pdi": "PDI",
      "record.standardDesc": "Warranty and standard service records",
      "record.roadassistDesc": "Road assistance quick record",
      "record.damagedDesc": "Damaged vehicles without plates",
      "record.pdiDesc": "Pre-delivery inspection for new vehicles",
      
      // Form Fields
      "field.plate": "License Plate",
      "field.workOrder": "Work Order No",
      "field.vin": "VIN / Chassis No",
      "field.referenceNo": "Reference No",
      "field.note": "Note",
      "field.required": "Required",
      "field.optional": "Optional",
      
      // Actions
      "action.save": "Save",
      "action.cancel": "Cancel",
      "action.delete": "Delete",
      "action.upload": "Upload",
      "action.scan": "Scan",
      "action.scanPlate": "Scan Plate",
      "action.takePhoto": "Take Photo",
      "action.recordVideo": "Record Video",
      "action.uploadPdf": "Upload PDF",
      "action.voiceNote": "Voice Note",
      "action.search": "Search",
      "action.filter": "Filter",
      "action.create": "Create",
      
      // Status
      "status.online": "Online",
      "status.offline": "Offline",
      "status.syncing": "Syncing...",
      "status.uploading": "Uploading...",
      "status.processing": "Processing...",
      "status.success": "Success",
      "status.error": "Error",
      "status.pending": "Pending",
      
      // Messages
      "msg.recordCreated": "Record created",
      "msg.fileUploaded": "File uploaded",
      "msg.fileDeleted": "File deleted",
      "msg.recordDeleted": "Record deleted",
      "msg.settingsSaved": "Settings saved",
      "msg.loginSuccess": "Login successful",
      "msg.loginError": "Login failed",
      "msg.plateDetected": "Plate detected",
      "msg.noPlateDetected": "No plate detected",
      "msg.confirmDelete": "Are you sure you want to delete?",
      "msg.offlineQueue": "Offline - Files queued",
      
      // Admin
      "admin.dashboard": "Dashboard",
      "admin.records": "Records",
      "admin.settings": "Settings",
      "admin.totalRecords": "Total Records",
      "admin.todayRecords": "Today's Records",
      "admin.recentRecords": "Recent Records",
      
      // Settings
      "settings.ocr": "OCR Settings",
      "settings.ocrProvider": "OCR Provider",
      "settings.browserOcr": "Browser (Tesseract.js)",
      "settings.visionApi": "Google Vision API",
      "settings.visionApiKey": "Vision API Key",
      "settings.storage": "Storage Settings",
      "settings.storageType": "Storage Type",
      "settings.localStorage": "Local Server",
      "settings.ftp": "FTP",
      "settings.awsS3": "AWS S3",
      "settings.googleDrive": "Google Drive",
      "settings.oneDrive": "OneDrive",
      "settings.language": "Language",
      "settings.ftpHost": "FTP Host",
      "settings.ftpUser": "FTP User",
      "settings.ftpPassword": "FTP Password",
      "settings.awsAccessKey": "AWS Access Key",
      "settings.awsSecretKey": "AWS Secret Key",
      "settings.awsBucket": "AWS Bucket",
      "settings.awsRegion": "AWS Region",
      
      // Misc
      "misc.noRecords": "No records found",
      "misc.loading": "Loading...",
      "misc.all": "All",
      "misc.photo": "Photo",
      "misc.video": "Video",
      "misc.pdf": "PDF",
      "misc.files": "Files"
    }
  }
};

export default translations;
