# pdf_generator.py
# Bu dosya, tüm projede kullanılan PDF oluşturma fonksiyonlarını içerir.

import io
import math
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, SimpleDocTemplate, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from .config import COMPANY_INFO, FIYATLAR, MATERIAL_INFO_ITEMS, TRANSLATIONS, VAT_RATE
from .utils import clean_invisible_chars, format_currency, calculate_rounded_up_cost, get_company_logo_base64

# --- Ortak PDF Yardımcı Fonksiyonları ---
def draw_pdf_header_and_footer_common(canvas_obj, doc, customer_info, company_info, logo_data_b64, language_code):
    """
    Tüm PDF sayfaları için ortak başlık ve altbilgiyi çizer.
    """
    canvas_obj.saveState()
    canvas_obj.setFont(doc.main_font, 7)

    # Header - Sol üstte logo ve Sağ üstte şirket bilgileri
    if logo_data_b64:
        try:
            img_data = base64.b64decode(logo_data_b64)
            img = Image(io.BytesIO(img_data))
            logo_width_mm = 40 * mm
            aspect_ratio = img.drawWidth / img.drawHeight
            logo_height_mm = logo_width_mm / aspect_ratio
            canvas_obj.drawImage(img, doc.leftMargin, A4[1] - logo_height_mm - 10 * mm, width=logo_width_mm, height=logo_height_mm, mask='auto')
        except Exception as e:
            pass # Logo çizilemezse hata vermeden devam et

    # Şirket Bilgileri (Sağ üst)
    company_name_text = clean_invisible_chars(company_info['name'])
    company_address_text = clean_invisible_chars(company_info['address'])
    company_email_text = clean_invisible_chars(f"Email: {company_info['email']}")
    company_phone_text = clean_invisible_chars(f"Phone: {company_info['phone']}")
    company_website_text = clean_invisible_chars(f"Website: {company_info['website']}")

    canvas_obj.setFont(doc.main_font, 8)
    canvas_obj.setFillColor(colors.HexColor('#2C3E50'))

    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 25 * mm, company_name_text)
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 30 * mm, company_address_text)
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 35 * mm, company_email_text)
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 40 * mm, company_phone_text)
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 45 * mm, company_website_text)

    # Footer
    canvas_obj.line(doc.leftMargin, 20 * mm, A4[0] - doc.rightMargin, 20 * mm)
    canvas_obj.setFont(doc.main_font, 7)
    canvas_obj.drawString(doc.leftMargin, 15 * mm, clean_invisible_chars(f"{company_info['name']} - {company_info['website']}"))
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, 15 * mm, clean_invisible_chars(f"Page {doc.page}"))
    canvas_obj.restoreState()


# --- Ek PDF Oluşturma Fonksiyonları ---
def _create_appendix_elements(key, data, styles, language_code):
    """
    Çeviri sözlüğünden veriyi çekerek ortak bir appendix öğesi oluşturur.
    """
    en_key = key
    tr_key = TRANSLATIONS[en_key][0]
    gr_key = TRANSLATIONS[en_key][1]
    
    heading_text = f"APPENDIX {key.split(' ')[1]}: {en_key.upper()} / ΠΑΡΑΡΤΗΜΑ {key.split(' ')[1]}: {gr_key}"
    elements = [
        PageBreak(),
        Paragraph(clean_invisible_chars(heading_text), styles['Heading']),
        Spacer(1, 8*mm),
    ]

    # Dinamik metinler ve tablolar burada oluşturulabilir
    # Örneğin: Solar veya Heating malzemeleri
    if key == "B: SOLAR ENERGY SYSTEM":
        solar_materials = [
            [clean_invisible_chars("<b>Component / Εξάρτημα</b>"), clean_invisible_chars("<b>Description / Περιγραφή</b>")],
            [clean_invisible_chars("Solar Panels / Ηλιακοί Συλλέκτες"), clean_invisible_chars(f"{data['solar_kw']} kW High-Efficiency Monocrystalline Panels")],
            [clean_invisible_chars("Inverter / Μετατροπέας"), clean_invisible_chars("Hybrid Inverter with Grid-Tie Capability")],
            # ... diğer malzemeler ...
        ]
        table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4a5568")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ])
        table_data = [[Paragraph(clean_invisible_chars(cell), styles['NormalBilingual']) for cell in row] for row in solar_materials]
        elements.append(Table(table_data, colWidths=[60*mm, 110*mm], style=table_style))
    
    # Diğer appendix tipleri için de benzer mantık eklenebilir
    
    return elements


