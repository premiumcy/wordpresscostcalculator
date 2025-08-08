# calculator_api.py
# Bu dosya, WordPress'ten gelen istekleri işleyecek olan ana Python API'sini (backend) içerir.

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import A4
from datetime import datetime
import pandas as pd
import math
import re
import base64
import io

# Projenin diğer dosyalarını içe aktar
from config import FIYATLAR, COMPANY_INFO, clean_invisible_chars
from pdf_generator import create_internal_cost_report_pdf, create_customer_proposal_pdf_tr, create_customer_proposal_pdf_en_gr, create_sales_contract_pdf
from calculator import calculate_costs_detailed

# Flask uygulamasını başlat ve CORS'u etkinleştir
app = Flask(__name__)
# Tüm kaynaklardan gelen isteklere izin ver (güvenlik riskini azaltmak için
# daha sonra sadece WordPress URL'niz ile sınırlandırmanız önerilir)
CORS(app)

# === GÜVENLİK VE E-POSTA AYARLARI ===
# Bu bilgileri Render ortam değişkenleri olarak saklamanız önerilir.
# Örnek: MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_USERNAME = "your_email@example.com"
MAIL_PASSWORD = "your_email_password" # Bu, e-postanızın uygulama şifresi olmalıdır
MAIL_SERVER = "smtp.your_provider.com"
MAIL_PORT = 587
# Gönderen ve alıcı adreslerini ayarla
SENDER_EMAIL = MAIL_USERNAME
RECIPIENT_EMAIL_COMPANY = COMPANY_INFO["email"]

