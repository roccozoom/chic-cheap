import Image from "next/image";
import Link from "next/link";
import { PrismaClient } from "@prisma/client";

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient({
  datasourceUrl: process.env.DATABASE_URL || "file:./dev.db"
});

export default async function Home() {
  const featuredProducts = await prisma.product.findMany({
    take: 8,
    orderBy: { aiScore: "desc" },
    include: { category: true }
  });

  const featuredBlogs = await prisma.blogPost.findMany({
    take: 2,
    orderBy: { createdAt: "desc" }
  });

  return (
    <div className="flex flex-col gap-16 md:gap-24">
      {/* HERO SECTION */}
      <section className="relative overflow-hidden bg-white">
        <div className="max-w-7xl mx-auto px-6 md:px-12 pt-16 pb-24 md:py-32 grid md:grid-cols-2 gap-12 items-center">
          <div className="z-10 flex flex-col items-start">
            <span className="inline-block py-1.5 px-4 rounded-full bg-pink-100 text-pink-600 text-[10px] font-bold tracking-widest uppercase mb-6">
              ✦ New Arrivals Updated Daily
            </span>
            <h1 className="font-playfair text-5xl md:text-7xl font-bold leading-[1.1] tracking-tight mb-6 text-zinc-900">
              Curated Style.<br/>
              <em className="not-italic text-pink-500">Smart Prices.</em>
            </h1>
            <p className="text-zinc-600 text-lg md:text-xl max-w-md leading-relaxed mb-10">
              We find the best fashion deals on Amazon so you don't have to. Fresh picks every single day.
            </p>
            <Link href="/shop" className="bg-zinc-950 text-white hover:bg-pink-500 transition-all transform hover:-translate-y-1 duration-300 py-4 px-8 rounded-full text-xs font-bold uppercase tracking-widest">
              Shop Today's Picks →
            </Link>
          </div>
          <div className="relative aspect-square md:aspect-[4/5] rounded-3xl overflow-hidden shadow-2xl">
            <Image 
              src="https://images.unsplash.com/photo-1558769132-cb1aea458c5e?q=80&w=900&auto=format&fit=crop" 
              alt="Fashion" 
              fill 
              className="object-cover"
              priority
              unoptimized
            />
            <div className="absolute bottom-6 left-6 right-6 md:right-auto bg-white/95 backdrop-blur-md p-5 rounded-2xl shadow-xl">
              <strong className="block font-playfair text-lg font-bold text-zinc-900 mb-1">Today's Editor's Pick</strong>
              <span className="text-xs text-zinc-600">Curated from 1,000+ Amazon listings</span>
            </div>
          </div>
        </div>
      </section>

      {/* TICKER */}
      <div className="bg-zinc-950 text-white py-3 overflow-hidden">
        <div className="flex gap-16 animate-[ticker_30s_linear_infinite] whitespace-nowrap w-max">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="flex gap-16 items-center text-xs font-bold tracking-[0.15em] uppercase">
              <span>Free Shipping on Orders $25+</span><span className="text-pink-500">✦</span>
              <span>New Arrivals Every Day</span><span className="text-pink-500">✦</span>
              <span>All Products on Amazon</span><span className="text-pink-500">✦</span>
            </div>
          ))}
        </div>
      </div>

      {/* TRENDING PRODUCTS */}
      <section className="max-w-7xl mx-auto px-6 md:px-12 w-full">
        <div className="flex justify-between items-end mb-12 border-b border-zinc-200 pb-4">
          <h2 className="font-playfair text-3xl md:text-4xl font-bold text-zinc-900">Today's Top Picks</h2>
          <Link href="/shop" className="text-xs font-bold tracking-widest uppercase text-pink-500 hover:text-pink-600 border-b border-pink-500 pb-1">
            View All →
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {featuredProducts.map((p, idx) => (
            <div key={p.id} className="group flex flex-col bg-white rounded-2xl overflow-hidden shadow-[0_4px_24px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_40px_rgba(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1 border border-zinc-100">
              <div className="relative aspect-[3/4] overflow-hidden bg-zinc-100">
                <Image src={p.imageUrl} alt={p.title} fill className="object-cover transition-transform duration-500 group-hover:scale-105" unoptimized={p.imageUrl.includes('pollinations') || p.imageUrl.includes('loremflickr') || p.imageUrl.includes('amazon')} />
                {idx === 0 && <span className="absolute top-3 left-3 bg-zinc-950 text-white text-[10px] font-bold tracking-widest uppercase px-3 py-1.5 rounded-full z-10">New</span>}
                {idx === 1 && <span className="absolute top-3 left-3 bg-pink-500 text-white text-[10px] font-bold tracking-widest uppercase px-3 py-1.5 rounded-full z-10">Deal</span>}
                <div className="absolute bottom-3 right-3 bg-white/95 backdrop-blur-sm px-2.5 py-1.5 rounded-lg text-[10px] font-bold text-zinc-900 z-10 shadow-sm">
                  Score <span className="text-pink-500">{p.aiScore}</span>
                </div>
              </div>
              <div className="p-5 flex flex-col flex-1">
                <span className="text-[10px] font-bold tracking-[0.1em] uppercase text-pink-500 mb-2">{p.category.name}</span>
                <h3 className="font-playfair text-base font-semibold leading-snug mb-2 line-clamp-2 text-zinc-900">{p.title}</h3>
                <p className="text-xs text-zinc-500 line-clamp-2 mb-4 flex-1">{p.reviewText}</p>
                
                <div className="flex items-center justify-between mt-auto pt-4 border-t border-zinc-50">
                  <span className="font-playfair text-xl font-bold text-zinc-900">{p.price}</span>
                  <a href={p.link} target="_blank" rel="noopener sponsored" className="bg-zinc-950 hover:bg-pink-500 text-white text-[10px] font-bold tracking-wider uppercase px-4 py-2 rounded-full transition-colors">
                    Buy Now
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* BLOG TEASERS */}
      <section className="bg-zinc-50 py-24">
        <div className="max-w-7xl mx-auto px-6 md:px-12 w-full">
          <div className="flex justify-between items-end mb-12 border-b border-zinc-200 pb-4">
            <h2 className="font-playfair text-3xl md:text-4xl font-bold text-zinc-900">Style Blog</h2>
            <Link href="/blog" className="text-xs font-bold tracking-widest uppercase text-pink-500 hover:text-pink-600 border-b border-pink-500 pb-1">
              Read All →
            </Link>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {featuredBlogs.map((b) => (
              <Link href={`/blog/${b.slug}`} key={b.id} className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col sm:flex-row">
                <div className="relative w-full sm:w-2/5 aspect-[4/3] sm:aspect-auto overflow-hidden">
                  <Image src={b.imageUrl} alt={b.title} fill className="object-cover transition-transform duration-500 group-hover:scale-105" unoptimized={b.imageUrl.includes('pollinations') || b.imageUrl.includes('loremflickr')} />
                </div>
                <div className="p-6 sm:p-8 flex flex-col justify-center sm:w-3/5">
                  <span className="text-[10px] font-bold tracking-[0.1em] uppercase text-pink-500 mb-3">Style Guide</span>
                  <h3 className="font-playfair text-xl md:text-2xl font-bold leading-tight mb-3 text-zinc-900 group-hover:text-pink-500 transition-colors">{b.title}</h3>
                  <p className="text-sm text-zinc-500 line-clamp-2">{b.summary}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* NEWSLETTER */}
      <section id="newsletter" className="max-w-4xl mx-auto px-6 md:px-12 text-center my-12">
        <div className="bg-zinc-950 rounded-[2rem] p-12 md:p-20 text-white relative overflow-hidden shadow-2xl">
          <div className="relative z-10">
            <h2 className="font-playfair text-3xl md:text-5xl font-bold mb-4">Get Weekly Style Drops 💌</h2>
            <p className="text-zinc-400 text-sm md:text-base max-w-lg mx-auto mb-10">
              Join 2,000+ women who get our best Amazon fashion finds every Friday — free.
            </p>
            <form className="flex flex-col sm:flex-row max-w-md mx-auto gap-3 sm:gap-0" action="/#newsletter">
              <input 
                type="email" 
                placeholder="Your email address" 
                className="flex-1 bg-white/10 border border-zinc-800 text-white placeholder:text-zinc-500 px-6 py-4 rounded-full sm:rounded-r-none focus:outline-none focus:ring-2 focus:ring-pink-500 text-sm"
                required
              />
              <button type="submit" className="bg-pink-500 hover:bg-pink-600 text-white px-8 py-4 rounded-full sm:rounded-l-none text-xs font-bold tracking-widest uppercase transition-colors">
                Subscribe
              </button>
            </form>
          </div>
        </div>
      </section>

    </div>
  );
}
