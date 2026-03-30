"""
CHIC-CHEAP.COM — Automation Engine v3.0 (Final)
================================================
- Gemini 2.0 Flash API (ücretsiz tier) ile AI içerik
- Gemini çalışmazsa akıllı şablon sistemi devreye girer
- Amazon PAAPI ile gerçek ürünler (kota açılınca aktif olur)
- Kota yoksa zengin fallback ürün havuzu kullanılır
- Her gün sabah 07:00 UTC otomatik çalışır
"""

import os, json, time, random, csv, xml.etree.ElementTree as ET
from datetime import datetime

# ── BAĞIMLILIKLAR ──────────────────────────────────────────
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from amazon_paapi import AmazonApi
except ImportError:
    try:
        from amazon_creatorsapi import AmazonApi
    except ImportError:
        AmazonApi = None

# ── AYARLAR (GitHub Secrets) ───────────────────────────────
GEMINI_KEY   = os.environ.get("GEMINI_API_KEY", "")
AMAZON_KEY   = os.environ.get("AMAZON_ACCESS_KEY", "")
AMAZON_SECRET= os.environ.get("AMAZON_SECRET_KEY", "")
AMAZON_TAG   = os.environ.get("AMAZON_TAG", "chiccheap-20")
ADSENSE_ID   = os.environ.get("ADSENSE_ID", "")
ADSENSE_SLOT = os.environ.get("ADSENSE_SLOT", "")
PINTEREST_URL= os.environ.get("PINTEREST_URL", "https://www.pinterest.com/chiccheapcom")
COUNTRY      = "US"

# ── AMAZON KATEGORİLERİ ────────────────────────────────────
AMAZON_CATEGORIES = [
    {"keyword": "women floral maxi dress",        "category": "Dresses"},
    {"keyword": "women casual midi dress",         "category": "Dresses"},
    {"keyword": "women wrap dress",                "category": "Dresses"},
    {"keyword": "women silk blouse top",           "category": "Tops"},
    {"keyword": "women oversized knit cardigan",   "category": "Tops"},
    {"keyword": "women crossbody bag leather",     "category": "Bags"},
    {"keyword": "women tote bag fashion",          "category": "Bags"},
    {"keyword": "women gold layered necklace",     "category": "Jewelry"},
    {"keyword": "women hoop earrings",             "category": "Jewelry"},
    {"keyword": "women cat eye sunglasses",        "category": "Accessories"},
    {"keyword": "women strappy sandals heels",     "category": "Shoes"},
    {"keyword": "women white sneakers",            "category": "Shoes"},
]

