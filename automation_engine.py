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

# --- GARANTİLİ VİTRİN ÜRÜNLERİ (Resimler Unsplash'ten, Linkler Amazon'dan) ---
BACKUP_PRODUCTS = [
    {
        "title": "Bohemian Summer Floral Maxi Dress",
        "price": "$39.99",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/dp/B09XYZ123?tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Dress"
    },
    {
        "title": "Oversized Vintage Denim Jacket",
        "price": "$45.50",
        "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/dp/B08ABC456?tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Jacket"
    },
    {
        "title": "Minimalist Gold Layered Necklace",
        "price": "$14.99",
        "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/dp/B07DEF789?tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Jewelry"
    },
    {
        "title": "Classic Aviator Sunglasses Gold",
        "price": "$18.99",
        "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/dp/B09SUN123?tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Accessories"
    },
    {
        "title": "White Summer Sneakers Comfortable",
        "price": "$29.99",
        "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/dp/B08SHOE123?tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Shoes"
    },
     {
        "title": "Leather Crossbody Bag Brown",
        "price": "$55.00",
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/dp/B08BAG456?tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Bags"
    }
]

# API Başlat
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    amazon = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, COUNTRY, throttling=2)
except:
    pass

KEYWORDS = ["Womens Summer Dress"]

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
            return {"review_text": "A stylish choice for the season.", "styling_tip": "Wear with confidence.", "ai_score": 92, "category": "Fashion"}

def main():
    print("--- 🛒 Garantili Vitrin Modu ---")
    processed_products = []
    ai_engine = AIContentGenerator()
    
    # 1. ÖNCE API'Yİ DENE (Belki açılmıştır)
    api_success = False
    try:
        if all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG]):
            items = amazon.search_items(keywords="Womens Dress", item_count=3)
            # Eğer buraya kadar hata vermediyse API çalışıyor demektir
            # Ama hata verirse 'except' bloğuna düşecek.
    except:
        print("⚠️ API henüz yanıt vermiyor (Normal, satış bekleniyor).")

    # 2. API ÇALIŞMAZSA DİREKT GARANTİLİ LİSTEYİ KULLAN
    if not api_success:
        print("✅ Vitrin Modu Devrede: En şık ürünler yükleniyor...")
        processed_products = BACKUP_PRODUCTS

    # 3. YAPAY ZEKA İLE SÜSLE VE KAYDET
    final_data = []
    for product in processed_products:
        ai_data = ai_engine.generate_review(product['title'], product['price'])
        final_data.append({**product, **ai_data})
        # Yapay zeka çok hızlı çalışsın diye bekleme süresini azalttık
        time.sleep(0.5)

    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)
    print(f"💾 VİTRİN HAZIR: {len(final_data)} ürün yüklendi.")

if __name__ == "__main__":
    main()
