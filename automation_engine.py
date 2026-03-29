"""
CHIC-CHEAP.COM — Automation Engine v2.0
GitHub Actions ile her gün otomatik çalışır.
Yazar: Claude (Anthropic)
"""

import os
import json
import time
import random
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import google.generativeai as genai
try:
    from amazon_paapi import AmazonApi
except ImportError:
    try:
        from amazon_creatorsapi import AmazonApi
    except ImportError:
        AmazonApi = None

# ============================================================
# AYARLAR — Tüm değerler GitHub Secrets'tan gelir
# ============================================================
GEMINI_KEY      = os.environ.get("GEMINI_API_KEY")
try:
    from amazon_paapi import AmazonApi
except ImportError:
    AmazonApi = None
AMAZON_KEY      = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET   = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_TAG      = os.environ.get("AMAZON_TAG", "chiccheap-20")
ADSENSE_ID      = os.environ.get("ADSENSE_ID", "")
ADSENSE_SLOT    = os.environ.get("ADSENSE_SLOT", "")
PINTEREST_URL   = os.environ.get("PINTEREST_URL", "https://www.pinterest.com/chiccheapcom")
COUNTRY         = "US"

# ============================================================
# ÜRÜN KATEGORİLERİ — Amazon PAAPI arama terimleri
# ============================================================
AMAZON_CATEGORIES = [
    {"keyword": "women floral maxi dress",        "category": "Dresses"},
    {"keyword": "women casual mini dress",         "category": "Dresses"},
    {"keyword": "women silk blouse top",           "category": "Tops"},
    {"keyword": "women knit cardigan sweater",     "category": "Tops"},
    {"keyword": "women crossbody leather bag",     "category": "Bags"},
    {"keyword": "women tote bag fashion",          "category": "Bags"},
    {"keyword": "women gold layered necklace",     "category": "Jewelry"},
    {"keyword": "women hoop earrings gold",        "category": "Jewelry"},
    {"keyword": "women cat eye sunglasses",        "category": "Accessories"},
    {"keyword": "women strappy heels sandals",     "category": "Shoes"},
    {"keyword": "women white sneakers casual",     "category": "Shoes"},
    {"keyword": "women leather ankle boots",       "category": "Shoes"},
]

