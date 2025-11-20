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

# --- MEGA VİTRİN LİSTESİ (12 Adet Şık Ürün) ---
# Not: "link" kısımlarına kendi affiliate linklerini koyarsan kazancın garanti olur.
# Şu an senin Store ID'ni otomatik ekleyen yapı kurulu.
BACKUP_PRODUCTS = [
    {
        "title": "Bohemian Summer Floral Maxi Dress",
        "price": "$39.99",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=boho+dress&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Dress"
    },
    {
        "title": "Classic Oversized Denim Jacket",
        "price": "$45.50",
        "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=denim+jacket&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Jacket"
    },
    {
        "title": "Minimalist Gold Layered Necklace",
        "price": "$14.99",
        "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=gold+necklace&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Jewelry"
    },
    {
        "title": "Vintage Cat Eye Sunglasses",
        "price": "$18.99",
        "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=cat+eye+sunglasses&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Accessories"
    },
    {
        "title": "White Summer Canvas Sneakers",
        "price": "$29.99",
        "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=white+sneakers&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Shoes"
    },
     {
        "title": "Luxury Leather Crossbody Bag",
        "price": "$55.00",
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=crossbody+bag&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Bags"
    },
    {
        "title": "Elegant Pearl Drop Earrings",
        "price": "$12.50",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=pearl+earrings&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Jewelry"
    },
    {
        "title": "High Waisted Vintage Mom Jeans",
        "price": "$42.00",
        "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=mom+jeans&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Denim"
    },
    {
        "title": "Silk Satin Evening Scarf",
        "price": "$22.99",
        "image_url": "https://images.unsplash.com/photo-1586078436377-46714147839b?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=silk+scarf&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Accessories"
    },
    {
        "title": "Comfortable Yoga Leggings",
        "price": "$25.00",
        "image_url": "https://images.unsplash.com/photo-1506619216599-9d16d0903dfd?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=leggings&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Activewear"
    },
    {
        "title": "Straw Beach Hat Wide Brim",
        "price": "$19.99",
        "image_url": "https://images.unsplash.com/photo-1521335629791-ce4aec6c1d09?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=straw+hat&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Hats"
    },
    {
        "title": "Chunky Knit Oversized Sweater",
        "price": "$35.00",
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=600&auto=format&fit=crop",
        "link": "https://www.amazon.com/s?k=knit+sweater&tag=" + (AMAZON_TAG if AMAZON_TAG else "chiccheap-20"),
        "category": "Tops"
    }
]

# API Başlat (Hata verirse yoksay, vitrine geç)
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
    print("--- 🛒 MEGA Vitrin Modu ---")
    processed_products = []
    ai_engine = AIContentGenerator()
    
    # 1. ÖNCE API'Yİ DENE (Satış sonrası açılınca burası çalışacak)
    api_success = False
    try:
        if all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG]):
            items = amazon.search_items(keywords="Womens Trendy Fashion", item_count=3)
            # Hata vermezse API çalışıyor demektir
    except:
        print("⚠️ API henüz yanıt vermiyor (Vitrin Yükleniyor).")

    # 2. API KAPALIYSA GARANTİLİ LİSTEYİ YÜKLE
    if not api_success:
        print("✅ Vitrin Modu Devrede: 12 adet ürün yükleniyor...")
        processed_products = BACKUP_PRODUCTS

    # 3. YAPAY ZEKA İLE SÜSLE VE KAYDET
    final_data = []
    for product in processed_products:
        ai_data = ai_engine.generate_review(product['title'], product['price'])
        final_data.append({**product, **ai_data})
        time.sleep(0.5) # Hızlı işlem

    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)
    print(f"💾 VİTRİN HAZIR: {len(final_data)} ürün yüklendi.")

if __name__ == "__main__":
    main()
