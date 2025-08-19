# pdf_generator.py
# Bu dosya, tüm projede kullanılan PDF oluşturma fonksiyonlarını içerir.

import io
import math
from datetime import datetime
import pandas as pd
import base64
import requests
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, SimpleDocTemplate, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
# Göreceli içe aktarma hatasını gidermek için noktalar (.) kaldırıldı.
from config import FIYATLAR, COMPANY_INFO, MATERIAL_INFO_ITEMS, TRANSLATIONS, VAT_RATE
from utils import clean_invisible_chars, format_currency, calculate_rounded_up_cost, get_company_logo_base64


# --- Ortak PDF Yardımcı Fonksiyonları ---
def draw_pdf_header_and_footer_common(canvas_obj, doc, customer_info, company_info, logo_data_b64, language_code):
    canvas_obj.saveState()
    main_font_bold = f"{doc.main_font}-Bold"
    main_font = doc.main_font
    
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
            pass

    # Şirket Bilgileri (Sağ üst)
    company_name_text = clean_invisible_chars(company_info['name'])
    company_address_text = clean_invisible_chars(company_info['address'])
    company_email_text = clean_invisible_chars(f"Email: {company_info['email']}")
    company_phone_text = clean_invisible_chars(f"Phone: {company_info['phone']}")
    company_website_text = clean_invisible_chars(f"Website: {company_info['website']}")

    canvas_obj.setFont(main_font, 8)
    canvas_obj.setFillColor(colors.HexColor('#2C3E50'))

    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 25 * mm, company_name_text)
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 30 * mm, company_address_text)
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 35 * mm, company_email_text)
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 40 * mm, company_phone_text)
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, A4[1] - 45 * mm, company_website_text)

    # Footer
    canvas_obj.line(doc.leftMargin, 20 * mm, A4[0] - doc.rightMargin, 20 * mm)
    canvas_obj.setFont(main_font, 7)
    canvas_obj.drawString(doc.leftMargin, 15 * mm, clean_invisible_chars(f"{company_info['name']} - {company_info['website']}"))
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, 15 * mm, clean_invisible_chars(f"Page {doc.page}"))
    canvas_obj.restoreState()


