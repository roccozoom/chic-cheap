import os
import json
import time
import google.generativeai as genai

# --- AYARLAR ---
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

# --- MANUEL SEÇİLMİŞ ÜRÜNLER (İLK 3 SATIŞ İÇİN) ---
# Burayı sen dolduracaksın! Amazon'dan bulduğun gerçek linkleri yapıştır.
MANUAL_PRODUCTS = [
    {
        "title": "Boho Floral V-Neck Summer Beach Dress",
        "price": "$34.99",
        "image_url": "https://m.media-amazon.com/images/I/71lJ8B8-qUL._AC_SY879_.jpg", # Gerçek Amazon resim linki
        "link": "https://amzn.to/EXAMPLE1", # SENİN AFFILIATE LINKIN BURAYA
        "category": "Dresses"
    },
    {
        "title": "Classic Oversized Denim Jacket",
        "price": "$42.50",
        "image_url": "https://m.media-amazon.com/images/I/61q+M9XzRlL._AC_SY879_.jpg",
        "link": "https://amzn.to/EXAMPLE2", # SENİN AFFILIATE LINKIN BURAYA
        "category": "Jackets"
    },
    # İstediğin kadar ürün ekleyebilirsin...
]

class AIContentGenerator:
    def generate_review(self, product_title, price):
        print(f"🤖 Gemini AI çalışıyor: {product_title} inceleniyor...")
        prompt = f"""
        Act as a high-end fashion editor for Vogue US. 
        Write a persuasive review for: "{product_title}" (${price}).
        
        Output JSON with keys: 'review_text' (max 30 words, catchy), 'styling_tip' (short), 'ai_score' (85-99).
        Tone: Excited, trendy. No markdown.
        """
        try:
            response = model.generate_content(prompt)
            clean_text = response.text.replace('```json', '').replace('```', '')
            return json.loads(clean_text)
        except:
            return {"review_text": "Trending piece!", "styling_tip": "Must have.", "ai_score": 88}

def main():
    processed_products = []
    ai_engine = AIContentGenerator()
    
    print(f"--- Hibrit Mod: {len(MANUAL_PRODUCTS)} ürün işleniyor ---")

    for product in MANUAL_PRODUCTS:
        ai_data = ai_engine.generate_review(product['title'], product['price'])
        final_product = {**product, **ai_data}
        processed_products.append(final_product)
        time.sleep(2) # API nezaket süresi

    # Kaydet
    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump(processed_products, f, indent=4, ensure_ascii=False)
    print("✅ Site verisi güncellendi!")

if __name__ == "__main__":
    main()
