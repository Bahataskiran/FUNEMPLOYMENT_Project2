import json
import os
import time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, expect
from PIL import Image
import io
import pytesseract
import shutil

from notifier import broadcast_notification

# Optimizasyon motoru ve site ayarları
from optimizer_engine import build_optimal_schedule
from ois_config import ACTIVE_CONFIG

# Tesseract OCR yolu kontrolü ve tanımlaması
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if shutil.which("tesseract"):
    pass
elif os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

BASE_URL = ACTIVE_CONFIG["BASE_URL"]
STATE_FILE = "monitor_state.json"
CHECK_INTERVAL_SECONDS = 120  # Kontrol periyodu (saniye)

# --- SİSTEM DURUMU TAKİBİ ---
def load_saved_state():
    # Kayıtlı son kontrol durumunu dosyadan okur
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"registration_open": False}
    return {"registration_open": False}

def save_state(is_open):
    # Ders seçimi açıldı mı bilgisini zaman damgasıyla kaydeder
    now_utc = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"registration_open": is_open, "last_check": now_utc}, f, indent=2)

# --- CAPTCHA ÇÖZÜMÜ ---
def solve_captcha_from_element(page):
    # Güvenlik kodunun ekran görüntüsünü alır
    captcha_img_el = page.locator("#img_captcha")
    expect(captcha_img_el).to_be_visible()
    
    img_bytes = captcha_img_el.screenshot()
    img = Image.open(io.BytesIO(img_bytes))
    
    # OCR doğruluğunu artırmak için resmi büyütüp siyah-beyaza çevirir
    w, h = img.size
    img_resized = img.resize((w * 3, h * 3), Image.Resampling.BICUBIC)
    gray = img_resized.convert('L')
    bw = gray.point(lambda p: 0 if p < 150 else 255, '1')
    
    # Sadece harf ve rakamları okuyacak şekilde Tesseract çalıştırır
    custom_config = r'--psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz23456789'
    raw_text = pytesseract.image_to_string(bw, config=custom_config)
    clean_code = "".join(raw_text.split()).strip().lower()
    print(f"[*] Okunan Güvenlik Kodu: '{clean_code}'")
    return clean_code

def notify_user(title, message):
    broadcast_notification(title, message)

# --- GİRİŞ İŞLEMLERİ ---
def perform_login(page, max_retries=6):
    sel = ACTIVE_CONFIG["SELECTORS"]
    
    for attempt in range(1, max_retries + 1):
        print(f"[*] Giriş denemesi ({attempt}/{max_retries})...")
        
        # 1. Giriş alanlarını doldur
        page.locator(sel["username"]).fill("2409111037")
        page.locator(sel["password"]).fill("sifre1")
        
        code = solve_captcha_from_element(page)
        page.locator(sel["captcha_input"]).fill(code)
        page.locator(sel["login_button"]).click()
        
        # 2. Sonucu bekle
        error_el = page.locator(sel["error_modal"])
        success_indicator = page.locator(sel.get("logout_toggle", ".user-info, .navbar-inner .dropdown-toggle"))

        try:
            # Hata penceresi ekranda belirdi mi?
            error_el.wait_for(state="visible", timeout=3500)
            print("[-] Güvenlik kodu veya şifre hatalı, modal kapatılıyor...")
            
            # Modal kapatma butonuna tıkla (Kapat butonu veya X butonu)
            try:
                close_btn = error_el.locator("button:has-text('Kapat'), .close")
                if close_btn.is_visible():
                    close_btn.first.click()
            except Exception:
                pass

            # Bootstrap animasyonunun takılma ihtimaline karşı JavaScript ile modalı ve arkaplan perdesini temizle
            page.evaluate("""() => {
                if (typeof $ !== 'undefined') {
                    $('#errorModal').modal('hide');
                    $('.modal-backdrop').remove();
                }
            }""")
            
            # Modalın tamamen gizlendiğinden emin ol
            try:
                error_el.wait_for(state="hidden", timeout=2000)
            except Exception:
                pass

            time.sleep(0.5)

            # Captcha ve parola alanını temizle, yeni captcha al
            try:
                page.locator(sel["captcha_refresh"]).click()
            except Exception:
                pass

            page.locator(sel["captcha_input"]).fill("")
            time.sleep(1.0)
            continue  # Sonraki denemeye geç
            
        except Exception:
            # Hata penceresi çıkmadıysa başarılı girişi doğrula
            is_logged_in = False
            
            try:
                success_indicator.wait_for(state="visible", timeout=4000)
                is_logged_in = True
            except Exception:
                # Giriş butonu sayfadan kalktıysa veya URL değiştiyse
                if not page.locator(sel["login_button"]).is_visible():
                    is_logged_in = True

            if is_logged_in:
                print("[+] Giriş başarılı!")
                return True
            else:
                print("[-] Giriş doğrulanamadı, sayfa yenilenerek tekrar deneniyor...")
                try:
                    page.locator(sel["captcha_refresh"]).click()
                except Exception:
                    page.reload()
                time.sleep(1.0)

    return False

