import os
import json
import time
import random
import google.generativeai as genai
from amazon_paapi import AmazonApi

# --- AYARLAR ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
AMAZON_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_TAG = os.environ.get("AMAZON_TAG")
COUNTRY = "US" 

# --- YEDEK PARAŞÜTÜ (MANUEL ÜRÜNLER) ---
# Eğer API çalışmazsa bu ürünler devreye girecek.
BACKUP_PRODUCTS = [
    {
        "title": "Womens Boho Floral V-Neck Maxi Dress",
        "price": "$39.99",
        "image_url": "https://m.media-amazon.com/images/I/71lJ8B8-qUL._AC_SY879_.jpg",
        "link": "https://www.amazon.com/dp/B09XYZ123?tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Dress"
    },
    {
        "title": "Classic Oversized Denim Jacket Blue",
        "price": "$45.50",
        "image_url": "https://m.media-amazon.com/images/I/61q+M9XzRlL._AC_SY879_.jpg",
        "link": "https://www.amazon.com/dp/B08ABC456?tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Jacket"
    },
    {
        "title": "Gold Plated Layered Chain Necklace",
        "price": "$14.99",
        "image_url": "https://m.media-amazon.com/images/I/61-wX1+D2JL._AC_SY695_.jpg",
        "link": "https://www.amazon.com/dp/B07DEF789?tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Jewelry"
    }
]

# API Başlat
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    amazon = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, COUNTRY, throttling=2)
except:
    pass # Hata olursa aşağıda kontrol edeceğiz

KEYWORDS = ["Womens Summer Dress", "Womens Gold Jewelry", "Womens Trendy Bags"]

class AIContentGenerator:
    def generate_review(self, product_title, price):
        print(f"🤖 AI İnceliyor: {product_title[:30]}...")
        prompt = f"""
        Act as a fashion editor. Review: "{product_title}" (${price}).
        Output JSON keys: 'review_text' (max 20 words), 'styling_tip' (max 10 words), 'ai_score' (85-99), 'category'.
        """
        try:
            response = model.generate_content(prompt)
            return json.loads(response.text.replace('```json', '').replace('```', '').strip())
        except:
            return {"review_text": "Stylish choice!", "styling_tip": "Wear it well.", "ai_score": 90, "category": "Fashion"}

def main():
    print("--- 🛡️ Zırhlı Otomasyon Modu ---")
    processed_products = []
    ai_engine = AIContentGenerator()
    
    # 1. API İLE DENEME
    try:
        search_term = random.choice(KEYWORDS)
        print(f"🔍 API Deneniyor: '{search_term}'")
        if all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG]):
            items = amazon.search_items(keywords=search_term, item_count=5) # Hız için 5 ürün
            for item in items:
                try:
                    title = item.item_info.title.display_value
                    link = item.detail_page_url
                    image_url = item.images.primary.large.url
                    price = item.offers.listings[0].price.display_amount if item.offers and item.offers.listings else "$Check Price"
                    
                    processed_products.append({
                        "title": title, "price": price, "image_url": image_url, "link": link
                    })
                except: continue
    except Exception as e:
        print(f"⚠️ API Hatası: {e}")

    # 2. KONTROL: API BOŞ DÖNDÜYSE YEDEKLERİ KULLAN
    if len(processed_products) == 0:
        print("🚨 API ürün bulamadı! Yedek Paraşüt açılıyor (Manuel Ürünler)...")
        processed_products = BACKUP_PRODUCTS
    else:
        print(f"✅ API Başarılı! {len(processed_products)} ürün bulundu.")

    # 3. YAPAY ZEKA İLE SÜSLE VE KAYDET
    final_data = []
    for product in processed_products:
        ai_data = ai_engine.generate_review(product['title'], product['price'])
        final_data.append({**product, **ai_data})
        time.sleep(1)

    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)
    print(f"💾 SONUÇ: {len(final_data)} ürün siteye gönderildi.")

if __name__ == "__main__":
    main()
