# config.py
# Bu dosya, uygulamanın tüm sabitlerini ve yapılandırma sözlüklerini içerir.
# Bu yaklaşım, kodun daha temiz ve yönetilebilir olmasını sağlar.

import re

# --- Görünmez Karakter Temizleme Fonksiyonu ---
def clean_invisible_chars(text):
    """
    Metindeki görünmez karakterleri (U+00A0, U+200B, U+FEFF) temizler ve
    gereksiz boşlukları kaldırır.
    """
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r'[\s\u00A0\u200B\uFEFF]+', ' ', text).strip()

# ==============================================================================
# ŞİRKET BİLGİLERİ VE SABİTLER
# ==============================================================================

# LOGO_URL'nin genel erişime açık bir URL olduğundan emin olun.
# Bu URL, şirket logosunu PDF'lere dinamik olarak çekmek için kullanılır.
LOGO_URL = "https://drive.google.com/uc?export=download&id=1RD27Gas035iUqe4Ucl3phFwxZPWfzlzn"

COMPANY_INFO = {
    "name": clean_invisible_chars("PREMIUM HOME LTD"),
    "address": clean_invisible_chars("Iasonos 1, 1082, Nicosia Cyprus"),
    "email": clean_invisible_chars("info@premiumpluscy.eu"),
    "phone": clean_invisible_chars("+35722584081, +35797550946"),
    "website": clean_invisible_chars("www.premiumpluscy.eu"),
    "linktree": clean_invisible_chars("https://linktr.ee/premiumplushome"),
    "company_no": clean_invisible_chars("HE 467707"),
    "bank_name": clean_invisible_chars("BANK OF CYPRUS GROUP"),
    "bank_address": clean_invisible_chars("12 Esperidon Street 1087 Nicosia"),
    "account_name": clean_invisible_chars("SOYKOK PREMIUM HOME LTD"),
    "iban": clean_invisible_chars("CY27 0020 0195 0000 3570 4239 2044"),
    "account_number": clean_invisible_chars("357042392044"),
    "currency_type": clean_invisible_chars("EURO"),
    "swift_bic": clean_invisible_chars("BCYPCY2N")
}

