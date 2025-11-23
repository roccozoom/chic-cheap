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
    "pinterest_url": os.environ.get("PINTEREST_URL", "https://pinterest.com/chiccheapcom")
}

# --- YEDEK ÜRÜNLER (Genişletilmiş) ---
INVENTORY_POOL = [
    {"title": "Bohemian Floral Maxi Dress", "price": "$39.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600", "link": f"https://www.amazon.com/s?k=boho+maxi+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Classic Oversized Denim Jacket", "price": "$45.50", "category": "Jacket", "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=600", "link": f"https://www.amazon.com/s?k=oversized+denim+jacket&tag={REAL_AMAZON_TAG}"},
    {"title": "Minimalist Gold Layered Necklace", "price": "$14.99", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600", "link": f"https://www.amazon.com/s?k=gold+layered+necklace&tag={REAL_AMAZON_TAG}"},
    {"title": "Vintage Cat Eye Sunglasses", "price": "$18.99", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600", "link": f"https://www.amazon.com/s?k=cat+eye+sunglasses&tag={REAL_AMAZON_TAG}"},
    {"title": "White Summer Canvas Sneakers", "price": "$29.99", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+canvas+sneakers&tag={REAL_AMAZON_TAG}"},
    {"title": "Luxury Leather Crossbody Bag", "price": "$55.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600", "link": f"https://www.amazon.com/s?k=crossbody+bag&tag={REAL_AMAZON_TAG}"},
    {"title": "Red Satin Evening Gown", "price": "$59.50", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600", "link": f"https://www.amazon.com/s?k=red+satin+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Beige Trench Coat Classic", "price": "$65.00", "category": "Coat", "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600", "link": f"https://www.amazon.com/s?k=beige+trench+coat&tag={REAL_AMAZON_TAG}"},
    {"title": "Cozy Knitted Oversized Sweater", "price": "$35.99", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=600", "link": f"https://www.amazon.com/s?k=chunky+knit+sweater&tag={REAL_AMAZON_TAG}"},
    {"title": "Pearl Drop Earrings", "price": "$12.50", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=600", "link": f"https://www.amazon.com/s?k=pearl+earrings&tag={REAL_AMAZON_TAG}"},
    {"title": "Wide Brim Straw Beach Hat", "price": "$22.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1521335629791-ce4aec6c1d09?q=80&w=600", "link": f"https://www.amazon.com/s?k=straw+beach+hat&tag={REAL_AMAZON_TAG}"},
    {"title": "Leather Ankle Boots", "price": "$65.00", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600", "link": f"https://www.amazon.com/s?k=ankle+boots+women&tag={REAL_AMAZON_TAG}"},
    {"title": "White Linen Summer Dress", "price": "$34.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+linen+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Vintage Polka Dot Midi Dress", "price": "$42.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1612336307429-8a898d10e223?q=80&w=600", "link": f"https://www.amazon.com/s?k=polka+dot+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Black Cocktail Mini Dress", "price": "$45.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?q=80&w=600", "link": f"https://www.amazon.com/s?k=black+cocktail+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Yellow Floral Sundress", "price": "$29.99", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?q=80&w=600", "link": f"https://www.amazon.com/s?k=yellow+sundress&tag={REAL_AMAZON_TAG}"},
    {"title": "Pastel Pink Slip Dress", "price": "$38.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?q=80&w=600", "link": f"https://www.amazon.com/s?k=pink+slip+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Emerald Green Wrap Dress", "price": "$55.00", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1605763240004-7e93b172d754?q=80&w=600", "link": f"https://www.amazon.com/s?k=green+wrap+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "Navy Blue Office Dress", "price": "$49.90", "category": "Dress", "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600", "link": f"https://www.amazon.com/s?k=navy+blue+office+dress&tag={REAL_AMAZON_TAG}"},
    {"title": "White Silk Blouse", "price": "$49.90", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1598554060854-b827048d7458?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+silk+blouse&tag={REAL_AMAZON_TAG}"},
    {"title": "Striped Breton Top", "price": "$24.00", "category": "Tops", "image_url": "https://images.unsplash.com/photo-1503342394128-c104d54dba01?q=80&w=600", "link": f"https://www.amazon.com/s?k=striped+shirt+women&tag={REAL_AMAZON_TAG}"},
    {"title": "Silver Stackable Rings Set", "price": "$18.00", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?q=80&w=600", "link": f"https://www.amazon.com/s?k=silver+rings+set&tag={REAL_AMAZON_TAG}"},
    {"title": "Statement Gold Hoop Earrings", "price": "$16.99", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a51?q=80&w=600", "link": f"https://www.amazon.com/s?k=gold+hoop+earrings&tag={REAL_AMAZON_TAG}"},
    {"title": "Rose Gold Watch", "price": "$85.00", "category": "Jewelry", "image_url": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?q=80&w=600", "link": f"https://www.amazon.com/s?k=rose+gold+watch+women&tag={REAL_AMAZON_TAG}"},
    {"title": "Luxury Silk Scarf Patterned", "price": "$25.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1586078436377-46714147839b?q=80&w=600", "link": f"https://www.amazon.com/s?k=silk+scarf&tag={REAL_AMAZON_TAG}"},
    {"title": "Classic Leather Belt", "price": "$20.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1624223359990-8b050454b378?q=80&w=600", "link": f"https://www.amazon.com/s?k=women+leather+belt&tag={REAL_AMAZON_TAG}"},
    {"title": "Strappy High Heels Nude", "price": "$49.99", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600", "link": f"https://www.amazon.com/s?k=nude+heels&tag={REAL_AMAZON_TAG}"},
    {"title": "Comfortable Running Shoes", "price": "$55.00", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600", "link": f"https://www.amazon.com/s?k=running+shoes+women&tag={REAL_AMAZON_TAG}"},
    {"title": "Summer Flat Sandals", "price": "$24.50", "category": "Shoes", "image_url": "https://images.unsplash.com/photo-1562273138-f46be4ebdf6e?q=80&w=600", "link": f"https://www.amazon.com/s?k=flat+sandals&tag={REAL_AMAZON_TAG}"},
    {"title": "Chic Tote Bag Beige", "price": "$32.50", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?q=80&w=600", "link": f"https://www.amazon.com/s?k=beige+tote+bag&tag={REAL_AMAZON_TAG}"},
    {"title": "Woven Beach Bag", "price": "$28.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600", "link": f"https://www.amazon.com/s?k=straw+bag&tag={REAL_AMAZON_TAG}"},
    {"title": "Black Designer Handbag", "price": "$120.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?q=80&w=600", "link": f"https://www.amazon.com/s?k=black+handbag&tag={REAL_AMAZON_TAG}"},
    {"title": "Red Clutch Bag", "price": "$45.00", "category": "Bags", "image_url": "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?q=80&w=600", "link": f"https://www.amazon.com/s?k=red+clutch&tag={REAL_AMAZON_TAG}"}
]

# BLOG KONULARI
BLOG_TOPICS = [
    "Summer 2025 Fashion Trends You Need to Know",
    "How to Style Boho Dresses for Any Occasion",
    "Top 10 Affordable Accessories That Look Expensive",
    "The Ultimate Guide to Capsule Wardrobe Essentials",
    "Why Oversized Denim Jackets Are Making a Comeback",
    "Best Office Wear Ideas for Modern Women",
    "How to Layer Jewelry Like a Pro"
]

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
            return {"review_text": "Stylish choice.", "styling_tip": "Wear with confidence.", "ai_score": 90, "category": "Fashion", "pin_title": "Fashion Find", "pin_desc": "Trendy style"}

    def generate_blog_post(self):
        topic = random.choice(BLOG_TOPICS)
        print(f"📝 Blog Yazılıyor: {topic}")
        prompt = f"""
        Write a short, engaging fashion blog post about: "{topic}".
        Target audience: Women looking for affordable style.
        Tone: Excited, professional, trendy.
        Output JSON keys:
        - 'title': The blog title.
        - 'summary': A short summary (2 sentences) for SEO description.
        - 'content': The blog content in HTML format (use <p>, <strong>, <ul>, <li> tags only). 200-250 words. No markdown.
        - 'image_keyword': A keyword to search for an image on Unsplash (e.g. 'summer dress').
        """
        try:
            response = model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            data['image_url'] = f"https://source.unsplash.com/800x400/?{data['image_keyword'].replace(' ', ',')}"
            if "source.unsplash" in data['image_url']:
                 data['image_url'] = f"https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800&auto=format&fit=crop" 
            return data
        except Exception as e:
            print(f"Blog Hatası: {e}")
            return {
                "title": "Trend Alert: Essential Styles for 2025",
                "summary": "Discover the must-have pieces for your wardrobe this season. Affordable luxury is just a click away.",
                "content": "<p>Fashion is about expressing yourself without breaking the bank. This season, we are seeing a return to classic staples mixed with bold accessories.</p><p>From oversized denim jackets to minimalist jewelry, the key is versatility.</p>",
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
    print("--- 🚀 Chic-Cheap V18.0 (Blog Engine) ---")
    processed_products = []
    ai_engine = AIContentGenerator()
    
    api_success = False
    try:
        if all([GEMINI_KEY, AMAZON_KEY, AMAZON_SECRET]):
            items = amazon.search_items(keywords="Womens Fashion", item_count=2)
    except: pass

    if not api_success:
        count = min(len(INVENTORY_POOL), 15) 
        processed_products = random.sample(INVENTORY_POOL, count)

    final_products = []
    for product in processed_products:
        try:
            ai_data = ai_engine.generate_review(product['title'], product['price'])
            final_products.append({**product, **ai_data})
            time.sleep(0.5)
        except: continue

    blog_data = ai_engine.generate_blog_post()

    final_output = {
        "config": SITE_CONFIG,
        "products": final_products,
        "blog": blog_data
    }
    with open('website_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4)

    create_pinterest_files(final_products)
    print("💾 Tüm içerik (Ürünler + Blog) güncellendi.")

if __name__ == "__main__":
    main()
