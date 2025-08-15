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

# --- Malzeme Bilgi Kalemleri (PDF'lerde açıklama için) ---
MATERIAL_INFO_ITEMS = {
    "steel_skeleton_info": clean_invisible_chars("Metal skeleton"),
    "protective_automotive_paint_info": clean_invisible_chars("Protective automotive paint"),
    "insulation_info": clean_invisible_chars("Insulation"),
    "60mm_eps_sandwich_panel_info": clean_invisible_chars("Standard 60mm EPS or Polyurethane Sandwich Panels (white)"),
    "100mm_eps_isothermal_panel_info": clean_invisible_chars("High-performance 100mm EPS or Polyurethane Isothermal Panels"),
    "galvanized_sheet_info": clean_invisible_chars("Galvanized sheet"),
    "plywood_osb_floor_panel_info": clean_invisible_chars("Plywood/OSB floor panel"),
    "12mm_laminate_parquet_info": clean_invisible_chars("12mm Laminate Flooring"),
    "induction_hob_info": clean_invisible_chars("Induction hob"),
    "electric_faucet_info": clean_invisible_chars("Electric faucet"),
    "kitchen_sink_info": clean_invisible_chars("Kitchen sink"),
    "fully_functional_bathroom_fixtures_info": clean_invisible_chars("Fully functional bathroom fixtures (toilet, sink, electric shower)"),
    "kitchen_bathroom_countertops_info": clean_invisible_chars("Kitchen and bathroom countertops"),
    "treated_pine_floor_info": clean_invisible_chars("Reclaimed Pine Flooring (with Terrace Option)"),
    "porcelain_tiles_info": clean_invisible_chars("Porcelain Tiles"),
    "concrete_panel_floor_info": clean_invisible_chars("Concrete Panel Floor"),
    "premium_faucets_info": clean_invisible_chars("Premium Faucets (e.g. Hansgrohe)"),
    "integrated_refrigerator_info": clean_invisible_chars("Integrated Refrigerator"),
    "integrated_custom_furniture_info": clean_invisible_chars("Integrated Designer Furniture (high-quality MDF/lacquer)"),
    "italian_sofa_info": clean_invisible_chars("Italian Sofa"),
    "inclass_chairs_info": clean_invisible_chars("Inclass Chairs"),
    "smart_home_systems_info": clean_invisible_chars("Smart Home Systems"),
    "advanced_security_camera_pre_installation_info": clean_invisible_chars("Advanced security camera pre-installation"),
    "exterior_wood_cladding_lambiri_info": clean_invisible_chars("Exterior wood cladding - Wainscoting"),
    "brushed_grey_granite_countertops_info": clean_invisible_chars("Brushed Gray Kale Granite Kitchen/Bathroom Countertops"),
    "knauf_aquapanel_gypsum_board_info": clean_invisible_chars("Knauf Aquapanel Plasterboard"),
    "eps_styrofoam_info": clean_invisible_chars("EPS STYROFOAM"),
    "knauf_mineralplus_insulation_info": clean_invisible_chars("Knauf MineralPlus Insulation"),
    "knauf_guardex_gypsum_board_info": clean_invisible_chars("Knauf Guardex Plasterboard"),
    "satin_plaster_paint_info": clean_invisible_chars("Satin plaster and paint"),
    "supportive_headboard_furniture_info": clean_invisible_chars("Bedheadboard with Supportive Furniture"),

    "electrical_cable_info": clean_invisible_chars("Electrical Cables (3x2.5 mm², 3x1.5 mm²)"),
    "electrical_conduits_info": clean_invisible_chars("Spiral Pipes and Ducts for Wiring"),
    "electrical_junction_boxes_info": clean_invisible_chars("Junction Boxes"),
    "electrical_distribution_board_info": clean_invisible_chars("Fuse Box (Distribution Board)"),
    "electrical_circuit_breakers_info": clean_invisible_chars("Fuses & Residual Current Circuit Breakers"),
    "electrical_sockets_switches_info": clean_invisible_chars("Sockets and Switches"),
    "electrical_lighting_fixtures_info": clean_invisible_chars("Indoor Lighting Fixtures (LED Spotlights / Ceiling Lights)"),
    "electrical_grounding_info": clean_invisible_chars("Grounding System Components"),

    "plumbing_pprc_pipes_info": clean_invisible_chars("Hot/Cold PPRC Pipes for Water"),
    "plumbing_faucets_info": clean_invisible_chars("Kitchen and Bathroom Faucets"),
    "plumbing_shower_mixer_info": clean_invisible_chars("Shower Head and Faucet"),
    "plumbing_valves_info": clean_invisible_chars("Main and Intermediate Shut-Off Valves"),
    "plumbing_pvc_pipes_info": clean_invisible_chars("PVC Drain Pipes (50mm / 100mm)"),
    "plumbing_siphons_info": clean_invisible_chars("Siphons and floor drains"),

    "wc_toilet_bowl_info": clean_invisible_chars("Toilet & Cistern"),
    "wc_washbasin_info": clean_invisible_chars("Hand Wash Sink & Faucet"),
    "wc_towel_rail_info": clean_invisible_chars("Towel Rail"),
    "wc_mirror_info": clean_invisible_chars("Mirror"),
    "wc_accessories_info": clean_invisible_chars("Bathroom Accessories"),
    "wc_shower_unit_info": clean_invisible_chars("Shower Unit (Shower Head and Faucet)"),

    "kitchen_mdf_info": clean_invisible_chars("Glossy White MDF Material"),
    "kitchen_cabinets_info": clean_invisible_chars("Custom-Made Kitchen Cabinets (custom sizes)"),
    "kitchen_countertop_info": clean_invisible_chars("Countertop (Laminate or specified equivalent)"),
    "kitchen_sink_faucet_info": clean_invisible_chars("Sink and Faucet"),
    "aether_package_smart_home_info": clean_invisible_chars("Smart Home Systems (Aether Package)"),
    "aether_package_white_goods_info": clean_invisible_chars("White Goods (Aether Package)"),
    "aether_package_sofa_info": clean_invisible_chars("Sofa (Aether Package)"),
    "aether_package_security_camera_info": clean_invisible_chars("Security Camera (Aether Package)"),
    "aether_package_exterior_cladding_info": clean_invisible_chars("Exterior Cladding (Knauf Aquapanel) (Aether Package)"),
    "aether_package_bedroom_set_info": clean_invisible_chars("Bedroom Set (Aether Package)"),
    "aether_package_terrace_flooring_info": clean_invisible_chars("Terrace Laminate Wood Flooring (Aether Package)"),
    "aether_package_porcelain_tile_info": clean_invisible_chars("Porcelain Tiles (Aether Pack)"),
    "aether_package_concrete_panel_floor_info": clean_invisible_chars("Concrete Panel Floor (Aether Package)"),
    "aether_package_premium_faucets_info": clean_invisible_chars("Premium Batteries (Aether Pack)"),
    "aether_package_designer_furniture_info": clean_invisible_chars("Designer Furniture (Aether Pack)"),
    "aether_package_italian_sofa_info": clean_invisible_chars("Italian Sofa (Aether Package)"),
    "aether_package_inclass_chairs_info": clean_invisible_chars("Inclass Chairs (Aether Pack)"),
    "aether_package_exterior_wood_cladding_info": clean_invisible_chars("Exterior Wood Cladding (Wallpaper) (Aether Package)"),
    "aether_package_brushed_grey_granite_countertops_info": clean_invisible_chars("Brushed Gray Kale Granite Kitchen/Bathroom Countertops (Aether Package)"),
}
