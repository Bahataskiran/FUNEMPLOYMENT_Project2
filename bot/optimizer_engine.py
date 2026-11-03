"""
Ders Programı Çakışma Kontrolü ve Optimizasyon Motoru
"""

# Şube numarası 51 ve üzeri olanlar laboratuvar kabul edilir
LAB_SECTION_THRESHOLD = 51
DAY_ORDER = {"Pazartesi": 1, "Salı": 2, "Çarşamba": 3, "Perşembe": 4, "Cuma": 5}

def parse_time_to_minutes(time_str):
    # '09:30' formatındaki saati hesaplama kolaylığı için dakikaya (570) çevirir
    clean_str = str(time_str).strip()
    if not clean_str or ":" not in clean_str:
        return -1
    parts = clean_str.split(":")
    if len(parts) != 2:
        return -1
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        return -1

def has_time_conflict(session_a, session_b):
    # İki ders bloğunun aynı gün ve çakışan saat aralığında olup olmadığını denetler
    if session_a["gun"].strip().lower() != session_b["gun"].strip().lower():
        return False

    start_a = parse_time_to_minutes(session_a["baslangic"])
    end_a = parse_time_to_minutes(session_a["bitis"])
    start_b = parse_time_to_minutes(session_b["baslangic"])
    end_b = parse_time_to_minutes(session_b["bitis"])

    if -1 in (start_a, end_a, start_b, end_b):
        return False
        
    # [BaşlangıçA, BitişA) ile [BaşlangıçB, BitişB) zaman çakışması kontrolü
    return (start_a < end_b) and (start_b < end_a)

def find_valid_schedules(unit_pools, current_schedule=None, index=0):
    # Backtracking yöntemiyle tüm ders/lab havuzlarını tarar ve çakışmasız varyasyonları toplar
    if current_schedule is None:
        current_schedule = []

    # Tüm dersler çakışmasız eklendiyse geçerli bir program oluşmuştur
    if index == len(unit_pools):
        return [list(current_schedule)]

    valid_results = []
    pool_name, options = unit_pools[index]

    # Mevcut dersin tüm şube alternatiflerini sırayla dene
    for candidate in options:
        conflict = False
        for scheduled in current_schedule:
            if has_time_conflict(candidate, scheduled):
                conflict = True
                break

        # Çakışma yoksa programa ekle, bir sonraki derse geç (özyineleme)
        if not conflict:
            current_schedule.append(candidate)
            sub_results = find_valid_schedules(unit_pools, current_schedule, index + 1)
            valid_results.extend(sub_results)
            current_schedule.pop()  # Geri adım at (backtrack)

    return valid_results

def calculate_total_days(schedule):
    # Programın haftada kaç farklı güne yayıldığını hesaplar
    return len(set(session["gun"] for session in schedule))

def calculate_latest_start_score(schedule):
    # Derslerin en geç başlama saatine göre önceliklendirme puanı üretir
    day_starts = {}
    for session in schedule:
        day = session["gun"]
        start_min = parse_time_to_minutes(session["baslangic"])
        if start_min != -1:
            if day not in day_starts or start_min < day_starts[day]:
                day_starts[day] = start_min

    if not day_starts:
        return (0, 0)
    return (min(day_starts.values()), sum(day_starts.values()) / len(day_starts))

def calculate_total_idle_time(schedule):
    # Gün içindeki dersler arasında kalan boşlukların (blok ders arası bekleme) toplamını bulur
    days_map = {}
    for session in schedule:
        day = session["gun"]
        start = parse_time_to_minutes(session["baslangic"])
        end = parse_time_to_minutes(session["bitis"])
        if start != -1 and end != -1:
            days_map.setdefault(day, []).append((start, end))

    total_gap = 0
    for day, intervals in days_map.items():
        intervals.sort(key=lambda x: x[0])
        for i in range(len(intervals) - 1):
            if intervals[i + 1][0] > intervals[i][1]:
                total_gap += (intervals[i + 1][0] - intervals[i][1])
    return total_gap