# --- Ek PDF Oluşturma Fonksiyonları ---
def _create_solar_appendix_elements_en_gr(styles, project_details):
    en_key = "SOLAR ENERGY SYSTEM"
    gr_key = "ΣΥΣΤΗΜΑ ΗΛΙΑΚΗΣ ΕΝΕΡΓΕΙΑΣ"
    
    heading_text = f"APPENDIX B: {en_key.upper()} / ΠΑΡΑΡΤΗΜΑ Β: {gr_key}"
    elements = [
        PageBreak(),
        Paragraph(clean_invisible_chars(heading_text), styles['Heading']),
        Spacer(1, 8*mm),
        Paragraph(clean_invisible_chars(f"Below are the details for the included <b>{project_details['solar_kw']} kW</b> Solar Energy System. The price for this system is handled separately from the main house payment plan.<br/><br/>Ακολουθούν οι λεπτομέρειες για το συμπεριλαμβανόμενο Σύστημα Ηλιακής Ενέργειας <b>{project_details['solar_kw']} kW</b>. Η τιμή για αυτό το σύστημα διαχειρίζεται ξεχωριστά από το πρόγραμμα πληρωμών του κυρίως σπιτιού."), styles['NormalBilingual']),
        Spacer(1, 8*mm),
    ]

    solar_materials = [
        [clean_invisible_chars("<b>Component / Εξάρτημα</b>"), clean_invisible_chars("<b>Description / Περιγραφή</b>")],
        [clean_invisible_chars("Solar Panels / Ηλιακοί Συλλέκτες"), clean_invisible_chars(f"{project_details['solar_kw']} kW High-Efficiency Monocrystalline Panels")],
        [clean_invisible_chars("Inverter / Μετατροπέας"), clean_invisible_chars("Hybrid Inverter with Grid-Tie Capability")],
        [clean_invisible_chars("Batteries / Μπαταρίες"), clean_invisible_chars("Lithium-Ion Battery Storage System (optional, priced separately)")],
        [clean_invisible_chars("Mounting System / Σύστημα Στήριξης"), clean_invisible_chars("Certified mounting structure for roof installation")],
        [clean_invisible_chars("Cabling & Connectors / Καλωδίωση & Συνδέσεις"), clean_invisible_chars("All necessary DC/AC cables, MC4 connectors, and safety switches")],
        [clean_invisible_chars("Installation & Commissioning / Εγκατάσταση & Θέση σε Λειτουργία"), clean_invisible_chars("Full professional installation and system commissioning")],
    ]
    table_data = [[Paragraph(clean_invisible_chars(cell), styles['NormalBilingual']) for cell in row] for row in solar_materials]
    solar_table = Table(table_data, colWidths=[60*mm, 110*mm], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4a5568")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(solar_table)
    
    elements.append(Spacer(1, 12*mm))
    elements.append(Paragraph(clean_invisible_chars("Total Price (Solar System) / Συνολική Τιμή (Ηλιακό Σύστημα)"), styles['Heading']))
    elements.append(Paragraph(format_currency(project_details['solar_price']), styles['PriceTotal']))
    return elements

def _create_heating_appendix_elements_en_gr(styles, project_details):
    en_key = "FLOOR HEATING SYSTEM"
    gr_key = "ΣΥΣΤΗΜΑ ΕΝΔΟΔΑΠΕΔΙΑΣ ΘΕΡΜΑΝΣΗΣ"
    
    heading_text = f"APPENDIX C: {en_key.upper()} / ΠΑΡΑΡΤΗΜΑ Γ: {gr_key}"
    elements = [
        PageBreak(),
        Paragraph(clean_invisible_chars(heading_text), styles['Heading']),
        Spacer(1, 8*mm),
        Paragraph(clean_invisible_chars("Below are the standard materials included in the Floor Heating System:<br/><br/>Ακολουθούν τα στάνταρ υλικά που περιλαμβάνονται στο Σύστημα Ενδοδαπέδιας Θέρμανσης:"), styles['NormalBilingual']),
        Spacer(1, 4*mm),
    ]
    heating_materials_en_lines = [
        "Nano Heat Paint", "48V 2000W Transformer", "Thermostat Control Unit",
        "Wiring and Connection Terminals", "Insulation Layers", "Subfloor Preparation Materials"
    ]
    heating_materials_gr_lines = [
        "Νάνο Θερμική Βαφή", "Μετασχηματιστής 48V 2000W", "Μονάδα Ελέγχου Θερμοστάτη",
        "Καλωδίωση και Τερματικά Σύνδεσης", "Στρώσεις Μόνωσης", "Υλικά Προετοιμασίας Υποδαπέδου"
    ]
    
    heating_materials = [
        [clean_invisible_chars("<b>Component / Εξάρτημα</b>"), clean_invisible_chars("<b>Description / Περιγραφή</b>")],
    ]
    for en_mat, gr_mat in zip(heating_materials_en_lines, heating_materials_gr_lines):
        heating_materials.append([
            Paragraph(clean_invisible_chars(en_mat) + " / " + clean_invisible_chars(gr_mat), styles['NormalBilingual'])
        ])

    table_data = [[Paragraph(clean_invisible_chars(cell), styles['NormalBilingual']) for cell in row] for row in heating_materials]
    elements.append(Table(table_data, colWidths=[70*mm, 100*mm], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4a5568")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ])))
    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(clean_invisible_chars("Note: Final material selection and detailed specifications will be confirmed during the design phase based on specific project requirements.<br/><br/>Σημείωση: Η τελική επιλογή υλικών και οι λεπτομερείς προδιαγραφές θα επιβεβαιωθούν κατά τη φάση του σχεδιασμού με βάση τις συγκεκριμένες απαιτήσεις του έργου."), styles['NormalBilingual']))
    return elements


def _create_aether_appendix_elements_en_gr(styles, project_details):
    en_key = "AETHER PACKAGE"
    gr_key = "ΠΑΚΕΤΟ AETHER"
    
    heading_text = f"APPENDIX D: {en_key.upper()} / ΠΑΡΑΡΤΗΜΑ Δ: {gr_key}"
    elements = [
        PageBreak(),
        Paragraph(clean_invisible_chars(heading_text), styles['Heading']),
        Spacer(1, 8*mm),
        Paragraph(clean_invisible_chars(f"Below are the details for the included Aether Package. This package offers a comprehensive upgrade to the standard features.<br/><br/>Ακολουθούν οι λεπτομέρειες για το συμπεριλαμβανόμενο Πακέτο Aether. Αυτό το πακέτο προσφέρει μια ολοκληρωμένη αναβάθμιση στις στάνταρ λειτουργίες."), styles['NormalBilingual']),
        Spacer(1, 8*mm),
    ]

    aether_materials = [
        [clean_invisible_chars("<b>Component / Εξάρτημα</b>"), clean_invisible_chars("<b>Description / Περιγραφή</b>")],
    ]
    
    aether_items = [
        "smart_home_systems_info", "white_goods_info", "sofa_info", "security_camera_info",
        "exterior_cladding_info", "bedroom_set_info", "terrace_laminated_wood_flooring_info",
        "porcelain_tiles_info", "concrete_panel_floor_info", "premium_faucets_info",
        "designer_furniture_info", "italian_sofa_info", "inclass_chairs_info",
        "exterior_wood_cladding_lambiri_info", "brushed_grey_granite_countertops_info"
    ]
    
    for item_key in aether_items:
        en_desc = MATERIAL_INFO_ITEMS.get(item_key)
        gr_desc = TRANSLATIONS.get(en_desc, ["", ""])[1]
        aether_materials.append([
            Paragraph(clean_invisible_chars(en_desc), styles['NormalBilingual']),
            Paragraph(clean_invisible_chars(gr_desc), styles['NormalBilingual'])
        ])

    table_data = [[Paragraph(clean_invisible_chars(cell), styles['NormalBilingual']) for cell in row] for row in aether_materials]
    elements.append(Table(table_data, colWidths=[70*mm, 100*mm], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4a5568")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ])))
    elements.append(Spacer(1, 12*mm))
    elements.append(Paragraph(clean_invisible_chars("Total Price (Aether Package) / Συνολική Τιμή (Πακέτο Aether)"), styles['Heading']))
    elements.append(Paragraph(format_currency(project_details['aether_package_sales_price']), styles['PriceTotal']))
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
        draw_pdf_header_and_footer_common(canvas_obj, doc, customer_info, COMPANY_INFO, doc.logo_data_b64, 'en_gr')
    
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
    elements.append(Spacer(1, 40*mm))
    elements.append(Paragraph(clean_invisible_chars(f"{TRANSLATIONS['PREFABRICATED HOUSE PROPOSAL'][0]} / {TRANSLATIONS['PREFABRICATED HOUSE PROPOSAL'][1]}"), title_style))
    elements.append(Spacer(1, 20*mm))
    elements.append(Paragraph(clean_invisible_chars(f"{TRANSLATIONS['For'][0]} / {TRANSLATIONS['For'][1]}: {customer_info['name']}"), subtitle_style))
    if customer_info['company']:
        elements.append(Paragraph(clean_invisible_chars(f"{TRANSLATIONS['Company'][0]} / {TRANSLATIONS['Company'][1]}: {customer_info['company']}"), subtitle_style))
    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph(clean_invisible_chars(f"{TRANSLATIONS['Date'][0]} / {TRANSLATIONS['Date'][1]}: {datetime.now().strftime('%d/%m/%Y')}"), subtitle_style))
    elements.append(PageBreak())

    elements.append(Paragraph(clean_invisible_chars(f"{TRANSLATIONS['CUSTOMER & PROJECT INFORMATION'][0]} / {TRANSLATIONS['CUSTOMER & PROJECT INFORMATION'][1]}"), styles['Heading']))
    elements.append(Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Room Configuration'][0]} / {TRANSLATIONS['Room Configuration'][1]}:</b> {project_details.get('room_configuration', '')}"), styles['NormalBilingual']))
    elements.append(Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Dimensions'][0]} / {TRANSLATIONS['Dimensions'][1]}:</b> {project_details['width']}m x {project_details['length']}m x {project_details['height']}m | <b>{TRANSLATIONS['Total Area'][0]} / {TRANSLATIONS['Total Area'][1]}:</b> {project_details['area']:.2f} m² | <b>{TRANSLATIONS['Structure Type'][0]} / {TRANSLATIONS['Structure Type'][1]}:</b> {project_details['structure_type']}"), styles['NormalBilingual']))
    elements.append(Spacer(1, 8*mm))

    customer_info_table_data = [
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Name'][0]} / {TRANSLATIONS['Name'][1]}:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info['name']}"), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Company'][0]} / {TRANSLATIONS['Company'][1]}:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info.get('company', '')}"), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Address'][0]} / {TRANSLATIONS['Address'][1]}:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info.get('address', '')}"), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Phone'][0]} / {TRANSLATIONS['Phone'][1]}:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info.get('phone', '')}"), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['ID/Passport No'][0]} / {TRANSLATIONS['ID/Passport No'][1]}:</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(f"{customer_info.get('id_no', '')}"), styles['NormalBilingual'])],
    ]
    customer_info_table = Table(customer_info_table_data, colWidths=[65*mm, 105*mm])
    customer_info_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(customer_info_table)
    elements.append(Spacer(1, 8*mm))

    elements.append(Paragraph(clean_invisible_chars(f"{TRANSLATIONS['TECHNICAL SPECIFICATIONS'][0]} / {TRANSLATIONS['TECHNICAL SPECIFICATIONS'][1]}"), styles['Heading']))
    
    def get_yes_no(value):
        return 'Yes / Ναι' if value else 'No / Όχι'
    
    def get_yes_no_empty(value):
        return 'Yes / Ναι' if value else ''

    building_structure_details_en_gr = ""
    if project_details['structure_type'] == 'Light Steel':
        profiles_en_str = ", ".join([f"{p['Item']} ({p['Quantity']} pieces)" for p in project_details.get('profile_analysis', []) if p['Quantity'] > 0])
        building_structure_details_en_gr = f"""
        <b>Building structure details:</b><br/>
        Skeleton: Box profile with dimensions of {profiles_en_str} will be used. Antirust will be applied to all box profiles and can be painted with the desired color. All our profile welding works have EN3834 certification in accordance with European standards. The construction operations of the entire building are subject to European standards and EN 1090-1 Light Steel Construction license inspection.
        <br/><br/>
        <b>Λεπτομέρειες δομής κτιρίου:</b><br/>
        Σκελετός: Θα χρησιμοποιηθεί προφίλ κουτιού διαστάσεων {profiles_en_str}. Αντισκωριακή προστασία θα εφαρμοστεί σε όλα τα προφίλ κουτιού και μπορεί να βαφτεί με το επιθυμητό χρώμα. Όλες οι εργασίες συγκόλλησης προφίλ μας διαθέτουν πιστοποίηση EN3834 σύμφωνα με τα ευρωπαϊκά πρότυπα. Οι κατασκευαστικές εργασίες ολόκληρου του κτιρίου υπόκεινται σε ευρωπαϊκά πρότυπα και επιθεώρηση άδειας κατασκευασίας EN 1090-1 Light Steel Construction.
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
        Αντισκωριακή προστασία θα εφαρμοστεί σε όλα τα προφίλ ve can be painted in the desired color.<br/>
        Όλες οι εργασίες συγκόλλησης προφίλ μας διαθέτουν πιστοποιητικό EN3834 σύμφωνα με τα ευρωπαϊκά πρότυπα. Όλες οι διαδικασίες κατασκευασίας του κτιρίου υπόκεινται σε ευρωπαϊκά πρότυπα ve επιθεώρηση άδειας κατασκευασίας EN 1090-1 Steel Construction.
        """
    building_structure_table_data = [
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Construction Type'][0]} / {TRANSLATIONS['Construction Type'][1]}</b>"), styles['NormalBilingual']), Paragraph(project_details['structure_type'], styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Steel Structure Details'][0]} / {TRANSLATIONS['Steel Structure Details'][1]}</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(building_structure_details_en_gr), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Interior Walls'][0]} / {TRANSLATIONS['Interior Walls'][1]}</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(INTERIOR_WALLS_DESCRIPTION_EN_GR), styles['NormalBilingual']) if project_details['plasterboard_interior'] or project_details['plasterboard_all'] else Paragraph(clean_invisible_chars("Not Included / Δεν περιλαμβάνεται"), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Roof'][0]} / {TRANSLATIONS['Roof'][1]}</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(ROOF_DESCRIPTION_EN_GR), styles['NormalBilingual'])],
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Exterior Walls'][0]} / {TRANSLATIONS['Exterior Walls'][1]}</b>"), styles['NormalBilingual']), Paragraph(clean_invisible_chars(EXTERIOR_WALLS_DESCRIPTION_EN_GR), styles['NormalBilingual']) if project_details['facade_sandwich_panel_included'] else Paragraph(clean_invisible_chars("Not Included / Δεν περιλαμβάνεται"), styles['NormalBilingual'])],
    ]
    building_materials_table = Table(building_structure_table_data, colWidths=[60*mm, 110*mm])
    building_materials_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(building_materials_table)
    elements.append(Spacer(1, 5*mm))

    interior_insulation_table_data = []
    
    floor_covering_text = project_details.get('floor_covering_type', 'N/A')
    interior_insulation_table_data.append([
        Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Interior'][0]} / {TRANSLATIONS['Interior'][1]}</b>"), styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(f"{TRANSLATIONS['Floor Covering'][0]}: {floor_covering_text}."), styles['NormalBilingual'])
    ])
    
    insulation_text = f"{TRANSLATIONS['Floor Insulation'][0]}: {get_yes_no_empty(project_details['insulation_floor'])}. {TRANSLATIONS['Wall Insulation'][0]}: {get_yes_no_empty(project_details['insulation_wall'])}."
    interior_insulation_table_data.append([
        Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Insulation'][0]} / {TRANSLATIONS['Insulation'][1]}</b>"), styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(insulation_text), styles['NormalBilingual'])
    ])
    
    if project_details['insulation_floor']:
        floor_insulation_details_text = [FLOOR_INSULATION_MATERIALS_EN_GR]
        if project_details.get('skirting_length_val', 0) > 0:
            floor_insulation_details_text.append(clean_invisible_chars(f"• Skirting / Σοβατεπί ({project_details['skirting_length_val']:.2f} m)"))
        if project_details.get('laminate_flooring_m2_val', 0) > 0:
            floor_insulation_details_text.append(clean_invisible_chars(f"• Laminate Flooring 12mm / Laminate Δάπεδο 12mm ({project_details['laminate_flooring_m2_val']:.2f} m²)"))
        if project_details.get('under_parquet_mat_m2_val', 0) > 0:
            floor_insulation_details_text.append(clean_invisible_chars(f"• Under Parquet Mat 4mm / Υπόστρωμα Πακέτου 4mm ({project_details['under_parquet_mat_m2_val']:.2f} m²)"))
        if project_details.get('osb2_18mm_count_val', 0) > 0:
            floor_insulation_details_text.append(clean_invisible_chars(f"• OSB2 18mm or Concrete Panel 18mm / OSB2 18mm ή Πάνελ Σκυροδέματος 18mm ({project_details['osb2_18mm_count_val']} pcs)"))
        if project_details.get('galvanized_sheet_m2_val', 0) > 0:
            floor_insulation_details_text.append(clean_invisible_chars(f"• 5mm Galvanized Sheet / 5mm Γαλβανισμένο Φύλλο ({project_details['galvanized_sheet_m2_val']:.2f} m²)"))
        floor_insulation_details_text.append(clean_invisible_chars("<i>Note: Insulation thickness can be increased. Ceramic coating can be preferred. (without concrete, special floor system)</i>"))
        
        interior_insulation_table_data.append([
            Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Floor Insulation Materials'][0]} / {TRANSLATIONS['Floor Insulation Materials'][1]}:</b>"), styles['NormalBilingual']),
            Paragraph("<br/>".join(floor_insulation_details_text), styles['NormalBilingual'])
        ])

    interior_insulation_table = Table(interior_insulation_table_data, colWidths=[60*mm, 110*mm])
    interior_insulation_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(interior_insulation_table)
    elements.append(Spacer(1, 5*mm))

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
        [Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Openings'][0]} / {TRANSLATIONS['Openings'][1]}</b>"), styles['NormalBilingual']), Paragraph(openings_text_en_gr_str, styles['NormalBilingual'])],
    ]
    openings_table = Table(openings_table_data, colWidths=[60*mm, 110*mm])
    openings_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(openings_table)
    elements.append(Spacer(1, 5*mm))

    elements.append(PageBreak())

    other_features_table_data = []

    kitchen_choice = project_details.get('kitchen_choice', 'No Kitchen')
    other_features_table_data.append([
        Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Kitchen'][0]} / {TRANSLATIONS['Kitchen'][1]}</b>"), styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(project_details.get('kitchen_type_display_en_gr', 'No')), styles['NormalBilingual'])
    ])
    if kitchen_choice != 'No Kitchen':
        other_features_table_data.append([
            Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Kitchen Materials'][0]} / {TRANSLATIONS['Kitchen Materials'][1]}</b>"), styles['NormalBilingual']),
            Paragraph(clean_invisible_chars(KITCHEN_MATERIALS_EN) + "<br/><br/>" + clean_invisible_chars(KITCHEN_MATERIALS_GR), styles['NormalBilingual'])
        ])

    other_features_table_data.append([
        Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Shower/WC'][0]} / {TRANSLATIONS['Shower/WC'][1]}</b>"), styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(get_yes_no_empty(project_details['shower_wc'])), styles['NormalBilingual'])
    ])
    if project_details['shower_wc']:
        other_features_table_data.append([
            Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Shower/WC Materials'][0]} / {TRANSLATIONS['Shower/WC'][1]}:</b>"), styles['NormalBilingual']),
            Paragraph(clean_invisible_chars(SHOWER_WC_MATERIALS_EN) + "<br/><br/>" + clean_invisible_chars(SHOWER_WC_MATERIALS_GR), styles['NormalBilingual'])
        ])

    other_features_table_data.append([
        Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Electrical'][0]} / {TRANSLATIONS['Electrical'][1]}</b>"), styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(get_yes_no_empty(project_details['electrical'])), styles['NormalBilingual'])
    ])
    if project_details['electrical']:
        other_features_table_data.append([
            Paragraph('', styles['NormalBilingual']),
            Paragraph(clean_invisible_chars(ELECTRICAL_MATERIALS_EN.strip()) + "<br/><br/>" + clean_invisible_chars(ELECTRICAL_MATERIALS_GR.strip()), styles['NormalBilingual'])
        ])

    other_features_table_data.append([
        Paragraph(clean_invisible_chars(f"<b>{TRANSLATIONS['Plumbing'][0]} / {TRANSLATIONS['Plumbing'][1]}</b>"), styles['NormalBilingual']),
        Paragraph(clean_invisible_chars(get_yes_no_empty(project_details['plumbing'])), styles['NormalBilingual'])
    ])
    if project_details['plumbing']:
        other_features_table_data.append([
            Paragraph('', styles['NormalBilingual']),
            Paragraph(clean_invisible_chars(PLUMBING_MATERIALS_EN.strip()) + "<br/><br/>" + clean_invisible_chars(PLUMBING_MATERIALS_GR.strip()), styles['NormalBilingual'])
        ])

    extra_general_additions_list_en_gr = []
    if project_details['heating']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Floor Heating: {get_yes_no_empty(project_details['heating'])}"))
    if project_details['solar']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Solar System: {get_yes_no_empty(project_details['solar'])} ({project_details['solar_kw']} kW)") if project_details['solar'] else '')
    if project_details['wheeled_trailer']:
        extra_general_additions_list_en_gr.append(clean_invisible_chars(f"Wheeled Trailer: {get_yes_no_empty(project_details['wheeled_trailer'])} ({format_currency(project_details['wheeled_trailer_price'])})" if project_details['wheeled_trailer'] else ''))
    
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
        payment_data.append([Paragraph("Aether Package Price / Τιμή Πακέτου Aether", payment_heading_style), Paragraph(format_currency(aether_package_price), payment_heading_style)])
        payment_data.append([Paragraph("   - Due upon contract signing / Με την υπογραφή της σύμβασης.", styles['NormalBilingual']), ""])
    if extra_expenses_info['amount'] > 0:
        payment_data.append([Paragraph("Extra Expenses / Έξτρα Έξοδα", payment_heading_style), Paragraph(format_currency(extra_expenses_info['amount']), payment_heading_style)])
        payment_data.append([Paragraph("   - Due upon contract signing / Με την υπογραφή της σύμβασης.", styles['NormalBilingual']), ""])

    payment_table = Table(payment_data, colWidths=[120*mm, 50*mm])
    payment_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    final_page_elements.append(payment_table)
    elements.append(KeepTogether(final_page_elements))

    if project_details['solar']:
        solar_elements = _create_solar_appendix_elements_en_gr(styles, project_details)
        elements.extend(solar_elements)
    if project_details['heating']:
        heating_elements = _create_heating_appendix_elements_en_gr(styles)
        elements.extend(heating_elements)
    if project_details['aether_package_choice'] != 'None':
        aether_elements = _create_aether_appendix_elements_en_gr(styles, project_details)
        elements.extend(aether_elements)