# --- GÜNCELLENMİŞ FİYAT LİSTESİ ---
# Tüm fiyatlar KDV hariç maliyet fiyatlarıdır.
FIYATLAR = {
    # Çelik Profil Fiyatları (6m parça başına)
    "steel_profile_100x100x3": 45.00,
    "steel_profile_100x50x3": 33.00,
    "steel_profile_40x60x2": 14.00,
    "steel_profile_120x60x5mm": 60.00,
    "steel_profile_50x50x2": 11.00,
    "steel_profile_30x30x2": 8.50,
    "steel_profile_hea160": 155.00,
    "steel_profile_120x60x3mm": 50.00, 
    
    # Temel Malzeme Fiyatları
    "heavy_steel_m2": 400.00,
    "sandwich_panel_m2": 22.00,
    "plywood_piece": 44.44,
    "aluminum_window_piece": 250.00,
    "sliding_glass_door_piece": 300.00,
    "wc_window_piece": 120.00,
    "wc_sliding_door_piece": 150.00,
    "door_piece": 280.00,
    
    # Kurulum/İşçilik Fiyatları
    "kitchen_installation_standard_piece": 550.00,
    "kitchen_installation_special_piece": 1000.00,
    "shower_wc_installation_piece": 1000.00,
    "connection_element_m2": 1.50,
    "transportation": 350.00,
    "floor_heating_m2": 50.00,
    "wc_ceramic_m2_material": 20.00,
    "wc_ceramic_m2_labor": 20.00,
    "electrical_per_m2": 25.00,
    "plumbing_per_m2": 25.00,
    "osb_piece": 12.25, # GÜNCELLENDİ
    "insulation_per_m2": 5.25, # GÜNCELLENDİ
    
    # İşçilik Fiyatları
    "welding_labor_m2_standard": 160.00,
    "welding_labor_m2_trmontaj": 20.00,
    "panel_assembly_labor_m2": 5.00,
    "plasterboard_material_m2": 20.00,
    "plasterboard_labor_m2_avg": 80.00,
    "plywood_flooring_labor_m2": 11.11,
    "door_window_assembly_labor_piece": 10.00,
    "solar_per_kw": 1250.00,

    # Yeni Zemin Sistemi Malzemeleri Fiyatları
    "skirting_meter_price": 2.00,
    "laminate_flooring_m2_price": 18.00,
    "under_parquet_mat_m2_price": 3.00,
    "osb2_18mm_piece_price": 30.00,
    "galvanized_sheet_m2_price": 10.00,

    # Aether Living Paketleri için Malzeme Fiyatları
    "smart_home_systems_total_price": 350.00,
    "white_goods_total_price": 800.00,
    "sofa_total_price": 400.00,
    "security_camera_total_price": 650.00,
    "exterior_cladding_price_per_m2": 150.00,
    "bedroom_set_total_price": 800.00,
    "terrace_laminated_wood_flooring_price_per_m2": 40.00,
    "porcelain_tile_m2_price": 25.00,
    "concrete_panel_floor_price_per_m2": 50.00,
    "premium_faucets_total_price": 200.00,
    "designer_furniture_total_price": 1000.00,
    "italian_sofa_total_price": 800.00,
    "inclass_chairs_unit_price": 150.00,
    "exterior_wood_cladding_m2_price": 150.00,
    "brushed_grey_granite_countertops_price_m2_avg": 425.00,
    "100mm_eps_isothermal_panel_unit_price": 27.00,
    "gypsum_board_white_per_unit_price": 8.65,
    "gypsum_board_green_per_unit_price": 11.95,
    "gypsum_board_blue_per_unit_price": 22.00,
    "otb_stone_wool_price": 19.80,
    "glass_wool_5cm_packet_price": 19.68,
    "tn25_screws_price_per_unit": 5.58,
    "cdx400_material_price": 3.40,
    "ud_material_price": 1.59,
    "oc50_material_price": 2.20,
    "oc100_material_price": 3.96,
    "ch100_material_price": 3.55,
    "aether_package_cost": 50000.00,
    "staircase_cost": 1000.00
}

# --- Sabit Oranlar ve Alanlar ---
FIRE_RATE = 0.05
VAT_RATE = 0.19
MONTHLY_ACCOUNTING_EXPENSES = 180.00
MONTHLY_OFFICE_RENT = 280.00
ANNUAL_INCOME_TAX_RATE = 0.235
OSB_PANEL_AREA_M2 = 1.22 * 2.44
GYPSUM_BOARD_UNIT_AREA_M2 = 2.88
GLASS_WOOL_M2_PER_PACKET = 10.0

