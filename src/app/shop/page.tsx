import Image from "next/image";
import Link from "next/link";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient({
  datasourceUrl: process.env.DATABASE_URL || "file:./dev.db"
});

export default async function ShopPage({ searchParams }: { searchParams: Promise<{ cat?: string }> }) {
  const params = await searchParams;
  const categorySlug = params.cat || null;

  const categories = await prisma.category.findMany();
  
  const products = await prisma.product.findMany({
    where: categorySlug ? { category: { slug: categorySlug } } : undefined,
    include: { category: true },
    orderBy: { createdAt: "desc" }
  });

  return (
    <div className="max-w-7xl mx-auto px-6 md:px-12 py-16">
      <div className="mb-12">
        <h1 className="font-playfair text-4xl md:text-5xl font-bold text-zinc-900 mb-6">Shop the Curated Collection</h1>
        
        {/* Filter Tabs */}
        <div className="flex flex-wrap gap-3">
          <Link 
            href="/shop" 
            className={`px-6 py-2.5 rounded-full text-xs font-bold tracking-widest uppercase transition-all border ${!categorySlug ? 'bg-zinc-950 text-white border-zinc-950' : 'bg-transparent text-zinc-500 border-zinc-200 hover:border-zinc-400'}`}
          >
            All
          </Link>
          {categories.map(c => (
            <Link 
              key={c.id}
              href={`/shop?cat=${c.slug}`} 
              className={`px-6 py-2.5 rounded-full text-xs font-bold tracking-widest uppercase transition-all border ${categorySlug === c.slug ? 'bg-zinc-950 text-white border-zinc-950' : 'bg-transparent text-zinc-500 border-zinc-200 hover:border-zinc-400'}`}
            >
              {c.name}
            </Link>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {products.map((p, idx) => (
          <div key={p.id} className="group flex flex-col bg-white rounded-2xl overflow-hidden shadow-[0_4px_24px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_40px_rgba(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1 border border-zinc-100">
            <Link href={`/product/${p.id}`} className="relative aspect-[3/4] overflow-hidden bg-zinc-100 block">
              <Image src={p.imageUrl} alt={p.title} fill className="object-cover transition-transform duration-500 group-hover:scale-105" />
              <div className="absolute bottom-3 right-3 bg-white/95 backdrop-blur-sm px-2.5 py-1.5 rounded-lg text-[10px] font-bold text-zinc-900 z-10 shadow-sm">
                Score <span className="text-pink-500">{p.aiScore}</span>
              </div>
            </Link>
            <div className="p-5 flex flex-col flex-1">
              <span className="text-[10px] font-bold tracking-[0.1em] uppercase text-pink-500 mb-2">{p.category.name}</span>
              <h3 className="font-playfair text-base font-semibold leading-snug mb-2 line-clamp-2 text-zinc-900">
                <Link href={`/product/${p.id}`} className="hover:text-pink-500 transition-colors">{p.title}</Link>
              </h3>
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

      {products.length === 0 && (
        <div className="py-24 text-center">
          <p className="text-zinc-500">No products found for this category.</p>
        </div>
      )}
    </div>
  );
}