# ============================================================
# YEDEK ÜRÜN HAVUZU — PAAPI çalışmazsa kullanılır
# ============================================================
FALLBACK_PRODUCTS = [
    {"title": "Bohemian Floral Maxi Dress",        "price": "$39.99", "category": "Dresses",     "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600", "link": f"https://www.amazon.com/s?k=boho+maxi+dress&tag=chiccheap-20"},
    {"title": "Red Satin Evening Gown",            "price": "$59.50", "category": "Dresses",     "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600", "link": f"https://www.amazon.com/s?k=red+satin+dress&tag=chiccheap-20"},
    {"title": "White Linen Summer Dress",          "price": "$34.00", "category": "Dresses",     "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+linen+dress&tag=chiccheap-20"},
    {"title": "Green Wrap Dress",                  "price": "$55.00", "category": "Dresses",     "image_url": "https://images.unsplash.com/photo-1605763240004-7e93b172d754?q=80&w=600", "link": f"https://www.amazon.com/s?k=green+wrap+dress&tag=chiccheap-20"},
    {"title": "Black Cocktail Mini Dress",         "price": "$45.00", "category": "Dresses",     "image_url": "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?q=80&w=600", "link": f"https://www.amazon.com/s?k=black+cocktail+dress&tag=chiccheap-20"},
    {"title": "White Silk Blouse",                 "price": "$49.90", "category": "Tops",        "image_url": "https://images.unsplash.com/photo-1598554060854-b827048d7458?q=80&w=600", "link": f"https://www.amazon.com/s?k=silk+blouse&tag=chiccheap-20"},
    {"title": "Pink Oversized Cardigan",           "price": "$30.00", "category": "Tops",        "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?q=80&w=600", "link": f"https://www.amazon.com/s?k=cardigan+women&tag=chiccheap-20"},
    {"title": "Striped Breton Top",                "price": "$24.00", "category": "Tops",        "image_url": "https://images.unsplash.com/photo-1503342394128-c104d54dba01?q=80&w=600", "link": f"https://www.amazon.com/s?k=striped+top+women&tag=chiccheap-20"},
    {"title": "Leather Crossbody Bag",             "price": "$55.00", "category": "Bags",        "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?q=80&w=600", "link": f"https://www.amazon.com/s?k=crossbody+bag+women&tag=chiccheap-20"},
    {"title": "Chic Canvas Tote Bag",              "price": "$32.50", "category": "Bags",        "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?q=80&w=600", "link": f"https://www.amazon.com/s?k=tote+bag+women&tag=chiccheap-20"},
    {"title": "Gold Layered Necklace",             "price": "$14.99", "category": "Jewelry",     "image_url": "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600", "link": f"https://www.amazon.com/s?k=gold+necklace+women&tag=chiccheap-20"},
    {"title": "Gold Hoop Earrings",                "price": "$16.99", "category": "Jewelry",     "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a51?q=80&w=600", "link": f"https://www.amazon.com/s?k=hoop+earrings+gold&tag=chiccheap-20"},
    {"title": "Cat Eye Sunglasses",                "price": "$18.99", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600", "link": f"https://www.amazon.com/s?k=cat+eye+sunglasses&tag=chiccheap-20"},
    {"title": "Strappy High Heels",                "price": "$49.99", "category": "Shoes",       "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600", "link": f"https://www.amazon.com/s?k=strappy+heels&tag=chiccheap-20"},
    {"title": "White Canvas Sneakers",             "price": "$29.99", "category": "Shoes",       "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600", "link": f"https://www.amazon.com/s?k=white+sneakers+women&tag=chiccheap-20"},
    {"title": "Leather Ankle Boots",               "price": "$65.00", "category": "Shoes",       "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600", "link": f"https://www.amazon.com/s?k=ankle+boots+women&tag=chiccheap-20"},
    {"title": "Rose Gold Watch",                   "price": "$85.00", "category": "Accessories", "image_url": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?q=80&w=600", "link": f"https://www.amazon.com/s?k=rose+gold+watch+women&tag=chiccheap-20"},
    {"title": "Woven Straw Beach Bag",             "price": "$28.00", "category": "Bags",        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600", "link": f"https://www.amazon.com/s?k=straw+beach+bag&tag=chiccheap-20"},
]

# ============================================================
# BLOG KONULARI — Haftalık rotasyon
# ============================================================
BLOG_TOPICS = [
    {"topic": "10 Amazon Dresses Under $40 That Look Incredibly Expensive",        "keyword": "affordable dresses amazon 2026"},
    {"topic": "How to Build a Chic Capsule Wardrobe for Under $200",               "keyword": "capsule wardrobe budget 2026"},
    {"topic": "The Best Amazon Fashion Finds This Week — Editor's Picks",          "keyword": "amazon fashion finds 2026"},
    {"topic": "5 Outfit Formulas That Work for Every Body Type",                   "keyword": "outfit ideas women 2026"},
    {"topic": "Summer Accessories Under $25 That Elevate Any Look",               "keyword": "affordable summer accessories"},
    {"topic": "How to Style a Maxi Dress 5 Different Ways",                        "keyword": "how to style maxi dress"},
    {"topic": "Amazon vs Designer: Same Look for a Fraction of the Price",         "keyword": "amazon dupe designer fashion"},
    {"topic": "The Ultimate Guide to Affordable Jewelry That Doesn't Tarnish",     "keyword": "affordable jewelry that lasts"},
    {"topic": "Spring 2026 Fashion Trends You Can Get on Amazon Right Now",        "keyword": "spring 2026 fashion trends amazon"},
    {"topic": "Work Outfits Under $60: Look Professional Without Overspending",    "keyword": "affordable work outfits women"},
]

# ============================================================
# AMAZON PAAPI — Ürün Çekme
# ============================================================
def fetch_amazon_products():
    """Amazon PAAPI'den gerçek ürünleri çeker."""
    if not all([AMAZON_KEY, AMAZON_SECRET]):
        print("⚠️  Amazon credentials eksik, fallback kullanılıyor.")
        return None

    try:
        amazon = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, COUNTRY, throttling=2)
        products = []
        # Her kategoriden 2 ürün çek
        selected_cats = random.sample(AMAZON_CATEGORIES, min(8, len(AMAZON_CATEGORIES)))

        for cat in selected_cats:
            try:
                results = amazon.search_items(
                    keywords=cat["keyword"],
                    item_count=2
                )
                if results and results.items:
                    for item in results.items:
                        price = "N/A"
                        if item.offers and item.offers.listings:
                            price = f"${item.offers.listings[0].price.amount}"

                        image = ""
                        if item.images and item.images.primary:
                            image = item.images.primary.large.url

                        products.append({
                            "title":     item.item_info.title.display_value,
                            "price":     price,
                            "category":  cat["category"],
                            "image_url": image,
                            "link":      item.detail_page_url,
                            "rating":    getattr(item, "customer_reviews", {}) and "4.5" or "4.3",
                        })
                time.sleep(1)
            except Exception as e:
                print(f"   Kategori hatası ({cat['keyword']}): {e}")
                continue

        print(f"✅ Amazon PAAPI: {len(products)} ürün çekildi.")
        return products if products else None

    except Exception as e:
        print(f"❌ Amazon PAAPI bağlantı hatası: {e}")
        return None


# ============================================================
# GEMINI AI — İçerik Üretimi (Ücretsiz)
# ============================================================
class GeminiContentEngine:
    def __init__(self):
        self.model = None
        if GEMINI_KEY:
            try:
                genai.configure(api_key=GEMINI_KEY)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"⚠️  Gemini başlatma hatası: {e}")

    def _call(self, prompt):
        """Gemini API çağrısı yapar."""
        if not self.model:
            return None
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"   Gemini API hatası: {e}")
            return None

    def enrich_product(self, title, price, category):
        """Ürün için AI açıklama + Pinterest metni üretir."""
        prompt = f"""You are a fashion influencer writing for chic-cheap.com.
Product: "{title}" — Price: {price} — Category: {category}

Return ONLY valid JSON (no markdown, no extra text):
{{
  "review_text": "One sentence (max 20 words) about why this piece is worth buying.",
  "styling_tip": "One practical styling tip (max 15 words).",
  "ai_score": <number between 85 and 98>,
  "pin_title": "Pinterest pin title (max 10 words, include price if known).",
  "pin_desc": "Pinterest pin description (max 25 words, include call to action)."
}}"""

        raw = self._call(prompt)
        if raw:
            try:
                clean = raw.strip()
                if "```" in clean:
                    clean = clean.split("```")[1]
                    if clean.startswith("json"):
                        clean = clean[4:]
                return json.loads(clean.strip())
            except:
                pass
        # Fallback
        return {
            "review_text": f"A must-have {category.lower()} piece at an unbeatable price.",
            "styling_tip": "Pair with neutral accessories for a polished look.",
            "ai_score": random.randint(85, 95),
            "pin_title": f"{title} — {price}",
            "pin_desc": f"Shop this chic {category.lower()} on Amazon. Curated by Chic-Cheap! 🛍️"
        }

    def generate_blog_post(self):
        """Haftalık SEO blog yazısı üretir."""
        topic_data = random.choice(BLOG_TOPICS)
        topic   = topic_data["topic"]
        keyword = topic_data["keyword"]

        print(f"📝 Blog yazılıyor: {topic}")

        prompt = f"""You are a senior fashion editor writing for chic-cheap.com.

Write a complete, SEO-optimized blog post about: "{topic}"
Target keyword: "{keyword}"

Requirements:
- Minimum 600 words
- Engaging, conversational tone
- Use proper HTML tags: <h2>, <h3>, <p>, <ul>, <li>, <strong>
- Include 3-5 Amazon product recommendations naturally in the text
- Add a Shopping Tips section
- End with a motivating conclusion
- DO NOT use markdown — pure HTML only

Return ONLY valid JSON (no markdown fence, no extra text):
{{
  "title": "The exact blog post title",
  "meta_description": "SEO meta description (max 155 characters)",
  "summary": "Two-sentence teaser for the homepage card.",
  "content": "Full HTML content of the article",
  "image_keyword": "Single English word for Unsplash image"
}}"""

        raw = self._call(prompt)
        if raw:
            try:
                clean = raw.strip()
                if "```" in clean:
                    clean = clean.split("```")[1]
                    if clean.startswith("json"):
                        clean = clean[4:]
                data = json.loads(clean.strip())
                data["image_url"] = "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800&auto=format&fit=crop"
                return data
            except Exception as e:
                print(f"   Blog parse hatası: {e}")

        # Fallback blog
        return {
            "title": topic,
            "meta_description": f"{keyword} — Curated picks from chic-cheap.com",
            "summary": "Discover this week's most stylish affordable fashion picks, handpicked by our editors.",
            "content": f"<h2>Editor's Note</h2><p>Our editors are working on bringing you the best guide on: <strong>{topic}</strong>. Check back soon!</p>",
            "image_url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800"
        }