# ── FALLBACK ÜRÜN HAVUZU (50 ürün) ────────────────────────
FALLBACK = [
    # DRESSES
    {"title":"Bohemian Floral Maxi Dress",          "price":"$39.99","category":"Dresses",    "image_url":"https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=600","link":f"https://www.amazon.com/s?k=boho+maxi+dress&tag={AMAZON_TAG}"},
    {"title":"Red Satin Evening Gown",              "price":"$59.50","category":"Dresses",    "image_url":"https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=600","link":f"https://www.amazon.com/s?k=red+satin+gown&tag={AMAZON_TAG}"},
    {"title":"White Linen Summer Dress",            "price":"$34.00","category":"Dresses",    "image_url":"https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?q=80&w=600","link":f"https://www.amazon.com/s?k=white+linen+dress&tag={AMAZON_TAG}"},
    {"title":"Green Wrap Midi Dress",               "price":"$55.00","category":"Dresses",    "image_url":"https://images.unsplash.com/photo-1605763240004-7e93b172d754?q=80&w=600","link":f"https://www.amazon.com/s?k=green+wrap+dress&tag={AMAZON_TAG}"},
    {"title":"Black Cocktail Mini Dress",           "price":"$45.00","category":"Dresses",    "image_url":"https://images.unsplash.com/photo-1539008835657-9e8e9680c956?q=80&w=600","link":f"https://www.amazon.com/s?k=black+cocktail+dress&tag={AMAZON_TAG}"},
    {"title":"Yellow Floral Sundress",              "price":"$29.99","category":"Dresses",    "image_url":"https://images.unsplash.com/photo-1566174053879-31528523f8ae?q=80&w=600","link":f"https://www.amazon.com/s?k=yellow+sundress&tag={AMAZON_TAG}"},
    {"title":"Vintage Polka Dot Dress",             "price":"$42.99","category":"Dresses",    "image_url":"https://images.unsplash.com/photo-1612336307429-8a898d10e223?q=80&w=600","link":f"https://www.amazon.com/s?k=polka+dot+dress&tag={AMAZON_TAG}"},
    {"title":"Pink Satin Slip Dress",               "price":"$38.00","category":"Dresses",    "image_url":"https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?q=80&w=600","link":f"https://www.amazon.com/s?k=pink+slip+dress&tag={AMAZON_TAG}"},
    # TOPS
    {"title":"White Silk Blouse",                   "price":"$49.90","category":"Tops",       "image_url":"https://images.unsplash.com/photo-1598554060854-b827048d7458?q=80&w=600","link":f"https://www.amazon.com/s?k=silk+blouse+women&tag={AMAZON_TAG}"},
    {"title":"Pink Oversized Cardigan",             "price":"$30.00","category":"Tops",       "image_url":"https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?q=80&w=600","link":f"https://www.amazon.com/s?k=oversized+cardigan+women&tag={AMAZON_TAG}"},
    {"title":"Striped Breton Top",                  "price":"$24.00","category":"Tops",       "image_url":"https://images.unsplash.com/photo-1503342394128-c104d54dba01?q=80&w=600","link":f"https://www.amazon.com/s?k=breton+striped+top&tag={AMAZON_TAG}"},
    {"title":"Black Ribbed Turtleneck",             "price":"$28.00","category":"Tops",       "image_url":"https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=600","link":f"https://www.amazon.com/s?k=ribbed+turtleneck+women&tag={AMAZON_TAG}"},
    {"title":"Effortless Satin Camisole Top",       "price":"$14.87","category":"Tops",       "image_url":"https://images.unsplash.com/photo-1621072156002-e2fccdc0b176?q=80&w=600","link":f"https://www.amazon.com/s?k=satin+camisole+top&tag={AMAZON_TAG}"},
    # BAGS
    {"title":"Leather Crossbody Bag",               "price":"$55.00","category":"Bags",       "image_url":"https://images.unsplash.com/photo-1590874103328-eac38a683ce7?q=80&w=600","link":f"https://www.amazon.com/s?k=leather+crossbody+bag&tag={AMAZON_TAG}"},
    {"title":"Chic Canvas Tote Bag",                "price":"$32.50","category":"Bags",       "image_url":"https://images.unsplash.com/photo-1591561954557-26941169b49e?q=80&w=600","link":f"https://www.amazon.com/s?k=canvas+tote+bag+women&tag={AMAZON_TAG}"},
    {"title":"Woven Straw Beach Bag",               "price":"$28.00","category":"Bags",       "image_url":"https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600","link":f"https://www.amazon.com/s?k=straw+beach+bag&tag={AMAZON_TAG}"},
    {"title":"Black Structured Handbag",            "price":"$65.00","category":"Bags",       "image_url":"https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600","link":f"https://www.amazon.com/s?k=structured+handbag+black&tag={AMAZON_TAG}"},
    {"title":"Pink Mini Clutch",                    "price":"$25.00","category":"Bags",       "image_url":"https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?q=80&w=600","link":f"https://www.amazon.com/s?k=mini+clutch+bag&tag={AMAZON_TAG}"},
    # JEWELRY
    {"title":"Gold Layered Necklace Set",           "price":"$14.99","category":"Jewelry",    "image_url":"https://images.unsplash.com/photo-1599643478518-17488fbbcd75?q=80&w=600","link":f"https://www.amazon.com/s?k=gold+layered+necklace&tag={AMAZON_TAG}"},
    {"title":"Gold Hoop Earrings",                  "price":"$16.99","category":"Jewelry",    "image_url":"https://images.unsplash.com/photo-1630019852942-f89202989a51?q=80&w=600","link":f"https://www.amazon.com/s?k=gold+hoop+earrings&tag={AMAZON_TAG}"},
    {"title":"Pearl Drop Earrings",                 "price":"$12.50","category":"Jewelry",    "image_url":"https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=600","link":f"https://www.amazon.com/s?k=pearl+drop+earrings&tag={AMAZON_TAG}"},
    {"title":"Silver Stacking Ring Set",            "price":"$18.00","category":"Jewelry",    "image_url":"https://images.unsplash.com/photo-1605100804763-247f67b3557e?q=80&w=600","link":f"https://www.amazon.com/s?k=silver+stacking+rings&tag={AMAZON_TAG}"},
    {"title":"Crystal Pendant Necklace",            "price":"$22.00","category":"Jewelry",    "image_url":"https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?q=80&w=600","link":f"https://www.amazon.com/s?k=crystal+pendant+necklace&tag={AMAZON_TAG}"},
    # SHOES
    {"title":"White Canvas Sneakers",               "price":"$29.99","category":"Shoes",      "image_url":"https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=600","link":f"https://www.amazon.com/s?k=white+canvas+sneakers+women&tag={AMAZON_TAG}"},
    {"title":"Strappy Stiletto Heels",              "price":"$49.99","category":"Shoes",      "image_url":"https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600","link":f"https://www.amazon.com/s?k=strappy+stiletto+heels&tag={AMAZON_TAG}"},
    {"title":"Leather Ankle Boots",                 "price":"$65.00","category":"Shoes",      "image_url":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600","link":f"https://www.amazon.com/s?k=leather+ankle+boots+women&tag={AMAZON_TAG}"},
    {"title":"Summer Flat Sandals",                 "price":"$24.50","category":"Shoes",      "image_url":"https://images.unsplash.com/photo-1562273138-f46be4ebdf6e?q=80&w=600","link":f"https://www.amazon.com/s?k=flat+sandals+women&tag={AMAZON_TAG}"},
    {"title":"Block Heel Mules",                    "price":"$38.00","category":"Shoes",      "image_url":"https://images.unsplash.com/photo-1518049362265-d5b2a6467637?q=80&w=600","link":f"https://www.amazon.com/s?k=block+heel+mules+women&tag={AMAZON_TAG}"},
    # ACCESSORIES
    {"title":"Cat Eye Sunglasses",                  "price":"$18.99","category":"Accessories","image_url":"https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600","link":f"https://www.amazon.com/s?k=cat+eye+sunglasses+women&tag={AMAZON_TAG}"},
    {"title":"Rose Gold Watch",                     "price":"$85.00","category":"Accessories","image_url":"https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?q=80&w=600","link":f"https://www.amazon.com/s?k=rose+gold+watch+women&tag={AMAZON_TAG}"},
    {"title":"Silk Hair Scarf",                     "price":"$14.99","category":"Accessories","image_url":"https://images.unsplash.com/photo-1586078436377-46714147839b?q=80&w=600","link":f"https://www.amazon.com/s?k=silk+hair+scarf&tag={AMAZON_TAG}"},
    {"title":"Straw Sun Hat",                       "price":"$22.00","category":"Accessories","image_url":"https://images.unsplash.com/photo-1521335629791-ce4aec6c1d09?q=80&w=600","link":f"https://www.amazon.com/s?k=straw+sun+hat+women&tag={AMAZON_TAG}"},
    {"title":"Leather Belt",                        "price":"$20.00","category":"Accessories","image_url":"https://images.unsplash.com/photo-1624223359990-8b050454b378?q=80&w=600","link":f"https://www.amazon.com/s?k=leather+belt+women&tag={AMAZON_TAG}"},
]

# ── ŞABLON VERİLERİ ────────────────────────────────────────
REVIEWS = {
    "Dresses":     ["This dreamy dress combines elegance and comfort — perfect for any occasion.","A wardrobe essential that transitions effortlessly from day to night.","Flattering silhouette at a price that won't break the bank.","Turn heads without overspending — style and value in one perfect package.","The kind of dress you'll reach for again and again, season after season."],
    "Tops":        ["Versatile top that pairs beautifully with jeans, skirts, or tailored trousers.","Elevated basics done right — soft, stylish, and incredibly affordable.","A closet staple you'll style a hundred different ways.","Effortlessly chic — proof that great style doesn't require a big budget.","The perfect layering piece for any season, any occasion."],
    "Bags":        ["Spacious, stylish, and surprisingly affordable — this bag does it all.","A chic carryall that looks far more expensive than it actually is.","From farmer's market to date night, this bag handles everything in style.","Elevated design at a fraction of the designer price tag.","The bag that completes every outfit, whatever the occasion."],
    "Shoes":       ["Step out in style without the splurge — comfort meets chic design perfectly.","These shoes prove you don't need to spend a fortune to look incredible.","All-day wearability with serious style credentials — a rare find.","From brunch to cocktails, one shoe with endless possibilities.","The perfect finishing touch for any outfit, at any budget."],
    "Jewelry":     ["Dainty, elegant, and incredibly affordable — jewelry goals fully achieved.","Layer it, stack it, mix it — this piece works beautifully every way.","Timeless design that elevates even the simplest outfit instantly.","Looks like fine jewelry, feels like a steal at this price.","The kind of accessory that gets compliments every single time you wear it."],
    "Accessories": ["The finishing touch your outfit has been waiting for — right here.","Small accessory, massive impact — instantly elevates any look.","A style-savvy pick that adds instant polish to any ensemble.","Functional, fashionable, and completely affordable — the holy trinity.","Because the right accessory genuinely changes everything."],
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
    {"title":"10 Amazon Dresses Under $50 That Look Incredibly Expensive","meta_description":"Discover 10 stunning Amazon dresses under $50 that look like they cost 10x more. Curated by Chic-Cheap editors.","summary":"Looking for dresses that look luxurious without the price tag? Our editors found 10 Amazon gems that will transform your wardrobe without emptying your wallet.","image_url":"https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=800","content":"<h2>Style Doesn't Have to Cost a Fortune</h2><p>One of fashion's best-kept secrets? Amazon is home to some of the most stylish, well-made dresses available — at prices that will genuinely surprise you. Our editors spend hours each week curating the very best finds so you don't have to.</p><h2>What to Look for When Shopping Amazon Dresses</h2><p>Before diving into our picks, here's what our team always checks: <strong>fabric composition</strong> (look for natural blends), <strong>customer reviews with photos</strong>, and <strong>size consistency ratings</strong>. These three factors separate a great Amazon buy from a disappointment.</p><h2>Our Top Picks This Season</h2><p>From flowing boho maxis to sleek cocktail styles, here are the dresses our editors are obsessing over right now. Each one is under $50, ships fast with Prime, and comes with hundreds of glowing reviews.</p><ul><li><strong>The Maxi:</strong> Perfect for beach days, garden parties, or weekend brunches. Look for adjustable straps and a forgiving elastic waist.</li><li><strong>The Midi:</strong> The most versatile length of the moment. Pairs with sneakers by day, heels by night.</li><li><strong>The Wrap:</strong> Universally flattering. Works on every body type, every single time.</li><li><strong>The Mini:</strong> For the days you want to feel bold. Keep accessories minimal and let the dress do all the talking.</li></ul><h2>Styling Tips from Our Editors</h2><p>A great dress is just the beginning. <strong>Add a thin belt</strong> to any loose-fitting dress to instantly create shape. <strong>Layer a denim jacket</strong> for daytime, swap for a blazer for evening. The right shoes change everything.</p><h2>Shopping Tips</h2><ul><li>Always read reviews that include photos — they give the most accurate color and fit representation.</li><li>Check the size chart for each listing individually, as sizing varies by brand.</li><li>Look for dresses with at least 100 reviews and a 4.0+ star rating.</li><li>Prime shipping means you can order and receive within days — perfect for last-minute occasions.</li></ul>"},
    {"title":"How to Build a Capsule Wardrobe for Under $200 — Amazon Edition","meta_description":"Build a complete, stylish capsule wardrobe for under $200 using Amazon finds. Step-by-step guide covering every essential piece.","summary":"A capsule wardrobe doesn't have to cost thousands. We show you exactly how to build a complete, versatile wardrobe for under $200 — entirely from Amazon.","image_url":"https://images.unsplash.com/photo-1558769132-cb1aea458c5e?q=80&w=800","content":"<h2>What Is a Capsule Wardrobe?</h2><p>A capsule wardrobe is a curated collection of timeless, versatile pieces that work together seamlessly. The goal: maximum outfits from minimum pieces. Done right, you'll have something perfect to wear for every occasion.</p><h2>The Essential Pieces</h2><ul><li><strong>2 quality basic tops</strong> — white and neutral. The foundation of everything.</li><li><strong>1 classic blouse</strong> — silk or satin look. Elevates any bottom instantly.</li><li><strong>1 versatile dress</strong> — wrap or midi style works for day and night equally.</li><li><strong>1 pair of straight-leg jeans</strong> — the most universal bottom you'll ever own.</li><li><strong>1 tailored blazer</strong> — transforms any casual outfit into polished perfection.</li><li><strong>1 cardigan or knit</strong> — your essential layering hero through every season.</li><li><strong>1 pair of white sneakers</strong> — the most versatile shoes in fashion history, period.</li><li><strong>1 pair of block heels</strong> — for when you want to effortlessly elevate.</li><li><strong>1 structured bag</strong> — pulls every single outfit together with instant sophistication.</li></ul><h2>The Color Strategy</h2><p>Stick to a neutral base — white, black, camel, navy, grey — and add one or two accent colors you genuinely love. Every piece should theoretically work with every other piece. This is the secret that makes a capsule wardrobe actually function beautifully.</p><h2>Shopping Tips for Amazon</h2><ul><li>Search for the Amazon Essentials brand — consistently good quality at reliably low prices.</li><li>Filter by 4+ stars and 200+ reviews for the most reliable quality picks.</li><li>Read the fabric content — avoid 100% polyester for basics; look for cotton blends.</li><li>Use Prime Try Before You Buy where available — order, try, return what doesn't work.</li></ul>"},
    {"title":"Amazon Fashion Finds: This Week's Most Stylish Affordable Picks","meta_description":"Our editors reveal this week's best Amazon fashion finds — stylish, affordable, and shipping fast with Prime. Updated weekly.","summary":"Every week our editors scour Amazon so you don't have to. This week's finds are genuinely exceptional — stylish pieces at prices that seem almost too good to be true.","image_url":"https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800","content":"<h2>This Week's Obsessions</h2><p>Every single week, our team dives deep into Amazon's fashion catalogue to find the pieces genuinely worth your attention and money. We look for quality, style, value, and — crucially — real customer photos that confirm what arrives actually matches the listing.</p><h2>Why We Trust Amazon for Fashion in 2026</h2><p>The stigma around Amazon fashion is fading fast. In 2026, the platform hosts hundreds of quality brands, ships within days with Prime, and offers easy, hassle-free returns. The key is simply knowing where to look — and that's exactly what we're here for every single week.</p><h2>What Makes a Great Amazon Find?</h2><ul><li><strong>Real photos in reviews:</strong> Always check customer-uploaded photos before buying. These show actual colours, fit, and fabric quality accurately.</li><li><strong>High review count:</strong> 200+ reviews with a 4.2+ rating is our absolute minimum threshold.</li><li><strong>Verified purchases:</strong> Filter reviews by Verified Purchase to avoid misleading fake reviews.</li><li><strong>Detailed size information:</strong> Great listings include model measurements and the size they're actually wearing.</li></ul><h2>This Season's Biggest Amazon Trends</h2><p><strong>Satin and silk-look fabrics</strong> are everywhere right now, and Amazon has dozens of stunning options under $30 that look legitimately luxurious. <strong>Wide-leg everything</strong> continues its absolute dominance — trousers, jeans, and even jumpsuits. <strong>Coastal grandmother aesthetic</strong> pieces — linen, relaxed knits, neutral palettes — remain incredibly popular and make the most beautiful gifts.</p><h2>Our Shopping Philosophy</h2><p>We believe great style is fundamentally about intention, not price tags. A $35 Amazon dress worn with confidence and the right accessories looks far better than an expensive piece worn without thought. Shop deliberately, choose pieces that genuinely excite you, and always remember: the best outfit is the one that makes you feel like the very best version of yourself.</p>"},
    {"title":"Summer Accessories Under $25 That Instantly Elevate Any Look","meta_description":"Discover the best summer accessories under $25 on Amazon. Sunglasses, bags, jewelry and more — all under $25 and all incredibly stylish.","summary":"The right accessories can transform any outfit from ordinary to outstanding. Here are the summer accessories our editors are obsessing over — all under $25.","image_url":"https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=800","content":"<h2>The Power of Accessories</h2><p>Fashion insiders have known this secret for decades: you don't need an entirely new wardrobe to look completely different. The right accessories — the perfect pair of sunglasses, a standout necklace, an eye-catching bag — can transform the most basic outfit into something that looks genuinely considered and stylish.</p><h2>Summer's Essential Accessories</h2><ul><li><strong>Sunglasses:</strong> The single most transformative accessory in fashion. A great pair of shades adds instant mystery and glamour to any look, whatever you're wearing underneath.</li><li><strong>Statement earrings:</strong> When you're wearing a simple white tee and jeans, bold earrings make the entire outfit. Gold hoops, drop pearls, or colourful resin styles — all incredibly effective.</li><li><strong>The straw bag:</strong> Summer's most versatile bag. Works at the beach, at brunch, at the farmer's market. Instantly casual-chic.</li><li><strong>A silk scarf:</strong> Wear it in your hair, around your neck, tied to your bag handle. Infinitely versatile and endlessly elegant.</li><li><strong>Layered necklaces:</strong> Stack two or three delicate chains at different lengths for a perfectly curated, editorial look that cost you almost nothing.</li></ul><h2>Shopping Accessories on Amazon</h2><p>Amazon's accessories section has genuinely improved dramatically. Key things to check: for jewelry, look for hypoallergenic materials and tarnish-resistant coatings. For sunglasses, check for UV400 protection — non-negotiable for eye health. For bags, look at the interior lining quality in customer photos.</p><h2>The Golden Rule of Accessorizing</h2><p>Choose one hero accessory per outfit and build everything else around it. If you're wearing statement earrings, skip the necklace. If your bag is bold, keep the jewelry delicate. This editing principle is what separates effortless, stylish dressing from looking overdone — and it costs absolutely nothing to apply.</p>"},
    {"title":"Work Outfits Under $60: Look Polished Without Overspending","meta_description":"Build a professional, stylish work wardrobe for under $60 per outfit using Amazon finds. Our editors' top picks for affordable office fashion.","summary":"Looking professional at work doesn't require spending a fortune. Our editors found the best Amazon pieces for building a polished work wardrobe on a real budget.","image_url":"https://images.unsplash.com/photo-1594938298603-c8148c4dae35?q=80&w=800","content":"<h2>The Modern Work Wardrobe</h2><p>Office dress codes have evolved dramatically. Today's professional wardrobe is about looking polished, put-together, and authentically you — not following rigid, outdated rules. And the best news? You can achieve this entirely through smart Amazon shopping.</p><h2>The Foundation Pieces</h2><p>Every great work wardrobe starts with the same essential building blocks. <strong>A well-fitted blazer</strong> is non-negotiable — it instantly elevates everything underneath it, from a basic tee to a floral blouse. <strong>Tailored trousers</strong> in a neutral colour form the most versatile work bottom you can own. <strong>A classic blouse</strong> in white, ivory, or a soft pastel completes the foundational trio.</p><h2>Building Complete Outfits Under $60</h2><ul><li><strong>The Classic:</strong> Tailored black trousers + white blouse + minimal jewelry. Timeless, authoritative, and always right.</li><li><strong>The Modern Professional:</strong> Wide-leg trousers + tucked-in silk camisole + blazer over the top. Contemporary and polished.</li><li><strong>The Smart Casual:</strong> Midi dress + blazer + block heels. Effortlessly appropriate for most modern offices.</li><li><strong>The Power Look:</strong> Matching co-ord set in a neutral tone. Looks like a tailored suit, costs a fraction of one.</li></ul><h2>What to Look For on Amazon</h2><p>For work clothes specifically, fabric quality is crucial. Avoid anything that looks shiny or cheap under office lighting — this often means high polyester content. Look instead for <strong>ponte fabric</strong> (holds shape beautifully), <strong>crepe</strong> (drapes elegantly and doesn't wrinkle), or <strong>cotton blends</strong> (breathable and professional). Check customer photos specifically for how the fabric looks under different lighting conditions.</p>"},
]

# ── AMAZON PAAPI ───────────────────────────────────────────
def fetch_amazon_products():
    if not all([AMAZON_KEY, AMAZON_SECRET, AmazonApi]):
        print("⚠️  Amazon PAAPI credentials eksik → fallback kullanılıyor.")
        return None
    try:
        amazon  = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, COUNTRY, throttling=2)
        products = []
        cats    = random.sample(AMAZON_CATEGORIES, min(8, len(AMAZON_CATEGORIES)))
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
                        products.append({
                            "title":     item.item_info.title.display_value,
                            "price":     price,
                            "category":  cat["category"],
                            "image_url": image,
                            "link":      item.detail_page_url,
                        })
                time.sleep(1)
            except Exception as e:
                print(f"   Kategori hatası ({cat['keyword']}): {e}")
        print(f"✅ Amazon PAAPI: {len(products)} ürün çekildi.")
        return products if products else None
    except Exception as e:
        print(f"❌ Amazon PAAPI hatası: {e}")
        return None

