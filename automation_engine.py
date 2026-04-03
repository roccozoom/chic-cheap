"""
CHIC-CHEAP.COM — Automation Engine v4.0 (Final)
================================================
- Groq API (Llama 3.3, tamamen ücretsiz) ile AI içerik
- Groq çalışmazsa akıllı şablon sistemi devreye girer
- Amazon PAAPI ile gerçek ürünler (kota açılınca aktif olur)
- Her ürüne kategoriye özel benzersiz görsel
- Her gün sabah 07:00 UTC otomatik çalışır
"""

import os, json, time, random, csv, xml.etree.ElementTree as ET, urllib.request, urllib.parse
from datetime import datetime

# ── BAĞIMLILIKLAR ──────────────────────────────────────────
try:
    from amazon_paapi import AmazonApi
except ImportError:
    try:
        from amazon_creatorsapi import AmazonApi
    except ImportError:
        AmazonApi = None

# ── AYARLAR (GitHub Secrets) ───────────────────────────────
GROQ_KEY     = os.environ.get("GROQ_API_KEY", "")
AMAZON_KEY   = os.environ.get("AMAZON_ACCESS_KEY", "")
AMAZON_SECRET= os.environ.get("AMAZON_SECRET_KEY", "")
AMAZON_TAG   = os.environ.get("AMAZON_TAG", "chiccheap-20")
ADSENSE_ID   = os.environ.get("ADSENSE_ID", "")
ADSENSE_SLOT = os.environ.get("ADSENSE_SLOT", "")
PINTEREST_URL= os.environ.get("PINTEREST_URL", "https://www.pinterest.com/chiccheapcom")
COUNTRY      = "US"
GROQ_MODEL   = "llama-3.3-70b-versatile"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"

# ── RESİM HAVUZU — Her ürüne özel, kategoriye göre ─────────
IMAGES = {
    "Dresses": [
        "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600",
        "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600",
        "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?q=80&w=600",
        "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?q=80&w=600",
        "https://images.unsplash.com/photo-1566174053879-31528523f8ae?q=80&w=600",
        "https://images.unsplash.com/photo-1612336307429-8a898d10e223?q=80&w=600",
        "https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?q=80&w=600",
        "https://images.unsplash.com/photo-1605763240004-7e93b172d754?q=80&w=600",
        "https://images.unsplash.com/photo-1496747611176-843222e1e57c?q=80&w=600",
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=600",
        "https://images.unsplash.com/photo-1518895949257-7621c3c786d7?q=80&w=600",
        "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?q=80&w=600",
    ],
    "Tops": [
        "https://images.unsplash.com/photo-1598554060854-b827048d7458?q=80&w=600",
        "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?q=80&w=600",
        "https://images.unsplash.com/photo-1503342394128-c104d54dba01?q=80&w=600",
        "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=600",
        "https://images.unsplash.com/photo-1621072156002-e2fccdc0b176?q=80&w=600",
        "https://images.unsplash.com/photo-1554568218-0f1715e72254?q=80&w=600",
        "https://images.unsplash.com/photo-1516762689617-e1cffcef479d?q=80&w=600",
        "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?q=80&w=600",
        "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?q=80&w=600",
        "https://images.unsplash.com/photo-1562572159-4efd90232bcd?q=80&w=600",
    ],
    "Bags": [
        "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?q=80&w=600",
        "https://images.unsplash.com/photo-1591561954557-26941169b49e?q=80&w=600",
        "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600",
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600",
        "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?q=80&w=600",
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?q=80&w=600",
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?q=80&w=600",
        "https://images.unsplash.com/photo-1578632767115-351597cf2477?q=80&w=600",
        "https://images.unsplash.com/photo-1614179818749-53a3e4a0b0e2?q=80&w=600",
        "https://images.unsplash.com/photo-1598532163257-ae3c6b2524b6?q=80&w=600",
    ],
    "Jewelry": [
        "https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600",
        "https://images.unsplash.com/photo-1630019852942-f89202989a51?q=80&w=600",
        "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=600",
        "https://images.unsplash.com/photo-1605100804763-247f67b3557e?q=80&w=600",
        "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?q=80&w=600",
        "https://images.unsplash.com/photo-1573408301185-9519f94816b5?q=80&w=600",
        "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?q=80&w=600",
        "https://images.unsplash.com/photo-1602173574767-37ac01994b2a?q=80&w=600",
        "https://images.unsplash.com/photo-1589128777073-263566ae5e4d?q=80&w=600",
        "https://images.unsplash.com/photo-1616697560949-8f6bf01b1c2f?q=80&w=600",
    ],
    "Shoes": [
        "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600",
        "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600",
        "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600",
        "https://images.unsplash.com/photo-1562273138-f46be4ebdf6e?q=80&w=600",
        "https://images.unsplash.com/photo-1518049362265-d5b2a6467637?q=80&w=600",
        "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?q=80&w=600",
        "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?q=80&w=600",
        "https://images.unsplash.com/photo-1607522370275-f14206abe5d3?q=80&w=600",
        "https://images.unsplash.com/photo-1571945153237-4929e783af4a?q=80&w=600",
        "https://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?q=80&w=600",
    ],
    "Accessories": [
        "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600",
        "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?q=80&w=600",
        "https://images.unsplash.com/photo-1586078436377-46714147839b?q=80&w=600",
        "https://images.unsplash.com/photo-1521335629791-ce4aec6c1d09?q=80&w=600",
        "https://images.unsplash.com/photo-1624223359990-8b050454b378?q=80&w=600",
        "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?q=80&w=600",
        "https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93?q=80&w=600",
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?q=80&w=600",
        "https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?q=80&w=600",
        "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?q=80&w=600",
    ],
}