# ============================================================
# PINTEREST DOSYALARI
# ============================================================
def create_pinterest_files(products):
    """Pinterest XML feed ve CSV yükleme dosyası oluşturur."""
    # XML
    rss     = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Chic-Cheap Fashion Finds"
    ET.SubElement(channel, "link").text  = "https://chic-cheap.com"
    ET.SubElement(channel, "description").text = "Curated Style. Smart Prices."

    # CSV
    with open("pinterest_upload.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f,
            fieldnames=["Title", "Description", "Link", "Image", "Board"],
            quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for p in products:
            # XML item
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text    = p.get("pin_title", p["title"])
            ET.SubElement(item, "link").text     = "https://chic-cheap.com"
            ET.SubElement(item, "description").text = p.get("pin_desc", "")
            enc = ET.SubElement(item, "enclosure")
            enc.set("url",  p["image_url"])
            enc.set("type", "image/jpeg")
            ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

            # CSV satırı
            board = {
                "Dresses":     "Affordable Dresses",
                "Tops":        "Chic Tops & Blouses",
                "Bags":        "Bags & Purses",
                "Jewelry":     "Affordable Jewelry",
                "Shoes":       "Shoes Under $70",
                "Accessories": "Style Accessories",
            }.get(p.get("category", ""), "Chic on a Budget")

            writer.writerow({
                "Title":       p.get("pin_title", p["title"]),
                "Description": p.get("pin_desc", p["title"]),
                "Link":        "https://chic-cheap.com",
                "Image":       p["image_url"],
                "Board":       board,
            })

    ET.ElementTree(rss).write("pinterest.xml", encoding="utf-8", xml_declaration=True)
    print("📌 Pinterest XML + CSV oluşturuldu.")


# ============================================================
# ANA FONKSİYON
# ============================================================
def main():
    print("=" * 55)
    print("  CHIC-CHEAP.COM — Automation Engine v2.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    ai = GeminiContentEngine()

    # 1. Ürünleri çek
    print("\n📦 Ürünler çekiliyor...")
    products = fetch_amazon_products()

    if not products:
        print("ℹ️  Fallback ürün havuzu kullanılıyor.")
        products = random.sample(FALLBACK_PRODUCTS, min(15, len(FALLBACK_PRODUCTS)))

    # 2. Her ürüne AI içerik ekle
    print(f"\n🤖 {len(products)} ürün için AI içerik üretiliyor...")
    enriched = []
    for p in products:
        ai_data = ai.enrich_product(p["title"], p["price"], p["category"])
        enriched.append({**p, **ai_data})
        time.sleep(0.3)

    # 3. Blog yazısı üret
    print("\n📝 Blog yazısı üretiliyor...")
    blog = ai.generate_blog_post()

    # 4. Tüm veriyi paketle
    output = {
        "generated_at": datetime.now().isoformat(),
        "amazon_tag":   AMAZON_TAG,
        "config": {
            "adsense_id":    ADSENSE_ID,
            "adsense_slot":  ADSENSE_SLOT,
            "pinterest_url": PINTEREST_URL,
            "site_url":      "https://chic-cheap.com",
        },
        "products": enriched,
        "blog":     blog,
        "stats": {
            "total_products": len(enriched),
            "categories":     list(set(p["category"] for p in enriched)),
        }
    }

    # 5. Kaydet
    with open("website_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # 6. Pinterest dosyaları
    create_pinterest_files(enriched)

    print("\n✅ TAMAMLANDI!")
    print(f"   → {len(enriched)} ürün işlendi")
    print(f"   → Blog: {blog['title'][:60]}...")
    print(f"   → website_data.json kaydedildi")
    print(f"   → pinterest.xml + pinterest_upload.csv kaydedildi")
    print("=" * 55)


if __name__ == "__main__":
    main()