def build_optimal_schedule(available_courses_dict, preference="minimum_days"):
    """
    Şube havuzlarını hazırlar, çakışmasız tüm programları çıkarır 
    ve seçilen kritere göre en iyi haftalık takvimi döndürür.
    """
    unit_pools = []
    
    # 1. Her dersin teorik ve pratik (lab) gruplarını ayrı seçim havuzu olarak listele
    for code, details in available_courses_dict.items():
        if details.get("teorik") and len(details["teorik"]) > 0:
            unit_pools.append((f"{code}_THEORY", details["teorik"]))
        if details.get("lab") and len(details["lab"]) > 0:
            unit_pools.append((f"{code}_LAB", details["lab"]))

    # 2. Backtracking ile çakışma yaratmayan tüm varyasyonları bul
    all_valid_schedules = find_valid_schedules(unit_pools)
    
    if not all_valid_schedules:
        print("[-] Uyarı: Hiçbir çakışmasız program kombinasyonu bulunamadı!")
        return None, ""

    print(f"[*] Toplam {len(all_valid_schedules)} farklı çakışmasız haftalık program bulundu.")

    # 3. İstenen kritere göre listeyi sırala
    if preference == "latest_start":
        all_valid_schedules.sort(key=calculate_latest_start_score, reverse=True)
    elif preference == "compact":
        all_valid_schedules.sort(key=calculate_total_idle_time)
    else:  # minimum_days: Kampüse en az gün gitme ve az boşluk kalma önceliği
        all_valid_schedules.sort(key=lambda s: (calculate_total_days(s), calculate_total_idle_time(s)))

    # Sıralamada ilk sıraya yerleşen en ideal planı al
    best_plan = all_valid_schedules[0]
    
    secilen_gunler = set(x["gun"] for x in best_plan)
    print(f"[+] Optimize Edilen Plan: Toplam {len(secilen_gunler)} gün ({', '.join(secilen_gunler)})")

    # Botun sayfada tıklayabileceği {Ders: {teorik: id, lab: id}} formatına dönüştür
    actionable_plan = {}
    for item in best_plan:
        code = item["ders_kodu"]
        sube_id = str(item["sube"])
        is_lab = int(sube_id) >= LAB_SECTION_THRESHOLD
        
        if code not in actionable_plan:
            actionable_plan[code] = {}
            
        if is_lab:
            actionable_plan[code]["lab"] = sube_id
        else:
            actionable_plan[code]["teorik"] = sube_id

    table_str = format_schedule_table(best_plan)    

    return actionable_plan, table_str

def format_schedule_table(schedule_list):
    """
    Seçilen en iyi ders programı listesini gün ve saat sırasına göre 
    hizalı bir ASCII tablosuna dönüştürür.
    """
    if not schedule_list:
        return ""

    headers = ["Ders Kodu", "Tür", "Şube", "Gün", "Saat"]
    col_widths = [10, 8, 6, 12, 13]

    # Günleri haftalık sıraya göre dizmek için
    day_weights = {"Pazartesi": 1, "Salı": 2, "Çarşamba": 3, "Perşembe": 4, "Cuma": 5}
    
    # Listeyi gün ve başlangıç saatine göre sırala
    sorted_sessions = sorted(
        schedule_list, 
        key=lambda x: (day_weights.get(x.get("gun"), 9), parse_time_to_minutes(x.get("baslangic")))
    )

    rows = []
    for s in sorted_sessions:
        code = s["ders_kodu"]
        sube = str(s["sube"])
        is_lab = int(sube) >= LAB_SECTION_THRESHOLD
        tur = "Lab" if is_lab else "Teorik"
        gun = s["gun"]
        saat = f"{s['baslangic']}-{s['bitis']}"
        rows.append([code, tur, sube, gun, saat])

    line = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    header_str = "|" + "|".join([f" {h:<{w}} " for h, w in zip(headers, col_widths)]) + "|"
    
    table_lines = [line, header_str, line]
    for r in rows:
        row_str = "|" + "|".join([f" {val:<{w}} " for val, w in zip(r, col_widths)]) + "|"
        table_lines.append(row_str)
    table_lines.append(line)

    return "\n".join(table_lines)