def get_unique_image(category, used_images):
    """Kategoriye özel, daha önce kullanılmamış bir görsel seç."""
    pool = IMAGES.get(category, IMAGES["Accessories"])
    available = [img for img in pool if img not in used_images]
    if not available:
        available = pool  # Hepsi kullanıldıysa sıfırla
    chosen = random.choice(available)
    used_images.add(chosen)
    return chosen

# ── AMAZON KATEGORİLERİ ────────────────────────────────────
AMAZON_CATEGORIES = [
    {"keyword": "women floral maxi dress",       "category": "Dresses"},
    {"keyword": "women casual midi dress",        "category": "Dresses"},
    {"keyword": "women wrap dress",               "category": "Dresses"},
    {"keyword": "women silk blouse top",          "category": "Tops"},
    {"keyword": "women oversized knit cardigan",  "category": "Tops"},
    {"keyword": "women crossbody bag leather",    "category": "Bags"},
    {"keyword": "women tote bag fashion",         "category": "Bags"},
    {"keyword": "women gold layered necklace",    "category": "Jewelry"},
    {"keyword": "women hoop earrings",            "category": "Jewelry"},
    {"keyword": "women cat eye sunglasses",       "category": "Accessories"},
    {"keyword": "women strappy sandals heels",    "category": "Shoes"},
    {"keyword": "women white sneakers",           "category": "Shoes"},
]

# ── FALLBACK ÜRÜN HAVUZU ──────────────────────────────────
FALLBACK = [
    {"title":"Bohemian Floral Maxi Dress",         "price":"$39.99","category":"Dresses",     "link":f"https://www.amazon.com/s?k=boho+maxi+dress&tag={AMAZON_TAG}"},
    {"title":"Red Satin Evening Gown",             "price":"$59.50","category":"Dresses",     "link":f"https://www.amazon.com/s?k=red+satin+gown&tag={AMAZON_TAG}"},
    {"title":"White Linen Summer Dress",           "price":"$34.00","category":"Dresses",     "link":f"https://www.amazon.com/s?k=white+linen+dress&tag={AMAZON_TAG}"},
    {"title":"Green Wrap Midi Dress",              "price":"$55.00","category":"Dresses",     "link":f"https://www.amazon.com/s?k=green+wrap+dress&tag={AMAZON_TAG}"},
    {"title":"Black Cocktail Mini Dress",          "price":"$45.00","category":"Dresses",     "link":f"https://www.amazon.com/s?k=black+cocktail+dress&tag={AMAZON_TAG}"},
    {"title":"Yellow Floral Sundress",             "price":"$29.99","category":"Dresses",     "link":f"https://www.amazon.com/s?k=yellow+sundress&tag={AMAZON_TAG}"},
    {"title":"Vintage Polka Dot Dress",            "price":"$42.99","category":"Dresses",     "link":f"https://www.amazon.com/s?k=polka+dot+dress&tag={AMAZON_TAG}"},
    {"title":"Pink Satin Slip Dress",              "price":"$38.00","category":"Dresses",     "link":f"https://www.amazon.com/s?k=pink+slip+dress&tag={AMAZON_TAG}"},
    {"title":"Navy Blue Wrap Dress",               "price":"$46.00","category":"Dresses",     "link":f"https://www.amazon.com/s?k=navy+wrap+dress&tag={AMAZON_TAG}"},
    {"title":"White Silk Blouse",                  "price":"$49.90","category":"Tops",        "link":f"https://www.amazon.com/s?k=silk+blouse+women&tag={AMAZON_TAG}"},
    {"title":"Pink Oversized Cardigan",            "price":"$30.00","category":"Tops",        "link":f"https://www.amazon.com/s?k=oversized+cardigan+women&tag={AMAZON_TAG}"},
    {"title":"Striped Breton Top",                 "price":"$24.00","category":"Tops",        "link":f"https://www.amazon.com/s?k=breton+striped+top&tag={AMAZON_TAG}"},
    {"title":"Black Ribbed Turtleneck",            "price":"$28.00","category":"Tops",        "link":f"https://www.amazon.com/s?k=ribbed+turtleneck+women&tag={AMAZON_TAG}"},
    {"title":"Effortless Satin Camisole",          "price":"$14.87","category":"Tops",        "link":f"https://www.amazon.com/s?k=satin+camisole+top&tag={AMAZON_TAG}"},
    {"title":"Cream Linen Button Blouse",          "price":"$32.00","category":"Tops",        "link":f"https://www.amazon.com/s?k=linen+blouse+women&tag={AMAZON_TAG}"},
    {"title":"Leather Crossbody Bag",              "price":"$55.00","category":"Bags",        "link":f"https://www.amazon.com/s?k=leather+crossbody+bag&tag={AMAZON_TAG}"},
    {"title":"Chic Canvas Tote Bag",               "price":"$32.50","category":"Bags",        "link":f"https://www.amazon.com/s?k=canvas+tote+bag+women&tag={AMAZON_TAG}"},
    {"title":"Woven Straw Beach Bag",              "price":"$28.00","category":"Bags",        "link":f"https://www.amazon.com/s?k=straw+beach+bag&tag={AMAZON_TAG}"},
    {"title":"Black Structured Handbag",           "price":"$65.00","category":"Bags",        "link":f"https://www.amazon.com/s?k=structured+handbag+black&tag={AMAZON_TAG}"},
    {"title":"Pink Mini Clutch",                   "price":"$25.00","category":"Bags",        "link":f"https://www.amazon.com/s?k=mini+clutch+bag&tag={AMAZON_TAG}"},
    {"title":"Tan Bucket Bag",                     "price":"$42.00","category":"Bags",        "link":f"https://www.amazon.com/s?k=bucket+bag+women&tag={AMAZON_TAG}"},
    {"title":"Gold Layered Necklace Set",          "price":"$14.99","category":"Jewelry",     "link":f"https://www.amazon.com/s?k=gold+layered+necklace&tag={AMAZON_TAG}"},
    {"title":"Gold Hoop Earrings",                 "price":"$16.99","category":"Jewelry",     "link":f"https://www.amazon.com/s?k=gold+hoop+earrings&tag={AMAZON_TAG}"},
    {"title":"Pearl Drop Earrings",                "price":"$12.50","category":"Jewelry",     "link":f"https://www.amazon.com/s?k=pearl+drop+earrings&tag={AMAZON_TAG}"},
    {"title":"Silver Stacking Ring Set",           "price":"$18.00","category":"Jewelry",     "link":f"https://www.amazon.com/s?k=silver+stacking+rings&tag={AMAZON_TAG}"},
    {"title":"Crystal Pendant Necklace",           "price":"$22.00","category":"Jewelry",     "link":f"https://www.amazon.com/s?k=crystal+pendant+necklace&tag={AMAZON_TAG}"},
    {"title":"White Canvas Sneakers",              "price":"$29.99","category":"Shoes",       "link":f"https://www.amazon.com/s?k=white+canvas+sneakers+women&tag={AMAZON_TAG}"},
    {"title":"Strappy Stiletto Heels",             "price":"$49.99","category":"Shoes",       "link":f"https://www.amazon.com/s?k=strappy+stiletto+heels&tag={AMAZON_TAG}"},
    {"title":"Leather Ankle Boots",                "price":"$65.00","category":"Shoes",       "link":f"https://www.amazon.com/s?k=leather+ankle+boots+women&tag={AMAZON_TAG}"},
    {"title":"Summer Flat Sandals",                "price":"$24.50","category":"Shoes",       "link":f"https://www.amazon.com/s?k=flat+sandals+women&tag={AMAZON_TAG}"},
    {"title":"Block Heel Mules",                   "price":"$38.00","category":"Shoes",       "link":f"https://www.amazon.com/s?k=block+heel+mules+women&tag={AMAZON_TAG}"},
    {"title":"Cat Eye Sunglasses",                 "price":"$18.99","category":"Accessories", "link":f"https://www.amazon.com/s?k=cat+eye+sunglasses+women&tag={AMAZON_TAG}"},
    {"title":"Rose Gold Watch",                    "price":"$85.00","category":"Accessories", "link":f"https://www.amazon.com/s?k=rose+gold+watch+women&tag={AMAZON_TAG}"},
    {"title":"Silk Hair Scarf",                    "price":"$14.99","category":"Accessories", "link":f"https://www.amazon.com/s?k=silk+hair+scarf&tag={AMAZON_TAG}"},
    {"title":"Straw Sun Hat",                      "price":"$22.00","category":"Accessories", "link":f"https://www.amazon.com/s?k=straw+sun+hat+women&tag={AMAZON_TAG}"},
    {"title":"Leather Belt",                       "price":"$20.00","category":"Accessories", "link":f"https://www.amazon.com/s?k=leather+belt+women&tag={AMAZON_TAG}"},
]

