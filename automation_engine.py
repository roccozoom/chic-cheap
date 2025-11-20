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

# Pano adını buraya yazdım, Pinterest'tekiyle birebir aynı olmalı.
BOARD_NAME = "Summer Trends 2025" 

SITE_CONFIG = {
    "adsense_id": os.environ.get("ADSENSE_ID", ""),
    "adsense_slot": os.environ.get("ADSENSE_SLOT", ""),
    "pinterest_url": os.environ.get("PINTEREST_URL", "https://pinterest.com")
}

# --- YEDEK ÜRÜNLER ---
BACKUP_PRODUCTS = [
    {
        "title": "Bohemian Summer Floral Maxi Dress",
        "price": "$39.99",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600&auto=format&fit=crop",
        "link": f"https://www.amazon.com/s?k=boho+dress&tag={REAL_AMAZON_TAG}&language=en_US",
        "category": "Dress"
    },
    {
        "title": "Classic Oversized Denim Jacket",
        "price": "$45.50",
        "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=600&auto=format&fit=crop",
        "link": f"https://www.amazon.com/s?k=denim+jacket&tag={REAL_AMAZON_TAG}&language=en_US",
        "category": "Jacket"
    },
    {
        "title": "Minimalist Gold Layered Necklace",
        "price": "$14.99",
        "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600&auto=format&fit=crop",
        "link": f"https://www.amazon.com/s?k=gold+necklace&tag={REAL_AMAZON_TAG}&language=en_US",
        "category": "Jewelry"
    },
    {
        "title": "Vintage Cat Eye Sunglasses",
        "price": "$18.99",
        "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600&auto=format&fit=crop",
        "link": f"https://www.amazon.com/s?k=cat+eye+sunglasses&tag={REAL_AMAZON_TAG}&language=en_US",
        "category": "Accessories"
    },
    {
        "title": "White Summer Canvas Sneakers",
        "price": "$29.99",
        "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600&auto=format&fit=crop",
        "link": f"https://www.amazon.com/s?k=white+sneakers&tag={REAL_AMAZON_TAG}&language=en_US",
        "category": "Shoes"
    },
     {
        "title": "Luxury Leather Crossbody Bag",
        "price": "$55.00",
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600&auto=format&fit=crop",
        "link": f"https://www.amazon.com/s?k=crossbody+bag&tag={REAL_AMAZON_TAG}&language=en_US",
        "category": "Bags"
    }
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
        Act as a fashion influencer. Analyze: "{product_title}" (${price}).
        Output JSON keys:
        - 'review_text': Web review (max 20 words).
        - 'styling_tip': Short tip.
        - 'ai_score': 85-99.
        - 'category': Category name.
        - 'pin_title': Catchy Pinterest Title (max 50 chars).
        - 'pin_desc': Pinterest Description with hashtags.
        """
        try:
            response = model.generate_content(prompt)
            return json.loads(response.text.replace('```json', '').replace('```', '').strip())
        except:
            return {
                "review_text": "Stylish choice!", "styling_tip": "Wear with confidence.", "ai_score": 90, "category": "Fashion",
                "pin_title": "Trendy Fashion Find", "pin_desc": "Check out this style #fashion"
            }

def create_pinterest_feed(products):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Chic-Cheap Trends"
    ET.SubElement(channel, "link").text = "https://chic-cheap.com"
    ET.SubElement(channel, "description").text = "Daily Fashion Deals"

    for p in products:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = p.get('pin_title', p['title'])
        ET.SubElement(item, "link").text = "https://chic-cheap.com"
        ET.SubElement(item, "description").text = p.get('pin_desc', p['title'])
        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", p['image_url'])
        enclosure.set("type", "image/jpeg")
        ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    tree = ET.ElementTree(rss)
    tree.write("pinterest.xml", encoding='utf-8', xml_declaration=True)

# --- CSV OLUŞTURUCU (V10 - ZIRHLI FORMAT) ---
def create_pinterest_csv(products):
    print("📊 Pinterest CSV Dosyası Hazırlanıyor (UTF-8-SIG + QuoteAll)...")
    
    # 1. utf-8-sig: Excel ve Pinterest'in karakterleri tanımasını sağlar (BOM)
    # 2. QUOTE_ALL: Her hücreyi "..." içine alır, böylece virgüller karışmaz.
    with open('pinterest_upload.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Title', 'Description', 'Link', 'Image', 'Board']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for p in products:
            writer.writerow({
                'Title': p.get('pin_title', p['title']),
                'Description': p.get('pin_desc', p['title']),
                'Link': "https://chic-cheap.com",
                'Image': p['image_url'],
                'Board': BOARD_NAME 
            })
    print("✅ pinterest_upload.csv oluşturuldu!")

def main():
    print("--- 🚀 Chic-Cheap V10.0 (Final CSV) ---")
    processed_products = []
    ai_engine = AIContentGenerator()
    
    api_success = False
    try:
        if all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET]):
            items = amazon.search_items(keywords="Womens Fashion", item_count=1)
    except:
        pass

    if not api_success:
        print("✅ Vitrin Modu: Yedek ürünler işleniyor...")
        processed_products = BACKUP_PRODUCTS

    final_data = []
    for product in processed_products:
        try:
            ai_data = ai_engine.generate_review(product['title'], product['price'])
            final_data.append({**product, **ai_data})
            time.sleep(0.5)
        except:
            continue

    final_output = {
        "config": SITE_CONFIG,
        "products": final_data
    }

    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
    
    create_pinterest_feed(final_data)
    create_pinterest_csv(final_data)
    
    print(f"💾 İŞLEM TAMAM: {len(final_data)} ürün işlendi.")

if __name__ == "__main__":
    main()
