import io
import math
import random
import string
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template, request, redirect, url_for, session, send_file

app = Flask(__name__)
app.secret_key = "ois_guvenlik_anahtari_123"

# Ders seçim durumu
SISTEM_ACIK_MI = False

EKIP_UYELERI = {
    "2409011013": "sifre1",
    "2509011054": "sifre1",
    "2409111037": "sifre1",
    "2409011034": "sifre1",
    "2409011003": "sifre1"
}

def generate_captcha_image(text):
    width, height = 100, 43
    image = Image.new("RGB", (width, height), color=(252, 252, 252))
    draw = ImageDraw.Draw(image)

    for _ in range(110):
        nx = random.randint(0, width - 1)
        ny = random.randint(0, height - 1)
        draw.point((nx, ny), fill=(165, 165, 165))

    wave_offset = random.randint(20, 24)
    freq = random.uniform(0.08, 0.11)
    for x in range(width):
        y = int(wave_offset + 3 * math.sin(x * freq))
        if 0 <= y < height:
            draw.point((x, y), fill=(150, 150, 150))
            if y + 1 < height:
                draw.point((x, y + 1), fill=(160, 160, 160))

    draw.line(
        [(0, random.randint(20, 32)), (width, random.randint(18, 28))],
        fill=(170, 170, 170),
        width=1
    )

    try:
        font = ImageFont.truetype("arialbd.ttf", 23)
    except IOError:
        try:
            font = ImageFont.truetype("arial.ttf", 23)
        except IOError:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    start_x = (width - text_width) // 2
    start_y = (height - text_height) // 2 - 2

    draw.text((start_x, start_y), text, font=font, fill=(70, 70, 70))

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr

@app.route("/auth/captcha")
def auth_captcha():
    chars = string.ascii_lowercase + "23456789"
    captcha_text = "".join(random.choices(chars, k=4))
    session["captcha_text"] = captcha_text
    return send_file(generate_captcha_image(captcha_text), mimetype="image/png")

# Orijinal sistemde hem / hem de /auth/login girişe bakar
@app.route("/", methods=["GET", "POST"])
@app.route("/auth/login", methods=["GET", "POST"])
def login():
    hata_mesaji = None

    if request.method == "POST":
        kullanici = request.form.get("kullanici_adi", "").strip()
        sifre = request.form.get("kullanici_sifre", "")
        kod = request.form.get("captcha", "").strip().lower()
        dogru_kod = session.get("captcha_text", "").lower()

        # Terminalde değerleri anlık kontrol et
        print(f"[*] Girilen Kullanıcı: '{kullanici}', Şifre: '{sifre}'")
        print(f"[*] Girilen Captcha: '{kod}' <---> Beklenen Captcha: '{dogru_kod}'")

        # Kontrol kriterleri
        captcha_gecerli = (kod == dogru_kod and kod != "")
        kullanici_var = kullanici in EKIP_UYELERI
        sifre_gecerli = kullanici_var and (EKIP_UYELERI[kullanici] == sifre)

        if captcha_gecerli and kullanici_var and sifre_gecerli:
            session["user"] = kullanici
            return redirect(url_for("anasayfa", dogrulandi=0))
        else:
            hata_mesaji = "Kullanıcı Doğrulama Başarısız!!--"
            return render_template("login.html", hata=hata_mesaji)

    return render_template("login.html")

# Çıkış Rotaları: Session'ı temizler ve giriş sayfasına yönlendirir
@app.route("/logout")
@app.route("/auth/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/anasayfa")
def anasayfa():
    dogrulandi = request.args.get("dogrulandi", "0") == "1"
    return render_template("mainmenu.html", dogrulandi=dogrulandi)

# Orijinal OİS yolu ile Mock rotasını eşitledik
@app.route("/ders-secme")
@app.route("/ogrenci/ders-kayit")
def ders_secme():
    return render_template("derssecme.html", acik_mi=SISTEM_ACIK_MI)

@app.route("/sistemi-degistir")
def sistemi_degistir():
    global SISTEM_ACIK_MI
    SISTEM_ACIK_MI = not SISTEM_ACIK_MI
    durum = "AÇILDI" if SISTEM_ACIK_MI else "KAPATILDI"
    return f"Sistem durumu değiştirildi: <b>{durum}</b>. <br><br><a href='/ders-secme'>Ders Seçme Ekranına Git</a>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)