# ── ŞABLON VERİLERİ ────────────────────────────────────────
REVIEWS = {
    "Dresses":     ["This dreamy dress combines elegance and comfort — perfect for any occasion.","A wardrobe essential that transitions effortlessly from day to night.","Flattering silhouette at a price that won't break the bank.","Turn heads without overspending — style and value in one perfect package.","The kind of dress you'll reach for again and again, season after season.","Effortlessly beautiful — the kind of piece that makes getting dressed genuinely fun.","Stunning construction at a price point that will genuinely surprise you."],
    "Tops":        ["Versatile top that pairs beautifully with jeans, skirts, or tailored trousers.","Elevated basics done right — soft, stylish, and incredibly affordable.","A closet staple you'll style a hundred different ways.","Effortlessly chic — proof that great style doesn't require a big budget.","The perfect layering piece for any season, any occasion.","Beautifully crafted and incredibly wearable — a true everyday essential.","Simple, elegant, and endlessly versatile — exactly what every wardrobe needs."],
    "Bags":        ["Spacious, stylish, and surprisingly affordable — this bag does it all.","A chic carryall that looks far more expensive than it actually is.","From farmer's market to date night, this bag handles everything in style.","Elevated design at a fraction of the designer price tag.","The bag that completes every outfit, whatever the occasion.","Beautifully structured and surprisingly roomy — a genuine everyday workhorse.","Luxurious look, accessible price — the very definition of smart shopping."],
    "Shoes":       ["Step out in style without the splurge — comfort meets chic design perfectly.","These shoes prove you don't need to spend a fortune to look incredible.","All-day wearability with serious style credentials — a rare find.","From brunch to cocktails, one shoe with endless possibilities.","The perfect finishing touch for any outfit, at any budget.","Surprisingly comfortable and genuinely beautiful — shoes you'll actually wear constantly.","Head-turning style at a price that makes buying two pairs feel completely justified."],
    "Jewelry":     ["Dainty, elegant, and incredibly affordable — jewelry goals fully achieved.","Layer it, stack it, mix it — this piece works beautifully every single way.","Timeless design that elevates even the simplest outfit instantly.","Looks like fine jewelry, feels like a steal at this price.","The kind of accessory that gets compliments every single time you wear it.","Delicate, beautiful, and incredibly versatile — the ideal everyday jewelry piece.","Simple luxury at an accessible price — exactly what great accessorizing looks like."],
    "Accessories": ["The finishing touch your outfit has been waiting for — right here.","Small accessory, massive impact — instantly elevates any look.","A style-savvy pick that adds instant polish to any ensemble.","Functional, fashionable, and completely affordable — the holy trinity.","Because the right accessory genuinely changes everything.","Understated elegance at an unbeatable price — an instant wardrobe upgrade.","The kind of piece that makes people ask where you got it — every single time."],
}

