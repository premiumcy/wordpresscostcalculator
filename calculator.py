# calculator.py
# Bu dosya, maliyet hesaplama mantığını içerir ve API'den gelen verilere göre çalışır.

import math
import pandas as pd
import re
from .config import FIYATLAR, MONTHLY_ACCOUNTING_EXPENSES, MONTHLY_OFFICE_RENT, FIRE_RATE, VAT_RATE, MATERIAL_INFO_ITEMS, OSB_PANEL_AREA_M2, GYPSUM_BOARD_UNIT_AREA_M2, GLASS_WOOL_M2_PER_PACKET
from .utils import calculate_rounded_up_cost, calculate_area

def calculate_costs_detailed(project_inputs, areas):
    """
    Proje girdilerine ve alanlara göre tüm maliyetleri detaylı olarak hesaplar.
    Maliyet dökümü (DataFrame), finansal özet ve diğer anahtar sonuçları döndürür.
    Bu fonksiyon, API'den gelen 'project_details' sözlüğünü kullanır.
    """
    floor_area = areas["floor"]
    wall_area = areas["wall"]
    roof_area = areas["roof"]
    is_two_story = project_inputs.get('is_two_story', False)
    
    costs = []
    profile_analysis_details = []
    
    # --- 1. Yapısal Maliyetler (Çelik, Kaynak, Bağlantı Elemanları) ---
    # Koruyucu boya maliyeti 0 olsa bile bilgi olarak eklenir.
    costs.append({'Item': MATERIAL_INFO_ITEMS['protective_automotive_paint_info'], 'Quantity': 'N/A', 'Unit Price (€)': 0.0, 'Total (€)': 0.0})

    if project_inputs['structure_type'] == 'Light Steel':
        manual_profiles = {
            "100x100x3": project_inputs.get('profile_100x100_count', 0),
            "100x50x3": project_inputs.get('profile_100x50_count', 0),
            "40x60x2": project_inputs.get('profile_40x60_count', 0),
            "50x50x2": project_inputs.get('profile_50x50_count', 0),
            "120x60x5mm": project_inputs.get('profile_120x60x5mm_count', 0),
            "HEA160": project_inputs.get('profile_HEA160_count', 0),
        }
        
        has_manual_steel_profiles = sum(manual_profiles.values()) > 0
        
        if has_manual_steel_profiles:
            for p_type, p_count in manual_profiles.items():
                if p_count > 0:
                    price_key = f"steel_profile_{p_type.replace('x', '_').lower()}"
                    cost_per_piece = FIYATLAR.get(price_key, 0.0)
                    total_cost = p_count * cost_per_piece
                    costs.append({'Item': f"{MATERIAL_INFO_ITEMS['steel_skeleton_info']} ({p_type})", 'Quantity': f"{p_count} adet", 'Unit Price (€)': cost_per_piece, 'Total (€)': calculate_rounded_up_cost(total_cost)})
                    profile_analysis_details.append({'Item': p_type, 'Quantity': p_count, 'Unit Price (€)': cost_per_piece, 'Total (€)': calculate_rounded_up_cost(total_cost)})
        else: # Otomatik hesaplama
            auto_100x100_count = math.ceil(floor_area * (12 / 27.0))
            auto_50x50_count = math.ceil(floor_area * (6 / 27.0))
            if auto_100x100_count > 0:
                cost = auto_100x100_count * FIYATLAR['steel_profile_100x100x3']
                costs.append({'Item': MATERIAL_INFO_ITEMS['steel_skeleton_info'] + ' (100x100x3) (Auto)', 'Quantity': f"{auto_100x100_count} adet", 'Unit Price (€)': FIYATLAR['steel_profile_100x100x3'], 'Total (€)': calculate_rounded_up_cost(cost)})
                profile_analysis_details.append({'Item': '100x100x3 (Auto)', 'Quantity': auto_100x100_count, 'Unit Price (€)': FIYATLAR['steel_profile_100x100x3'], 'Total (€)': calculate_rounded_up_cost(cost)})
            if auto_50x50_count > 0:
                cost = auto_50x50_count * FIYATLAR['steel_profile_50x50x2']
                costs.append({'Item': MATERIAL_INFO_ITEMS['steel_skeleton_info'] + ' (50x50x2) (Auto)', 'Quantity': f"{auto_50x50_count} adet", 'Unit Price (€)': FIYATLAR['steel_profile_50x50x2'], 'Total (€)': calculate_rounded_up_cost(cost)})
                profile_analysis_details.append({'Item': '50x50x2 (Auto)', 'Quantity': auto_50x50_count, 'Unit Price (€)': FIYATLAR['steel_profile_50x50x2'], 'Total (€)': calculate_rounded_up_cost(cost)})
    else: # Heavy Steel
        heavy_steel_cost = floor_area * FIYATLAR['heavy_steel_m2']
        costs.append({'Item': 'Heavy Steel Structure', 'Quantity': f"{floor_area:.2f} m²", 'Unit Price (€)': FIYATLAR['heavy_steel_m2'], 'Total (€)': calculate_rounded_up_cost(heavy_steel_cost)})
        profile_analysis_details.append({'Item': 'Heavy Steel Structure', 'Quantity': f"{floor_area:.2f} m²", 'Unit Price (€)': FIYATLAR['heavy_steel_m2'], 'Total (€)': calculate_rounded_up_cost(heavy_steel_cost)})
        
    welding_price_key = 'welding_labor_m2_standard' if 'Standard' in project_inputs['welding_type'] else 'welding_labor_m2_trmontaj'
    welding_price = FIYATLAR[welding_price_key]
    welding_cost = floor_area * welding_price
    costs.append({'Item': f"Steel Welding Labor ({project_inputs['welding_type'].split(' ')[0]})", 'Quantity': f"{floor_area:.2f} m²", 'Unit Price (€)': welding_price, 'Total (€)': calculate_rounded_up_cost(welding_cost)})

    connection_elements_cost = floor_area * FIYATLAR['connection_element_m2']
    costs.append({'Item': 'Connection Elements', 'Quantity': f"{floor_area:.2f} m²", 'Unit Price (€)': FIYATLAR['connection_element_m2'], 'Total (€)': calculate_rounded_up_cost(connection_elements_cost)})

    # --- 2. Duvar ve Çatı Maliyetleri (Panel, Alçıpan, Yalıtım) ---
    panel_area = wall_area + roof_area
    panel_price_key = '100mm_eps_isothermal_panel_unit_price' if project_inputs.get('aether_package_choice') == 'Aether Living | Loft Elite (LUXURY)' else 'sandwich_panel_m2'
    panel_info_key = '100mm_eps_isothermal_panel_info' if project_inputs.get('aether_package_choice') == 'Aether Living | Loft Elite (LUXURY)' else '60mm_eps_sandwich_panel_info'
    panel_cost = panel_area * FIYATLAR[panel_price_key]
    costs.append({'Item': MATERIAL_INFO_ITEMS[panel_info_key], 'Quantity': f"{panel_area:.2f} m²", 'Unit Price (€)': FIYATLAR[panel_price_key], 'Total (€)': calculate_rounded_up_cost(panel_cost)})
    
    panel_labor_cost = panel_area * FIYATLAR['panel_assembly_labor_m2']
    costs.append({'Item': 'Panel Assembly Labor', 'Quantity': f"{panel_area:.2f} m²", 'Unit Price (€)': FIYATLAR['panel_assembly_labor_m2'], 'Total (€)': calculate_rounded_up_cost(panel_labor_cost)})
    
    if project_inputs.get('facade_sandwich_panel_option', False) and project_inputs['structure_type'] == 'Heavy Steel':
        facade_panel_cost = wall_area * FIYATLAR['sandwich_panel_m2']
        costs.append({'Item': 'Facade (Sandwich Panel)', 'Quantity': f"{wall_area:.2f} m²", 'Unit Price (€)': FIYATLAR['sandwich_panel_m2'], 'Total (€)': calculate_rounded_up_cost(facade_panel_cost)})

    plasterboard_total_area = 0
    if project_inputs.get('plasterboard_interior_option', False):
        plasterboard_total_area = wall_area
    elif project_inputs.get('plasterboard_all_option', False):
        plasterboard_total_area = wall_area * 2

    if plasterboard_total_area > 0:
        costs.append({'Item': MATERIAL_INFO_ITEMS['satin_plaster_paint_info'], 'Quantity': 'N/A', 'Unit Price (€)': 0.0, 'Total (€)': 0.0})
        plasterboard_material_cost = plasterboard_total_area * FIYATLAR['plasterboard_material_m2']
        plasterboard_labor_cost = plasterboard_total_area * FIYATLAR['plasterboard_labor_m2_avg']
        costs.append({'Item': 'Plasterboard Material', 'Quantity': f'{plasterboard_total_area:.2f} m²', 'Unit Price (€)': FIYATLAR['plasterboard_material_m2'], 'Total (€)': calculate_rounded_up_cost(plasterboard_material_cost)})
        costs.append({'Item': 'Plasterboard Labor', 'Quantity': f'{plasterboard_total_area:.2f} m²', 'Unit Price (€)': FIYATLAR['plasterboard_labor_m2_avg'], 'Total (€)': calculate_rounded_up_cost(plasterboard_labor_cost)})
        profile_cdx400_count = math.ceil(plasterboard_total_area / 3)
        profile_ud_count = math.ceil(plasterboard_total_area / 5)
        screws_count = math.ceil(plasterboard_total_area * 10)
        costs.append({'Item': 'CDX400 Profil', 'Quantity': f'{profile_cdx400_count} adet', 'Unit Price (€)': FIYATLAR['cdx400_material_price'], 'Total (€)': calculate_rounded_up_cost(profile_cdx400_count * FIYATLAR['cdx400_material_price'])})
        costs.append({'Item': 'UD Profil', 'Quantity': f'{profile_ud_count} adet', 'Unit Price (€)': FIYATLAR['ud_material_price'], 'Total (€)': calculate_rounded_up_cost(profile_ud_count * FIYATLAR['ud_material_price'])})
        costs.append({'Item': 'TN25 Screws', 'Quantity': f'{screws_count} adet', 'Unit Price (€)': FIYATLAR['tn25_screws_price_per_unit'], 'Total (€)': calculate_rounded_up_cost(screws_count * FIYATLAR['tn25_screws_price_per_unit'])})

    if project_inputs.get('osb_inner_wall_option', False):
        osb_inner_wall_pieces = math.ceil(wall_area / OSB_PANEL_AREA_M2)
        osb_cost = osb_inner_wall_pieces * FIYATLAR['osb_piece']
        costs.append({'Item': 'Inner Wall OSB Material', 'Quantity': f'{osb_inner_wall_pieces} adet', 'Unit Price (€)': FIYATLAR['osb_piece'], 'Total (€)': calculate_rounded_up_cost(osb_cost)})

    if project_inputs.get('insulation_wall', False) and project_inputs.get('insulation_material_type', '') != 'Yalıtım Yapılmayacak':
        if project_inputs['insulation_material_type'] == 'Stone Wool':
            insulation_cost = wall_area * FIYATLAR['otb_stone_wool_price']
            costs.append({'Item': f"Wall Insulation ({project_inputs['insulation_material_type']})", 'Quantity': f'{wall_area:.2f} m²', 'Unit Price (€)': FIYATLAR['otb_stone_wool_price'], 'Total (€)': calculate_rounded_up_cost(insulation_cost)})
        elif project_inputs['insulation_material_type'] == 'Glass Wool':
            packets_needed = math.ceil(wall_area / GLASS_WOOL_M2_PER_PACKET)
            insulation_cost = packets_needed * FIYATLAR['glass_wool_5cm_packet_price']
            costs.append({'Item': f"Wall Insulation ({project_inputs['insulation_material_type']})", 'Quantity': f'{packets_needed} paket', 'Unit Price (€)': FIYATLAR['glass_wool_5cm_packet_price'], 'Total (€)': calculate_rounded_up_cost(insulation_cost)})

    if project_inputs.get('exterior_cladding_m2_option', False) and project_inputs.get('exterior_cladding_m2_val', 0) > 0:
        exterior_cladding_cost = project_inputs['exterior_cladding_m2_val'] * FIYATLAR['exterior_cladding_price_per_m2']
        costs.append({'Item': MATERIAL_INFO_ITEMS['knauf_aquapanel_gypsum_board_info'] + ' (Cladding)', 'Quantity': f"{project_inputs['exterior_cladding_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['exterior_cladding_price_per_m2'], 'Total (€)': calculate_rounded_up_cost(exterior_cladding_cost)})
        costs.append({'Item': MATERIAL_INFO_ITEMS['eps_styrofoam_info'], 'Quantity': 'N/A', 'Unit Price (€)': 0.0, 'Total (€)': 0.0})
        costs.append({'Item': MATERIAL_INFO_ITEMS['knauf_mineralplus_insulation_info'], 'Quantity': 'N/A', 'Unit Price (€)': 0.0, 'Total (€)': 0.0})
    
    if project_inputs.get('exterior_wood_cladding_m2_option', False) and project_inputs.get('exterior_wood_cladding_m2_val', 0) > 0:
        wood_cladding_cost = project_inputs['exterior_wood_cladding_m2_val'] * FIYATLAR['exterior_wood_cladding_m2_price']
        costs.append({'Item': MATERIAL_INFO_ITEMS['exterior_wood_cladding_lambiri_info'], 'Quantity': f"{project_inputs['exterior_wood_cladding_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['exterior_wood_cladding_m2_price'], 'Total (€)': calculate_rounded_up_cost(wood_cladding_cost)})

    # --- 3. Zemin Maliyetleri (Yalıtım ve Kaplama) ---
    if project_inputs.get('insulation_floor', False):
        floor_insulation_cost = floor_area * FIYATLAR['insulation_per_m2']
        costs.append({'Item': 'Floor Insulation', 'Quantity': f"{floor_area:.2f} m²", 'Unit Price (€)': FIYATLAR['insulation_per_m2'], 'Total (€)': calculate_rounded_up_cost(floor_insulation_cost)})
        
    if project_inputs.get('floor_covering', '') == 'Laminate Parquet':
        if project_inputs.get('skirting_length_val', 0) > 0:
            costs.append({'Item': 'Skirting', 'Quantity': f"{project_inputs['skirting_length_val']:.2f} m", 'Unit Price (€)': FIYATLAR['skirting_meter_price'], 'Total (€)': calculate_rounded_up_cost(project_inputs['skirting_length_val'] * FIYATLAR['skirting_meter_price'])})
        if project_inputs.get('laminate_flooring_m2_val', 0) > 0:
            costs.append({'Item': 'Laminate Flooring 12mm', 'Quantity': f"{project_inputs['laminate_flooring_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['laminate_flooring_m2_price'], 'Total (€)': calculate_rounded_up_cost(project_inputs['laminate_flooring_m2_val'] * FIYATLAR['laminate_flooring_m2_price'])})
        if project_inputs.get('under_parquet_mat_m2_val', 0) > 0:
            costs.append({'Item': 'Under Parquet Mat 4mm', 'Quantity': f"{project_inputs['under_parquet_mat_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['under_parquet_mat_m2_price'], 'Total (€)': calculate_rounded_up_cost(project_inputs['under_parquet_mat_m2_val'] * FIYATLAR['under_parquet_mat_m2_price'])})
        if project_inputs.get('osb2_18mm_count_val', 0) > 0:
            costs.append({'Item': 'OSB2 18mm Panel', 'Quantity': f"{project_inputs['osb2_18mm_count_val']} adet", 'Unit Price (€)': FIYATLAR['osb2_18mm_piece_price'], 'Total (€)': calculate_rounded_up_cost(project_inputs['osb2_18mm_count_val'] * FIYATLAR['osb2_18mm_piece_price'])})
        if project_inputs.get('galvanized_sheet_m2_val', 0) > 0:
            costs.append({'Item': '5mm Galvanized Sheet', 'Quantity': f"{project_inputs['galvanized_sheet_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['galvanized_sheet_m2_price'], 'Total (€)': calculate_rounded_up_cost(project_inputs['galvanized_sheet_m2_val'] * FIYATLAR['galvanized_sheet_m2_price'])})
        # Plywood döşeme işçiliği (toplam zemin alanı için)
        plywood_flooring_labor_cost = floor_area * FIYATLAR['plywood_flooring_labor_m2']
        costs.append({'Item': 'Plywood Flooring Labor', 'Quantity': f"{floor_area:.2f} m²", 'Unit Price (€)': FIYATLAR['plywood_flooring_labor_m2'], 'Total (€)': calculate_rounded_up_cost(plywood_flooring_labor_cost)})
    
    elif project_inputs.get('floor_covering', '') == 'Ceramic':
        ceramic_floor_cost = floor_area * (FIYATLAR['wc_ceramic_m2_material'] + FIYATLAR['wc_ceramic_m2_labor'])
        costs.append({'Item': 'Seramik Zemin Kaplaması', 'Quantity': f'{floor_area:.2f} m²', 'Unit Price (€)': (FIYATLAR['wc_ceramic_m2_material'] + FIYATLAR['wc_ceramic_m2_labor']), 'Total (€)': calculate_rounded_up_cost(ceramic_floor_cost)})

    if project_inputs.get('concrete_panel_floor_option', False) and project_inputs.get('concrete_panel_floor_m2_val', 0) > 0:
        concrete_panel_cost = project_inputs['concrete_panel_floor_m2_val'] * FIYATLAR['concrete_panel_floor_price_per_m2']
        costs.append({'Item': MATERIAL_INFO_ITEMS['concrete_panel_floor_info'], 'Quantity': f"{project_inputs['concrete_panel_floor_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['concrete_panel_floor_price_per_m2'], 'Total (€)': calculate_rounded_up_cost(concrete_panel_cost)})

    if project_inputs.get('terrace_laminated_wood_flooring_option', False) and project_inputs.get('terrace_laminated_wood_flooring_m2_val', 0) > 0:
        terrace_laminated_cost = project_inputs['terrace_laminated_wood_flooring_m2_val'] * FIYATLAR['terrace_laminated_wood_flooring_price_per_m2']
        costs.append({'Item': MATERIAL_INFO_ITEMS['treated_pine_floor_info'], 'Quantity': f"{project_inputs['terrace_laminated_wood_flooring_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['terrace_laminated_wood_flooring_price_per_m2'], 'Total (€)': calculate_rounded_up_cost(terrace_laminated_cost)})

    if project_inputs.get('porcelain_tiles_option', False) and project_inputs.get('porcelain_tiles_m2_val', 0) > 0:
        porcelain_tiles_cost = project_inputs['porcelain_tiles_m2_val'] * (FIYATLAR['wc_ceramic_m2_material'] + FIYATLAR['wc_ceramic_m2_labor'])
        costs.append({'Item': MATERIAL_INFO_ITEMS['porcelain_tiles_info'], 'Quantity': f"{project_inputs['porcelain_tiles_m2_val']:.2f} m²", 'Unit Price (€)': (FIYATLAR['wc_ceramic_m2_material'] + FIYATLAR['wc_ceramic_m2_labor']), 'Total (€)': calculate_rounded_up_cost(porcelain_tiles_cost)})
        
    # --- 4. Doğramalar (Pencere ve Kapılar) ---
    window_count = project_inputs.get('window_count', 0)
    door_count = project_inputs.get('door_count', 0)
    sliding_door_count = project_inputs.get('sliding_door_count', 0)
    wc_window_count = project_inputs.get('wc_window_count', 0)
    wc_sliding_door_count = project_inputs.get('wc_sliding_door_count', 0)
    
    if window_count > 0:
        window_cost = window_count * FIYATLAR['aluminum_window_piece']
        costs.append({'Item': f"Window ({project_inputs['window_size_val']})", 'Quantity': window_count, 'Unit Price (€)': FIYATLAR['aluminum_window_piece'], 'Total (€)': calculate_rounded_up_cost(window_cost)})
    
    if sliding_door_count > 0:
        sliding_door_cost = sliding_door_count * FIYATLAR['sliding_glass_door_piece']
        costs.append({'Item': f"Sliding Glass Door ({project_inputs['sliding_door_size_val']})", 'Quantity': sliding_door_count, 'Unit Price (€)': FIYATLAR['sliding_glass_door_piece'], 'Total (€)': calculate_rounded_up_cost(sliding_door_cost)})

    if wc_window_count > 0:
        wc_window_cost = wc_window_count * FIYATLAR['wc_window_piece']
        costs.append({'Item': f"WC Window ({project_inputs['wc_window_size_val']})", 'Quantity': wc_window_count, 'Unit Price (€)': FIYATLAR['wc_window_piece'], 'Total (€)': calculate_rounded_up_cost(wc_window_cost)})

    if wc_sliding_door_count > 0:
        wc_sliding_door_cost = wc_sliding_door_count * FIYATLAR['wc_sliding_door_piece']
        costs.append({'Item': f"WC Sliding Door ({project_inputs['wc_sliding_door_size_val']})", 'Quantity': wc_sliding_door_count, 'Unit Price (€)': FIYATLAR['wc_sliding_door_piece'], 'Total (€)': calculate_rounded_up_cost(wc_sliding_door_cost)})
    
    if door_count > 0:
        door_cost = door_count * FIYATLAR['door_piece']
        costs.append({'Item': f"Door ({project_inputs['door_size_val']})", 'Quantity': door_count, 'Unit Price (€)': FIYATLAR['door_piece'], 'Total (€)': calculate_rounded_up_cost(door_cost)})
    
    total_doors_windows = window_count + sliding_door_count + wc_window_count + wc_sliding_door_count + door_count
    if total_doors_windows > 0:
        door_window_assembly_cost = total_doors_windows * FIYATLAR['door_window_assembly_labor_piece']
        costs.append({'Item': 'Door/Window Assembly Labor', 'Quantity': f"{total_doors_windows} adet", 'Unit Price (€)': FIYATLAR['door_window_assembly_labor_piece'], 'Total (€)': calculate_rounded_up_cost(door_window_assembly_cost)})

    # --- 5. Mutfak ve Banyo Tesisatları ---
    kitchen_cost_calc = 0.0
    kitchen_type_display_en_gr = 'No Kitchen'
    kitchen_type_display_tr = 'Mutfak Yok'
    kitchen_included_in_calc = False

    if project_inputs['kitchen_choice'] == 'Standard Kitchen':
        kitchen_cost_calc = FIYATLAR['kitchen_installation_standard_piece']
        kitchen_type_display_en_gr = "Yes (Standard)"
        kitchen_type_display_tr = "Var (Standart)"
        kitchen_included_in_calc = True
        costs.append({'Item': f"Kitchen ({kitchen_type_display_en_gr.split('(')[0].strip()})", 'Quantity': '1 adet', 'Unit Price (€)': FIYATLAR['kitchen_installation_standard_piece'], 'Total (€)': calculate_rounded_up_cost(kitchen_cost_calc)})
    elif project_inputs['kitchen_choice'] == 'Special Design Kitchen':
        kitchen_cost_calc = FIYATLAR['kitchen_installation_special_piece']
        kitchen_type_display_en_gr = "Yes (Special Design)"
        kitchen_type_display_tr = "Var (Özel Tasarım)"
        kitchen_included_in_calc = True
        costs.append({'Item': f"Kitchen ({kitchen_type_display_en_gr.split('(')[0].strip()})", 'Quantity': '1 adet', 'Unit Price (€)': FIYATLAR['kitchen_installation_special_piece'], 'Total (€)': calculate_rounded_up_cost(kitchen_cost_calc)})
        
    if project_inputs.get('shower_wc', False):
        shower_wc_cost = FIYATLAR['shower_wc_installation_piece']
        costs.append({'Item': 'Shower/WC Installation', 'Quantity': '1', 'Unit Price (€)': FIYATLAR['shower_wc_installation_piece'], 'Total (€)': calculate_rounded_up_cost(shower_wc_cost)})
        if project_inputs.get('wc_ceramic', False) and project_inputs.get('wc_ceramic_area', 0) > 0:
            wc_ceramic_total_cost = project_inputs['wc_ceramic_area'] * (FIYATLAR['wc_ceramic_m2_material'] + FIYATLAR['wc_ceramic_m2_labor'])
            costs.append({'Item': 'WC Ceramic Material & Labor', 'Quantity': f'{project_inputs["wc_ceramic_area"]:.2f} m²', 'Unit Price (€)': (FIYATLAR['wc_ceramic_m2_material'] + FIYATLAR['wc_ceramic_m2_labor']), 'Total (€)': calculate_rounded_up_cost(wc_ceramic_total_cost)})

    if project_inputs.get('electrical', False):
        electrical_cost = floor_area * FIYATLAR['electrical_per_m2']
        costs.append({'Item': 'Electrical Installation', 'Quantity': f"{floor_area:.2f} m²", 'Unit Price (€)': FIYATLAR['electrical_per_m2'], 'Total (€)': calculate_rounded_up_cost(electrical_cost)})

    if project_inputs.get('plumbing', False):
        plumbing_cost = floor_area * FIYATLAR['plumbing_per_m2']
        costs.append({'Item': 'Plumbing Installation', 'Quantity': f"{floor_area:.2f} m²", 'Unit Price (€)': FIYATLAR['plumbing_per_m2'], 'Total (€)': calculate_rounded_up_cost(plumbing_cost)})

    if project_inputs.get('transportation', False):
        costs.append({'Item': 'Transportation', 'Quantity': '1', 'Unit Price (€)': FIYATLAR['transportation'], 'Total (€)': calculate_rounded_up_cost(FIYATLAR['transportation'])})

    if project_inputs.get('heating', False):
        total_heating_cost = floor_area * FIYATLAR['floor_heating_m2']
        costs.append({'Item': 'Floor Heating System', 'Quantity': f'{floor_area:.2f} m²', 'Unit Price (€)': FIYATLAR['floor_heating_m2'], 'Total (€)': calculate_rounded_up_cost(total_heating_cost)})

    solar_cost = 0.0
    if project_inputs.get('solar', False):
        solar_cost = calculate_rounded_up_cost(project_inputs['solar_kw'] * FIYATLAR['solar_per_kw'])
        costs.append({'Item': f'Solar Energy System ({project_inputs["solar_kw"]} kW)', 'Quantity': 1, 'Unit Price (€)': FIYATLAR['solar_per_kw'], 'Total (€)': solar_cost})

    if project_inputs.get('wheeled_trailer', False) and project_inputs.get('wheeled_trailer_price', 0) > 0:
        trailer_price = calculate_rounded_up_cost(project_inputs['wheeled_trailer_price'])
        costs.append({'Item': 'Wheeled Trailer', 'Quantity': '1', 'Unit Price (€)': trailer_price, 'Total (€)': trailer_price})

    # İki katlı yapı için merdiven maliyeti
    if is_two_story:
        staircase_cost = FIYATLAR['staircase_cost']
        costs.append({'Item': 'Internal Staircase', 'Quantity': '1', 'Unit Price (€)': staircase_cost, 'Total (€)': calculate_rounded_up_cost(staircase_cost)})

    # --- 6. Aether Living Ek Opsiyonları ---
    aether_package_cost = 0.0
    if project_inputs.get('aether_package_choice') != 'None':
        # Buradaki maliyetler pakete dahilse 0 olarak eklenir, sadece bilgi içindir.
        # Toplam paket fiyatı aşağıda tek seferde eklenecektir.
        aether_package_cost = FIYATLAR.get('aether_package_cost', 0.0)
        costs.append({'Item': f'Aether Package ({project_inputs["aether_package_choice"]})', 'Quantity': '1', 'Unit Price (€)': aether_package_cost, 'Total (€)': aether_package_cost})
        
        # Ek donanımları da maliyet dökümüne ekleyelim (sabit fiyatları FIYATLAR'da mevcut)
        if project_inputs.get('bedroom_set_option', False):
            costs.append({'Item': MATERIAL_INFO_ITEMS['supportive_headboard_furniture_info'], 'Quantity': 1, 'Unit Price (€)': FIYATLAR['bedroom_set_total_price'], 'Total (€)': calculate_rounded_up_cost(FIYATLAR['bedroom_set_total_price'])})
        if project_inputs.get('brushed_granite_countertops_option', False) and project_inputs.get('brushed_granite_countertops_m2_val', 0) > 0:
            granite_cost = project_inputs['brushed_granite_countertops_m2_val'] * FIYATLAR['brushed_grey_granite_countertops_price_m2_avg']
            costs.append({'Item': MATERIAL_INFO_ITEMS['brushed_grey_granite_countertops_info'], 'Quantity': f"{project_inputs['brushed_granite_countertops_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['brushed_grey_granite_countertops_price_m2_avg'], 'Total (€)': calculate_rounded_up_cost(granite_cost)})
        if project_inputs.get('exterior_cladding_m2_option', False) and project_inputs.get('exterior_cladding_m2_val', 0) > 0:
            cladding_cost = project_inputs['exterior_cladding_m2_val'] * FIYATLAR['exterior_cladding_price_per_m2']
            costs.append({'Item': MATERIAL_INFO_ITEMS['knauf_aquapanel_gypsum_board_info'], 'Quantity': f"{project_inputs['exterior_cladding_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['exterior_cladding_price_per_m2'], 'Total (€)': calculate_rounded_up_cost(cladding_cost)})
        if project_inputs.get('porcelain_tiles_option', False) and project_inputs.get('porcelain_tiles_m2_val', 0) > 0:
            porcelain_tiles_cost = project_inputs['porcelain_tiles_m2_val'] * (FIYATLAR['wc_ceramic_m2_material'] + FIYATLAR['wc_ceramic_m2_labor'])
            costs.append({'Item': MATERIAL_INFO_ITEMS['porcelain_tiles_info'], 'Quantity': f"{project_inputs['porcelain_tiles_m2_val']:.2f} m²", 'Unit Price (€)': (FIYATLAR['wc_ceramic_m2_material'] + FIYATLAR['wc_ceramic_m2_labor']), 'Total (€)': calculate_rounded_up_cost(porcelain_tiles_cost)})
        if project_inputs.get('concrete_panel_floor_option', False) and project_inputs.get('concrete_panel_floor_m2_val', 0) > 0:
            concrete_panel_cost = project_inputs['concrete_panel_floor_m2_val'] * FIYATLAR['concrete_panel_floor_price_per_m2']
            costs.append({'Item': MATERIAL_INFO_ITEMS['concrete_panel_floor_info'], 'Quantity': f"{project_inputs['concrete_panel_floor_m2_val']:.2f} m²", 'Unit Price (€)': FIYATLAR['concrete_panel_floor_price_per_m2'], 'Total (€)': calculate_rounded_up_cost(concrete_panel_cost)})
        #... Diğer tüm Aether Living opsiyonları da buraya eklenecek ...

    # --- 7. Finansal Hesaplamalar ---
    material_subtotal = sum(item['Total (€)'] for item in costs if 'Total (€)' in item)
    waste_cost = calculate_rounded_up_cost(material_subtotal * FIRE_RATE)
    overhead_cost = MONTHLY_ACCOUNTING_EXPENSES + MONTHLY_OFFICE_RENT

    # Ana Ev Fiyatı hesaplaması (solar ve aether paket maliyeti hariç)
    house_subtotal_base = sum([item['Total (€)'] for item in costs if not any(keyword in item['Item'] for keyword in ['Solar', 'Aether'])])
    total_house_cost_before_profit_vat = calculate_rounded_up_cost(house_subtotal_base + waste_cost + overhead_cost)

    profit_rate = project_inputs.get('profit_rate', [None, 0.20])[1]
    profit = calculate_rounded_up_cost(total_house_cost_before_profit_vat * profit_rate)
    
    price_before_vat = total_house_cost_before_profit_vat + profit
    vat_amount = calculate_rounded_up_cost(price_before_vat * VAT_RATE)
    house_sales_price = calculate_rounded_up_cost(price_before_vat + vat_amount)

    total_sales_price = calculate_rounded_up_cost(house_sales_price + solar_cost + aether_package_cost)

    # Finansal özeti oluştur
    financial_summary_data = {
        'Total Material and Labor Cost': material_subtotal,
        f'Waste Cost ({FIRE_RATE*100:.0f}%)': waste_cost,
        'Total Overhead Cost': overhead_cost,
        'Total Cost Before Profit': total_cost_before_profit_vat,
        f'Profit ({project_inputs.get("profit_rate", [None, 0.20])[0]})': profit,
        'VAT Excluded Sales Price': price_before_vat,
        f'VAT ({VAT_RATE*100:.0f}%)': vat_amount,
        'House Sales Price (VAT Included)': house_sales_price,
        'Solar System Price (VAT Included)': solar_cost,
        'Aether Package Price (VAT Included)': aether_package_cost,
        'Total Sales Price (VAT Included)': total_sales_price,
    }

    # Tahmini teslimat süresi
    delivery_duration_business_days = math.ceil((floor_area / 27.0) * 35)
    if is_two_story:
        delivery_duration_business_days += math.ceil((floor_area / 27.0) * 15)
    if delivery_duration_business_days < 10:
        delivery_duration_business_days = 10

    # Sonuçları DataFrame ve sözlük olarak hazırla
    costs_df = pd.DataFrame(costs)
    if not costs_df.empty:
        costs_df = costs_df.set_index('Item').reset_index()
    else:
        costs_df = pd.DataFrame(columns=['Item', 'Quantity', 'Unit Price (€)', 'Total (€)'])
    
    profile_analysis_df = pd.DataFrame(profile_analysis_details)
    if not profile_analysis_df.empty:
        profile_analysis_df = profile_analysis_df.set_index('Item').reset_index()
    else:
        profile_analysis_df = pd.DataFrame(columns=['Item', 'Quantity', 'Unit Price (€)', 'Total (€)'])

    # Sonuç sözlüğünü döndür
    return {
        'costs_df': costs_df,
        'financial_summary': financial_summary_data,
        'profile_analysis_df': profile_analysis_df,
        'house_sales_price': house_sales_price,
        'solar_sales_price': solar_cost,
        'aether_package_sales_price': aether_package_cost,
        'total_sales_price': total_sales_price,
        'extra_expenses_info': {'description': project_inputs.get('extra_expenses_description', ''), 'amount': project_inputs.get('extra_expenses_amount', 0)},
        'delivery_duration_business_days': delivery_duration_business_days,
        'logo_data_b64': get_company_logo_base64(COMPANY_INFO['logo_url'])
    }
