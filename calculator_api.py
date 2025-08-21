# calculator_api.py
# Bu dosya, WordPress'ten gelen istekleri işleyecek olan ana Python API'sini (backend) içerir.

import sys
import os
# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import pandas as pd
import math
import re
import base64
import io

# Projenin diğer dosyalarını içe aktar
from config import FIYATLAR, COMPANY_INFO, MATERIAL_INFO_ITEMS, TRANSLATIONS
from pdf_generator import create_internal_cost_report_pdf, create_customer_proposal_pdf_tr, create_customer_proposal_pdf_en_gr, create_sales_contract_pdf
from calculator import calculate_costs_detailed
from utils import clean_invisible_chars, calculate_area, get_company_logo_base64

# Flask uygulamasını başlat ve CORS'u etkinleştir
app = Flask(__name__)
# Tüm kaynaklardan gelen isteklere izin ver (güvenlik riskini azaltmak için
# daha sonra sadece WordPress URL'niz ile sınırlandırmanız önerilir)
CORS(app)

# === GÜVENLİ E-POSTA AYARLARI (RENDER ORTAM DEĞİŞKENLERİ) ===
# Bu bilgileri Render arayüzünden "Environment Variables" olarak ekleyin.
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") # Uygulama şifresi
MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.hostinger.com") # Varsayılan değer eklenmiştir
MAIL_PORT = int(os.environ.get("MAIL_PORT", 587)) # Varsayılan değer eklenmiştir

SENDER_EMAIL = MAIL_USERNAME
RECIPIENT_EMAIL_COMPANY = COMPANY_INFO["email"]

# E-posta gönderme fonksiyonu
def send_email_with_pdf(to_address, subject, body, pdf_data, pdf_filename):
    """
    Belirtilen adrese PDF ekiyle e-posta gönderir.
    """
    if not all([MAIL_USERNAME, MAIL_PASSWORD, MAIL_SERVER, MAIL_PORT]):
        print("UYARI: E-posta ayarları eksik. E-posta gönderimi yapılamadı.")
        return False

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_address
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))
    
    # PDF dosyasını ek olarak ekle
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {pdf_filename}")
    msg.attach(part)
    
    try:
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_address, text)
        server.quit()
        return True
    except Exception as e:
        print(f"E-posta gönderme hatası: {e}")
        return False