# --- PDF Metinleri için Çeviri Sözlüğü (YENİ EKLEME) ---
# Bu sözlük, PDF metinlerinin tek bir yerden yönetilmesini sağlar.
# Anahtar: İngilizce metnin birincil kısmı
# Değer: [Türkçe metin, Yunanca metin]
TRANSLATIONS = {
    # Genel
    "PREFABRICATED HOUSE PROPOSAL": ["PREFABRİK EV TEKLİFİ", "ΠΡΟΤΑΣΗ ΠΡΟΚΑΤΑΣΚΕΥΑΣΜΕΝΟΥ ΣΠΙΤΙΟΥ"],
    "For": ["Müşteri", "Για"],
    "Company": ["Firma", "Εταιρεία"],
    "Date": ["Tarih", "Ημερομηνία"],
    "CUSTOMER & PROJECT INFORMATION": ["MÜŞTERİ VE PROJE BİLGİLERİ", "ΠΛΗΡΟΦΟΡΙΕΣ ΠΕΛΑΤΗ & ΕΡΓΟΥ"],
    "Room Configuration": ["Oda Konfigürasyonu", "Διαμόρφωση Δωματίου"],
    "Dimensions": ["Boyutlar", "Διαστάσεις"],
    "Total Area": ["Toplam Alan", "Συνολική Επιφάνεια"],
    "Structure Type": ["Yapı Tipi", "Τύπος Κατασκευής"],
    "Name": ["Adı Soyadı", "Όνομα"],
    "Address": ["Adres", "Διεύθυνση"],
    "Phone": ["Telefon", "Τηλέφωνο"],
    "ID/Passport No": ["Kimlik/Pasaport No", "Αρ. Ταυτότητας/Διαβατηρίου"],
    "TECHNICAL SPECIFICATIONS": ["TEKNİK ÖZELLİKLER", "ΤΕΧΝΙΚΑ ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ"],
    "Construction Type": ["Yapı Tipi", "Τύπος Κατασκευής"],
    "Steel Structure Details": ["Çelik Yapı Detayları", "Λεπτομέρειες Χαλύβδινης Κατασκευής"],
    "Interior Walls": ["İç Duvarlar", "Εσωτερικοί Τοίχοι"],
    "Roof": ["Çatı", "Στέγη"],
    "Exterior Walls": ["Dış Duvarlar", "Εξωτερικοί Τοίχοι"],
    "Interior": ["İç Mekan", "Εσωτερικό"],
    "Insulation": ["Yalıtım", "Μόνωση"],
    "Floor Covering": ["Zemin Kaplama", "Δάπεδο"],
    "Floor Insulation": ["Zemin Yalıtımı", "Μόνωση Δαπέδου"],
    "Wall Insulation": ["Duvar Yalıtımı", "Μόνωση Τοίχου"],
    "Floor Insulation Materials": ["Zemin Yalıtım Malzemeleri", "Υλικά Μόνωσης Δαπέδου"],
    "Openings": ["Doğramalar", "Ανοίγματα"],
    "ADDITIONAL TECHNICAL FEATURES": ["DİĞER TEKNİK ÖZELLİKLER", "ΠΡΟΣΘΕΤΑ ΤΕΧΝΙΚΑ ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ"],
    "Kitchen": ["Mutfak", "Κουζίνα"],
    "Kitchen Materials": ["Mutfak Malzemeleri", "Υλικά Κουζίνας"],
    "Shower/WC": ["Duş/WC", "Ντους/WC"],
    "Shower/WC Materials": ["Duş/WC Malzemeleri", "Υλικά Ντους/WC"],
    "Electrical": ["Elektrik Tesisatı", "Ηλεκτρολογικά"],
    "Plumbing": ["Sıhhi Tesisat", "Υδραυλικά"],
    "Extra General Additions": ["Ekstra Genel İlaveler", "Έξτρα Γενικές Προσθήκες"],
    "Estimated Delivery": ["Tahmini Teslimat", "Εκτιμώμενη Παράδοση"],
    "business days": ["iş günü", "εργάσιμες ημέρες"],
    "CUSTOMER NOTES": ["MÜŞTERİ NOTLARI", "ΣΗΜΕΙΩΣΕΙΣ ΠΕΛΑΤΗ"],
    "PRICE & PAYMENT SCHEDULE": ["FİYAT VE ÖDEME PLANI", "ΤΙΜΗ & ΠΡΟΓΡΑΜΜΑ ΠΛΗΡΩΜΩΝ"],
    "Main House Price": ["Ana Ev Bedeli", "Τιμή Κυρίως Σπιτιού"],
    "Solar System Price": ["Güneş Enerjisi Sistemi Bedeli", "Τιμή Ηλιακού Συστήματος"],
    "Aether Package Price": ["Aether Paketi Bedeli", "Τιμή Πακέτου Aether"],
    "Extra Expenses": ["Ekstra Giderler", "Έξτρα Έξοδα"],
    "TOTAL PRICE": ["TOPLAM BEDEL", "ΣΥΝΟΛΙΚΗ ΤΙΜΗ"],
    "All prices are VAT included": ["Tüm fiyatlar KDV dahildir", "Όλες οι τιμές περιλαμβάνουν ΦΠΑ."],
    "Our prefabricated living spaces have a 3-year warranty.": ["Prefabrik yaşam alanlarımız 3 yıl garantiye sahiptir.", "Οι προκατασκευασμένοι χώροι διαβίωσης μας έχουν 3ετή εγγύηση."],
    "Main House Payment Plan": ["Ana Ev Ödeme Planı", "Πρόγραμμα Πληρωμών Κυρίως Σπιτιού"],
    "Down Payment": ["Peşinat", "Προκαταβολή"],
    "Due upon contract signing": ["Sözleşme anında ödenir", "Με την υπογραφή της σύμβασης."],
    "1st Installment": ["1. Ara Ödeme", "1η Δόση"],
    "Due upon completion of structure": ["Karkas imalatı bitiminde ödenir", "Με την ολοκλήρωση της κατασκευής."],
    "2nd Installment": ["2. Ara Ödeme", "2η Δόση"],
    "Due upon completion of interior works": ["İç imalatlar bitiminde ödenir", "Με την ολοκλήρωση των εσωτερικών εργασιών."],
    "Final Payment": ["Son Ödeme", "Τελική Εξόφληση"],
    "Due upon final delivery": ["Teslimat sırasında ödenir", "Με την τελική παράδοση."],
    "SALES CONTRACT": ["SATIŞ SÖZLEŞMESİ", ""],
    "Subject of the Agreement": ["Sözleşmenin Konusu", ""],
    "Definitions": ["Tanımlar", ""],
    "Sales Price and Payment Terms": ["Satış Fiyatı ve Ödeme Koşulları", ""],
    "Bank Details": ["Banka Detayları", ""],
    "Inspection of the Property and Defects": ["Mülkün Denetimi ve Kusurlar", ""],
    "Completion of the House": ["Evin Tamamlanması", ""],
    "Termination": ["Fesih", ""],
    "Notifications": ["Bildirimler", ""],
    "Warranty and Defects liability": ["Garanti ve Kusurlardan Sorumluluk", ""],
    "Applicable Law": ["Uygulanacak Hukuk", ""],
    "Dispute Resolution - Mediation / Arbitration": ["Anlaşmazlık Çözümü - Arabuluculuk / Tahkim", ""],
    "Amendments": ["Değişiklikler", ""],
    "APPENDIX \"A\" - SCOPE OF WORK": ["EK \"A\" - İŞ KAPSAMI", "ΠΑΡΑΡΤΗΜΑ \"A\" - ΠΕΔΙΟ ΕΡΓΑΣΙΑΣ"],
    "TOTAL COST BEFORE PROFIT": ["KAR ÖNCESİ TOPLAM MALİYET", ""],
    "PROFIT": ["KAR", ""],
    "VAT EXCLUDED SALES PRICE": ["KDV HARİÇ SATIŞ FİYATI", ""],
    "TOTAL SALES PRICE": ["TOPLAM SATIŞ FİYATI", ""],
    "TOTAL VAT": ["TOPLAM KDV", ""],
    "Subtotal (All Items)": ["Ara Toplam (Tüm Kalemler)", ""],
    "Total Overhead Cost": ["Toplam Genel Giderler", ""],
    "Total Waste Cost": ["Toplam Atık Maliyeti", ""],
    "Profile Analysis Details": ["Profil Analiz Detayları", ""],
    "Item": ["Kalem", ""],
    "Quantity": ["Miktar", ""],
    "Unit Price (€)": ["Birim Fiyat (€)", ""],
    "Total (€)": ["Toplam (€)", ""],
}
