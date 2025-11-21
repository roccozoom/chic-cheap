import os
import json
import time
import random
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import google.generativeai as genai
from amazon_paapi import AmazonApi

# --- AYARLAR ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
AMAZON_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_TAG = os.environ.get("AMAZON_TAG")
REAL_AMAZON_TAG = "chiche0420-20"
COUNTRY = "US"
BOARD_NAME = "Summer Trends 2025"

SITE_CONFIG = {
    "adsense_id": os.environ.get("ADSENSE_ID", ""),
    "adsense_slot": os.environ.get("ADSENSE_SLOT", ""),
    "pinterest_url": os.environ.get("PINTEREST_URL", "https://pinterest.com")
}

# --- YEDEK ÜRÜNLER ---
BACKUP_PRODUCTS = [
    { "title": "Bohemian Summer Floral Maxi Dress", "price": "$39.99", "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600", "link": f"https://www.amazon.com/s?k=boho+dress&tag={REAL_AMAZON_TAG}", "category": "Dress" },
    { "title": "Classic Oversized Denim Jacket", "price": "$45.50", "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=600", "link": f"https://www.amazon.com/s?k=denim+jacket&tag={REAL_AMAZON_TAG}", "category": "Jacket" },
    { "title": "Minimalist Gold Layered Necklace", "price": "$14.99", "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600", "link": f"https://www.amazon.com/s?k=gold+necklace&tag={REAL_AMAZON_TAG}", "category": "Jewelry" },
    { "title": "Vintage Cat Eye Sunglasses", "price": "$18.99", "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600", "link": f"https://www.amazon.com/s?k=cat+eye+sunglasses&tag={REAL_AMAZON_TAG}", "category": "Accessories" },
    { "title": "White Summer Canvas Sneakers", "price": "$29.99", "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+sneakers&tag={REAL_AMAZON_TAG}", "category": "Shoes" },
    { "title": "Luxury Leather Crossbody Bag", "price": "$55.00", "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600", "link": f"https://www.amazon.com/s?k=crossbody+bag&tag={REAL_AMAZON_TAG}", "category": "Bags" }
]

try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    # Throttling'i artırdık, belki yavaş sorarsak cevap verir
    amazon = AmazonApi(AMAZON_KEY, AMAZON_SECRET, REAL_AMAZON_TAG, COUNTRY, throttling=5)
except:
    pass

class AIContentGenerator:
    def generate_review(self, product_title, price):
        print(f"🤖 AI İnceliyor: {product_title[:30]}...")
        prompt = f"""
        Act as a fashion influencer. Review: "{product_title}" (${price}).
        Output JSON: 'review_text' (20 words), 'styling_tip', 'ai_score' (85-99), 'category', 'pin_title', 'pin_desc'.
        """
        try:
            response = model.generate_content(prompt)
            return json.loads(response.text.replace('```json', '').replace('```', '').strip())
        except:
            return {"review_text": "Great style!", "styling_tip": "Must have.", "ai_score": 88, "category": "Fashion", "pin_title": "Fashion Find", "pin_desc": "Cool style"}

def create_pinterest_files(products):
    rss = ET.Element("rss", version="2.0"); channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Chic-Cheap Trends"; ET.SubElement(channel, "link").text = "https://chic-cheap.com"
    
    with open('pinterest_upload.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Title', 'Description', 'Link', 'Image', 'Board'])
        writer.writeheader()
        
        for p in products:
            # XML Item
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = p.get('pin_title', p['title'])
            ET.SubElement(item, "link").text = "https://chic-cheap.com"
            enclosure = ET.SubElement(item, "enclosure"); enclosure.set("url", p['image_url']); enclosure.set("type", "image/jpeg")
            ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            
            # CSV Row
            writer.writerow({'Title': p.get('pin_title', p['title']), 'Description': p.get('pin_desc', p['title']), 'Link': "https://chic-cheap.com", 'Image': p['image_url'], 'Board': BOARD_NAME})

    ET.ElementTree(rss).write("pinterest.xml", encoding='utf-8', xml_declaration=True)

def main():
    print("--- 🧪 AMAZON API TEST MODU ---")
    processed_products = []
    ai_engine = AIContentGenerator()
    api_success = False

    try:
        if all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET]):
            print("📡 Amazon API'ye bağlanılıyor...")
            # Spesifik bir ürün arayalım (Daha kolay sonuç verir)
            items = amazon.search_items(keywords="Womens Dress", item_count=3)
            
            if items:
                print("🎉 BAŞARILI! Amazon veri gönderdi!")
                api_success = True
                for item in items:
                    try:
                        title = item.item_info.title.display_value
                        link = item.detail_page_url
                        img = item.images.primary.large.url
                        price = item.offers.listings[0].price.display_amount if item.offers else "$Check"
                        processed_products.append({"title": title, "price": price, "image_url": img, "link": link})
                    except: continue
            else:
                print("⚠️ Amazon bağlandı ama ürün listesi boş döndü.")
    except Exception as e:
        print(f"❌ AMAZON HATASI: {e}")
        print("👉 Bu hata, henüz satış yapılmadığı için API'nin kilitli olduğunu gösterir.")

    if not processed_products:
        print("🔄 Yedek ürünler devreye alınıyor...")
        processed_products = BACKUP_PRODUCTS

    final_data = []
    for product in processed_products:
        ai_data = ai_engine.generate_review(product['title'], product['price'])
        final_data.append({**product, **ai_data})
        time.sleep(0.5)

    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump({"config": SITE_CONFIG, "products": final_data}, f, indent=4)
    
    create_pinterest_files(final_data)
    print("💾 İşlem tamamlandı.")

if __name__ == "__main__":
    main()
