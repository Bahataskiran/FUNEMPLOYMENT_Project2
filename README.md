# OİS Course Registration Bot & Schedule Optimizer 🎓🤖

Bu proje, İstinye Üniversitesi Öğrenci İşleri Bilgi Sistemi (OİS) üzerinde ders kayıt dönemlerinde otomatik çakışmasız ders programı oluşturmayı ve ders seçimini otonom olarak gerçekleştirmeyi amaçlayan bir optimizasyon ve otomasyon botudur.

Proje bünyesinde geliştirme ve güvenli test süreçleri için birebir OİS arayüzünü ve işleyişini taklit eden yerel bir **Mock Flask Sunucusu** yer almaktadır.

---

## 🚀 Temel Özellikler

- **Dahili Mock Sunucu:** Gerçek sisteme istek atmadan tüm senaryoları test edebilmek için Flask tabanlı sahte OİS simülasyonu.
- **Güvenlik Kodu (Captcha) Çözümü:** Tesseract OCR ve PIL görüntü işleme filtreleri kullanılarak OİS güvenlik kodlarını otomatik ayrıştırır.
- **Otonom Tarayıcı Otomasyonu:** Playwright tabanlı altyapısıyla sisteme giriş yapar, ders kayıt ekranının açılmasını periyodik olarak bekler ve açıldığı anda optimize edilen şubeleri seçip oturumu güvenle kapatır.
- **Backtracking Optimizasyon Motoru:** Derslerin teorik ve laboratuvar şubelerini tarayarak sıfır zaman çakışması garantili kombinasyonları türetir, kampüse en az gün gitme (`minimum_days`) veya en kompakt program kriterlerine göre en uygun takvimi belirler.


---

## 🛠️ Kurulum

### 1. Gereksinimlerin Yüklenmesi
Python 3.10+ kurulu olduğundan emin olun ve bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
playwright install chromium

2. Tesseract OCR KurulumuBotun güvenlik kodlarını çözebilmesi için sisteminizde Tesseract OCR kurulu olmalıdır:   Windows: Tesseract-OCR Windows Installer üzerinden C:\Program Files\Tesseract-OCR dizinine kurun.   Linux: sudo apt-get install tesseract-ocrmacOS: brew install tesseract

------ Kullanım Kılavuzu ------

Proje iki farklı modda çalıştırılabilir: Yerel Mock Test Ortamı ve Gerçek OİS (Production) Ortamı.

Senaryo A: Yerel Mock Sunucuda Test Etme

1. Mock Sunucuyu Başlatın:
Terminalde Flask uygulamasını çalıştırın:
python app.py

2. Çalışma Ortamını Doğrulayın:
ois_config.py dosyasında ENV değişkeninin "MOCK" olduğundan emin olun:
ENV = "MOCK"

3. Optimizasyon Kriterini Belirleyin (İsteğe Bağlı):
ois_bot.py içinde yer alan build_optimal_schedule fonksiyonuna dilediğiniz önceliği parametre olarak verebilirsiniz.

4. Botu Çalıştırın:
Yeni bir terminal penceresi açıp botu başlatın:
python ois_bot.py
Bot otomatik olarak tarayıcıyı açacak, güvenlik kodunu çözüp sisteme giriş yapacak ve ders kayıt ekranının açılmasını beklemeye başlayacaktır.

5. Ders Kayıtlarını Simüle Edin (Sistemi Açma/Kapama):
Ders kayıt ekranı varsayılan olarak "Kapalı" durumdadır. app.py dosyasında şu satırdan ders kayıt sistemini açık hale getirebilirsiniz:
SISTEM_ACIK_MI = False
Sistem açıldığı anda bot durumu algılayacak, çakışmasız en iyi ders programını hesaplayacak ve dersleri sırayla seçerek oturumu kapatacaktır.

Senaryo B: Gerçek OİS Sisteminde Çalıştırma
1. ois_config.py dosyasını açın ve ortamı değiştirin:
ENV = "PRODUCTION"

2. ois_bot.py içerisindeki giriş fonksiyonunda (perform_login) yer alan öğrenci numarası ve şifre alanlarını kendi OİS giriş bilgilerinizle güncelleyin.

3.Botu başlatın
python ois_bot.py


PROJE YAPISI
├── app.py                 # Test amaçlı geliştirilmiş yerel Flask Mock sunucusu
├── ois_bot.py             # Giriş, Captcha çözümü ve ders seçimini yöneten Playwright botu
├── ois_config.py          # Mock ve Production ortamlarına ait selector ve URL ayarları
├── optimizer_engine.py    # Çakışma kontrolü ve backtracking optimizasyon motoru
├── requirements.txt       # Proje bağımlılıkları
├── templates/             # OİS arayüz simülasyonu için HTML şablonları
│   ├── login.html
│   ├── mainmenu.html
│   └── derssecme.html
└── README.md

Group Members
Mehmet Baha Taşkıran (2409011013) - @Bahataskiran
Muhammet Emin Bakırcı (2409111037) - @Eminbakircii
Yunus Çerkezoğlu (2409011003) - @yunuscerkezoglu
Mehmet Ali Saray (2509011054) - @MehmetAliS480
Sinan İnan (2409011034) - @sinaninan