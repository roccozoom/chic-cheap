import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { PrismaClient } from "@prisma/client";

import { Metadata } from "next";

const prisma = new PrismaClient({
  datasourceUrl: process.env.DATABASE_URL || "file:./dev.db"
});

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const product = await prisma.product.findUnique({ where: { id: params.id } });
  if (!product) return { title: "Product Not Found | Chic-Cheap" };
  
  return {
    title: `${product.title} | Chic-Cheap Picks`,
    description: product.reviewText || "Curated fashion deals on Amazon.",
    openGraph: {
      title: product.title,
      description: product.reviewText || "",
      images: [product.imageUrl],
    }
  };
}

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await prisma.product.findUnique({
    where: { id: params.id },
    include: { category: true }
  });

  if (!product) notFound();

  return (
    <div className="max-w-6xl mx-auto px-6 md:px-12 py-16">
      <div className="mb-8">
        <Link href="/shop" className="text-xs font-bold tracking-widest uppercase text-zinc-500 hover:text-pink-500 transition-colors">
          ← Back to Shop
        </Link>
      </div>
      
      <div className="grid md:grid-cols-2 gap-12 lg:gap-20 items-start">
        {/* Left: Image */}
        <div className="relative aspect-[3/4] md:aspect-auto md:h-[600px] rounded-3xl overflow-hidden bg-zinc-100 shadow-2xl">
          <Image src={product.imageUrl} alt={product.title} fill className="object-cover" priority />
        </div>

        {/* Right: Details */}
        <div className="flex flex-col pt-4">
          <span className="text-xs font-bold tracking-[0.15em] uppercase text-pink-500 mb-4">{product.category.name}</span>
          <h1 className="font-playfair text-3xl md:text-5xl font-bold text-zinc-900 leading-[1.15] mb-6">
            {product.title}
          </h1>
          
          <div className="flex items-center gap-4 mb-8 pb-8 border-b border-zinc-100">
            <span className="font-playfair text-3xl font-bold text-zinc-900">{product.price}</span>
            <div className="h-8 w-px bg-zinc-200"></div>
            <div className="flex items-center gap-1">
              <span className="text-amber-400">★</span>
              <span className="text-sm font-bold">{product.rating}</span>
              <span className="text-xs text-zinc-500">({product.reviewCount} reviews)</span>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-900 mb-3">Editor's Note</h3>
            <p className="text-zinc-600 leading-relaxed text-sm md:text-base">
              {product.reviewText}
            </p>
          </div>

          {product.stylingTip && (
            <div className="bg-pink-50 border-l-4 border-pink-500 p-5 rounded-r-2xl mb-10">
              <h3 className="text-xs font-bold uppercase tracking-widest text-pink-600 mb-2">Styling Tip</h3>
              <p className="text-sm text-pink-900/80 italic">{product.stylingTip}</p>
            </div>
          )}

          <a 
            href={product.link} 
            target="_blank" 
            rel="noopener sponsored" 
            className="w-full bg-zinc-950 hover:bg-pink-500 text-white text-sm font-bold tracking-[0.15em] uppercase py-5 rounded-full transition-all duration-300 text-center shadow-xl hover:shadow-pink-500/20 hover:-translate-y-1"
          >
            Buy on Amazon
          </a>
        </div>
      </div>
    </div>
  );
}
