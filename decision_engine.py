def evaluate_irrigation(soil_moisture, et0, rain, stage):
    # Çiçeklenme döneminde pamuk suya çok hassastır, kritik eşik yükselir.
    critical_moisture = 45 if "Çiçeklenme" in stage else 30
    
    if soil_moisture < critical_moisture and rain == 0:
        amount = 22 if "Çiçeklenme" in stage else 15
        msg = f"🔴 {stage} evresinde yüksek su ihtiyacı! (Kritik Nem Eşiği: %{critical_moisture})"
        return "SU STRESİ RİSKİ", amount, msg
    elif critical_moisture <= soil_moisture <= (critical_moisture + 15):
        return "İZLE", 0, f"🟡 {stage} evresi seyri normal. Nem sınırda, izleniyor."
    else:
        return "NORMAL", 0, "🟢 Optımum koşullar. Sulama gerekmiyor."