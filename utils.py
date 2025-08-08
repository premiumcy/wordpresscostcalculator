# utils.py
# Bu dosya, tüm projede kullanılan temel yardımcı fonksiyonları içerir.

import math
import re
import base64
import io
import requests
from datetime import datetime
from PIL import Image as PILImage

# --- Görünmez Karakter Temizleme Fonksiyonu ---
# Metinlerdeki görünmez karakterleri ve gereksiz boşlukları temizler.
def clean_invisible_chars(text):
    """
    Metindeki görünmez karakterleri (U+00A0, U+200B, U+FEFF) temizler ve
    gereksiz boşlukları kaldırır.
    """
    if not isinstance(text, str):
        text = str(text)
    # Unicode kategori Zs (Space Separator) veya Cc (Other, Control) olan
    # karakterleri hedefler. Ayrıca yaygın sorun çıkaran karakterleri de dahil eder.
    return re.sub(r'[\s\u00A0\u200B\uFEFF]+', ' ', text).strip()

# --- Temel Hesaplama Fonksiyonları ---
# Boyutlara göre alanları hesaplar.
def calculate_area(width, length, height, is_two_story, height_2nd_floor=0):
    """
    Boyutlara göre zemin, duvar ve çatı alanlarını hesaplar.
    İki katlı yapıları da dikkate alır.
    """
    floor_area = width * length
    roof_area = floor_area

    # İki katlı yapılar için duvar alanı hesaplaması
    if is_two_story:
        wall_area = math.ceil(2 * (width + length) * (height + height_2nd_floor))
    else:
        wall_area = math.ceil(2 * (width + length) * height)

    return {"floor": floor_area, "wall": wall_area, "roof": roof_area}

# Parasal değeri formatlar.
def format_currency(value):
    """
    Parasal değeri Euro para birimi olarak biçimlendirir.
    Örnek: €1.234,56
    """
    try:
        value = round(float(value), 2)
        # Python'ın yerel formatlaması genellikle virgül kullanır,
        # bu yüzden noktaya çevirmek için geçici bir 'X' kullanılır.
        return f"€{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "€0,00"

# Parasal değeri yukarı yuvarlar.
def calculate_rounded_up_cost(value):
    """Parasal değeri yukarıya doğru iki ondalık basamağa yuvarlar."""
    if not isinstance(value, (int, float)):
        return 0.0
    return math.ceil(value * 100) / 100.0

# --- PDF İçin Gerekli Yardımcılar ---
# Logoyu URL'den çeker ve base64 olarak döndürür.
def get_company_logo_base64(url, width=180):
    """Şirket logosunu URL'den çeker ve base64 string olarak döndürür."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # HTTP hatalarını yakala
        img = PILImage.open(io.BytesIO(response.content))
        w_percent = (width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((width, h_size), PILImage.LANCZOS)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        print(f"Hata: Logo yüklenirken bir sorun oluştu: {e}")
        return None
    
# PDF için gerekli fontları kaydeder.
def register_fonts_for_pdf():
    """
    PDF için gerekli fontları kaydeder. Yerel 'fonts' klasörünü kontrol eder.
    Aksi takdirde varsayılan Helvetica'yı kullanır.
    """
    global MAIN_FONT
    try:
        font_path = "fonts/FreeSans.ttf"
        font_bold_path = "fonts/FreeSansBold.ttf"

        if os.path.exists(font_path) and os.path.exists(font_bold_path):
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            pdfmetrics.registerFont(TTFont("FreeSans", font_path))
            pdfmetrics.registerFont(TTFont("FreeSans-Bold", font_bold_path))
            pdfmetrics.registerFontFamily('FreeSans', normal='FreeSans', bold='FreeSans-Bold')
            MAIN_FONT = "FreeSans"
            print("INFO: FreeSans fontları başarıyla yüklendi.")
        else:
            print("UYARI: FreeSans font dosyaları bulunamadı. Helvetica kullanılacak.")
            MAIN_FONT = "Helvetica"
    except Exception as e:
        print(f"UYARI: Font yükleme hatası: {e}. Helvetica kullanılacak.")
        MAIN_FONT = "Helvetica"

# PDF indirme linki oluşturur (Sadece Colab/Jupyter ortamları için)
def create_pdf_download_link(pdf_bytes, filename):
    """PDF içeriği için HTML indirme linki oluşturur."""
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a class="pdf-button" href="data:application/pdf;base64,{b64}" download="{filename}">Download {filename}</a>'