TIPS = {
    "Dresses":     ["Add a leather belt to define your waist and elevate the silhouette.","Layer with a denim jacket for a casual, effortlessly cool daytime vibe.","Pair with strappy heels and gold jewelry for instant evening glam.","Style with white sneakers for an effortlessly chic weekend outfit.","Add a blazer and heels to take it straight from desk to dinner."],
    "Tops":        ["Tuck into high-waisted trousers for a polished, put-together look.","Knot at the waist over jeans for relaxed, stylish weekend vibes.","Layer under a blazer for perfect smart-casual office styling.","Pair with wide-leg pants and mules for an elevated everyday look.","Style with a midi skirt and block heels for effortless chic."],
    "Bags":        ["Let it be the statement — keep the rest of your outfit beautifully neutral.","Cross-body styling keeps hands free and looks effortlessly cool always.","Mix textures: pair a leather bag with a linen outfit for gorgeous contrast.","Tuck a silk scarf through the handle for a designer-inspired finishing touch.","Go monochrome — match your bag to your shoes for ultimate polish."],
    "Shoes":       ["Pair with cropped jeans to show off the ankle detail beautifully.","Match to your bag for a coordinated, pulled-together look every time.","Wear with bare legs and a midi dress for effortless summer elegance.","Style with tailored trousers for sophisticated, polished workwear.","Add colorful socks for a fun, completely on-trend fashion twist."],
    "Jewelry":     ["Layer multiple necklaces at different lengths for a perfectly curated look.","Mix metals freely — gold and silver together is very on-trend right now.","Stack rings on multiple fingers for a bold, editorial feel.","Keep clothing simple and let the jewelry be the star of the show.","Wear your hair up to show off earrings in the most beautiful way."],
    "Accessories": ["Choose one statement accessory and keep everything else beautifully minimal.","Match accessory tones to your outfit's undertones for perfect cohesion.","Use accessories to inject color into an all-neutral, monochrome outfit.","A great accessory can make an old favourite outfit feel completely brand new.","Invest in versatile pieces that work seamlessly across multiple looks."],
}