@app.route('/calculate', methods=['POST'])
def calculate_and_generate_pdfs():
    """
    WordPress'ten gelen proje verilerini alır, maliyetleri hesaplar,
    PDF'leri oluşturur ve e-posta ile gönderir.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

        # Müşteri ve proje verilerini al
        customer_info = data.get('customer_info', {})
        project_details = data.get('project_details', {})
        
        # HTML formunda olmayan ancak API'nin beklediği değerler için varsayılan değerler
        project_details['id_no'] = customer_info.get('id_no', 'N/A')
        project_details['height_2nd_floor'] = project_details.get('height_2nd_floor', 0)
        project_details['room_config_2nd_floor'] = project_details.get('room_config_2nd_floor', 'N/A')
        project_details['plasterboard_interior'] = project_details.get('plasterboard_interior', False)
        project_details['plasterboard_all'] = project_details.get('plasterboard_all', False)
        project_details['facade_sandwich_panel_included'] = project_details.get('facade_sandwich_panel_included', False)
        project_details['osb_inner_wall_option'] = project_details.get('osb_inner_wall_option', False)
        project_details['insulation_wall'] = project_details.get('insulation_wall', False)
        project_details['insulation_floor'] = project_details.get('insulation_floor', False)
        project_details['skirting_length_val'] = project_details.get('skirting_length_val', 0)
        project_details['laminate_flooring_m2_val'] = project_details.get('laminate_flooring_m2_val', 0)
        project_details['under_parquet_mat_m2_val'] = project_details.get('under_parquet_mat_m2_val', 0)
        project_details['osb2_18mm_count_val'] = project_details.get('osb2_18mm_count_val', 0)
        project_details['galvanized_sheet_m2_val'] = project_details.get('galvanized_sheet_m2_val', 0)
        project_details['concrete_panel_floor_option'] = project_details.get('concrete_panel_floor_option', False)
        project_details['concrete_panel_floor_m2_val'] = project_details.get('concrete_panel_floor_m2_val', 0)
        project_details['terrace_laminated_wood_flooring_option'] = project_details.get('terrace_laminated_wood_flooring_option', False)
        project_details['terrace_laminated_wood_flooring_m2_val'] = project_details.get('terrace_laminated_wood_flooring_m2_val', 0)
        project_details['porcelain_tiles_option'] = project_details.get('porcelain_tiles_option', False)
        project_details['porcelain_tiles_m2_val'] = project_details.get('porcelain_tiles_m2_val', 0)
        project_details['wheeled_trailer'] = project_details.get('wheeled_trailer', False)
        project_details['wheeled_trailer_price'] = project_details.get('wheeled_trailer_price', 0)
        project_details['solar_kw'] = project_details.get('solar_kw', 0)
        project_details['solar'] = project_details.get('solar', False)
        project_details['extra_expenses_info'] = project_details.get('extra_expenses_info', {'description': '', 'amount': 0})
        project_details['transportation_count'] = project_details.get('transportation_count', 0)
        project_details['heating'] = project_details.get('heating', False)
        project_details['aether_package_choice'] = project_details.get('aether_package_choice', 'None')
        project_details['room_config_2nd_floor'] = project_details.get('room_config_2nd_floor', 'N/A')
        project_details['height_2nd_floor'] = project_details.get('height_2nd_floor', 0)

        # Gelen verilerle hesaplama motorunu çalıştır
        areas = calculate_area(
            project_details.get('width', 0),
            project_details.get('length', 0),
            project_details.get('height', 0),
            project_details.get('is_two_story', False),
            project_details.get('height_2nd_floor', 0)
        )
        
        results = calculate_costs_detailed(project_details, areas)

        # PDF'leri oluştur
        internal_pdf_data = create_internal_cost_report_pdf(
            results['costs_df'],
            results['financial_summary'],
            results['profile_analysis_df'],
            project_details,
            customer_info,
            results.get('logo_data_b64', None)
        )
        
        if project_details.get('pdf_language', 'en_gr') == 'en_gr':
            customer_proposal_data = create_customer_proposal_pdf_en_gr(
                results['house_sales_price'],
                results['solar_sales_price'],
                results['aether_package_sales_price'],
                results['total_sales_price'],
                project_details,
                customer_info,
                results['extra_expenses_info'],
                results.get('logo_data_b64', None)
            )
        else: # Türkçe dil seçeneği
             customer_proposal_data = create_customer_proposal_pdf_tr(
                results['house_sales_price'],
                results['solar_sales_price'],
                results['aether_package_sales_price'],
                results['total_sales_price'],
                project_details,
                customer_info,
                results['extra_expenses_info'],
                results.get('logo_data_b64', None)
            )


        sales_contract_data = create_sales_contract_pdf(
            customer_info,
            results['house_sales_price'],
            results['solar_sales_price'],
            results['aether_package_sales_price'],
            project_details,
            COMPANY_INFO,
            results['extra_expenses_info'],
            results.get('logo_data_b64', None)
        )

        email_sent_to_customer = send_email_with_pdf(
            customer_info.get('email', ''),
            "Premium Home Teklifiniz / Your Premium Home Offer",
            "Sayın Müşterimiz, talebiniz üzerine oluşturulan teklifiniz ektedir. / Dear Customer, your offer is attached.",
            customer_proposal_data,
            f"Customer_Proposal_{clean_invisible_chars(customer_info.get('name', 'General')).replace(' ', '_')}.pdf"
        )
        
        company_email_body = f"""
        Yeni bir teklif talebi alındı.

        Müşteri Adı: {customer_info.get('name', '')}
        E-posta: {customer_info.get('email', '')}
        Telefon: {customer_info.get('phone', '')}
        Proje Alanı: {project_details.get('width', 0)}m x {project_details.get('length', 0)}m
        """
        email_sent_to_company = send_email_with_pdf(
            RECIPIENT_EMAIL_COMPANY,
            f"Yeni Teklif Talebi: {customer_info.get('name', 'General')}",
            company_email_body,
            internal_pdf_data,
            f"Internal_Report_{clean_invisible_chars(customer_info.get('name', 'General')).replace(' ', '_')}.pdf"
        )
        
        if email_sent_to_customer and email_sent_to_company:
            return jsonify({"status": "success", "message": "Teklifler başarıyla oluşturuldu ve e-posta ile gönderildi."}), 200
        else:
            return jsonify({"status": "error", "message": "Teklifler oluşturuldu ancak e-posta gönderimi başarısız oldu."}), 500

    except Exception as e:
        print(f"Genel hata: {e}")
        import traceback
        return jsonify({"status": "error", "message": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))
