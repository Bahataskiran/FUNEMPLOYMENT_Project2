ENV = "MOCK"# Orijinal sisteme geçiş yaparken sadece "PRODUCTION" yapman yeterlidir
#ENV = "PRODUCTION" 

CONFIG = {
    "MOCK": {
        "BASE_URL": "http://127.0.0.1:5000",
        "LOGIN_PATH": "/auth/login",
        "COURSE_REG_PATH": "/ogrenci/ders-kayit",
        "SELECTORS": {
            "username": "#kullanici_adi",
            "password": "#kullanici_sifre",
            "captcha_img": "#img_captcha",
            "captcha_input": "#captcha",
            "login_button": "button:has-text('Giriş Yap')",
            "error_modal": "#errorModal",
            "error_close": "#errorModal button:has-text('Kapat'), #errorModal .close",
            "captcha_refresh": "a[onclick*='refreshCaptcha']",
            "verify_continue": "#btn-devam",
            "closed_indicator": "h3:has-text('Ders kayıt dönemi kapalıdır!')",
            "enroll_modal": "#sube-modal",
            "enroll_confirm": "button:has-text('Seçimi Tamamla ve Ekle')",
            "logout_toggle": ".user-info .dropdown-toggle",
            "logout_link": "a[href*='logout'], a[href*='cikis']"
        },
        "DATA_SOURCE": "JS_OBJECT"
    },
    "PRODUCTION": {
        "BASE_URL": "https://ois.istinye.edu.tr",
        "LOGIN_PATH": "/auth/login",
        "COURSE_REG_PATH": "/ogrenci/ders-kayit",
        "SELECTORS": {
            "username": "#kullanici_adi",
            "password": "#kullanici_sifre",
            "captcha_img": "img[src*='captcha'], div.pull-left img",
            "captcha_input": "#captcha",
            "login_button": "button[type='submit']",
            "error_modal": "#errorModal, .modal",
            "error_close": "button:has-text('Kapat'), .close",
            "captcha_refresh": "i.icon-refresh, a[onclick*='refresh']",
            "verify_continue": "#btn-devam",
            "closed_indicator": "text='Ders kayıt dönemi kapalıdır'",
            "enroll_modal": "#sube-modal",
            "enroll_confirm": "button:has-text('Seçimi Tamamla')",
            "logout_toggle": ".user-info, .navbar-inner .dropdown-toggle",
            "logout_link": "a[href*='logout'], a[href*='cikis']"
        },
        "DATA_SOURCE": "DOM_TABLE"
    }
}

ACTIVE_CONFIG = CONFIG[ENV]