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

# Site Ayarları
SITE_CONFIG = {
    "adsense_id": os.environ.get("ADSENSE_ID", ""),
    "adsense_slot": os.environ.get("ADSENSE_SLOT", ""),
    "pinterest_url": os.environ.get("PINTEREST_URL", "https://www.pinterest.com/chiccheapcom")
}

# --- SANAL DEPO (30+ Ürünlük Havuz) ---
# Robot her gün buradan rastgele seçim yapacak.
INVENTORY_POOL = [
    # DRESSES
{"title": "Bohemian Floral Maxi Dress", "price": "$39.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600", "link": f"https://www.amazon.com/s?k=boho+dress&tag={REAL_AMAZON_TAG}"},
{"title": "Elegant Red Evening Gown", "price": "$59.50", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600", "link": f"https://www.amazon.com/s?k=red+evening+dress&tag={REAL_AMAZON_TAG}"},
{"title": "Casual White Summer Dress", "price": "$34.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+summer+dress&tag={REAL_AMAZON_TAG}"},
{"title": "Vintage Polka Dot Midi Dress", "price": "$42.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1612336307429-8a898d10e223?q=80&w=600", "link": f"https://www.amazon.com/s?k=vintage+dress&tag={REAL_AMAZON_TAG}"},
{"title": "Enchanted Garden: Black Floral Mesh Overlay Evening Gown", "price": "$168.42", "category": "Dress", "image_url": "https://m.media-amazon.com/images/I/912ZoPZhcdS._AC_SX569_.jpg", "link": f"https://amzn.to/4reV5Mv"},
{"title": "Classic Crew Neck Career Dress: Professional Office Wear for Women", "price": "$59.97", "category": "Dress", "image_url": "https://m.media-amazon.com/images/I/41ZV9tUZJ1L._AC_SX679_.jpg", "link": f"https://amzn.to/3XdSN2r"},
{"title": "Women's Navy Blue Sequin Lace Mother of the Bride Dress with 3/4 Sleeves", "price": "$83.57", "category": "Dress", "image_url": "https://m.media-amazon.com/images/I/816IuEGnk+L._AC_SX679_.jpg", "link": f"https://amzn.to/3K8nIdB"},
{"title": "Vintage Romance: Gold Brocade Evening Dress with Bow Waist Detail", "price": "$220", "category": "Dress", "image_url": "https://m.media-amazon.com/images/I/614bG0bdWuL._AC_SX679_.jpg", "link": f"https://amzn.to/3XHdPXh"},
{"title": "The Ultimate Fall Essential: Mocha Ribbed Trim Long Sleeve Cardigan", "price": "$32.99", "category": "Dress", "image_url": "https://m.media-amazon.com/images/I/71bAtUniWkL._AC_SY741_.jpg", "link": f"https://amzn.to/3LWjKVU"},
{"title": "White Linen Summer Dress", "price": "$34.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+linen+dress&tag={REAL_AMAZON_TAG}"},
{"title": "Black Cocktail Mini Dress", "price": "$45.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?q=80&w=600", "link": f"https://www.amazon.com/s?k=black+cocktail+dress&tag={REAL_AMAZON_TAG}"},
{"title": "Yellow Sundress Floral", "price": "$29.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?q=80&w=600", "link": f"https://www.amazon.com/s?k=yellow+sundress&tag={REAL_AMAZON_TAG}"},

# JACKETS & TOPS
{"title": "Classic Oversized Denim Jacket", "price": "$45.50", "category": "Jacket", "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=600", "link": f"https://www.amazon.com/s?k=denim+jacket&tag={REAL_AMAZON_TAG}"},
{"title": "Leather Biker Jacket Black", "price": "$89.99", "category": "Jacket", "image_url": "https://images.unsplash.com/photo-1551028919-ac7edd992304?q=80&w=600", "link": f"https://www.amazon.com/s?k=leather+jacket&tag={REAL_AMAZON_TAG}"},
{"title": "Beige Trench Coat", "price": "$65.00", "category": "Coat", "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600", "link": f"https://www.amazon.com/s?k=trench+coat&tag={REAL_AMAZON_TAG}"},
{"title": "Cozy Knitted Oversized Sweater", "price": "$35.99", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=600", "link": f"https://www.amazon.com/s?k=knit+sweater&tag={REAL_AMAZON_TAG}"},
{"title": "Retro Collegiate Vibe: Classic Color Block Letterman Style Jacket", "price": "$23.98", "category": "Jacket", "image_url": "https://m.media-amazon.com/images/I/81WUhR-bAYL._AC_SX569_.jpg", "link": f"https://amzn.to/4ifyZ8t"},
{"title": "Cabin Core Aesthetic: Rustic Plaid Zip-Up Hoodie with Cozy Fleece Lining", "price": "$75", "category": "Jacket", "image_url": "https://m.media-amazon.com/images/I/81QScF0IIZL._AC_SX679_.jpg", "link": f"https://amzn.to/48cvFWW"},
{"title": "Effortless Elegance: Loose Fit Satin Summer Top in Soft Beige", "price": "$14.87", "category": "Tops", "image_url": "https://m.media-amazon.com/images/I/71u9ikmOOGL._AC_SX569_.jpg", "link": f"https://amzn.to/49FBQ8F"},
{"title": "Festive Chic: Vintage Style Xmas Graphic T-Shirt for Holiday Parties", "price": "$19.99", "category": "Tops", "image_url": "https://m.media-amazon.com/images/I/81NV-bN5vKL._AC_SX569_.jpg", "link": f"https://amzn.to/3LWmSkC"},
{"title": "Faux Leather Biker Jacket", "price": "$89.99", "category": "Jacket", "image_url": "https://images.unsplash.com/photo-1551028919-ac7edd992304?q=80&w=600", "link": f"https://www.amazon.com/s?k=leather+jacket+women&tag={REAL_AMAZON_TAG}"},
{"title": "White Silk Blouse", "price": "$49.90", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1598554060854-b827048d7458?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+silk+blouse&tag={REAL_AMAZON_TAG}"},

# JEWELRY
{"title": "Minimalist Gold Layered Necklace", "price": "$14.99", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600", "link": f"https://www.amazon.com/s?k=gold+necklace&tag={REAL_AMAZON_TAG}"},
{"title": "Pearl Drop Earrings", "price": "$12.50", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=600", "link": f"https://www.amazon.com/s?k=pearl+earrings&tag={REAL_AMAZON_TAG}"},
{"title": "Silver Stackable Rings Set", "price": "$18.00", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?q=80&w=600", "link": f"https://www.amazon.com/s?k=silver+rings&tag={REAL_AMAZON_TAG}"},
{"title": "The Perfect Gift: Classic Crystal Bridal & Bridesmaid Earrings", "price": "$46.74", "category": "Jewelry", "image_url": "https://m.media-amazon.com/images/I/61z3JeZn+SL._AC_SY535_.jpg", "link": f"https://amzn.to/4ppaA2u"},
{"title": "Coquette Aesthetic Essential: Cute Pink Ribbon Gold Ball Stackable Bracelet", "price": "$49", "category": "Jewelry", "image_url": "https://m.media-amazon.com/images/I/611yvW2iVeL._AC_SY675_.jpg", "link": f"https://amzn.to/3KhApmo"},
{"title": "Modern Art Deco: Chevron Link Diamond Simulant Gold Bracelet", "price": "$23.95", "category": "Jewelry", "image_url": "https://m.media-amazon.com/images/I/71WicjEyxdL._AC_SY675_.jpg", "link": f"https://amzn.to/48cyiIi"},

# ACCESSORIES
{"title": "Vintage Cat Eye Sunglasses", "price": "$18.99", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600", "link": f"https://www.amazon.com/s?k=cat+eye+sunglasses&tag={REAL_AMAZON_TAG}"},
{"title": "Wide Brim Straw Beach Hat", "price": "$22.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1521335629791-ce4aec6c1d09?q=80&w=600", "link": f"https://www.amazon.com/s?k=straw+hat&tag={REAL_AMAZON_TAG}"},
{"title": "Luxury Silk Scarf", "price": "$25.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1586078436377-46714147839b?q=80&w=600", "link": f"https://www.amazon.com/s?k=silk+scarf&tag={REAL_AMAZON_TAG}"},
{"title": "Y2K Aesthetic Essential: Slim Gold Frame Hipster Sunnies", "price": "$12.74", "category": "Accessories", "image_url": "https://m.media-amazon.com/images/I/516PqKi4juL._AC_SX679_.jpg", "link": f"https://amzn.to/3XKUDrK"},
{"title": "Cowgirl Chic Essential: Boho Western Pattern Coin Purse with Keychain Strap", "price": "$22.79", "category": "Accessories", "image_url": "https://m.media-amazon.com/images/I/812+hK6191L._AC_SL1500_.jpg", "link": f"https://amzn.to/4prcLCS"},
{"title": "The Streetwear Icon: Classic Carhartt Acrylic Watch Hat", "price": "$19.99", "category": "Accessories", "image_url": "https://m.media-amazon.com/images/I/71zEr5V7AZL._AC_SX679_.jpg", "link": f"https://amzn.to/3XHpIwu"},

# SHOES
{"title": "White Summer Canvas Sneakers", "price": "$29.99", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+sneakers&tag={REAL_AMAZON_TAG}"},
{"title": "Leather Ankle Boots", "price": "$65.00", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600", "link": f"https://www.amazon.com/s?k=ankle+boots&tag={REAL_AMAZON_TAG}"},
{"title": "Strappy High Heels", "price": "$49.99", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600", "link": f"https://www.amazon.com/s?k=high+heels&tag={REAL_AMAZON_TAG}"},
{"title": "The Ultimate Fall Essential: Vintage Style Faux Leather Tall Boots in Rich Tan", "price": "$43.69", "category": "Shoes", "image_url": "https://m.media-amazon.com/images/I/713Yi+YJDKL._AC_SY695_.jpg", "link": f"https://amzn.to/4iixt5t"},
{"title": "Festive & Cozy: Embroidered Christmas Tree Teddy Slippers with Non-Slip Sole", "price": "$19.50", "category": "Shoes", "image_url": "https://m.media-amazon.com/images/I/71snjErBFxL._AC_SY695_.jpg", "link": f"https://amzn.to/4oVpWMn"},
{"title": "Comfortable Running Shoes", "price": "$55.00", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600", "link": f"https://www.amazon.com/s?k=running+shoes+women&tag={REAL_AMAZON_TAG}"},

# BAGS
{"title": "Luxury Leather Crossbody Bag", "price": "$55.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600", "link": f"https://www.amazon.com/s?k=crossbody+bag&tag={REAL_AMAZON_TAG}"},
{"title": "Chic Tote Bag", "price": "$32.50", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?q=80&w=600", "link": f"https://www.amazon.com/s?k=tote+bag&tag={REAL_AMAZON_TAG}"},
{"title": "Woven Beach Bag", "price": "$28.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600", "link": f"https://www.amazon.com/s?k=woven+bag&tag={REAL_AMAZON_TAG}"},
{"title": "Cloud-Like Comfort: Featherlight Soft Nylon Mini Travel Rucksack for Women", "price": "$24.99", "category": "Bags", "image_url": "https://m.media-amazon.com/images/I/71uB3S+DCaL._AC_SL1500_.jpg", "link": f"https://amzn.to/48895ik"},
{"title": "Black Designer Handbag", "price": "$120.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?q=80&w=600", "link": f"https://www.amazon.com/s?k=black+handbag&tag={REAL_AMAZON_TAG}"},
]

# API Başlatma Denemesi
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
            return {"review_text": "A stylish choice for the season.", "styling_tip": "Wear with confidence.", "ai_score": 92, "category": "Fashion", "pin_title": "Fashion Find", "pin_desc": "Trendy style"}

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
    print("--- 🚀 Chic-Cheap V15.0 (Mega Envanter) ---")
    processed_products = []
    ai_engine = AIContentGenerator()
    
    api_success = False
    try:
        if all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET]):
            items = amazon.search_items(keywords="Womens Fashion", item_count=2)
            # Şu an API kapalı, satış gelince burayı açacağız
    except: pass

    if not api_success:
        print("✅ Vitrin Modu: Sanal Depodan RASTGELE ürünler seçiliyor...")
        # BURASI SİHRİN OLDUĞU YER:
        # 30+ ürünlük havuzdan, rastgele 15 tanesini seç ve karıştır.
        # Böylece site her gün farklı görünür.
        count = min(len(INVENTORY_POOL), 15) 
        processed_products = random.sample(INVENTORY_POOL, count)

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