BLOG_POOL = [
    {"title":"10 Amazon Dresses Under $50 That Look Incredibly Expensive","meta_description":"Discover 10 stunning Amazon dresses under $50 that look like they cost 10x more. Curated by Chic-Cheap editors.","summary":"Looking for dresses that look luxurious without the price tag? Our editors found 10 Amazon gems that will transform your wardrobe without emptying your wallet.","image_url":"https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=800","content":"<h2>Style Doesn't Have to Cost a Fortune</h2><p>One of fashion's best-kept secrets? Amazon is home to some of the most stylish, well-made dresses available — at prices that will genuinely surprise you. Our editors spend hours each week curating the very best finds so you don't have to.</p><h2>What to Look for When Shopping Amazon Dresses</h2><p>Before diving into our picks, here's what our team always checks: <strong>fabric composition</strong> (look for natural blends), <strong>customer reviews with photos</strong>, and <strong>size consistency ratings</strong>. These three factors separate a great Amazon buy from a disappointment.</p><h2>Our Top Picks This Season</h2><p>From flowing boho maxis to sleek cocktail styles, here are the dresses our editors are obsessing over right now. Each one is under $50, ships fast with Prime, and comes with hundreds of glowing reviews.</p><ul><li><strong>The Maxi:</strong> Perfect for beach days, garden parties, or weekend brunches.</li><li><strong>The Midi:</strong> The most versatile length of the moment. Pairs with sneakers by day, heels by night.</li><li><strong>The Wrap:</strong> Universally flattering. Works on every body type, every single time.</li><li><strong>The Mini:</strong> For the days you want to feel bold. Keep accessories minimal.</li></ul><h2>Styling Tips from Our Editors</h2><p>A great dress is just the beginning. <strong>Add a thin belt</strong> to any loose-fitting dress to instantly create shape. <strong>Layer a denim jacket</strong> for daytime, swap for a blazer for evening.</p><h2>Shopping Tips</h2><ul><li>Always read reviews that include photos — they give the most accurate color and fit representation.</li><li>Check the size chart for each listing individually, as sizing varies by brand.</li><li>Look for dresses with at least 100 reviews and a 4.0+ star rating.</li><li>Prime shipping means you can order and receive within days — perfect for last-minute occasions.</li></ul>"},
    {"title":"How to Build a Capsule Wardrobe for Under $200 — Amazon Edition","meta_description":"Build a complete, stylish capsule wardrobe for under $200 using Amazon finds. Step-by-step guide covering every essential piece.","summary":"A capsule wardrobe doesn't have to cost thousands. We show you exactly how to build a complete, versatile wardrobe for under $200 — entirely from Amazon.","image_url":"https://images.unsplash.com/photo-1558769132-cb1aea458c5e?q=80&w=800","content":"<h2>What Is a Capsule Wardrobe?</h2><p>A capsule wardrobe is a curated collection of timeless, versatile pieces that work together seamlessly. The goal: maximum outfits from minimum pieces. Done right, you'll have something perfect for every occasion.</p><h2>The Essential Pieces</h2><ul><li><strong>2 quality basic tops</strong> — white and neutral. The foundation of everything.</li><li><strong>1 classic blouse</strong> — silk or satin look. Elevates any bottom instantly.</li><li><strong>1 versatile dress</strong> — wrap or midi style works for day and night equally.</li><li><strong>1 pair of straight-leg jeans</strong> — the most universal bottom you'll ever own.</li><li><strong>1 tailored blazer</strong> — transforms any casual outfit into polished perfection.</li><li><strong>1 cardigan or knit</strong> — your essential layering hero through every season.</li><li><strong>1 pair of white sneakers</strong> — the most versatile shoes in fashion history, period.</li><li><strong>1 structured bag</strong> — pulls every single outfit together with instant sophistication.</li></ul><h2>The Color Strategy</h2><p>Stick to a neutral base — white, black, camel, navy, grey — and add one or two accent colors you genuinely love. Every piece should work with every other piece.</p><h2>Shopping Tips for Amazon</h2><ul><li>Search for the Amazon Essentials brand — consistently good quality at reliably low prices.</li><li>Filter by 4+ stars and 200+ reviews for the most reliable quality picks.</li><li>Read the fabric content — avoid 100% polyester for basics; look for cotton blends.</li></ul>"},
    {"title":"Amazon Fashion Finds: This Week's Most Stylish Affordable Picks","meta_description":"Our editors reveal this week's best Amazon fashion finds — stylish, affordable, and shipping fast with Prime. Updated weekly.","summary":"Every week our editors scour Amazon so you don't have to. This week's finds are genuinely exceptional — stylish pieces at prices that seem almost too good to be true.","image_url":"https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800","content":"<h2>This Week's Obsessions</h2><p>Every single week, our team dives deep into Amazon's fashion catalogue to find the pieces genuinely worth your attention and money. We look for quality, style, value, and — crucially — real customer photos that confirm what arrives matches the listing.</p><h2>Why We Trust Amazon for Fashion in 2026</h2><p>The stigma around Amazon fashion is fading fast. In 2026, the platform hosts hundreds of quality brands, ships within days, and offers easy returns. The key is knowing where to look — and that's exactly what we're here for.</p><h2>What Makes a Great Amazon Find?</h2><ul><li><strong>Real photos in reviews:</strong> Always check customer-uploaded photos before buying.</li><li><strong>High review count:</strong> 200+ reviews with a 4.2+ rating is our minimum threshold.</li><li><strong>Verified purchases:</strong> Filter reviews by Verified Purchase to avoid fake reviews.</li></ul><h2>This Season's Biggest Amazon Trends</h2><p><strong>Satin and silk-look fabrics</strong> are everywhere right now, and Amazon has dozens of options under $30 that look legitimately luxurious. <strong>Wide-leg everything</strong> continues its dominance — trousers, jeans, and even jumpsuits.</p>"},
    {"title":"Summer Accessories Under $25 That Instantly Elevate Any Look","meta_description":"Discover the best summer accessories under $25 on Amazon. Sunglasses, bags, jewelry and more — all incredibly stylish.","summary":"The right accessories can transform any outfit from ordinary to outstanding. Here are the summer accessories our editors are obsessing over — all under $25.","image_url":"https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=800","content":"<h2>The Power of Accessories</h2><p>Fashion insiders have known this secret for decades: you don't need an entirely new wardrobe to look completely different. The right accessories — perfect sunglasses, a standout necklace, an eye-catching bag — can transform even the most basic outfit into something that looks genuinely considered.</p><h2>Summer's Essential Accessories</h2><ul><li><strong>Sunglasses:</strong> The single most transformative accessory in fashion. A great pair adds instant mystery and glamour to any look.</li><li><strong>Statement earrings:</strong> When you're wearing a simple white tee and jeans, bold earrings make the entire outfit.</li><li><strong>The straw bag:</strong> Summer's most versatile bag. Works at the beach, at brunch, at the farmer's market.</li><li><strong>A silk scarf:</strong> Wear it in your hair, around your neck, tied to your bag handle. Infinitely versatile.</li><li><strong>Layered necklaces:</strong> Stack two or three delicate chains at different lengths for a perfectly curated look.</li></ul><h2>The Golden Rule of Accessorizing</h2><p>Choose one hero accessory per outfit and build everything else around it. This editing principle is what separates effortless dressing from looking overdone.</p>"},
    {"title":"Work Outfits Under $60: Look Polished Without Overspending","meta_description":"Build a professional, stylish work wardrobe for under $60 per outfit using Amazon finds. Our editors' top picks for affordable office fashion.","summary":"Looking professional at work doesn't require spending a fortune. Our editors found the best Amazon pieces for building a polished work wardrobe on a real budget.","image_url":"https://images.unsplash.com/photo-1594938298603-c8148c4dae35?q=80&w=800","content":"<h2>The Modern Work Wardrobe</h2><p>Office dress codes have evolved dramatically. Today's professional wardrobe is about looking polished and authentically you — not following rigid, outdated rules. And the best news? You can achieve this entirely through smart Amazon shopping.</p><h2>The Foundation Pieces</h2><p>Every great work wardrobe starts with the same essential building blocks. <strong>A well-fitted blazer</strong> is non-negotiable — it instantly elevates everything underneath. <strong>Tailored trousers</strong> in a neutral colour form the most versatile work bottom. <strong>A classic blouse</strong> in white or a soft pastel completes the foundational trio.</p><h2>Building Complete Outfits Under $60</h2><ul><li><strong>The Classic:</strong> Tailored black trousers + white blouse + minimal jewelry.</li><li><strong>The Modern Professional:</strong> Wide-leg trousers + tucked-in silk camisole + blazer.</li><li><strong>The Smart Casual:</strong> Midi dress + blazer + block heels.</li></ul><h2>What to Look For on Amazon</h2><p>For work clothes, fabric quality is crucial. Look for <strong>ponte fabric</strong> (holds shape beautifully), <strong>crepe</strong> (drapes elegantly), or <strong>cotton blends</strong> (breathable and professional).</p>"},
]