def extract_course_slots_from_page(page):
    """
    Sayfadaki 'dersProgrami' JS objesini okuyup 
    optimizasyon motoruna uygun sözlük yapısına çevirir.
    """
    raw_db = page.evaluate("() => typeof dersProgrami !== 'undefined' ? dersProgrami : null")
    
    if not raw_db:
        raise ValueError("Sayfada 'dersProgrami' nesnesi bulunamadı!")

    formatted_courses = {}

    # Ham ders verisini teorik ve lab bloklarına ayırarak düzenler
    for code, info in raw_db.items():
        formatted_courses[code] = {"teorik": [], "lab": []}
        
        for t in info.get("teorik", []):
            formatted_courses[code]["teorik"].append({
                "ders_kodu": code,
                "sube": int(t["id"]),
                "gun": t["gun"],
                "baslangic": t["bas"],
                "bitis": t["bit"]
            })
            
        for l in info.get("lab", []):
            formatted_courses[code]["lab"].append({
                "ders_kodu": code,
                "sube": int(l["id"]),
                "gun": l["gun"],
                "baslangic": l["bas"],
                "bitis": l["bit"]
            })

    return formatted_courses

def fetch_course_schedule(page):
    """
    Aktif konfigürasyona göre ders verisini çeker (Mock veya Gerçek DOM).
    """
    sel = ACTIVE_CONFIG
    if sel["DATA_SOURCE"] == "JS_OBJECT":
        return extract_course_slots_from_page(page)
    else:
        return extract_course_slots_from_page(page)
    
# --- OTOMATİK DERS SEÇİMİ ---
def enroll_course_with_sections(page, course_code, sections):
    """
    Açılan seçim modalı üzerinden belirlenen teorik ve lab şubelerini işaretleyip onaylar.
    """
    print(f"[*] '{course_code}' için şube seçim ekranı açılıyor...")
    
    # 1. 'Dersi Al' butonuna tıkla
    take_btn = page.locator(f"button[onclick*=\"subeSecimEkraniAc(this, '{course_code}')\"]")
    take_btn.click()
    
    # Seçim penceresinin açılmasını bekle
    sube_modal = page.locator("#sube-modal")
    expect(sube_modal).to_be_visible()
    
    # 2. Uygun teorik şubeyi işaretle
    if "teorik" in sections:
        teorik_val = sections["teorik"]
        teorik_radio = sube_modal.locator(f"input[name='teorik_secim'][value='{teorik_val}']")
        teorik_radio.check()
        print(f"    -> Teorik Şube {teorik_val} işaretlendi.")

    # 3. Varsa uygun laboratuvar şubesini işaretle
    if "lab" in sections:
        lab_val = sections["lab"]
        lab_radio = sube_modal.locator(f"input[name='lab_secim'][value='{lab_val}']")
        lab_radio.check()
        print(f"    -> Lab Şube {lab_val} işaretlendi.")

    # 4. Seçimi kaydet
    confirm_btn = sube_modal.locator("button:has-text('Seçimi Tamamla ve Ekle')")
    confirm_btn.click()
    
    # 5. Butonun 'Eklendi'ye döndüğünü doğrula
    expect(take_btn).to_have_text("Eklendi")
    print(f"[✓] {course_code} başarıyla programa eklendi.")