# E-posta gönderme fonksiyonu
def send_email_with_pdf(to_address, subject, body, pdf_data, pdf_filename):
    """
    Belirtilen adrese PDF ekiyle e-posta gönderir.
    """
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

        # Gelen verilerle hesaplama motorunu çalıştır
        areas = calculate_area(
            project_details['width'],
            project_details['length'],
            project_details['height'],
            project_details['is_two_story'],
            project_details['height_2nd_floor']
        )
        
        # Bu fonksiyon, hesaplamaları ve finansal özetleri döndürür
        results = calculate_costs_detailed(project_details, areas)

        # PDF'leri oluştur
        # Dahili Rapor (şirket için)
        internal_pdf_data = create_internal_cost_report_pdf(
            results['costs_df'],
            results['financial_summary'],
            results['profile_analysis_df'],
            project_details,
            customer_info,
            get_company_logo_base64(COMPANY_INFO['logo_url']) # Logoyu her PDF için çek
        )
        
        # Müşteri Teklifi (seçilen dile göre)
        if project_details['pdf_language'] == 'tr':
            customer_proposal_data = create_customer_proposal_pdf_tr(
                results['house_sales_price'],
                results['solar_sales_price'],
                results['aether_package_sales_price'],
                results['total_sales_price'],
                project_details,
                customer_info,
                results['extra_expenses_info'],
                get_company_logo_base64(COMPANY_INFO['logo_url'])
            )
        else:
            customer_proposal_data = create_customer_proposal_pdf_en_gr(
                results['house_sales_price'],
                results['solar_sales_price'],
                results['aether_package_sales_price'],
                results['total_sales_price'],
                project_details,
                customer_info,
                results['extra_expenses_info'],
                get_company_logo_base64(COMPANY_INFO['logo_url'])
            )

        # Satış Sözleşmesi (şirket için, İngilizce)
        sales_contract_data = create_sales_contract_pdf(
            customer_info,
            results['house_sales_price'],
            results['solar_sales_price'],
            results['aether_package_sales_price'],
            project_details,
            COMPANY_INFO,
            results['extra_expenses_info'],
            get_company_logo_base64(COMPANY_INFO['logo_url'])
        )

        # PDF'leri e-posta ile gönder
        email_sent_to_customer = send_email_with_pdf(
            customer_info['email'],
            "Premium Home Teklifiniz / Your Premium Home Offer",
            "Sayın Müşterimiz, talebiniz üzerine oluşturulan teklifiniz ektedir. / Dear Customer, your offer is attached.",
            customer_proposal_data,
            f"Customer_Proposal_{clean_invisible_chars(customer_info['name']).replace(' ', '_')}.pdf"
        )
        
        # Şirkete e-posta ile gönder (müşteri verileri ve dahili rapor)
        company_email_body = f"""
        Yeni bir teklif talebi alındı.

        Müşteri Adı: {customer_info['name']}
        E-posta: {customer_info['email']}
        Telefon: {customer_info['phone']}
        Proje Alanı: {project_details['width']}m x {project_details['length']}m

        Aşağıdaki bağlantılardan PDF'leri görüntüleyebilirsiniz.
        """
        email_sent_to_company = send_email_with_pdf(
            RECIPIENT_EMAIL_COMPANY,
            f"Yeni Teklif Talebi: {customer_info['name']}",
            company_email_body,
            internal_pdf_data,
            f"Internal_Report_{clean_invisible_chars(customer_info['name']).replace(' ', '_')}.pdf"
        )
        
        if email_sent_to_customer and email_sent_to_company:
            return jsonify({"status": "success", "message": "Teklifler başarıyla oluşturuldu ve e-posta ile gönderildi."}), 200
        else:
            return jsonify({"status": "error", "message": "Teklifler oluşturuldu ancak e-posta gönderimi başarısız oldu."}), 500

    except Exception as e:
        print(f"Genel hata: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Render'da çalışırken bu komutu doğrudan kullanır.
    # Eğer yerel olarak test ediyorsanız, debug=True ekleyebilirsiniz.
    # app.run(debug=True, port=os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))
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

        # Gelen verilerle hesaplama motorunu çalıştır
        areas = calculate_area(
            project_details['width'],
            project_details['length'],
            project_details['height'],
            project_details['is_two_story'],
            project_details.get('height_2nd_floor', 0)
        )
        
        # Bu fonksiyon, hesaplamaları ve finansal özetleri döndürür
        results = calculate_costs_detailed(project_details, areas)

        # PDF'leri oluştur
        # Dahili Rapor (şirket için)
        internal_pdf_data = create_internal_cost_report_pdf(
            results['costs_df'],
            results['financial_summary'],
            results['profile_analysis_df'],
            project_details,
            customer_info,
            results.get('logo_data_b64', None) # Logoyu her PDF için çek
        )
        
        # Müşteri Teklifi (seçilen dile göre)
        if project_details.get('pdf_language', 'tr') == 'tr':
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
        else:
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

        # Satış Sözleşmesi (şirket için, İngilizce)
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

        # PDF'leri e-posta ile gönder
        email_sent_to_customer = send_email_with_pdf(
            customer_info['email'],
            "Premium Home Teklifiniz / Your Premium Home Offer",
            "Sayın Müşterimiz, talebiniz üzerine oluşturulan teklifiniz ektedir. / Dear Customer, your offer is attached.",
            customer_proposal_data,
            f"Customer_Proposal_{clean_invisible_chars(customer_info['name']).replace(' ', '_')}.pdf"
        )
        
        # Şirkete e-posta ile gönder (müşteri verileri ve dahili rapor)
        company_email_body = f"""
        Yeni bir teklif talebi alındı.

        Müşteri Adı: {customer_info['name']}
        E-posta: {customer_info['email']}
        Telefon: {customer_info['phone']}
        Proje Alanı: {project_details['width']}m x {project_details['length']}m

        """
        email_sent_to_company = send_email_with_pdf(
            RECIPIENT_EMAIL_COMPANY,
            f"Yeni Teklif Talebi: {customer_info['name']}",
            company_email_body,
            internal_pdf_data,
            f"Internal_Report_{clean_invisible_chars(customer_info['name']).replace(' ', '_')}.pdf"
        )
        
        if email_sent_to_customer and email_sent_to_company:
            return jsonify({"status": "success", "message": "Teklifler başarıyla oluşturuldu ve e-posta ile gönderildi."}), 200
        else:
            return jsonify({"status": "error", "message": "E-posta gönderimi başarısız oldu."}), 500

    except Exception as e:
        print(f"Genel hata: {e}")
        import traceback
        return jsonify({"status": "error", "message": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    # Render'da çalışırken bu komutu doğrudan kullanır.
    # Eğer yerel olarak test ediyorsanız, debug=True ekleyebilirsiniz.
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))