# ── GROQ AI MOTORU ─────────────────────────────────────────
class GroqEngine:
    def __init__(self):
        self.client    = None
        self.available = False
        if not GROQ_KEY:
            print("⚠️  GROQ_API_KEY bulunamadı.")
            return
        try:
            from groq import Groq
            self.client = Groq(api_key=GROQ_KEY)
            test = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": "Say: OK"}],
                max_tokens=5,
            )
            if test.choices[0].message.content:
                self.available = True
                print(f"✅ Groq bağlandı: {GROQ_MODEL}")
        except ImportError:
            print("⚠️  groq paketi yüklü değil.")
        except Exception as e:
            print(f"⚠️  Groq başlatılamadı: {str(e)[:80]}")

    def _call(self, prompt, max_tokens=500):
        """Groq API çağrısı — resmi groq kütüphanesi."""
        resp = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content

    def enrich_product(self, title, price, category):
        if not self.available:
            return None
        prompt = f"""You are a fashion influencer for chic-cheap.com.
Product: "{title}" | Price: {price} | Category: {category}

Return ONLY this exact JSON, no extra text, no markdown:
{{"review_text":"One compelling sentence max 20 words why this is worth buying.","styling_tip":"One practical styling tip max 15 words.","ai_score":{random.randint(86,97)},"pin_title":"{category} find on Amazon — {price}!","pin_desc":"Shop this amazing {category.lower()} on Amazon for only {price}. Curated by Chic-Cheap! #fashion #amazonfashion #style"}}"""
        try:
            raw = self._call(prompt, max_tokens=200)
            if raw:
                start = raw.find("{")
                end   = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(raw[start:end])
        except Exception as e:
            print(f"   Groq ürün hatası: {str(e)[:60]}")
        return None

    def generate_blog(self):
        if not self.available:
            return None
        # Geniş konu havuzu — her hafta farklı konu
        all_topics = [
            ("Spring 2026 Fashion Trends You Can Get on Amazon Right Now", "spring 2026 fashion trends amazon"),
            ("Amazon vs Designer: Same Look for a Fraction of the Price", "amazon dupe designer fashion 2026"),
            ("The Best Affordable Jewelry That Actually Lasts", "affordable tarnish-free jewelry amazon"),
            ("How to Style a Wrap Dress 6 Different Ways", "how to style wrap dress amazon"),
            ("10 Amazon Bag Finds Under $50 That Look Luxurious", "affordable luxury bags amazon 2026"),
            ("The Ultimate Guide to Affordable Summer Dresses 2026", "affordable summer dresses amazon 2026"),
            ("How to Build a Minimalist Wardrobe on a Budget", "minimalist wardrobe budget amazon"),
            ("Best Amazon Fashion Finds Under $30 This Week", "amazon fashion finds under 30 dollars"),
            ("How to Look Expensive on a Shoestring Budget", "look expensive budget fashion tips"),
            ("10 Timeless Pieces Every Woman Needs in Her Closet", "timeless wardrobe essentials women"),
            ("The Best White Sneakers on Amazon — Tested and Reviewed", "best white sneakers amazon women 2026"),
            ("Amazon Handbag Dupes That Look Designer", "amazon designer handbag dupes 2026"),
            ("How to Style Oversized Blazers 5 Ways", "how to style oversized blazer outfit ideas"),
            ("The Best Amazon Dresses for Every Body Type", "amazon dresses every body type 2026"),
            ("Affordable Accessories That Instantly Elevate Any Outfit", "affordable accessories elevate outfit amazon"),
            ("How to Create the Perfect Capsule Wardrobe for $150", "capsule wardrobe 150 dollars amazon"),
            ("Best Amazon Shoes Under $50 — Our Editor Picks", "best amazon shoes under 50 dollars 2026"),
            ("The Quiet Luxury Trend: How to Get the Look for Less", "quiet luxury trend affordable amazon"),
            ("Work From Home Outfits That Actually Look Professional", "work from home outfits professional women"),
            ("Summer Sandals on Amazon: The Ultimate Buying Guide", "summer sandals amazon buying guide 2026"),
        ]
        # Arşivdeki konularla çakışmayı önle
        archive = load_blog_archive()
        used_titles = {p.get("title","") for p in archive}
        available = [t for t in all_topics if t[0] not in used_titles]
        topics = available if available else all_topics
        topic, keyword = random.choice(topics)
        prompt = f"""You are a senior fashion editor and SEO expert for chic-cheap.com, an Amazon affiliate fashion site.

Write a comprehensive, SEO-optimized blog post about: "{topic}"
Primary keyword to rank for: "{keyword}"

REQUIREMENTS:
- Minimum 700 words of engaging, original content
- Natural keyword usage (not stuffed) — use keyword in H1, first paragraph, and 2-3 subheadings
- Include secondary keywords naturally throughout
- Structure: Hook intro → What/Why → How-To or List → Product recommendations → Conclusion with CTA
- HTML tags only: h2, h3, p, ul, ol, li, strong, em — NO markdown
- Conversational but expert tone — like a knowledgeable friend giving advice
- Include 3-5 specific Amazon product type recommendations (not real ASINs, just product categories)
- Add a "Pro Tip" or "Editor's Note" callout using <strong> tag
- End with a clear call-to-action to shop the picks

Return ONLY valid JSON, no markdown fences, no extra text:
{{"title":"{topic}","meta_description":"Compelling SEO meta description max 155 chars, includes keyword naturally","summary":"Two engaging sentences that make readers want to click — include a hook and benefit.","content":"Full HTML article minimum 700 words","image_url":"https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800","slug":"{keyword.replace(' ','-').replace(',','')}"}}"""
        try:
            raw = self._call(prompt, max_tokens=1500)
            if raw:
                start = raw.find("{")
                end   = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    # Control karakterleri temizle
                    clean = raw[start:end]
                    clean = clean.replace("\r", " ").replace("\t", " ")
                    clean = "".join(ch if ord(ch) >= 32 or ch in "\n" else " " for ch in clean)
                    data = json.loads(clean)
                    if not data.get("image_url"):
                        data["image_url"] = "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800"
                    print(f"   → Groq blog: {data['title'][:55]}...")
                    return data
        except Exception as e:
            print(f"   Groq blog hatası: {str(e)[:60]}")
        return None