# --- ANA DÖNGÜ VE AKIŞ YÖNETİMİ ---
def start_bot_session():
    sel = ACTIVE_CONFIG["SELECTORS"]
    base_url = ACTIVE_CONFIG["BASE_URL"]
    login_url = f"{base_url}{ACTIVE_CONFIG['LOGIN_PATH']}"
    course_reg_url = f"{base_url}{ACTIVE_CONFIG['COURSE_REG_PATH']}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=0)
        context = browser.new_context()
        page = context.new_page()

        # Giriş ve sayfa açık mı kontrol döngüsü
        while True:
            print("\n[1] OİS Giriş Sayfası Açılıyor...")
            page.goto(login_url)
            
            if not perform_login(page):
                print("[-] Sisteme giriş yapılamadı, 1 dakika sonra tekrar denenecek.")
                time.sleep(60)
                continue

            # Varsa adres güncelleme/onay pop-up'ını geç
            devam_btn = page.locator(sel["verify_continue"])
            try:
                if devam_btn.is_visible(timeout=800):
                    devam_btn.click()
                    print("[+] Adres doğrulama adımı geçildi.")
            except Exception:
                pass

            print("[2] Ders seçme ekranına geçiliyor...")
            page.goto(course_reg_url)

            system_opened = False
            session_start_time = time.time()

            # Sayfa açılana kadar belirli aralıklarla F5 atan bekleme döngüsü
            while True:
                elapsed_minutes = (time.time() - session_start_time) / 60
                # OİS 20 dakikada bir oturumu kapattığı için periyodik yenileme
                if elapsed_minutes >= 19:
                    print("[*] 20 dakikalık oturum süresi dolmak üzere. Yeniden giriş yapılacak...")
                    break

                # Oturum düşerse tekrar baştan giriş yap
                if page.locator(sel["username"]).is_visible():
                    print("[-] Oturum düşmüş, tekrar giriş yapılıyor...")
                    break

                is_closed = page.locator(sel["closed_indicator"]).is_visible()
                
                # 'Kayıtlar kapalıdır' uyarısı kalktıysa seçim başlamıştır
                if not is_closed:
                    print("\n🎉 [!] DİKKAT: Ders kayıt ekranı açıldı!")
                    notify_user("Ders Kayıtları Başladı", "OİS ders seçim ekranı açıldı! Program optimizasyonu başlatılıyor.")
                    save_state(True)
                    system_opened = True
                    break
                else:
                    print(f"[*] Sistem kapalı. (Aktif oturum: {int(elapsed_minutes)} dk.) Sayfa 2 dakika sonra yenilenecek...")
                    save_state(False)

                time.sleep(CHECK_INTERVAL_SECONDS)
                print("[*] Ders seçme sayfası yenileniyor (F5)...")
                page.reload()

            if system_opened:
                break

        # SİSTEM AÇILDIKTAN SONRAKİ İŞLEMLER
        print("\n[3] Sayfadaki ders saatleri ve şubeleri taranıyor...")
        available_courses_data = fetch_course_schedule(page)

        print("[*] Backtracking optimizasyon algoritması çalıştırılıyor...")
        optimal_plan, schedule_table = build_optimal_schedule(available_courses_data, preference="minimum_days")

        if not optimal_plan:
            print("[-] HATA: Çakışmasız geçerli bir ders programı kombinasyonu bulunamadı!")
            browser.close()
            return

        print(f"[+] Belirlenen Çakışmasız Şube Planı: {optimal_plan}")

        # Dersleri sırayla seç ve onayla
        print("\n[4] Şubeler OİS sistemine işleniyor...")
        for course_code, sections in optimal_plan.items():
            enroll_course_with_sections(page, course_code, sections)

        # Güvenli çıkış yap
        print("\n[5] Tüm dersler başarıyla seçildi, oturum kapatılıyor...")
        page.locator(sel["logout_toggle"]).click()
        page.locator(sel["logout_link"]).click()
        
        notify_message = f"Tüm dersler çakışmasız olarak sisteme işlendi!\n\nHaftalık Programınız:\n{schedule_table}"
        notify_user("Kayıt Tamamlandı", notify_message)
        time.sleep(2)
        browser.close()
        
if __name__ == "__main__":
    print("🚀 OİS Otomasyon Botu Başlatıldı...")
    try:
        start_bot_session()
    except Exception as e:
        print(f"[!] Hata: {e}")