import os
import json
import time
import random

# Google Gemini Kütüphanesi (Bunu kurmak için: pip install google-generativeai)
import google.generativeai as genai

# --- KONFIGURASYON ---
# API Anahtarını buraya gireceğiz (Güvenlik için environment variable kullanmak en iyisidir)
API_KEY = os.environ.get("GEMINI_API_KEY", "BURAYA_GEMINI_API_KEY_GELECEK")

# Gemini Ayarları
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025') # Hızlı ve maliyetsiz model

# --- SAHTE AMAZON API (MODÜL 1) ---
# Henüz Amazon API anahtarımız olmadığı için (ilk 3 satış kuralı),
# sanki Amazon'dan veri çekiyormuşuz gibi davranan bir sınıf.
class MockAmazonAPI:
    def get_trending_products(self):
        print("📡 Amazon sunucularına bağlanılıyor (Simülasyon)...")
        time.sleep(1) # Gerçekçilik için bekleme
        
        # Bu veriler normalde Amazon PAAPI'den anlık çekilecek
        return [
            {
                "asin": "B08XXXXXXX",
                "title": "Women's Summer Boho Floral Midi Dress V-Neck",
                "price": "$45.99",
                "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600",
                "category": "Dresses"
            },
            {
                "asin": "B09YYYYYYY",
                "title": "Classic Aviator Sunglasses Gold Frame",
                "price": "$15.50",
                "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?q=80&w=600",
                "category": "Accessories"
            },
             {
                "asin": "B07ZZZZZZZ",
                "title": "Chunky Gold Hoops Earrings Lightweight",
                "price": "$12.99",
                "image_url": "https://images.unsplash.com/photo-1635767798638-3e25234d6c98?q=80&w=600",
                "category": "Jewelry"
            }
        ]

# --- İÇERİK ÜRETİCİ (MODÜL 2 - GEMINI AI) ---
class AIContentGenerator:
    def generate_review(self, product_title, price):
        print(f"🤖 Gemini AI çalışıyor: {product_title} inceleniyor...")
        
        # ABD Pazarı için optimize edilmiş "Prompt"
        # Gemini'ye bir moda editörü rolü veriyoruz.
        prompt = f"""
        Act as a high-end fashion editor for Vogue or Cosmopolitan US. 
        Write a short, punchy, and persuasive review for this product: "{product_title}" priced at {price}.
        
        Rules:
        1. Focus on 'Why buy this?' (Value & Style).
        2. Suggest a quick styling tip (e.g., 'Pair with white sneakers').
        3. Output format: JSON with keys 'review_text' (max 30 words), 'styling_tip' (max 15 words), and 'ai_score' (integer 80-99 based on style).
        4. Tone: Trendy, exciting, confident. English language only.
        """
        
        try:
            response = model.generate_content(prompt)
            # Gemini'nin yanıtını JSON'a çeviriyoruz (Basit string temizliği)
            text_response = response.text.replace('```json', '').replace('```', '')
            return json.loads(text_response)
        except Exception as e:
            print(f"❌ Hata: {e}")
            # Hata olursa varsayılan veri dön
            return {
                "review_text": "A must-have piece for this season. Great quality for the price.",
                "styling_tip": "Looks great with denim.",
                "ai_score": 85
            }

# --- VERİTABANI KAYDEDİCİ (MODÜL 3) ---
def save_to_database(products):
    print("💾 Veriler işleniyor ve kaydediliyor...")
    
    # Normalde burası Firebase'e yazacak.
    # Şimdilik bir JSON dosyasına kaydediyoruz (Frontend bu dosyayı okuyacak).
    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Başarılı! {len(products)} yeni ürün veritabanına eklendi.")

# --- ANA İŞ AKIŞI (WORKFLOW) ---
def main():
    print("--- Chic-Cheap Otomasyon Başlatılıyor (Hedef: ABD) ---")
    
    # 1. Adım: Ürünleri Bul
    amazon = MockAmazonAPI()
    raw_products = amazon.get_trending_products()
    
    processed_products = []
    
    # 2. Adım: Yapay Zeka ile Zenginleştir
    ai_engine = AIContentGenerator()
    
    for product in raw_products:
        ai_data = ai_engine.generate_review(product['title'], product['price'])
        
        # Verileri birleştir
        final_product = {
            **product, # Mevcut verileri al
            **ai_data, # AI verilerini ekle
            "processed_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        processed_products.append(final_product)
        
        # API limitine takılmamak için kısa bekleme
        time.sleep(1.5)

    # 3. Adım: Kaydet
    save_to_database(processed_products)

if __name__ == "__main__":
    main()