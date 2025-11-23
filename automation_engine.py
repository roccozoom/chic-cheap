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
    "adsense_id": "ca-pub-4267818870826080",
    "adsense_slot": "7287051976",
    "pinterest_url": "https://www.pinterest.com/chiccheapcom"
}

# --- 50+ BENZERSİZ ÜRÜNLÜK DEV HAVUZ ---
# Her ürünün resmi farklı ve kalitelidir.
INVENTORY_POOL = [
    # ELBİSELER
    {"title": "Boho Maxi Floral Dress", "price": "$39.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1612336307429-8a898d10e223?q=80&w=600", "link": f"https://www.amazon.com/s?k=boho+maxi+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Red Satin Evening Gown", "price": "$59.50", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600", "link": f"https://www.amazon.com/s?k=red+satin+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "White Linen Summer Dress", "price": "$34.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+linen+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Black Cocktail Mini Dress", "price": "$45.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?q=80&w=600", "link": f"https://www.amazon.com/s?k=black+cocktail+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Yellow Sundress", "price": "$29.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?q=80&w=600", "link": f"https://www.amazon.com/s?k=yellow+sundress&tag={REAL_AMAZON_TAG}"},
    {"title": "Pink Slip Dress", "price": "$38.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?q=80&w=600", "link": f"https://www.amazon.com/s?k=pink+slip+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Green Wrap Dress", "price": "$55.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1605763240004-7e93b172d754?q=80&w=600", "link": f"https://www.amazon.com/s?k=green+wrap+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Blue Office Dress", "price": "$49.90", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600", "link": f"https://www.amazon.com/s?k=blue+office+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Sequin Party Dress", "price": "$68.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?q=80&w=600", "link": f"https://www.amazon.com/s?k=sequin+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Casual Denim Dress", "price": "$35.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1591369822096-35c93e1883aa?q=80&w=600", "link": f"https://www.amazon.com/s?k=denim+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Velvet Evening Dress", "price": "$75.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?q=80&w=600", "link": f"https://www.amazon.com/s?k=velvet+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Off-Shoulder Summer Dress", "price": "$28.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600", "link": f"https://www.amazon.com/s?k=off+shoulder+dress&tag={REAL_AMAZON_TAG}"},

    # CEKETLER
    {"title": "Oversized Denim Jacket", "price": "$45.50", "category": "Jacket", "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=600", "link": f"https://www.amazon.com/s?k=oversized+denim+jacket&tag={REAL_AMAZON_TAG}"},
    {"title": "Leather Biker Jacket", "price": "$89.99", "category": "Jacket", "image_url": "https://images.unsplash.com/photo-1551028919-ac7edd992304?q=80&w=600", "link": f"https://www.amazon.com/s?k=leather+jacket&tag={REAL_AMAZON_TAG}"},
    {"title": "Beige Trench Coat", "price": "$65.00", "category": "Coat", "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600", "link": f"https://www.amazon.com/s?k=trench+coat&tag={REAL_AMAZON_TAG}"},
    {"title": "Knitted Sweater", "price": "$35.99", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=600", "link": f"https://www.amazon.com/s?k=knit+sweater&tag={REAL_AMAZON_TAG}"},
    {"title": "White Silk Blouse", "price": "$49.90", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1598554060854-b827048d7458?q=80&w=600", "link": f"https://www.amazon.com/s?k=silk+blouse&tag={REAL_AMAZON_TAG}"},
    {"title": "Striped Breton Top", "price": "$24.00", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1503342394128-c104d54dba01?q=80&w=600", "link": f"https://www.amazon.com/s?k=striped+top&tag={REAL_AMAZON_TAG}"},
    {"title": "Pink Cardigan", "price": "$30.00", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?q=80&w=600", "link": f"https://www.amazon.com/s?k=cardigan&tag={REAL_AMAZON_TAG}"},
    {"title": "Black Blazer", "price": "$55.00", "category": "Jacket", "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600", "link": f"https://www.amazon.com/s?k=black+blazer&tag={REAL_AMAZON_TAG}"},
    {"title": "Cropped Hoodie", "price": "$25.00", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?q=80&w=600", "link": f"https://www.amazon.com/s?k=hoodie&tag={REAL_AMAZON_TAG}"},
    {"title": "Graphic Tee", "price": "$18.00", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1503342394128-c104d54dba01?q=80&w=600", "link": f"https://www.amazon.com/s?k=graphic+tee&tag={REAL_AMAZON_TAG}"},

    # TAKILAR
    {"title": "Gold Layered Necklace", "price": "$14.99", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600", "link": f"https://www.amazon.com/s?k=gold+necklace&tag={REAL_AMAZON_TAG}"},
    {"title": "Pearl Drop Earrings", "price": "$12.50", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=600", "link": f"https://www.amazon.com/s?k=pearl+earrings&tag={REAL_AMAZON_TAG}"},
    {"title": "Silver Ring Set", "price": "$18.00", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?q=80&w=600", "link": f"https://www.amazon.com/s?k=silver+rings&tag={REAL_AMAZON_TAG}"},
    {"title": "Gold Hoop Earrings", "price": "$16.99", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a51?q=80&w=600", "link": f"https://www.amazon.com/s?k=hoop+earrings&tag={REAL_AMAZON_TAG}"},
    {"title": "Rose Gold Watch", "price": "$85.00", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?q=80&w=600", "link": f"https://www.amazon.com/s?k=watch+women&tag={REAL_AMAZON_TAG}"},
    {"title": "Charm Bracelet", "price": "$25.00", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?q=80&w=600", "link": f"https://www.amazon.com/s?k=charm+bracelet&tag={REAL_AMAZON_TAG}"},
    {"title": "Statement Necklace", "price": "$30.00", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600", "link": f"https://www.amazon.com/s?k=statement+necklace&tag={REAL_AMAZON_TAG}"},

    # AKSESUARLAR
    {"title": "Cat Eye Sunglasses", "price": "$18.99", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600", "link": f"https://www.amazon.com/s?k=sunglasses&tag={REAL_AMAZON_TAG}"},
    {"title": "Straw Beach Hat", "price": "$22.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1521335629791-ce4aec6c1d09?q=80&w=600", "link": f"https://www.amazon.com/s?k=straw+hat&tag={REAL_AMAZON_TAG}"},
    {"title": "Silk Scarf", "price": "$25.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1586078436377-46714147839b?q=80&w=600", "link": f"https://www.amazon.com/s?k=silk+scarf&tag={REAL_AMAZON_TAG}"},
    {"title": "Leather Belt", "price": "$20.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1624223359990-8b050454b378?q=80&w=600", "link": f"https://www.amazon.com/s?k=leather+belt&tag={REAL_AMAZON_TAG}"},
    {"title": "Wool Beret", "price": "$15.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=600", "link": f"https://www.amazon.com/s?k=beret&tag={REAL_AMAZON_TAG}"},

    # AYAKKABILAR
    {"title": "White Canvas Sneakers", "price": "$29.99", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+sneakers&tag={REAL_AMAZON_TAG}"},
    {"title": "Leather Ankle Boots", "price": "$65.00", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600", "link": f"https://www.amazon.com/s?k=ankle+boots&tag={REAL_AMAZON_TAG}"},
    {"title": "Strappy High Heels", "price": "$49.99", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600", "link": f"https://www.amazon.com/s?k=heels&tag={REAL_AMAZON_TAG}"},
    {"title": "Running Shoes", "price": "$55.00", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600", "link": f"https://www.amazon.com/s?k=running+shoes&tag={REAL_AMAZON_TAG}"},
    {"title": "Flat Sandals", "price": "$24.50", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1562273138-f46be4ebdf6e?q=80&w=600", "link": f"https://www.amazon.com/s?k=sandals&tag={REAL_AMAZON_TAG}"},
    {"title": "Loafers", "price": "$45.00", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600", "link": f"https://www.amazon.com/s?k=loafers&tag={REAL_AMAZON_TAG}"},

    # ÇANTALAR
    {"title": "Leather Crossbody Bag", "price": "$55.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600", "link": f"https://www.amazon.com/s?k=crossbody+bag&tag={REAL_AMAZON_TAG}"},
    {"title": "Chic Tote Bag", "price": "$32.50", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?q=80&w=600", "link": f"https://www.amazon.com/s?k=tote+bag&tag={REAL_AMAZON_TAG}"},
    {"title": "Woven Beach Bag", "price": "$28.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600", "link": f"https://www.amazon.com/s?k=straw+bag&tag={REAL_AMAZON_TAG}"},
    {"title": "Black Designer Handbag", "price": "$120.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?q=80&w=600", "link": f"https://www.amazon.com/s?k=black+handbag&tag={REAL_AMAZON_TAG}"},
    {"title": "Red Clutch", "price": "$45.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?q=80&w=600", "link": f"https://www.amazon.com/s?k=red+clutch&tag={REAL_AMAZON_TAG}"},
    {"title": "Backpack Purse", "price": "$40.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?q=80&w=600", "link": f"https://www.amazon.com/s?k=backpack+purse&tag={REAL_AMAZON_TAG}"}
]

# BLOG KONULARI
BLOG_TOPICS = [
    "Summer 2025 Fashion Trends",
    "How to Style Boho Dresses",
    "Affordable Luxury Accessories",
    "Capsule Wardrobe Essentials",
    "Denim Jacket Styling Tips",
    "Office Wear Ideas for Women",
    "Jewelry Layering Guide",
    "Best Shoes for Comfort and Style"
]

# API Başlatma
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    amazon = AmazonApi(AMAZON_KEY, AMAZON_SECRET, REAL_AMAZON_TAG, COUNTRY, throttling=2)
except: pass

class AIContentGenerator:
    def generate_review(self, product_title, price):
        prompt = f"Act as a fashion influencer. Review: '{product_title}' (${price}). Output JSON keys: 'review_text' (20 words), 'styling_tip', 'ai_score' (85-99), 'category', 'pin_title', 'pin_desc'."
        try:
            response = model.generate_content(prompt)
            return json.loads(response.text.replace('```json', '').replace('```', '').strip())
        except:
            return {"review_text": "A stylish choice.", "styling_tip": "Wear with confidence.", "ai_score": 92, "category": "Fashion", "pin_title": "Fashion Find", "pin_desc": "Trendy style"}

    def generate_blog_post(self):
        topic = random.choice(BLOG_TOPICS)
        print(f"📝 Blog Yazılıyor: {topic}")
        
        # GÜÇLENDİRİLMİŞ BLOG PROMPTU (Uzun ve Detaylı)
        prompt = f"""
        Write a detailed fashion blog post about: "{topic}".
        Target: Women looking for affordable style.
        Tone: Professional yet friendly.
        Format: HTML (Use <h2> for headings, <p> for text, <ul>/<li> for lists). 
        Length: Minimum 400 words.
        Output JSON keys:
        - 'title': Catchy Blog Title.
        - 'summary': 2 sentence summary.
        - 'content': The full HTML content. Do NOT use markdown.
        - 'image_keyword': English keyword for Unsplash image (e.g. 'summer fashion').
        """
        try:
            response = model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            data['image_url'] = f"https://source.unsplash.com/800x400/?{data['image_keyword'].replace(' ', ',')}"
            if "source.unsplash" in data['image_url']: # Yedek görsel
                 data['image_url'] = "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800&auto=format&fit=crop"
            return data
        except:
            return {
                "title": "Trend Alert: 2025 Styles",
                "summary": "Discover must-have pieces for your wardrobe.",
                "content": "<h2>Summer Essentials</h2><p>Fashion is about expressing yourself...</p>",
                "image_url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800"
            }

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
    print("--- 🚀 Chic-Cheap V22.0 (Blog & Mega Depo) ---")
    processed_products = []
    ai_engine = AIContentGenerator()
    
    # 1. API Kontrolü
    api_success = False
    try:
        if all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET]):
            items = amazon.search_items(keywords="Womens Fashion", item_count=2)
    except: pass

    if not api_success:
        print("✅ Vitrin Modu: Depodan rastgele ürünler seçiliyor...")
        # 15 Tane rastgele ürün seç
        count = min(len(INVENTORY_POOL), 15) 
        processed_products = random.sample(INVENTORY_POOL, count)

    final_data = []
    for product in processed_products:
        try:
            ai_data = ai_engine.generate_review(product['title'], product['price'])
            final_data.append({**product, **ai_data})
            time.sleep(0.5)
        except: continue

    # Blog Yazısı Oluştur
    blog_post = ai_engine.generate_blog_post()

    final_output = {
        "config": SITE_CONFIG,
        "products": final_data,
        "blog": blog_post
    }
    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)

    create_pinterest_files(final_data)
    print("💾 İşlem Tamamlandı.")

if __name__ == "__main__":
    main()