def create_customer_proposal_pdf_en_gr(house_price, solar_price, aether_package_price, total_price, project_details, customer_info, extra_expenses_info, logo_data_b64):
    """Müşteri için profesyonel bir teklif PDF'i oluşturur (İngilizce ve Yunanca)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=40*mm,
        bottomMargin=25*mm
    )
    doc.customer_name = customer_info['name']
    doc.company_name = COMPANY_INFO['name']
    doc.main_font = "FreeSans"
    doc.logo_data_b64 = logo_data_b64

    def _proposal_page_callback(canvas_obj, doc):
        draw_pdf_header_and_footer_common(canvas_obj, doc, doc.customer_name, doc.company_name, doc.logo_data_b64, 'en_gr')

    doc.onFirstPage = _proposal_page_callback
    doc.onLaterPages = _proposal_page_callback

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='NormalBilingual', parent=styles['Normal'], fontSize=8, leading=10, spaceAfter=2, fontName=doc.main_font))
    styles.add(ParagraphStyle(name='Heading', parent=styles['Heading2'], fontSize=11, spaceAfter=5, spaceBefore=10, fontName=f"{doc.main_font}-Bold", textColor=colors.HexColor("#3182ce"), alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='PriceTotal', parent=styles['Heading1'], fontSize=21, alignment=TA_CENTER, spaceAfter=10, fontName=f"{doc.main_font}-Bold", textColor=colors.HexColor("#c53030")))
    styles.add(ParagraphStyle(name='SectionSubheading', parent=styles['Heading3'], fontSize=9, spaceAfter=3, spaceBefore=7, fontName=f"{doc.main_font}-Bold", textColor=colors.HexColor("#4a5568")))
    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=17, alignment=TA_CENTER, spaceAfter=10, fontName=f"{doc.main_font}-Bold", textColor=colors.HexColor("#3182ce"))
    subtitle_style = ParagraphStyle(name='Subtitle', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=7, fontName=doc.main_font, textColor=colors.HexColor("#4a5568"))
    payment_heading_style = ParagraphStyle(name='PaymentHeading', parent=styles['Heading3'], fontSize=9, spaceAfter=3, spaceBefore=7, fontName=f"{doc.main_font}-Bold")
    colored_table_header_style = ParagraphStyle(name='ColoredTableHeader', parent=styles['Normal'], fontSize=8, fontName=f"{doc.main_font}-Bold", textColor=colors.white, alignment=TA_LEFT)
    
    elements = []
    # --- Kapak Sayfası ---
    elements.append(Spacer(1, 40*mm))
    elements.append(Paragraph(clean_invisible_chars("PREFABRICATED HOUSE PROPOSAL"), title_style))
    elements.append(Paragraph(clean_invisible_chars("ΠΡΟΤΑΣΗ ΠΡΟΚΑΤΑΣΚΕΥΑΣΜΕΝΟΥ ΣΠΙΤΙΟΥ"), title_style))
    elements.append(Spacer(1, 20*mm))
    elements.append(Paragraph(clean_invisible_chars(f"For / Για: {customer_info['name']}"), subtitle_style))
    if customer_info['company']:
        elements.append(Paragraph(clean_invisible_chars(f"Company / Εταιρεία: {customer_info['company']}"), subtitle_style))
    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(clean_invisible_chars(f"Date / Ημερομηνία: {datetime.now().strftime('%d/%m/%Y')}"), subtitle_style))
    elements.append(PageBreak())

    # --- Müşteri & Proje Bilgileri Bölümü ---
    elements.append(Paragraph(clean_invisible_chars("CUSTOMER & PROJECT INFORMATION / ΠΛΗΡΟΦΟΡΙΕΣ ΠΕΛΑΤΗ & ΕΡΓΟΥ"), styles['Heading']))
    elements.append(Paragraph(clean_invisible_chars(f"<b>Room Configuration / Διαμόρφωση Δωματίου:</b> {project_details.get('room_configuration', '')}"), styles['NormalBilingual']))
    elements.append(Paragraph(clean_invisible_chars(f"<b>Dimensions / Διαστάσεις:</b> {project_details['width']}m x {project_details['length']}m x {project_details['height']}m | <b>Total Area / Συνολική Επιφάνεια:</b> {project_details['area']:.2f} m² | <b>Structure Type / Τύπος Κατασκευής:</b> {project_details['structure_type']}"), styles['NormalBilingual']))
    elements.append(Spacer(1, 8*mm))

    customer_info_table_data = [
        [Paragraph(clean_invisible_chars("<b>Name / Όνομα:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info['name']}"), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars("<b>Company / Εταιρεία:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info.get('company', '')}"), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars("<b>Address / Διεύθυνση:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info.get('address', '')}"), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars("<b>Phone / Τηλέφωνο:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info.get('phone', '')}"), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars("<b>ID/Passport No / Αρ. Ταυτότητας/Διαβατηρίου:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info.get('id_no', '')}"), styles['NormalBilingual'])],
    ]
    customer_info_table = Table(customer_info_table_data, colWidths=[65*mm, 105*mm])
    customer_info_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(customer_info_table)
    elements.append(Spacer(1, 8*mm))

    # --- Teknik Özellikler Bölümü ---
    elements.append(Paragraph(clean_invisible_chars("TECHNICAL SPECIFICATIONS / ΤΕΧΝΙΚΑ ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ"), styles['Heading']))
    
    def get_yes_no(value):
        return 'Yes / Ναι' if value else 'No / Όχι'
    
    def get_yes_no_empty(value):
        return 'Yes / Ναι' if value else ''

    building_structure_details_en_gr = ""
    if project_details['structure_type'] == 'Light Steel':
        profiles_en_str = ", ".join([f"{p['Profile Type']} ({p['Count']} pieces)" for p in project_details.get('profile_analysis', []) if p['Count'] > 0])
        building_structure_details_en_gr = f"""
        <b>Building structure details:</b><br/>
        Skeleton: Box profile with dimensions of {profiles_en_str} will be used. Antirust will be applied to all box profiles and can be painted with the desired color. All our profile welding works have EN3834 certification in accordance with European standards. The construction operations of the entire building are subject to European standards and EN 1090-1 Light Steel Construction license inspection.
        <br/><br/>
        <b>Λεπτομέρειες δομής κτιρίου:</b><br/>
        Σκελετός: Θα χρησιμοποιηθεί προφίλ κουτιού διαστάσεων {profiles_en_str}. Αντισκωριακή προστασία θα εφαρμοστεί σε όλα τα προφίλ κουτιού και μπορεί να βαφτεί με το επιθυμητό χρώμα. Όλες οι εργασίες συγκόλλησης προφίλ μας διαθέτουν πιστοποίηση EN3834 σύμφωνα με τα ευρωπαϊκά πρότυπα. Οι κατασκευαστικές εργασίες ολόκληρου του κτιρίου υπόκεινται σε ευρωπαϊκά πρότυπα και επιθεώρηση άδειας κατασκευής EN 1090-1 Light Steel Construction.
        """
    else: # Heavy Steel
        building_structure_details_en_gr = f"""
        <b>Building structure details:</b><br/>
        Skeleton: Steel house frame with all necessary cross-sections (columns, beams), including connection components (flanges, screws, bolts), all as static drawings.<br/>
        HEA120 OR HEA160 Heavy metal will be used in models with title deed and construction permit. All non-galvanized metal surfaces will be sandblasted according to the Swedish standard Sa 2.5 and will be coated with a zincphosphate primer 80μm thick.<br/>
        Anti-rust will be applied to all profiles and can be painted in the desired color.<br/>
        All our profile welding works have EN3834 certificate in accordance with European standards. All construction processes of the building are subject to European standards and EN 1090-1 Steel Construction license inspection.
        <br/><br/>
        <b>Λεπτομέρειες δομής κτιρίου:</b><br/>
        Σκελετός: Ατσάλινος σκελετός σπιτιού με όλες τις απαραίτητες διατομές (κολώνες, δοκάρια), συμπεριλαμβανομένων των εξαρτημάτων σύνδεσης (φλάντζες, βίδες, μπουλόνια), όλα σύμφωνα με τα στατικά σχέδια.<br/>
        Στα μοντέλα με τίτλο ιδιοκτησίας και οικοδομική άδεια θα χρησιμοποιηθεί βαρύ μέταλλο HEA120 Ή HEA160. Όλες οι μη γαλβανισμένες μεταλλικές επιφάνειες θα αμμοβολιστούν σύμφωνα με το σουηδικό πρότυπο Sa 2.5 και θα επικαλυφθούν με αστάρι φωσφορικού ψευδαργύρου πάχους 80μm.<br/>
        Αντισκωριακή προστασία θα εφαρμοστεί σε όλα τα προφίλ και μπορεί να βαφτεί στο επιθυμητό χρώμα.<br/>
        Όλες οι εργασίες συγκόλλησης προφίλ μας διαθέτουν πιστοποιητικό EN3834 σύμφωνα με τα ευρωπαϊκά πρότυπα. Όλες οι διαδικασίες κατασκευής του κτιρίου υπόκεινται σε ευρωπαϊκά πρότυπα και επιθεώρηση άδειας κατασκευής EN 1090-1 Steel Construction.
        """
    building_structure_table_data = [
        [Paragraph('<b>Construction Type / Τύπος Κατασκευής</b>', styles['NormalBilingual']), Paragraph(project_details['structure_type'], styles['NormalBilingual'])],
        [Paragraph('<b>Steel Structure Details / Λεπτομέρειες Χαλύβδινης Κατασκευής</b>', styles['NormalBilingual']), Paragraph(clean_invisible_chars(building_structure_details_en_gr), styles['NormalBilingual'])],
        [Paragraph('<b>Interior Walls / Εσωτερικοί Τοίχοι</b>', styles['NormalBilingual']), Paragraph(clean_invisible_chars(INTERIOR_WALLS_DESCRIPTION_EN_GR), styles['NormalBilingual']) if project_details['plasterboard_interior'] or project_details['plasterboard_all'] else Paragraph(clean_invisible_chars("Not Included / Δεν περιλαμβάνεται"), styles['NormalBilingual'])],
        [Paragraph('<b>Roof / Στέγη</b>', styles['NormalBilingual']), Paragraph(clean_invisible_chars(ROOF_DESCRIPTION_EN_GR), styles['NormalBilingual'])],
        [Paragraph('<b>Exterior Walls / Εξωτερικοί Τοίχοι</b>', styles['NormalBilingual']), Paragraph(clean_invisible_chars(EXTERIOR_WALLS_DESCRIPTION_EN_GR), styles['NormalBilingual']) if project_details['facade_sandwich_panel_included'] else Paragraph(clean_invisible_chars("Not Included / Δεν περιλαμβάνεται"), styles['NormalBilingual'])],
    ]
    building_materials_table = Table(building_structure_table_data, colWidths=[60*mm, 110*mm])
    building_materials_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(building_materials_table)
    elements.append(Spacer(1, 5*mm))

    # --- Teknik Özellikler - İç Mekan, Yalıtım ve Doğramalar ---
    interior_insulation_table_data = []
    
    # Interior Covering
    floor_covering_text = project_details.get('floor_covering_type', 'N/A')
    interior_insulation_table_data.append([
        Paragraph('<b>Interior / Εσωτερικό</b>', styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(f"Floor Covering: {floor_covering_text}."), styles['NormalBilingual'])
    ])
    
    # Insulation
    insulation_text = f"Floor Insulation: {get_yes_no_empty(project_details['insulation_floor'])}. Wall Insulation: {get_yes_no_empty(project_details['insulation_wall'])}."
    interior_insulation_table_data.append([
        Paragraph('<b>Insulation / Μόνωση</b>', styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(insulation_text), styles['NormalBilingual'])
    ])
    
    # Floor Insulation Materials (if included)
    if project_details['insulation_floor']:
        floor_insulation_details_text = [FLOOR_INSULATION_MATERIALS_EN_GR]
        if project_details.get('skirting_length_val', 0) > 0:
            floor_insulation_details_text.append(clean_invisible_chars(f"• Skirting / Σοβατεπί ({project_details['skirting_length_val']:.2f} m)"))
        if project_details.get('laminate_flooring_m2_val', 0) > 0:
            floor_insulation_details_text.append(clean_invisible_chars(f"• Laminate Flooring 12mm / Laminate Δάπεδο 12mm ({project_details['laminate_flooring_m2_val']:.2f} m²)"))
        # Add other floor insulation materials here...
        floor_insulation_details_text.append(clean_invisible_chars("<i>Note: Insulation thickness can be increased. Ceramic coating can be preferred. (without concrete, special floor system)</i>"))
        
        interior_insulation_table_data.append([
            Paragraph('<b>Floor Insulation Materials / Υλικά Μόνωσης Δαπέδου:</b>', styles['NormalBilingual']),
            Paragraph("<br/>".join(floor_insulation_details_text), styles['NormalBilingual'])
        ])

    interior_insulation_table = Table(interior_insulation_table_data, colWidths=[60*mm, 110*mm])
    interior_insulation_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(interior_insulation_table)
    elements.append(Spacer(1, 5*mm))

    # Openings (Windows and Doors)
    openings_text_en_gr = []
    if project_details.get('window_count', 0) > 0:
        openings_text_en_gr.append(f"Windows: {project_details['window_count']} ({project_details.get('window_size_val', 'N/A')} - {project_details.get('window_door_color_val', 'N/A')})")
    if project_details.get('door_count', 0) > 0:
        openings_text_en_gr.append(f"Doors: {project_details['door_count']} ({project_details.get('door_size_val', 'N/A')} - {project_details.get('window_door_color_val', 'N/A')})")
    if project_details.get('sliding_door_count', 0) > 0:
        openings_text_en_gr.append(f"Sliding Doors: {project_details['sliding_door_count']} ({project_details.get('sliding_door_size_val', 'N/A')} - {project_details.get('window_door_color_val', 'N/A')})")
    if project_details.get('wc_window_count', 0) > 0:
        openings_text_en_gr.append(f"WC Windows: {project_details['wc_window_count']} ({project_details.get('wc_window_size_val', 'N/A')} - {project_details.get('window_door_color_val', 'N/A')})")
    if project_details.get('wc_sliding_door_count', 0) > 0:
        openings_text_en_gr.append(f"WC Sliding Doors: {project_details['wc_sliding_door_count']} ({project_details.get('wc_sliding_door_size_val', 'N/A')} - {project_details.get('window_door_color_val', 'N/A')})")

    openings_text_en_gr_str = "<br/>".join(clean_invisible_chars(item) for item in openings_text_en_gr)
    if not openings_text_en_gr_str:
        openings_text_en_gr_str = "No openings specified / Δεν καθορίστηκαν ανοίγματα"

    openings_table_data = [
        [Paragraph('<b>Openings / Ανοίγματα</b>', styles['NormalBilingual']), Paragraph(openings_text_en_gr_str, styles['NormalBilingual'])],
    ]
    openings_table = Table(openings_table_data, colWidths=[60*mm, 110*mm])
    openings_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(openings_table)
    elements.append(Spacer(1, 5*mm))

    # --- Sayfa Sonu: Teknik Özellikler Bölümünün Kalanı Yeni Sayfada ---
    elements.append(PageBreak())

    # Diğer Teknik Özellikler (Mutfak, Duş/WC, Elektrik, Sıhhi Tesisat, Ekstra Genel İlaveler)
    elements.append(Paragraph("ADDITIONAL TECHNICAL FEATURES / ΠΡΟΣΘΕΤΑ ΤΕΧΝΙΚΑ ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ", styles['Heading'])) # Yeni başlık

    other_features_table_data = []

    # Mutfak
    kitchen_choice = project_details.get('kitchen_choice', 'No Kitchen')
    other_features_table_data.append([
        Paragraph('<b>Kitchen / Κουζίνα</b>', styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(project_details.get('kitchen_type_display_en_gr', 'No')), styles['NormalBilingual'])
    ])
    if kitchen_choice != 'No Kitchen':
        other_features_table_data.append([
            Paragraph('<b>Kitchen Materials / Υλικά Κουζίνας</b>', styles['NormalBilingual']),
            Paragraph(clean_invisible_chars(KITCHEN_MATERIALS_EN) + "<br/><br/>" + clean_invisible_chars(KITCHEN_MATERIALS_GR), styles['NormalBilingual'])
        ])

    # Duş/WC
    other_features_table_data.append([
        Paragraph('<b>Shower/WC / Ντους/WC</b>', styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(get_yes_no_empty(project_details['shower_wc'])), styles['NormalBilingual'])
    ])
    if project_details['shower_wc']:
        other_features_table_data.append([
            Paragraph('<b>Shower/WC Materials / Υλικά Ντους/WC</b>', styles['NormalBilingual']),
            Paragraph(clean_invisible_chars(SHOWER_WC_MATERIALS_EN) + "<br/><br/>" + clean_invisible_chars(SHOWER_WC_MATERIALS_GR), styles['NormalBilingual'])
        ])

    # Elektrik ve Sıhhi Tesisat
    other_features_table_data.append([
        Paragraph('<b>Electrical / Ηλεκτρολογικά</b>', styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(get_yes_no_empty(project_details['electrical'])), styles['NormalBilingual'])
    ])
    if project_details['electrical']:
        other_features_table_data.append([
            Paragraph('', styles['NormalBilingual']),
            Paragraph(clean_invisible_chars(ELECTRICAL_MATERIALS_EN.strip()) + "<br/><br/>" + clean_invisible_chars(ELECTRICAL_MATERIALS_GR.strip()), styles['NormalBilingual'])
        ])

    other_features_table_data.append([
        Paragraph('<b>Plumbing / Υδραυλικά</b>', styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(get_yes_no_empty(project_details['plumbing'])), styles['NormalBilingual'])
    ])
    if project_details['plumbing']:
        other_features_table_data.append([
            Paragraph('', styles['NormalBilingual']),
            Paragraph(clean_invisible_chars(PLUMBING_MATERIALS_EN.strip()) + "<br/><br/>" + clean_invisible_chars(PLUMBING_MATERIALS_GR.strip()), styles['NormalBilingual'])
        ])

    # Ekstra Genel İlaveler
    extra_general_additions_list_en_gr = []
    if project_details['heating']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Floor Heating: {get_yes_no_empty(project_details['heating'])}"))
    if project_details['solar']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Solar System: {get_yes_no_empty(project_details['solar'])} ({project_details['solar_kw']} kW)") if project_details['solar'] else '')
    if project_details['wheeled_trailer']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Wheeled Trailer: {get_yes_no_empty(project_details['wheeled_trailer'])} ({format_currency(project_details['wheeled_trailer_price'])})") if project_details['wheeled_trailer'] else '')
    
    # Aether Living'e özel eklenenler
    if project_details['smart_home_systems_option']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Smart Home Systems: {get_yes_no_empty(project_details['smart_home_systems_option'])}"))
    if project_details['white_goods_fridge_tv_option']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"White Goods (Fridge, TV): {get_yes_no_empty(project_details['white_goods_fridge_tv_option'])}"))
    if project_details['sofa_option']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Sofa: {get_yes_no_empty(project_details['sofa_option'])}"))
    if project_details['security_camera_option']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Security Camera Pre-Installation: {get_yes_no_empty(project_details['security_camera_option'])}"))
    if project_details['exterior_cladding_m2_option'] and project_details['exterior_cladding_m2_val'] > 0:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Exterior Cladding (Knauf Aquapanel): Yes ({project_details['exterior_cladding_m2_val']:.2f} m²)"))
    if project_details['bedroom_set_option']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Bedroom Set: {get_yes_no_empty(project_details['bedroom_set_option'])}"))
    if project_details['terrace_laminated_wood_flooring_option'] and project_details['terrace_laminated_wood_flooring_m2_val'] > 0:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Treated Pine Floor (Terrace Option): Yes ({project_details['terrace_laminated_wood_flooring_m2_val']:.2f} m²)"))
    if project_details['porcelain_tiles_option'] and project_details['porcelain_tiles_m2_val'] > 0:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Porcelain Tiles: Yes ({project_details['porcelain_tiles_m2_val']:.2f} m²)"))
    if project_details['concrete_panel_floor_option'] and project_details['concrete_panel_floor_m2_val'] > 0:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Concrete Panel Floor: Yes ({project_details['concrete_panel_floor_m2_val']:.2f} m²)"))
    if project_details['premium_faucets_option']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Premium Faucets: {get_yes_no_empty(project_details['premium_faucets_option'])}"))
    if project_details['integrated_fridge_option']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Integrated Refrigerator: {get_yes_no_empty(project_details['integrated_fridge_option'])}"))
    if project_details['designer_furniture_option']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Integrated Custom Design Furniture: {get_yes_no_empty(project_details['designer_furniture_option'])}"))
    if project_details['italian_sofa_option']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Italian Sofa: {get_yes_no_empty(project_details['italian_sofa_option'])}"))
    if project_details['inclass_chairs_option'] and project_details['inclass_chairs_count'] > 0:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Inclass Chairs: Yes ({project_details['inclass_chairs_count']} pcs)"))
    if project_details['brushed_granite_countertops_option'] and project_details['brushed_granite_countertops_m2_val'] > 0:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Brushed Granite Countertops: Yes ({project_details['brushed_granite_countertops_m2_val']:.2f} m²)"))
    if project_details['exterior_wood_cladding_m2_option'] and project_details['exterior_wood_cladding_m2_val'] > 0:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Exterior Wood Cladding (Lambiri): Yes ({project_details['exterior_wood_cladding_m2_val']:.2f} m²)"))


    if extra_general_additions_list_en_gr:
        other_features_table_data.append([Paragraph('<b>Extra General Additions / Έξτρα Γενικές Προσθήκες</b>', styles['NormalBilingual']), Paragraph("<br/>".join(extra_general_additions_list_en_gr), styles['NormalBilingual'])])

    other_features_table = Table(other_features_table_data, colWidths=[60*mm, 110*mm])
    other_features_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(other_features_table)
    elements.append(Spacer(1, 5*mm))

    # --- PRICE & PAYMENT SCHEDULE on a NEW PAGE ---
    elements.append(PageBreak())
    final_page_elements = [Spacer(1, 12*mm)]

    final_page_elements.append(Paragraph("PRICE & PAYMENT SCHEDULE / ΤΙΜΗ & ΠΡΟΓΡΑΜΜΑ ΠΛΗΡΩΜΩΝ", styles['Heading']))

    price_table_data = []
    price_table_data.append([
        Paragraph("Main House Price / Τιμή Κυρίως Σπιτιού", colored_table_header_style),
        Paragraph(format_currency(house_price), colored_table_header_style)
    ])
    if solar_price > 0:
        price_table_data.append([
            Paragraph("Solar System Price / Τιμή Ηλιακού Συστήματος", colored_table_header_style),
            Paragraph(format_currency(solar_price), colored_table_header_style)
        ])
    if aether_package_price > 0:
        price_table_data.append([
            Paragraph("Aether Package Price / Τιμή Πακέτου Aether", colored_table_header_style),
            Paragraph(format_currency(aether_package_price), colored_table_header_style)
        ])
    if extra_expenses_info['amount'] > 0:
        price_table_data.append([
            Paragraph("Extra Expenses / Έξτρα Έξοδα", colored_table_header_style),
            Paragraph(format_currency(extra_expenses_info['amount']), colored_table_header_style)
        ])
    price_table_data.append([
        Paragraph("TOTAL PRICE / ΣΥΝΟΛΙΚΗ ΤΙΜΗ", colored_table_header_style),
        Paragraph(format_currency(total_price), colored_table_header_style)
    ])

    price_summary_table = Table(price_table_data, colWidths=[120*mm, 50*mm])
    price_summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#3182ce")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#4a5568")),
    ]))
    final_page_elements.append(price_summary_table)
    final_page_elements.append(Spacer(1, 8*mm))

    final_page_elements.append(Paragraph("All prices are VAT included / Όλες οι τιμές περιλαμβάνουν ΦΠΑ.", payment_heading_style))
    final_page_elements.append(Paragraph("Our prefabricated living spaces have a 3-year warranty. Hot and cold balance is provided with polyurethane panels, fire class is A quality and energy consumption is A+++. / Οι προκατασκευασμένοι χώροι διαβίωσης μας έχουν 3ετή εγγύηση. Η ισορροπία ζεστού και κρύου επιτυγχάνεται με πάνελ πολυουρεθάνης, η κλάση πυρός είναι Α ποιότητας και η κατανάλωση ενέργειας είναι Α+++.", styles['NormalBilingual']))
    
    final_page_elements.append(Spacer(1, 8*mm))
    final_page_elements.append(Paragraph(f"<b>Estimated Delivery / Εκτιμώμενη Παράδοση:</b> Approx. {project_details['delivery_duration_business_days']} business days / Περίπου {project_details['delivery_duration_business_days']} εργάσιμες ημέρες", payment_heading_style))
    final_page_elements.append(Spacer(1, 8*mm))


    final_page_elements.append(Paragraph("Main House Payment Plan / Πρόγραμμα Πληρωμών Κυρίως Σπιτιού", payment_heading_style))

    if project_details.get('installment_option', 'full') == 'full':
        payment_data = [
            [Paragraph("1. Full Payment / Πλήρης Εξόφληση (100%)", payment_heading_style), Paragraph(format_currency(house_price), payment_heading_style)],
            [Paragraph("   - Due upon contract signing / Με την υπογραφή της σύμβασης.", styles['NormalBilingual']), ""],
        ]
    else: # installments
        down_payment = house_price * 0.40
        remaining_balance = house_price - down_payment
        num_installments = int(project_details['installment_option'].split('_')[0])
        if num_installments > 0:
            installment_amount = remaining_balance / num_installments
        else:
            installment_amount = remaining_balance

        payment_data = [
            [Paragraph("1. Down Payment / Προκαταβολή (40%)", payment_heading_style), Paragraph(format_currency(down_payment), payment_heading_style)],
            [Paragraph("   - Due upon contract signing / Με την υπογραφή της σύμβασης.", styles['NormalBilingual']), ""],
        ]
        if num_installments >= 1:
            payment_data.append([Paragraph("2. 1st Installment / 1η Δόση", payment_heading_style), Paragraph(format_currency(installment_amount), payment_heading_style)])
            payment_data.append([Paragraph("   - Due upon completion of structure / Με την ολοκλήρωση της κατασκευής.", styles['NormalBilingual']), ""])
        if num_installments >= 2:
            payment_data.append([Paragraph("3. 2nd Installment / 2η Δόση", payment_heading_style), Paragraph(format_currency(installment_amount), payment_heading_style)])
            payment_data.append([Paragraph("   - Due upon completion of interior works / Με την ολοκλήρωση των εσωτερικών εργασιών.", styles['NormalBilingual']), ""])
        if num_installments >= 3:
            payment_data.append([Paragraph("4. Final Payment / Τελική Εξόφληση", payment_heading_style), Paragraph(format_currency(installment_amount), payment_heading_style)])
            payment_data.append([Paragraph("   - Due upon final delivery / Με την τελική παράδοση.", styles['NormalBilingual']), ""])


    if solar_price > 0:
        payment_data.append([Paragraph("Solar System / Ηλιακό Σύστημα", payment_heading_style), Paragraph(format_currency(solar_price), payment_heading_style)])
        payment_data.append([Paragraph("   - Due upon contract signing / Με την υπογραφή της σύμβασης.", styles['NormalBilingual']), ""])
    if aether_package_price > 0:
        payment_data.append([Paragraph("Aether Package / Πακέτο Aether", payment_heading_style), Paragraph(format_currency(aether_package_price), payment_heading_style)])
        payment_data.append([Paragraph("   - Due upon contract signing / Με την υπογραφή της σύμβασης.", styles['NormalBilingual']), ""])
    if extra_expenses_info['amount'] > 0:
        payment_data.append([Paragraph("Extra Expenses / Έξτρα Έξοδα", payment_heading_style), Paragraph(format_currency(extra_expenses_info['amount']), payment_heading_style)])
        payment_data.append([Paragraph("   - Due upon contract signing / Με την υπογραφή της σύμβασης.", styles['NormalBilingual']), ""])

    payment_table = Table(payment_data, colWidths=[120*mm, 50*mm])
    payment_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    final_page_elements.append(payment_table)
    elements.append(KeepTogether(final_page_elements))

    # Add appendices if selected
    if project_details['solar']:
        solar_elements = _create_solar_appendix_elements_en_gr(project_details['solar_kw'], project_details['solar_price'], styles['Heading'], styles['NormalBilingual'], styles['PriceTotal'])
        elements.extend(solar_elements)
    if project_details['heating']:
        heating_elements = _create_heating_appendix_elements_en_gr(styles)
        elements.extend(heating_elements)
    if project_details['aether_package_choice'] != 'None':
        aether_elements = _create_aether_appendix_elements_en_gr(aether_package_price, styles)
        elements.extend(aether_elements)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