def create_internal_cost_report_pdf(cost_breakdown_df, financial_summary_df, profile_analysis_df, project_details, customer_info, logo_data_b64):
    """
    Türkçe dahili maliyet raporu PDF'i oluşturur.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=40*mm, # Increased top margin for header
        bottomMargin=25*mm
    )

    doc.customer_name = customer_info['name']
    doc.company_name = COMPANY_INFO['name']
    doc.main_font = "FreeSans" # Varsayılan font
    doc.logo_data_b64 = logo_data_b64

    def _internal_page_callback(canvas_obj, doc):
        draw_pdf_header_and_footer_common(canvas_obj, doc, customer_info, COMPANY_INFO, doc.logo_data_b64, 'tr')

    doc.onFirstPage = _internal_page_callback
    doc.onLaterPages = _internal_page_callback

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Header', parent=styles['Normal'], fontSize=18, alignment=TA_CENTER,
        spaceAfter=20, fontName=f"{doc.main_font}-Bold", textColor=colors.HexColor("#3182ce")
    ))
    styles.add(ParagraphStyle(
        name='SectionHeading', parent=styles['Heading2'], fontSize=12, spaceBefore=12,
        spaceAfter=6, fontName=f"{doc.main_font}-Bold", textColor=colors.HexColor("#3182ce"), alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        name='NormalTR', parent=styles['Normal'], fontSize=9, leading=12, spaceAfter=4, fontName=doc.main_font
    ))
    styles.add(ParagraphStyle(
        name='SubsectionHeading', parent=styles['Heading3'], fontSize=10, spaceBefore=8, spaceAfter=4,
        fontName=f"{doc.main_font}-Bold", textColor=colors.HexColor("#4a5568"), alignment=TA_LEFT
    ))

    header_style = styles['Header']
    section_heading_style = styles['SectionHeading']
    normal_tr_style = styles['NormalTR']
    subsection_heading_style = styles['SubsectionHeading']

    table_header_style = ParagraphStyle(
        name='TableHeader', parent=styles['Normal'], fontSize=8, fontName=f"{doc.main_font}-Bold",
        textColor=colors.white, alignment=TA_CENTER
    )
    table_cell_style = ParagraphStyle(
        name='TableCell', parent=styles['Normal'], fontSize=8, fontName=doc.main_font, alignment=TA_LEFT
    )
    center_table_cell_style = ParagraphStyle(
        name='CenterTableCell', parent=styles['Normal'], fontSize=8, fontName=doc.main_font, alignment=TA_CENTER
    )
    right_table_cell_style = ParagraphStyle(
        name='RightTableCell', parent=styles['Normal'], fontSize=8, fontName=doc.main_font, alignment=TA_RIGHT
    )
    elements = []

    # --- Başlık ---
    elements.append(Paragraph(clean_invisible_chars("İÇ MALİYET RAPORU / INTERNAL COST REPORT"), header_style))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(clean_invisible_chars(f"<b>Müşteri:</b> {customer_info['name']} | <b>Tarih:</b> {datetime.now().strftime('%d/%m/%Y')}"), normal_tr_style))
    elements.append(Spacer(1, 10*mm))

    # --- Proje Bilgileri ---
    elements.append(Paragraph("PROJE BİLGİLERİ", section_heading_style))
    elements.append(Paragraph(clean_invisible_chars(f"<b>Boyutlar:</b> {project_details['width']}m x {project_details['length']}m x {project_details['height']}m | <b>Toplam Alan:</b> {project_details['area']:.2f} m² | <b>Yapı Tipi:</b> {project_details['structure_type']}"), normal_tr_style))

    if project_details.get('is_two_story', False):
        elements.append(Paragraph(clean_invisible_chars(f"<b>İki Katlı Bina:</b> Var | 2. Kat Yüksekliği: {project_details.get('height_2nd_floor', 0)}m | 2. Kat Oda Konfigürasyonu: {project_details.get('room_config_2nd_floor', 'N/A')}"), normal_tr_style))

    elements.append(Spacer(1, 8*mm))

    # --- Maliyet Dağılımı ---
    if not cost_breakdown_df.empty:
        cost_data = [[Paragraph(c, table_header_style) for c in cost_breakdown_df.columns]]
        for _, row in cost_breakdown_df.iterrows():
            cost_data.append([
                Paragraph(str(row['Item']), table_cell_style),
                Paragraph(str(row['Quantity']), center_table_cell_style),
                Paragraph(format_currency(row['Unit Price (€)']), right_table_cell_style),
                Paragraph(format_currency(row['Total (€)']), right_table_cell_style)
            ])
        cost_table = Table(cost_data, colWidths=[65*mm, 30*mm, 35*mm, 40*mm])
        cost_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3182ce")),('GRID', (0,0), (-1,-1), 0.5, colors.grey),('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f7fafc"), colors.white])]))
        elements.append(Paragraph("MALİYET DAĞILIMI", section_heading_style))
        elements.append(cost_table)

    # --- Steel Profile Analysis (if any) on a NEW PAGE ---
    if not profile_analysis_df.empty and project_details['structure_type'] == 'Light Steel':
        elements.append(PageBreak())
        elements.append(Paragraph("ÇELİK PROFİL ANALİZİ", section_heading_style))
        profile_data = [[Paragraph(c, table_header_style) for c in ['Profile Type', 'Count', 'Unit Price (€)', 'Total (€)']]]
        for _, row in profile_analysis_df.iterrows():
            profile_data.append([
                Paragraph(str(row['Item']), table_cell_style),
                Paragraph(str(row['Quantity']), center_table_cell_style),
                Paragraph(format_currency(row['Unit Price (€)']), right_table_cell_style),
                Paragraph(format_currency(row['Total (€)']), right_table_cell_style)
            ])
        profile_table = Table(profile_data, colWidths=[55*mm, 25*mm, 45*mm, 45*mm])
        profile_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3182ce")),('GRID', (0,0), (-1,-1), 0.5, colors.grey),('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f7fafc"), colors.white])]))
        elements.append(profile_table)

    # --- Financials on a NEW PAGE ---
    elements.append(PageBreak())
    elements.append(Paragraph("FİNANSAL ÖZET", section_heading_style))
    financial_data = []
    for item, amount in financial_summary_df.items():
        item_cell = Paragraph(str(item), table_cell_style)
        amount_cell = Paragraph(str(format_currency(amount)), right_table_cell_style)
        financial_data.append([item_cell, amount_cell])

    financial_table = Table(financial_data, colWidths=[100*mm, 70*mm])
    financial_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3182ce")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f7fafc"), colors.white])
    ]))
    elements.append(financial_table)

    def create_sales_contract_pdf(customer_info, house_sales_price, solar_sales_price, aether_package_sales_price, project_details, company_info, extra_expenses_info):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=25*mm,
        bottomMargin=25*mm
    )
    doc.customer_name = customer_info['name']
    doc.company_name = COMPANY_INFO['name']
    doc.main_font = "FreeSans"

    def _contract_page_callback(canvas_obj, doc):
        draw_pdf_header_and_footer_common(canvas_obj, doc, customer_info, COMPANY_INFO, doc.logo_data_b64, 'en_gr')

    doc.onFirstPage = _contract_page_callback
    doc.onLaterPages = _contract_page_callback
    doc.logo_data_b64 = get_company_logo_base64(COMPANY_INFO['logo_url'])

    styles = getSampleStyleSheet()
    contract_heading_style = ParagraphStyle(
        name='ContractHeading', parent=styles['Heading2'], fontSize=13, spaceAfter=8,
        spaceBefore=12, fontName=f"{doc.main_font}-Bold", textColor=colors.HexColor("#3182ce"), alignment=TA_CENTER
    )
    contract_subheading_style = ParagraphStyle(
        name='ContractSubheading', parent=styles['Heading3'], fontSize=10, spaceAfter=5,
        spaceBefore=8, fontName=f"{doc.main_font}-Bold", textColor=colors.HexColor("#4a5568")
    )
    contract_normal_style = ParagraphStyle(
        name='ContractNormal', parent=styles['Normal'], fontSize=8, leading=10,
        spaceAfter=4, fontName=doc.main_font, alignment=TA_LEFT
    )
    contract_list_style = ParagraphStyle(
        name='ContractList', parent=styles['Normal'], fontSize=8, leading=10,
        spaceAfter=2, leftIndent=8*mm, fontName=doc.main_font
    )
    contract_signature_style = ParagraphStyle(
        name='ContractSignature', parent=styles['Normal'], fontSize=8, leading=10,
        alignment=TA_CENTER
    )

    elements = []

    # Title
    elements.append(Paragraph("SALES CONTRACT", contract_heading_style))
    elements.append(Spacer(1, 6*mm))

    # Parties involved (updated with dynamic ID and Company No)
    today_date = datetime.now().strftime('%d')
    today_month = datetime.now().strftime('%B')
    today_year = datetime.now().year
    elements.append(Paragraph(f"This Agreement ('Agreement') is entered into as of this {today_date} day of {today_month}, {today_year} by and between,", contract_normal_style))
    elements.append(Paragraph(f"<b>{customer_info['name'].upper()}</b> (I.D. No: <b>{customer_info.get('id_no', 'N/A')}</b>) hereinafter referred to as the \"Buyer,\" and", contract_normal_style))
    elements.append(Paragraph(f"<b>{company_info['name'].upper()}</b>, Company No. <b>{company_info['company_no']}</b>, with a registered address at {company_info['address']}, hereinafter referred to as the \"Seller.\"", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Subject of the Agreement
    elements.append(Paragraph("Subject of the Agreement:", contract_subheading_style))
    elements.append(Paragraph(f"A. The Seller agrees to complete and deliver to the Buyer the LIGHT STEEL STRUCTURE CONSTRUCTION (Tiny House) being constructed under its coordination at the address specified by the Buyer, in accordance with the specifications detailed in Appendix A.", contract_normal_style))
    elements.append(Paragraph("B. The details of the construction related to the Portable House project will be considered as appendixes to this agreement, which constitute integral parts of the present agreement.", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Definitions
    elements.append(Paragraph("1. Definitions:", contract_subheading_style))
    elements.append(Paragraph("1.1. \"Completion\" refers to the point at which the Light Steel Structure House is fully constructed, inspected, and ready for delivery.", contract_normal_style))
    elements.append(Paragraph("1.2. \"Delivery Date\" refers to the date on which the property is handed over to the Buyer, at which point the Buyer assumes full ownership and risk.", contract_normal_style))
    elements.append(Paragraph("1.3. \"Force Majeure Event\" means any event beyond the reasonable control of the Seller that prevents the timely delivery of the house, including but not limited to acts of God, war, terrorism, strikes, lockouts, natural disasters, or any other event recognized under law.", contract_normal_style))
    elements.append(Paragraph("1.4. \"House\" means the structure, as described in Appendix A.", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Sales Price and Payment Terms
    total_sales_price_for_contract = house_sales_price + solar_sales_price + aether_package_sales_price + extra_expenses_info['amount']
    total_sales_price_formatted = format_currency(total_sales_price_for_contract)

    down_payment = house_sales_price * 0.40
    remaining_balance = house_sales_price - down_payment
    installment_amount = remaining_balance / 3

    elements.append(Paragraph("2. Sales Price and Payment Terms:", contract_subheading_style))
    elements.append(Paragraph(f"2.1. The sales price of the Portable Container House (herein after \"the house\") is <b>{format_currency(house_sales_price)}</b>, plus 19% VAT, according to the specifications, as described to APPENDIX \"A\", which constitutes an integral part of the present agreement.", contract_list_style))
    elements.append(Paragraph(f"2.2. The total sales price (including solar, Aether package and extra expenses if applicable) is <b>{total_sales_price_formatted}</b> (VAT Included).", contract_list_style))
    elements.append(Paragraph("2.3. The Buyer will pay the following amounts according to the schedule:", contract_list_style))

    # Payment plan based on installment_option
    if project_details.get('installment_option', 'full') == 'full':
        elements.append(Paragraph(f"- Full Payment: {format_currency(house_sales_price)} upon contract signing.", contract_list_style, bulletText=''))
    else: # installments
        down_payment = house_sales_price * 0.40
        remaining_balance = house_sales_price - down_payment
        num_installments = int(project_details['installment_option'].split('_')[0])
        if num_installments > 0:
            installment_amount = remaining_balance / num_installments
        else:
            installment_amount = remaining_balance

        elements.append(Paragraph(f"- Main House (Total: {format_currency(house_sales_price)})", contract_list_style, bulletText=''))
        elements.append(Paragraph(f"  - 40% Down Payment: {format_currency(down_payment)} upon contract signing.", contract_list_style, bulletText='-'))
        for i in range(num_installments):
            if i == 0:
                elements.append(Paragraph(f"  - 1st Installment: {format_currency(installment_amount)} upon completion of structure.", contract_list_style, bulletText='-'))
            elif i == 1:
                elements.append(Paragraph(f"  - 2nd Installment: {format_currency(installment_amount)} upon completion of interior works.", contract_list_style, bulletText='-'))
            elif i == 2:
                elements.append(Paragraph(f"  - Final Payment: {format_currency(installment_amount)} upon final delivery.", contract_list_style, bulletText='-'))


    if solar_sales_price > 0:
        elements.append(Paragraph(f"- Solar System: {format_currency(solar_sales_price)} due upon contract signing.", contract_list_style, bulletText=''))
    if aether_package_sales_price > 0:
        elements.append(Paragraph(f"- Aether Package: {format_currency(aether_package_sales_price)} due upon contract signing.", contract_list_style, bulletText=''))
    if extra_expenses_info['amount'] > 0:
        extra_desc_en = extra_expenses_info['description'] or "Unspecified Extra Expenses"
        elements.append(Paragraph(f"- Extra Expenses ({extra_desc_en}): {format_currency(extra_expenses_info['amount'])} due upon contract signing.", contract_list_style, bulletText=''))


    elements.append(Paragraph("2.4. Any delay in payment shall result in legal interest charges at 2% per month.", contract_list_style))
    elements.append(Paragraph("2.5. If the Buyer fails to pay any installment for more than 20 days upon written notice, the seller reserves the right to terminate the contract and keep the deposit, as a compensation for damages caused.", contract_list_style))
    elements.append(Paragraph("2.6. The payment terms and dates envisaged under the headings of the sales price, payment terms, and delivery above constitute the essence of this sales agreement and form its basis.", contract_list_style))
    elements.append(Spacer(1, 6*mm))

    # Bank Details
    elements.append(Paragraph("2.7. Bank Details:", contract_subheading_style))
    bank_details_data = [
        [Paragraph("Bank Name:", contract_normal_style), Paragraph(COMPANY_INFO['bank_name'], contract_normal_style)],
        [Paragraph("Bank Address:", contract_normal_style), Paragraph(COMPANY_INFO['bank_address'], contract_normal_style)],
        [Paragraph("Account Name:", contract_normal_style), Paragraph(COMPANY_INFO['account_name'], contract_normal_style)],
        [Paragraph("IBAN:", contract_normal_style), Paragraph(COMPANY_INFO['iban'], contract_normal_style)],
        [Paragraph("Account Number:", contract_normal_style), Paragraph(COMPANY_INFO['account_number'], contract_normal_style)],
        [Paragraph("Currency:", contract_normal_style), Paragraph(COMPANY_INFO['currency_type'], contract_normal_style)],
        [Paragraph("SWIFT/BIC:", contract_normal_style), Paragraph(COMPANY_INFO['swift_bic'], contract_normal_style)],
    ]
    bank_details_table = Table(bank_details_data, colWidths=[40*mm, 130*mm])
    bank_details_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(bank_details_table)
    elements.append(Spacer(1, 6*mm))

    # Inspection of the Property and Defects
    elements.append(Paragraph("3. Inspection of the Property and Defects:", contract_subheading_style))
    elements.append(Paragraph("3.1. The Buyer shall have the right to inspect the property during the construction process. The Buyer may request an inspection at any point with 7 days' notice.", contract_normal_style))
    elements.append(Paragraph("3.2. Any defects or concerns raised during inspections shall be addressed by the Seller at no additional cost to the Buyer. The buyer shall keep a written record of inspections which the byuer signs after each inspection, confirming the status of affairs.", contract_normal_style))
    elements.append(Paragraph("3.3. Final inspection of the completed house will occur within 10 days of the delivery date, after which the Buyer shall provide written a list of defects.", contract_normal_style))
    elements.append(Paragraph("3.4. If there are any possible defects, the seller will restore them within ........ days/months and notify the buyer. In such a case, the delivery of the house will be determined accordingly.", contract_normal_style))
    elements.append(Paragraph("3.5. The seller will repair and/or replace any possible defects, within ........ days/months.", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Completion of the House
    elements.append(Paragraph("4. Completion of the House:", contract_subheading_style))
    elements.append(Paragraph("4.1. The Seller will issue an invoice and deliver the property to the Buyer after the full payment of the sales price and all amounts specified in Article 2, upon completion of the construction of the light steel structure house. Document procurement related to this matter is outside the specified time for delivery.", contract_normal_style))
    elements.append(Paragraph("4.2. In order to complete processes such as partitioning, transfer, etc., the Buyer agrees to assist the Seller and, for this purpose, to apply to official, semi-official, and other authorities jointly or individually with the Seller and/or other shareholder or shareholders, to sign necessary signatures, fill out forms, and/or, if necessary, appoint the Seller as a representative.", contract_normal_style))
    elements.append(Paragraph("4.3. The Buyer will be responsible for the Tax (VAT) of the house from the delivery of the light steel structure house.", contract_normal_style))
    elements.append(Paragraph("4.4. Despite the Seller's completion of the necessary legal procedures, the Seller will not be responsible for delays and extra transit expenses related to customs procedures and exit of the materials of this house.", contract_normal_style))

    elements.append(Paragraph(f"4.5. The House will be delivered within approximately {project_details['delivery_duration_business_days']} working days (excluding weekends and public holidays), as from the signing of this agreement.", contract_normal_style))
    elements.append(Paragraph("4.6. Any delays caused by Force Majeure events or by the Buyer shall extend the delivery period accordingly.", contract_normal_style))
    elements.append(Paragraph("4.7. If the seller fails to deliver the house within the set delivery date (4.5.), due to unforeseen delays, he is obliged to notify the buyer in writing, stating the reasons for the delay and proposing ways of overcoming the said delay.", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Termination
    elements.append(Paragraph("5. Termination:", contract_subheading_style))
    elements.append(Paragraph("5.1. In case the Buyer fails to fulfill any of the conditions of this agreement, the Seller has the right to terminate the agreement immediately, by sending a written notification explaining the reasons for such termination.", contract_normal_style))
    elements.append(Paragraph("5.2. If the Buyer decides not to purchase the house by the given date, the Buyer acknowledges and undertakes that they will lose the entire deposit given as compensation for damages. In the event of a problem caused by the Seller or if the Seller decides not to transfer to the Buyer, the Seller will refund the full deposit to the Buyer.", contract_normal_style))
    elements.append(Paragraph("5.3. All notices to be given under this agreement will be deemed to have been given or served by being left at the above-mentioned addresses of the parties or by being sent by post.", contract_normal_style))
    elements.append(Paragraph("5.4. This agreement is made in 2 copies, signed and initialed by the parties.", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Notifications
    elements.append(Paragraph("6. Notifications:", contract_subheading_style))
    elements.append(Paragraph("The following shall be considered as valid notifications:", contract_normal_style))
    elements.append(Paragraph("6.1. By regular mail", contract_list_style))
    elements.append(Paragraph("6.2. By registered mail", contract_list_style))
    elements.append(Paragraph("6.3. By double registered mail", contract_list_style))
    elements.append(Paragraph("6.4. By email which shall be sent by the usual electronic email used by the parties", contract_list_style))
    elements.append(Paragraph("6.5. By service via a bailiff", contract_list_style))
    elements.append(Paragraph("6.6. By fax", contract_list_style))
    elements.append(Paragraph("6.7. Telephone conversations, telephone messages (SMS), messages through viber, whats'app, facebook messenger and any other application/s not mentioned in this paragraph, shall not constitute a valid notice under above paragraph (4c).", contract_list_style))
    elements.append(Spacer(1, 6*mm))

    # Warranty and Defects liability - START ON NEW PAGE
    elements.append(PageBreak())
    elements.append(Paragraph("7. Warranty and Defects liability:", contract_subheading_style))
    elements.append(Paragraph("7.1. The seller warrants that the house will be free if defects in materials and workmanship, for a period of ........ (months/year), from the day of delivery.", contract_normal_style))
    elements.append(Paragraph("7.2. The said warrantee does not cover damages caused by misuse, negligence, or external factors (e.g. natural disasters).", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Applicable Law
    elements.append(Paragraph("8. Applicable Law:", contract_subheading_style))
    elements.append(Paragraph("This Agreement and any matter relating thereto shall be governed, construed and interpreted in accordance with the laws of the Republic of Cyprus any dispute arising under it shall be subject to the exclusive jurisdiction of the Cyprus courts.", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Dispute Resolution - Mediation / Arbitration
    elements.append(Paragraph("9. Dispute Resolution - Mediation / Arbitration", contract_subheading_style))
    elements.append(Paragraph("9.1. Any disputes arising under this Agreement and prior to any litigation before the relevant Court, will first be addressed through negotiation between the parties.", contract_normal_style))
    elements.append(Paragraph("9.2. If the dispute cannot be resolved through negotiation, the parties agree to submit to mediation in the Republic of Cyprus, according to Mediation Act §159(1)/2012.", contract_normal_style))
    elements.append(Paragraph("9.3. If mediation fails, the dispute will be resolved through binding arbitration under the rules of [Arbitration Organization].", contract_normal_style))
    elements.append(Paragraph("9.4. The above alternative dispute resolution, do not conflict the Constitutional right of either party may seek relief in the courts of Cyprus if there will be no amicable settlement.", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Amendments
    elements.append(Paragraph("10. Amendements:", contract_subheading_style))
    elements.append(Paragraph("Any amendements or modifications to this agreement, must be made in writing and signed by both parties prior to a written notification as above (term 6).", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    # Final Clause
    elements.append(Paragraph("11. This Agreement is made in two (2) identical copies in English language, with each party receiving one copy of the Agreement.", contract_normal_style))
    elements.append(Spacer(1, 6*mm))

    elements.append(Paragraph("IN WITNESS THEREOF, the parties have caused their authorized representatives to sign this Agreement on their behalf, the day and year above written.", contract_normal_style))
    elements.append(Spacer(1, 25*mm))

    # Final Signature Block
    final_signature_data = [
        [Paragraph(f"<b>THE SELLER</b><br/><br/><br/>________________________________________<br/>For and on behalf of<br/>{company_info['name'].upper()}", contract_signature_style),
        Paragraph(f"<b>THE BUYER</b><br/><br/><br/>________________________________________<br/>{customer_info['name'].upper()}<br/>I.D. No: {customer_info.get('id_no', 'N/A')}", contract_signature_style)]
    ]
    final_signature_table = Table(final_signature_data, colWidths=[80*mm, 80*mm], hAlign='CENTER')
    final_signature_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(final_signature_table)

    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", contract_normal_style))

    # Witnesses
    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("Witnesses:", contract_normal_style))
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph("1 (Sgn.) _____________________________________", contract_normal_style))
    elements.append(Paragraph("(name and i.d.)", contract_normal_style))
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph("2 (Sgn.) _____________________________________", contract_normal_style))
    elements.append(Paragraph("(name and i.d.)", contract_normal_style))

    elements.append(PageBreak())

    # APPENDIX "A" - Scope of Work
    elements.append(Paragraph("APPENDIX \"A\" - SCOPE OF WORK", contract_heading_style))
    elements.append(Paragraph("Within the scope of this sales agreement, the specified Light Steel Structure House will have the following features and materials:", contract_normal_style))
    elements.append(Spacer(1, 5*mm))

    def get_yes_no_en(value):
        return 'Yes' if value else 'No'

    appendix_data = []
    appendix_data.append([Paragraph("<b>Dimensions and Area:</b>", contract_subheading_style), Paragraph(f"The house has dimensions of {project_details['width']}m x {project_details['length']}m x {project_details['height']}m. It has a total area of {project_details['area']:.2f} m².", contract_normal_style)])

    if project_details.get('is_two_story', False):
        appendix_data.append([Paragraph("<b>Two-Story Building:</b>", contract_subheading_style), Paragraph(f"Yes. 2nd Floor Height: {project_details['height_2nd_floor']}m. 2nd Floor Room Configuration: {project_details.get('room_config_2nd_floor', 'N/A')}. Staircase included.", contract_normal_style)])


    building_structure_details_appendix_en = ""
    if project_details['structure_type'] == 'Light Steel':
        profiles_en_str = ", ".join([f"{p['Item']} ({p['Quantity']} pieces)" for p in project_details.get('profile_analysis', []) if p['Quantity'] > 0])
        building_structure_details_appendix_en = f"""
        Skeleton: Box profile with dimensions of {profiles_en_str} will be used. Antirust will be applied to all box profiles and can be painted with the desired color. All our profile welding works have EN3834 certification in accordance with European standards. The construction operations of the entire building are subject to European standards and EN 1090-1 Light Steel Construction license inspection.
        """
    else: # Heavy Steel
        building_structure_details_appendix_en = f"""
        Skeleton: Steel house frame with all necessary cross-sections (columns, beams), including connection components (flanges, screws, bolts), all as static drawings.
        HEA120 OR HEA160 Heavy metal will be used in models with title deed and construction permit. All non-galvanized metal surfaces will be sandblasted according to the Swedish standard Sa 2.5 and will be coated with a zincphosphate primer 80μm thick.
        Anti-rust will be applied to all profiles and can be painted in the desired color.
        All our profile welding works have EN3834 certificate in accordance with European standards. All construction processes of the building are subject to European standards and EN 1090-1 Steel Construction license inspection.
        """
    appendix_data.append([Paragraph("<b>Construction Materials:</b>", contract_subheading_style), Paragraph(building_structure_details_appendix_en, contract_normal_style)])

    appendix_data.append([Paragraph("<b>Interior and Exterior Covering:</b>", contract_subheading_style), Paragraph(f"Floor Covering: {project_details.get('floor_covering_type', 'N/A')}. Inner Wall OSB: {get_yes_no_en(project_details.get('osb_inner_wall', False))}. Interior Walls: Plasterboard {get_yes_no_en(project_details.get('plasterboard_interior', False) or project_details.get('plasterboard_all', False))}.", contract_normal_style)])
    appendix_data.append([Paragraph("<b>Insulation:</b>", contract_subheading_style), Paragraph(f"Floor Insulation: {get_yes_no_en(project_details.get('insulation_floor', False))}. Wall Insulation: {get_yes_no_en(project_details.get('insulation_wall', False))}.", contract_normal_style)])
    appendix_data.append([Paragraph("<b>Floor Coverings:</b>", contract_subheading_style), Paragraph(f"{project_details.get('floor_covering_type', 'N/A')} will be used for floor coverings.", contract_normal_style)])
    appendix_data.append([Paragraph("<b>Roof Covering:</b>", contract_subheading_style), Paragraph("100mm Sandwich Panel will be used for the roof.", contract_normal_style)])

    if project_details.get('plumbing', False):
        appendix_data.append([Paragraph("<b>Plumbing:</b>", contract_subheading_style), Paragraph(f"Plumbing installation {'' if project_details['plumbing'] else 'does NOT'} include external water connection. {PLUMBING_MATERIALS_EN.strip()}", contract_normal_style)])
    else:
        appendix_data.append([Paragraph("<b>Plumbing:</b>", contract_subheading_style), Paragraph("Not Included", contract_normal_style)])


    if project_details.get('electrical', False):
        appendix_data.append([Paragraph("<b>Electrical:</b>", contract_subheading_style), Paragraph(f"Electrical installation {'' if project_details['electrical'] else 'does NOT'} include external connection. {ELECTRICAL_MATERIALS_EN.strip()}", contract_normal_style)])
    else:
        appendix_data.append([Paragraph("<b>Electrical:</b>", contract_subheading_style), Paragraph("Not Included", contract_normal_style)])


    appendix_data.append([Paragraph("<b>Windows and Doors:</b>", contract_subheading_style), Paragraph(f"Aluminum windows and doors of various sizes will be used, with a height of 2.00m. Color: {project_details.get('window_door_color_val', 'N/A')}. The following windows and doors will be included in this project:<br/>Windows: {project_details.get('window_count', 0)} ({project_details.get('window_size_val', 'N/A')})<br/>Sliding Doors: {project_details.get('sliding_door_count', 0)} ({project_details.get('sliding_door_size_val', 'N/A')})<br/>WC Windows: {project_details.get('wc_window_count', 0)} ({project_details.get('wc_window_size_val', 'N/A')}){'' if project_details.get('wc_sliding_door_count', 0) == 0 else '<br/>WC Sliding Doors: ' + str(project_details['wc_sliding_door_count']) + ' (' + project_details['wc_sliding_door_size_val'] + ')'}<br/>Doors: {project_details.get('door_count', 0)} ({project_details.get('door_size_val', 'N/A')})", contract_normal_style)])

    additional_features_text = []
    if project_details.get('kitchen_choice', 'No Kitchen') != 'No Kitchen':
        additional_features_text.append(f"Kitchen: {get_yes_no_en(project_details['kitchen_choice'] != 'No Kitchen')} ({project_details['kitchen_type_display_en_gr']})")
        additional_features_text.append(KITCHEN_MATERIALS_EN.replace('\n', '<br/>'))
    else:
        additional_features_text.append("Kitchen: Not Included")

    if project_details.get('shower_wc', False):
        additional_features_text.append(f"Shower/WC: {get_yes_no_en(project_details['shower_wc'])}")
        additional_features_text.append(SHOWER_WC_MATERIALS_EN.replace('\n', '<br/>'))
    else:
        additional_features_text.append("Shower/WC: Not Included")

    if project_details.get('heating', False):
        additional_features_text.append(f"Floor Heating: {get_yes_no_en(project_details['heating'])}")
    if project_details.get('solar', False):
        additional_features_text.append(f"Solar: {get_yes_no_en(project_details['solar'])} ({project_details['solar_kw']} kW)")
    if project_details.get('aether_package_choice', 'None') != 'None':
        additional_features_text.append(f"Aether Package: {get_yes_no_en(project_details['aether_package_choice'] != 'None')}")
    if project_details.get('wheeled_trailer', False):
        additional_features_text.append(f"Wheeled Trailer: {get_yes_no_en(project_details['wheeled_trailer'])} ({format_currency(project_details['wheeled_trailer_price'])})")
    if project_details.get('extra_expenses_info', {}).get('amount', 0) > 0:
        extra_desc_en = project_details['extra_expenses_info'].get('description', 'Unspecified Extra Expenses')
        additional_features_text.append(f"Extra Expenses: {extra_desc_en} ({format_currency(project_details['extra_expenses_info']['amount'])})")
    if project_details.get('transportation_count', 0) > 0:
        additional_features_text.append(f"Transportation: Included ({project_details['transportation_count']} trips)")
    if project_details.get('is_two_story', False):
        additional_features_text.append(f"Two-Story Building: Yes. 2nd Floor Height: {project_details['height_2nd_floor']}m. 2nd Floor Room Configuration: {project_details['room_config_2nd_floor']}. Staircase included.")


    if additional_features_text:
        appendix_data.append([Paragraph("<b>Additional Features:</b>", contract_subheading_style), Paragraph("<br/>".join(additional_features_text), contract_normal_style)])

    appendix_table = Table(appendix_data, colWidths=[40*mm, 130*mm])
    appendix_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.grey),
    ]))
    elements.append(appendix_table)


    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
