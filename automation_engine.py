import os
import json
import time
import random
import google.generativeai as genai
from amazon_paapi import AmazonApi

print("--- DEDEKTİF MODU DEVREDE: Şifre Kontrolü Yapılıyor ---")

# Şifreleri Ortamdan Çek
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
AMAZON_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_TAG = os.environ.get("AMAZON_TAG")
COUNTRY = "US" 

# 1. RAPORLAMA: Hangi anahtar var, hangisi yok?
print(f"1. Gemini Anahtarı Durumu: {'✅ VAR' if GEMINI_KEY else '❌ YOK (EKSİK)'}")
print(f"2. Amazon Access Key:      {'✅ VAR' if AMAZON_KEY else '❌ YOK (EKSİK)'}")
print(f"3. Amazon Secret Key:      {'✅ VAR' if AMAZON_SECRET else '❌ YOK (EKSİK)'}")
print(f"4. Amazon Tag (Store ID):  {'✅ VAR' if AMAZON_TAG else '❌ YOK (EKSİK)'}")

# Eksik varsa işlemi burada durdur ve rapor ver
if not all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG]):
    print("\n🚨 SONUÇ: Bazı anahtarlar eksik olduğu için Amazon'a bağlanamıyorum.")
    print("Lütfen GitHub -> Settings -> Secrets and variables -> Actions kısmını kontrol et.")
    exit(1)

print("\n✅ TÜM ANAHTARLAR TAMAM! Bağlantı deneniyor...")

# ... Kodun geri kalanı aynı (Eğer şifreler varsa çalışır) ...
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    amazon = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, COUNTRY, throttling=2)
except Exception as e:
    print(f"❌ Bağlantı Hatası: {e}")
    exit(1)

# --- KISA TEST (Sadece 1 ürün arayacak) ---
KEYWORDS = ["Womens Summer Dress"]

def main():
    search_term = random.choice(KEYWORDS)
    print(f"🔍 Test Araması Yapılıyor: '{search_term}'")
    try:
        items = amazon.search_items(keywords=search_term, item_count=1)
        for item in items:
            title = item.item_info.title.display_value
            print(f"🎉 BAŞARILI! Amazon'dan veri çekildi: {title[:30]}...")
            # Test başarılıysa dosyayı güncelleme (bozmamak için), sadece ekrana yaz.
    except Exception as e:
        print(f"❌ Amazon Hatası: {e}")

if __name__ == "__main__":
    main()