# ── ŞABLON MOTORU (Yedek) ─────────────────────────────────
class TemplateEngine:
    def enrich_product(self, title, price, category):
        cat = category if category in REVIEWS else "Accessories"
        emoji = {"Dresses":"✨","Tops":"💕","Bags":"👜","Shoes":"👠","Jewelry":"💎","Accessories":"🌟"}.get(cat,"🛍️")
        return {
            "review_text": random.choice(REVIEWS[cat]),
            "styling_tip": random.choice(TIPS[cat]),
            "ai_score":    random.randint(86, 97),
            "pin_title":   f"{emoji} {title[:45]} — {price}",
            "pin_desc":    f"Shop this stunning {cat.lower()} on Amazon for only {price}. Curated by Chic-Cheap editors! #fashion #amazonfashion #style",
        }

    def generate_blog(self):
        post = random.choice(BLOG_POOL)
        print(f"   → Şablon blog: {post['title'][:55]}...")
        return post

# ── AMAZON PAAPI ───────────────────────────────────────────
def fetch_amazon_products():
    if not all([AMAZON_KEY, AMAZON_SECRET, AmazonApi]):
        print("⚠️  Amazon PAAPI yok → fallback kullanılıyor.")
        return None
    try:
        amazon   = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, COUNTRY, throttling=2)
        products = []
        cats     = random.sample(AMAZON_CATEGORIES, min(8, len(AMAZON_CATEGORIES)))
        for cat in cats:
            try:
                res = amazon.search_items(keywords=cat["keyword"], item_count=2)
                if res and res.items:
                    for item in res.items:
                        price = "N/A"
                        if item.offers and item.offers.listings:
                            price = f"${item.offers.listings[0].price.amount}"
                        image = ""
                        if item.images and item.images.primary:
                            image = item.images.primary.large.url
                        products.append({"title":item.item_info.title.display_value,"price":price,"category":cat["category"],"image_url":image,"link":item.detail_page_url})
                time.sleep(1)
            except Exception as e:
                print(f"   Kategori hatası ({cat['keyword']}): {e}")
        print(f"✅ Amazon PAAPI: {len(products)} ürün çekildi.")
        return products if products else None
    except Exception as e:
        print(f"❌ Amazon PAAPI hatası: {e}")
        return None

