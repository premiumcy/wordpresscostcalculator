# config.py
# Bu dosya, uygulamanın tüm sabitlerini ve yapılandırma sözlüklerini içerir.

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
    "brushed_grey_granite_countertops_price_per_m2_avg": 425.00,
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

# --- PDF Metinleri için Çeviri Sözlüğü ---
# Bu sözlük, PDF metinlerinin tek bir yerden yönetilmesini sağlar.
# Anahtar: İngilizce metin
# Değer: [İngilizce metin, Yunanca metin]
TRANSLATIONS = {
    # Genel Metinler
    "PREFABRICATED HOUSE PROPOSAL": ["PREFABRICATED HOUSE PROPOSAL", "ΠΡΟΤΑΣΗ ΠΡΟΚΑΤΑΣΚΕΥΑΣΜΕΝΟΥ ΣΠΙΤΙΟΥ"],
    "For": ["For", "Για"],
    "Company": ["Company", "Εταιρεία"],
    "Date": ["Date", "Ημερομηνία"],
    "CUSTOMER & PROJECT INFORMATION": ["CUSTOMER & PROJECT INFORMATION", "ΠΛΗΡΟΦΟΡΙΕΣ ΠΕΛΑΤΗ & ΕΡΓΟΥ"],
    "Room Configuration": ["Room Configuration", "Διαμόρφωση Δωματίου"],
    "Dimensions": ["Dimensions", "Διαστάσεις"],
    "Total Area": ["Total Area", "Συνολική Επιφάνεια"],
    "Structure Type": ["Structure Type", "Τύπος Κατασκευής"],
    "Name": ["Name", "Όνομα"],
    "Address": ["Address", "Διεύθυνση"],
    "Phone": ["Phone", "Τηλέφωνο"],
    "ID/Passport No": ["ID/Passport No", "Αρ. Ταυτότητας/Διαβατηρίου"],
    "TECHNICAL SPECIFICATIONS": ["TECHNICAL SPECIFICATIONS", "ΤΕΧΝΙΚΑ ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ"],
    "Construction Type": ["Construction Type", "Τύπος Κατασκευής"],
    "Steel Structure Details": ["Steel Structure Details", "Λεπτομέρειες Χαλύβδινης Κατασκευής"],
    "Interior Walls": ["Interior Walls", "Εσωτερικοί Τοίχοι"],
    "Roof": ["Roof", "Στέγη"],
    "Exterior Walls": ["Exterior Walls", "Εξωτερικοί Τοίχοι"],
    "Interior": ["Interior", "Εσωτερικό"],
    "Insulation": ["Insulation", "Μόνωση"],
    "Floor Covering": ["Floor Covering", "Δάπεδο"],
    "Floor Insulation": ["Floor Insulation", "Μόνωση Δαπέδου"],
    "Wall Insulation": ["Wall Insulation", "Μόνωση Τοίχου"],
    "Floor Insulation Materials": ["Floor Insulation Materials", "Υλικά Μόνωσης Δαπέδου"],
    "Openings": ["Openings", "Ανοίγματα"],
    "ADDITIONAL TECHNICAL FEATURES": ["ADDITIONAL TECHNICAL FEATURES", "ΠΡΟΣΘΕΤΑ ΤΕΧΝΙΚΑ ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ"],
    "Kitchen": ["Kitchen", "Κουζίνα"],
    "Kitchen Materials": ["Kitchen Materials", "Υλικά Κουζίνας"],
    "Shower/WC": ["Shower/WC", "Ντους/WC"],
    "Shower/WC Materials": ["Shower/WC Materials", "Υλικά Ντους/WC"],
    "Electrical": ["Electrical", "Ηλεκτρολογικά"],
    "Plumbing": ["Plumbing", "Υδραυλικά"],
    "Extra General Additions": ["Extra General Additions", "Έξτρα Γενικές Προσθήκες"],
    "Estimated Delivery": ["Estimated Delivery", "Εκτιμώμενη Παράδοση"],
    "business days": ["business days", "εργάσιμες ημέρες"],
    "CUSTOMER NOTES": ["CUSTOMER NOTES", "ΣΗΜΕΙΩΣΕΙΣ ΠΕΛΑΤΗ"],
    "PRICE & PAYMENT SCHEDULE": ["PRICE & PAYMENT SCHEDULE", "ΤΙΜΗ & ΠΡΟΓΡΑΜΜΑ ΠΛΗΡΩΜΩΝ"],
    "Main House Price": ["Main House Price", "Τιμή Κυρίως Σπιτιού"],
    "Solar System Price": ["Solar System Price", "Τιμή Ηλιακού Συστήματος"],
    "Aether Package Price": ["Aether Package Price", "Τιμή Πακέτου Aether"],
    "Extra Expenses": ["Extra Expenses", "Έξτρα Έξοδα"],
    "TOTAL PRICE": ["TOTAL PRICE", "ΣΥΝΟΛΙΚΗ ΤΙΜΗ"],
    "All prices are VAT included": ["All prices are VAT included", "Όλες οι τιμές περιλαμβάνουν ΦΠΑ."],
    "Our prefabricated living spaces have a 3-year warranty.": ["Our prefabricated living spaces have a 3-year warranty.", "Οι προκατασκευασμένοι χώροι διαβίωσης μας έχουν 3ετή εγγύηση."],
    "Main House Payment Plan": ["Main House Payment Plan", "Πρόγραμμα Πληρωμών Κυρίως Σπιτιού"],
    "Down Payment": ["Down Payment", "Προκαταβολή"],
    "Due upon contract signing": ["Due upon contract signing", "Με την υπογραφή της σύμβασης."],
    "1st Installment": ["1st Installment", "1η Δόση"],
    "Due upon completion of structure": ["Due upon completion of structure", "Με την ολοκλήρωση της κατασκευής."],
    "2nd Installment": ["2nd Installment", "2η Δόση"],
    "Due upon completion of interior works": ["Due upon completion of interior works", "Με την ολοκλήρωση των εσωτερικών εργασιών."],
    "Final Payment": ["Final Payment", "Τελική Εξόφληση"],
    "Due upon final delivery": ["Due upon final delivery", "Με την τελική παράδοση."],
    "SALES CONTRACT": ["SALES CONTRACT", ""],
    "Subject of the Agreement": ["Subject of the Agreement", ""],
    "Definitions": ["Definitions", ""],
    "Sales Price and Payment Terms": ["Sales Price and Payment Terms", ""],
    "Bank Details": ["Bank Details", ""],
    "Inspection of the Property and Defects": ["Inspection of the Property and Defects", ""],
    "Completion of the House": ["Completion of the House", ""],
    "Termination": ["Termination", ""],
    "Notifications": ["Notifications", ""],
    "Warranty and Defects liability": ["Warranty and Defects liability", ""],
    "Applicable Law": ["Applicable Law", ""],
    "Dispute Resolution - Mediation / Arbitration": ["Dispute Resolution - Mediation / Arbitration", ""],
    "Amendments": ["Amendments", ""],
    "APPENDIX \"A\" - SCOPE OF WORK": ["APPENDIX \"A\" - SCOPE OF WORK", "ΠΑΡΑΡΤΗΜΑ \"A\" - ΠΕΔΙΟ ΕΡΓΑΣΙΑΣ"],
    "TOTAL COST BEFORE PROFIT": ["TOTAL COST BEFORE PROFIT", ""],
    "PROFIT": ["PROFIT", ""],
    "VAT EXCLUDED SALES PRICE": ["VAT EXCLUDED SALES PRICE", ""],
    "TOTAL SALES PRICE": ["TOTAL SALES PRICE", ""],
    "TOTAL VAT": ["TOTAL VAT", ""],
    "Subtotal (All Items)": ["Subtotal (All Items)", ""],
    "Total Overhead Cost": ["Total Overhead Cost", ""],
    "Total Waste Cost": ["Total Waste Cost", ""],
    "Profile Analysis Details": ["Profile Analysis Details", ""],
    "Item": ["Item", ""],
    "Quantity": ["Quantity", ""],
    "Unit Price (€)": ["Unit Price (€)", ""],
    "Total (€)": ["Total (€)", ""],
}
