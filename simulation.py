class FarmSimulation:
    def __init__(self):
        self.soil_moisture = 60.0  # Başlangıç %60
        self.terracore_water_used = 0
        self.traditional_water_used = 0

    def next_day(self, data):
        # Yağmur artırır, Bitki katsayısı (Kc) ve ET0 buharlaşma ile nemi azaltır
        self.soil_moisture += (data['rain'] * 0.5)
        self.soil_moisture -= (data['et0'] * data['kc'] * 1.5)
        self.soil_moisture = max(0, min(100, self.soil_moisture))
        
        # Geleneksel çiftçi yağmur yoksa her 2 günde bir 15mm sular varsayımı
        if data['rain'] == 0:
            self.traditional_water_used += 8  
            
        return self.soil_moisture

    def apply_irrigation(self, amount):
        self.soil_moisture += (amount * 1.8)
        self.soil_moisture = min(100, self.soil_moisture)
        self.terracore_water_used += amount