# ── PİNTEREST DOSYALARI ────────────────────────────────────
def create_pinterest_files(products):
    boards = {"Dresses":"Affordable Dresses 2026","Tops":"Chic Tops & Blouses","Bags":"Bags & Purses Under $70","Jewelry":"Affordable Jewelry Finds","Shoes":"Shoes Under $70","Accessories":"Style Accessories"}
    rss     = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel,"title").text       = "Chic-Cheap Fashion Finds"
    ET.SubElement(channel,"link").text        = "https://chic-cheap.com"
    ET.SubElement(channel,"description").text = "Curated Style. Smart Prices."
    with open("pinterest_upload.csv","w",newline="",encoding="utf-8-sig") as f:
        w = csv.DictWriter(f,fieldnames=["Title","Description","Link","Image","Board"],quoting=csv.QUOTE_ALL)
        w.writeheader()
        for p in products:
            item = ET.SubElement(channel,"item")
            ET.SubElement(item,"title").text       = p.get("pin_title",p["title"])[:100]
            ET.SubElement(item,"link").text        = "https://chic-cheap.com"
            ET.SubElement(item,"description").text = p.get("pin_desc","")[:500]
            enc = ET.SubElement(item,"enclosure"); enc.set("url",p["image_url"]); enc.set("type","image/jpeg")
            ET.SubElement(item,"pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            w.writerow({"Title":p.get("pin_title",p["title"])[:100],"Description":p.get("pin_desc","")[:500],"Link":"https://chic-cheap.com","Image":p["image_url"],"Board":boards.get(p.get("category",""),"Chic on a Budget")})
    ET.ElementTree(rss).write("pinterest.xml",encoding="utf-8",xml_declaration=True)
    print("📌 Pinterest XML + CSV oluşturuldu.")


# ── BLOG ARŞİVİ ───────────────────────────────────────────
def load_blog_archive():
    """Daha önce yayınlanan blogları yükler."""
    try:
        with open("blog_archive.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_blog_archive(archive):
    """Blog arşivini kaydeder (max 20 yazı tutar)."""
    with open("blog_archive.json", "w", encoding="utf-8") as f:
        json.dump(archive[-20:], f, indent=2, ensure_ascii=False)

# ── SİTEMAP ÜRETİCİ ──────────────────────────────────────
def generate_sitemap(blog_archive):
    """SEO için dinamik sitemap.xml üretir."""
    root = ET.Element("urlset")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    # Ana sayfa
    url = ET.SubElement(root, "url")
    ET.SubElement(url, "loc").text     = "https://chic-cheap.com/"
    ET.SubElement(url, "changefreq").text = "daily"
    ET.SubElement(url, "priority").text   = "1.0"
    ET.SubElement(url, "lastmod").text    = datetime.now().strftime("%Y-%m-%d")

    # Blog yazıları
    for i, post in enumerate(reversed(blog_archive[-10:])):
        url = ET.SubElement(root, "url")
        slug = post.get("slug", f"blog-post-{i+1}")
        ET.SubElement(url, "loc").text        = f"https://chic-cheap.com/#{slug}"
        ET.SubElement(url, "changefreq").text = "weekly"
        ET.SubElement(url, "priority").text   = "0.8"
        ET.SubElement(url, "lastmod").text    = post.get("date", datetime.now().strftime("%Y-%m-%d"))

    # Kategori sayfaları
    for cat, priority in [("dresses","0.7"),("tops","0.7"),("bags","0.7"),("shoes","0.7"),("jewelry","0.6"),("accessories","0.6")]:
        url = ET.SubElement(root, "url")
        ET.SubElement(url, "loc").text        = f"https://chic-cheap.com/#{cat}"
        ET.SubElement(url, "changefreq").text = "daily"
        ET.SubElement(url, "priority").text   = priority

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write("sitemap.xml", encoding="utf-8", xml_declaration=True)
    print("🗺️  sitemap.xml güncellendi.")

# ── GOOGLE PING ───────────────────────────────────────────
def ping_search_engines():
    """Arama motorlarına sitemap güncellendiğini bildirir."""
    sitemap_url = urllib.parse.quote("https://chic-cheap.com/sitemap.xml")
    engines = [
        ("Bing", f"https://www.bing.com/ping?sitemap={sitemap_url}"),
    ]
    for name, url in engines:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ChicCheapBot/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"📡 {name} ping: {resp.status} OK")
        except Exception as e:
            print(f"   {name} ping: {str(e)[:50]}")
    print("💡 Google: Search Console'dan sitemap'i manuel ekle (bir kez yeterli)")

# ── ROBOTS.TXT ────────────────────────────────────────────
def generate_robots():
    """robots.txt dosyası üretir."""
    content = """User-agent: *
Allow: /

Sitemap: https://chic-cheap.com/sitemap.xml
"""
    with open("robots.txt", "w") as f:
        f.write(content)
    print("🤖 robots.txt güncellendi.")

# ── ANA FONKSİYON ─────────────────────────────────────────
def main():
    print("="*55)
    print("  CHIC-CHEAP.COM — Automation Engine v4.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*55)

    groq     = GroqEngine()
    template = TemplateEngine()
    ai_mode  = groq.available
    print(f"\n🤖 AI Modu: {'Groq ✅' if ai_mode else 'Şablon'}")

    # 1. Ürünleri çek
    print("\n📦 Ürünler çekiliyor...")
    products = fetch_amazon_products()
    if not products:
        products = random.sample(FALLBACK, min(16, len(FALLBACK)))
        print(f"ℹ️  Fallback: {len(products)} ürün seçildi.")

    # 2. Her ürüne benzersiz görsel + içerik ekle
    print(f"\n✍️  {len(products)} ürün işleniyor...")
    used_images = set()
    enriched = []
    for p in products:
        # Benzersiz görsel ata — her zaman yeni bir tane seç
        p["image_url"] = get_unique_image(p["category"], used_images)

        # AI veya şablon içerik
        result = None
        if ai_mode:
            result = groq.enrich_product(p["title"], p["price"], p["category"])
        if not result:
            result = template.enrich_product(p["title"], p["price"], p["category"])
        enriched.append({**p, **result})

    # 3. Blog üret
    print("\n📝 Blog üretiliyor...")
    blog = None
    if ai_mode:
        blog = groq.generate_blog()
    if not blog:
        blog = template.generate_blog()

    # 4. Kaydet
    output = {
        "generated_at": datetime.now().isoformat(),
        "amazon_tag":   AMAZON_TAG,
        "ai_mode":      "groq" if ai_mode else "template",
        "config":       {"adsense_id":ADSENSE_ID,"adsense_slot":ADSENSE_SLOT,"pinterest_url":PINTEREST_URL,"site_url":"https://chic-cheap.com"},
        "products":     enriched,
        "blog":         blog,
        "stats":        {"total_products":len(enriched),"categories":list(set(p["category"] for p in enriched))},
    }
    with open("website_data.json","w",encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    create_pinterest_files(enriched)

    # 5. Blog arşivini güncelle
    archive = load_blog_archive()
    if blog:
        blog_entry = {
            "title":   blog.get("title",""),
            "summary": blog.get("summary",""),
            "slug":    blog.get("slug", blog.get("title","").lower().replace(" ","-")[:50]),
            "date":    datetime.now().strftime("%Y-%m-%d"),
        }
        # Aynı başlıklı yazı yoksa ekle
        if not any(a.get("title") == blog_entry["title"] for a in archive):
            archive.append(blog_entry)
            save_blog_archive(archive)
            print(f"📚 Blog arşivi güncellendi: {len(archive)} yazı")

    # 6. Sitemap güncelle
    generate_sitemap(archive)

    # 7. robots.txt güncelle
    generate_robots()

    # 8. Google'a bildir
    ping_search_engines()

    print("\n✅ TAMAMLANDI!")
    print(f"   → {len(enriched)} ürün işlendi")
    print(f"   → AI: {'Groq' if ai_mode else 'Şablon'}")
    print(f"   → Blog arşivi: {len(archive)} yazı")
    print(f"   → website_data.json, sitemap.xml, robots.txt güncellendi")
    print("="*55)

if __name__ == "__main__":
    main()
