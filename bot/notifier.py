import requests

# Telefona bildirim düşmesi için belirlediğimiz benzersiz kanal adı
NTFY_TOPIC = "funemployment_ois_baha_2026"

def send_terminal_log(title, message):
    """Terminal çıktısı"""
    print(f"\n📢 [BİLDİRİM] {title.upper()}: {message}\n")

def send_desktop_notification(title, message):
    """Masaüstü Windows/Mac Bildirimi"""
    try:
        from plyer import notification
        notification.notify(
            title=f"OİS: {title}",
            message=message,
            app_name="OİS Otomasyon",
            timeout=8
        )
    except Exception as e:
        print(f"[-] Masaüstü bildirimi hatası: {e}")

def send_sms_push_notification(title, message):
    """Telefona Anlık Bildirim (ntfy - Slide 42 & 56)"""
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={"Title": title.encode("utf-8")},
            timeout=5
        )
        print("[+] Telefona bildirim başarıyla iletildi.")
    except Exception as e:
        print(f"[-] Mobil bildirim iletilemedi: {e}")

def broadcast_notification(title, message):
    """Tüm kanallara aynı anda basar"""
    send_terminal_log(title, message)
    send_desktop_notification(title, message)
    send_sms_push_notification(title, message)