import Image from "next/image";
import Link from "next/link";
import { PrismaClient } from "@prisma/client";

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient({
  datasourceUrl: process.env.DATABASE_URL || "file:./dev.db"
});

export default async function BlogPage() {
  const blogs = await prisma.blogPost.findMany({
    orderBy: { createdAt: "desc" }
  });

  return (
    <div className="max-w-7xl mx-auto px-6 md:px-12 py-16">
      <div className="mb-16">
        <h1 className="font-playfair text-4xl md:text-5xl font-bold text-zinc-900 mb-4">Style Blog</h1>
        <p className="text-zinc-500">Discover the latest fashion trends, styling tips, and curated Amazon finds.</p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-10">
        {blogs.map((b, idx) => (
          <Link href={`/blog/${b.slug}`} key={b.id} className="group flex flex-col bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-zinc-100">
              <div className="relative w-full aspect-[4/3] overflow-hidden">
                <Image src={b.imageUrl} alt={b.title} fill className="object-cover transition-transform duration-500 group-hover:scale-105" unoptimized={b.imageUrl.includes('pollinations') || b.imageUrl.includes('loremflickr')} />
              </div>
            <div className="p-8 flex flex-col flex-1">
              <span className="text-[10px] font-bold tracking-[0.1em] uppercase text-pink-500 mb-3">Style Guide</span>
              <h2 className="font-playfair text-xl font-bold leading-snug mb-4 text-zinc-900 group-hover:text-pink-500 transition-colors">
                {b.title}
              </h2>
              <p className="text-sm text-zinc-500 line-clamp-3 mb-6 flex-1 leading-relaxed">
                {b.summary}
              </p>
              <div className="mt-auto text-xs font-bold tracking-widest uppercase text-zinc-400 group-hover:text-pink-500 transition-colors">
                Read Article →
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