# ── GEMİNİ AI MOTORU (google-genai SDK) ───────────────────
class GeminiEngine:
    def __init__(self):
        self.client = None
        self.model  = None
        if not GENAI_AVAILABLE or not GEMINI_KEY:
            return
        try:
            self.client = genai.Client(api_key=GEMINI_KEY)
            # Ücretsiz tier modelleri sırayla dene
            for model_name in [
                "gemini-2.0-flash-lite",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
            ]:
                try:
                    test = self.client.models.generate_content(
                        model=model_name,
                        contents="Say: OK"
                    )
                    if test and test.text:
                        self.model = model_name
                        print(f"✅ Gemini bağlandı: {model_name}")
                        break
                except Exception as e:
                    print(f"   {model_name} denendi → {str(e)[:60]}")
                    continue
        except Exception as e:
            print(f"⚠️  Gemini başlatılamadı: {e}")

    def call(self, prompt, max_retries=2):
        if not self.client or not self.model:
            return None
        for attempt in range(max_retries):
            try:
                resp = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                return resp.text
            except Exception as e:
                err = str(e)
                if "429" in err or "quota" in err.lower():
                    wait = 40 * (attempt + 1)
                    print(f"   ⏳ Rate limit ({attempt+1}/{max_retries}), {wait}s bekleniyor...")
                    time.sleep(wait)
                elif "404" in err or "not found" in err.lower():
                    print(f"   Model bulunamadı.")
                    return None
                else:
                    print(f"   Gemini hatası: {err[:80]}")
                    return None
        return None

    def enrich_product(self, title, price, category):
        prompt = f"""Fashion influencer for chic-cheap.com. Product: "{title}", Price: {price}, Category: {category}.
Return ONLY valid JSON, no markdown:
{{"review_text":"One compelling sentence (max 20 words) why this is worth buying.","styling_tip":"One practical styling tip (max 15 words).","ai_score":{random.randint(86,97)},"pin_title":"{category} find — {price} on Amazon!","pin_desc":"Shop this amazing {category.lower()} on Amazon. Curated by Chic-Cheap editors! #fashion #amazonfashion"}}"""
        raw = self.call(prompt)
        if raw:
            try:
                clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                return json.loads(clean)
            except:
                pass
        return None

    def generate_blog(self):
        topics = [
            ("Spring 2026 Fashion Trends You Can Get on Amazon Right Now", "spring 2026 fashion trends amazon"),
            ("Amazon vs Designer: Same Look for a Fraction of the Price", "amazon dupe designer fashion 2026"),
            ("The Best Affordable Jewelry That Actually Lasts", "affordable jewelry that doesn't tarnish"),
            ("How to Style a Wrap Dress 6 Different Ways", "how to style wrap dress"),
        ]
        topic, keyword = random.choice(topics)
        prompt = f"""Senior fashion editor for chic-cheap.com.
Write SEO blog post about: "{topic}" (keyword: "{keyword}")
Minimum 500 words. Use HTML tags: h2, p, ul, li, strong. No markdown.
Return ONLY valid JSON, no markdown fences:
{{"title":"{topic}","meta_description":"SEO description max 155 chars","summary":"Two engaging teaser sentences.","content":"Full HTML article here","image_url":"https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800"}}"""
        raw = self.call(prompt)
        if raw:
            try:
                clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                data  = json.loads(clean)
                if not data.get("image_url"):
                    data["image_url"] = "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=800"
                return data
            except:
                pass
        return None

