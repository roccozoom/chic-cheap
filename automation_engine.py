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

# --- SANAL DEPO (GENİŞLETİLMİŞ ENVANTER) ---
# Buradaki ürün havuzundan her gün rastgele seçim yapılacak.
INVENTORY_POOL = [
    # DRESSES
    {"title": "Bohemian Floral Maxi Dress", "price": "$39.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600", "link": f"https://www.amazon.com/s?k=boho+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Elegant Red Evening Gown", "price": "$59.50", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600", "link": f"https://www.amazon.com/s?k=red+evening+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Casual White Summer Dress", "price": "$34.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+summer+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Vintage Polka Dot Midi Dress", "price": "$42.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1612336307429-8a898d10e223?q=80&w=600", "link": f"https://www.amazon.com/s?k=vintage+dress&tag={REAL_AMAZON_TAG}"},
    
    # JACKETS & TOPS
    {"title": "Classic Oversized Denim Jacket", "price": "$45.50", "category": "Jacket", "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=600", "link": f"https://www.amazon.com/s?k=denim+jacket&tag={REAL_AMAZON_TAG}"},
    {"title": "Leather Biker Jacket Black", "price": "$89.99", "category": "Jacket", "image_url": "https://images.unsplash.com/photo-1551028919-ac7edd992304?q=80&w=600", "link": f"https://www.amazon.com/s?k=leather+jacket&tag={REAL_AMAZON_TAG}"},
    {"title": "Beige Trench Coat", "price": "$65.00", "category": "Coat", "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600", "link": f"https://www.amazon.com/s?k=trench+coat&tag={REAL_AMAZON_TAG}"},
    {"title": "Cozy Knitted Oversized Sweater", "price": "$35.99", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=600", "link": f"https://www.amazon.com/s?k=knit+sweater&tag={REAL_AMAZON_TAG}"},

    # JEWELRY
    {"title": "Minimalist Gold Layered Necklace", "price": "$14.99", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600", "link": f"https://www.amazon.com/s?k=gold+necklace&tag={REAL_AMAZON_TAG}"},
    {"title": "Pearl Drop Earrings", "price": "$12.50", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=600", "link": f"https://www.amazon.com/s?k=pearl+earrings&tag={REAL_AMAZON_TAG}"},
    {"title": "Silver Stackable Rings Set", "price": "$18.00", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?q=80&w=600", "link": f"https://www.amazon.com/s?k=silver+rings&tag={REAL_AMAZON_TAG}"},
    
    # ACCESSORIES
    {"title": "Vintage Cat Eye Sunglasses", "price": "$18.99", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600", "link": f"https://www.amazon.com/s?k=cat+eye+sunglasses&tag={REAL_AMAZON_TAG}"},
    {"title": "Wide Brim Straw Beach Hat", "price": "$22.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1521335629791-ce4aec6c1d09?q=80&w=600", "link": f"https://www.amazon.com/s?k=straw+hat&tag={REAL_AMAZON_TAG}"},
    {"title": "Luxury Silk Scarf", "price": "$25.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1586078436377-46714147839b?q=80&w=600", "link": f"https://www.amazon.com/s?k=silk+scarf&tag={REAL_AMAZON_TAG}"},

    # SHOES
    {"title": "White Summer Canvas Sneakers", "price": "$29.99", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+sneakers&tag={REAL_AMAZON_TAG}"},
    {"title": "Leather Ankle Boots", "price": "$65.00", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600", "link": f"https://www.amazon.com/s?k=ankle+boots&tag={REAL_AMAZON_TAG}"},
    {"title": "Strappy High Heels", "price": "$49.99", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600", "link": f"https://www.amazon.com/s?k=high+heels&tag={REAL_AMAZON_TAG}"},

    # BAGS
    {"title": "Luxury Leather Crossbody Bag", "price": "$55.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600", "link": f"https://www.amazon.com/s?k=crossbody+bag&tag={REAL_AMAZON_TAG}"},
    {"title": "Chic Tote Bag", "price": "$32.50", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?q=80&w=600", "link": f"https://www.amazon.com/s?k=tote+bag&tag={REAL_AMAZON_TAG}"},
    {"title": "Woven Beach Bag", "price": "$28.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600", "link": f"https://www.amazon.com/s?k=woven+bag&tag={REAL_AMAZON_TAG}"}
]

try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    amazon = AmazonApi(AMAZON_KEY, AMAZON_SECRET, REAL_AMAZON_TAG, COUNTRY, throttling=2)
except:
    pass

class AIContentGenerator:
    def generate_review(self, product_title, price):
        print(f"🤖 AI İnceliyor: {product_title[:30]}...")
        prompt = f"""
        Act as a fashion influencer. Review: "{product_title}" (${price}).
        Output JSON keys: 'review_text' (20 words), 'styling_tip', 'ai_score' (85-99), 'category', 'pin_title', 'pin_desc'.
        """
        try:
            response = model.generate_content(prompt)
            return json.loads(response.text.replace('```json', '').replace('```', '').strip())
        except:
            return {"review_text": "Stylish choice!", "styling_tip": "Wear with confidence.", "ai_score": 90, "category": "Fashion", "pin_title": "Fashion Find", "pin_desc": "Cool style"}

def create_pinterest_files(products):
    rss = ET.Element("rss", version="2.0"); channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Chic-Cheap Trends"; ET.SubElement(channel, "link").text = "https://chic-cheap.com"
    
    with open('pinterest_upload.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Title', 'Description', 'Link', 'Image', 'Board'], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for p in products:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = p.get('pin_title', p['title'])
            ET.SubElement(item, "link").text = "https://chic-cheap.com"
            enclosure = ET.SubElement(item, "enclosure"); enclosure.set("url", p['image_url']); enclosure.set("type", "image/jpeg")
            ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            writer.writerow({'Title': p.get('pin_title', p['title']), 'Description': p.get('pin_desc', p['title']), 'Link': "https://chic-cheap.com", 'Image': p['image_url'], 'Board': BOARD_NAME})
    ET.ElementTree(rss).write("pinterest.xml", encoding='utf-8', xml_declaration=True)

def main():
    print("--- 🚀 Chic-Cheap V12.0 (Genişletilmiş Envanter) ---")
    processed_products = []
    ai_engine = AIContentGenerator()
    
    # 1. API Denemesi (Satış gelince açılacak)
    api_success = False
    try:
        if all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET]):
            items = amazon.search_items(keywords="Womens Fashion", item_count=2)
            # Şu an kapalı, satış gelince burayı açarız
    except: pass

    if not api_success:
        print("✅ Vitrin Modu: Depodan rastgele ürünler seçiliyor...")
        # BURASI YENİ: Havuzdan rastgele 12 ürün seç
        # Her gün farklı kombinasyon olacak!
        processed_products = random.sample(INVENTORY_POOL, min(len(INVENTORY_POOL), 12))

    final_data = []
    for product in processed_products:
        try:
            ai_data = ai_engine.generate_review(product['title'], product['price'])
            final_data.append({**product, **ai_data})
            time.sleep(0.5)
        except: continue

    final_output = {"config": SITE_CONFIG, "products": final_data}
    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
    
    create_pinterest_files(final_data)
    print(f"💾 İŞLEM TAMAM: {len(final_data)} ürün işlendi.")

if __name__ == "__main__":
    main()
