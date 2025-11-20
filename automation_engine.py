import os
import json
import time
import random
import google.generativeai as genai
from amazon_paapi import AmazonApi

# --- GÜVENLİK VE AYARLAR ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
AMAZON_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_TAG = os.environ.get("AMAZON_TAG")
COUNTRY = "US" # Hedef Pazar: Amerika

# API Anahtarları Kontrolü
if not all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG]):
    print("❌ HATA: Anahtarlar eksik! Ama az önce çalıştığını doğruladık, tekrar kontrol et.")
    exit(1)

# API'leri Başlat
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    
    # Throttling=2 (Amazon'a saygılı ol, banlanma)
    amazon = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, COUNTRY, throttling=2)
except Exception as e:
    print(f"❌ Başlangıç Hatası: {e}")
    exit(1)

# Arama Kelimeleri (Robot her gün bunlardan birini seçer)
KEYWORDS = [
    "Womens Boho Summer Dress", "Womens Gold Layered Necklaces", 
    "Womens Crossbody Bags Trendy", "Womens Oversized Blazers", 
    "Womens High Waisted Vintage Jeans", "Womens Aviator Sunglasses",
    "Womens Chunky Gold Hoops", "Womens Cocktail Party Dresses",
    "Womens Summer Sandals Wedge", "Womens Floral Maxi Dress"
]

class AIContentGenerator:
    def generate_review(self, product_title, price):
        # Log için başlığı kısalt
        short_title = product_title[:40]
        print(f"🤖 AI İnceliyor: {short_title}...")
        
        prompt = f"""
        Act as a fashion editor for Vogue US. Write a review for: "{product_title}" (Price: {price}).
        Return ONLY a JSON object with these keys:
        - "review_text": Catchy review (max 25 words). English.
        - "styling_tip": Short fashion tip (max 10 words).
        - "ai_score": Integer between 85-99.
        - "category": One word category (e.g. Dress, Shoes, Bag).
        """
        try:
            response = model.generate_content(prompt)
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except:
            # Hata olursa varsayılan metin
            return {
                "review_text": "A trending piece that is selling fast! Perfect for the season.", 
                "styling_tip": "Pair with confidence.", 
                "ai_score": 88, 
                "category": "Fashion"
            }

def main():
    print("--- 🚀 Amazon Tam Otomasyon Modu Başlatılıyor ---")
    
    # Rastgele kategori seç
    search_term = random.choice(KEYWORDS)
    print(f"🔍 Bugünün Araması: '{search_term}'")
    
    processed_products = []
    ai_engine = AIContentGenerator()

    try:
        # Amazon'dan ilk 10 ürünü çek
        items = amazon.search_items(keywords=search_term, item_count=10)
        
        for item in items:
            try:
                # Verileri Al
                title = item.item_info.title.display_value
                link = item.detail_page_url
                
                # Resim Al
                try: image_url = item.images.primary.large.url
                except: continue # Resmi yoksa atla

                # Fiyat Al
                price = "$Check Price"
                try: 
                    if item.offers and item.offers.listings:
                        price = item.offers.listings[0].price.display_amount
                except: pass

                # Yapay Zeka Yorumu
                ai_data = ai_engine.generate_review(title, price)
                
                final_product = {
                    "title": title, "price": price, 
                    "image_url": image_url, "link": link, 
                    **ai_data
                }
                
                processed_products.append(final_product)
                print(f"✅ Eklendi: {title[:20]}...")
                time.sleep(1.5) # Bekle

            except Exception as e:
                print(f"⚠️ Ürün hatası: {e}")
                continue

    except Exception as e:
        print(f"❌ Amazon Arama Hatası: {e}")

    # Kaydet
    if processed_products:
        with open('website_data.json', 'w', encoding='utf-8') as f:
            json.dump(processed_products, f, indent=4, ensure_ascii=False)
        print(f"💾 BAŞARILI: {len(processed_products)} ürün veritabanına kaydedildi.")
    else:
        print("⚠️ Hiç ürün bulunamadı.")

if __name__ == "__main__":
    main()