# ── ŞABLON MOTORU (Yedek) ─────────────────────────────────
class TemplateEngine:
    def enrich_product(self, title, price, category):
        cat = category if category in REVIEWS else "Accessories"
        pin_cat = {
            "Dresses":"✨","Tops":"💕","Bags":"👜",
            "Shoes":"👠","Jewelry":"💎","Accessories":"🌟"
        }.get(cat,"🛍️")
        return {
            "review_text": random.choice(REVIEWS[cat]),
            "styling_tip": random.choice(TIPS[cat]),
            "ai_score":    random.randint(86, 97),
            "pin_title":   f"{pin_cat} {title[:45]} — {price}",
            "pin_desc":    f"Shop this stunning {cat.lower()} on Amazon for only {price}. Curated by Chic-Cheap! #fashion #amazonfashion #style",
        }

    def generate_blog(self):
        post = random.choice(BLOG_POOL)
        print(f"📝 Şablon blog seçildi: {post['title'][:55]}...")
        return post

# ── PİNTEREST DOSYALARI ────────────────────────────────────
def create_pinterest_files(products):
    board_map = {"Dresses":"Affordable Dresses 2026","Tops":"Chic Tops & Blouses","Bags":"Bags & Purses Under $70","Jewelry":"Affordable Jewelry Finds","Shoes":"Shoes Under $70","Accessories":"Style Accessories"}
    rss     = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text       = "Chic-Cheap Fashion Finds"
    ET.SubElement(channel, "link").text        = "https://chic-cheap.com"
    ET.SubElement(channel, "description").text = "Curated Style. Smart Prices."

    with open("pinterest_upload.csv","w",newline="",encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["Title","Description","Link","Image","Board"], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for p in products:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item,"title").text       = p.get("pin_title", p["title"])[:100]
            ET.SubElement(item,"link").text        = "https://chic-cheap.com"
            ET.SubElement(item,"description").text = p.get("pin_desc","")[:500]
            enc = ET.SubElement(item,"enclosure")
            enc.set("url", p["image_url"]); enc.set("type","image/jpeg")
            ET.SubElement(item,"pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            writer.writerow({"Title":p.get("pin_title",p["title"])[:100],"Description":p.get("pin_desc","")[:500],"Link":"https://chic-cheap.com","Image":p["image_url"],"Board":board_map.get(p.get("category",""),"Chic on a Budget")})

    ET.ElementTree(rss).write("pinterest.xml", encoding="utf-8", xml_declaration=True)
    print("📌 Pinterest XML + CSV oluşturuldu.")

# ── ANA FONKSİYON ─────────────────────────────────────────
def main():
    print("="*55)
    print("  CHIC-CHEAP.COM — Automation Engine v3.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*55)

    # Motorları başlat
    gemini   = GeminiEngine()
    template = TemplateEngine()
    ai_mode  = gemini.client is not None and gemini.model is not None
    print(f"\n🤖 AI Modu: {'Gemini ✅' if ai_mode else 'Şablon (Gemini bağlanamadı)'}")

    # 1. Ürünleri çek
    print("\n📦 Ürünler çekiliyor...")
    products = fetch_amazon_products()
    if not products:
        products = random.sample(FALLBACK, min(15, len(FALLBACK)))
        print(f"ℹ️  Fallback: {len(products)} ürün seçildi.")

    # 2. Her ürüne içerik ekle
    print(f"\n✍️  {len(products)} ürün için içerik üretiliyor...")
    enriched = []
    for p in products:
        result = None
        if ai_mode:
            result = gemini.enrich_product(p["title"], p["price"], p["category"])
            if result:
                time.sleep(3)
        if not result:
            result = template.enrich_product(p["title"], p["price"], p["category"])
        enriched.append({**p, **result})

    # 3. Blog üret
    print("\n📝 Blog üretiliyor...")
    blog = None
    if ai_mode:
        blog = gemini.generate_blog()
    if not blog:
        blog = template.generate_blog()
    print(f"   → {blog['title'][:60]}...")

    # 4. Kaydet
    output = {
        "generated_at": datetime.now().isoformat(),
        "amazon_tag":   AMAZON_TAG,
        "ai_mode":      "gemini" if ai_mode else "template",
        "config": {"adsense_id":ADSENSE_ID,"adsense_slot":ADSENSE_SLOT,"pinterest_url":PINTEREST_URL,"site_url":"https://chic-cheap.com"},
        "products": enriched,
        "blog":     blog,
        "stats":    {"total_products":len(enriched),"categories":list(set(p["category"] for p in enriched))},
    }
    with open("website_data.json","w",encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    create_pinterest_files(enriched)

    print("\n✅ TAMAMLANDI!")
    print(f"   → {len(enriched)} ürün işlendi")
    print(f"   → AI modu: {'Gemini' if ai_mode else 'Şablon'}")
    print(f"   → website_data.json kaydedildi")
    print("="*55)

if __name__ == "__main__":
    main()
