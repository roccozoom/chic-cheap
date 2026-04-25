import { NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient({
  datasourceUrl: process.env.DATABASE_URL || "file:./dev.db"
});

function slugify(text: string) {
  if (!text) return 'item-' + Math.random().toString(36).substring(7);
  return text
    .toString()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-')
    .replace(/^-+/, '')
    .replace(/-+$/, '');
}

export async function POST(req: Request) {
  try {
    const authHeader = req.headers.get("authorization");
    if (authHeader !== `Bearer ${process.env.BOT_SECRET || 'chic61'}`) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const data = await req.json();
    const { action } = data;

    if (action === "add_product") {
      const { title, price, categoryName, imageUrl, link, reviewText, stylingTip, aiScore, rating, reviewCount } = data.payload;

      if (!title || !categoryName || !link) {
        return NextResponse.json({ error: "Missing required product fields" }, { status: 400 });
      }

      // Find or create category
      let category = await prisma.category.findUnique({ where: { name: categoryName } });
      if (!category) {
        category = await prisma.category.create({
          data: { name: categoryName, slug: slugify(categoryName) }
        });
      }

      const product = await prisma.product.create({
        data: {
          title,
          price: price || 'N/A',
          categoryId: category.id,
          imageUrl: imageUrl || '',
          link,
          reviewText: reviewText || '',
          stylingTip: stylingTip || '',
          aiScore: aiScore || 90,
          rating: rating || '4.5',
          reviewCount: reviewCount || '100+',
        }
      });

      return NextResponse.json({ success: true, product });
    }

    if (action === "add_blog") {
      const { title, metaDescription, summary, content, imageUrl } = data.payload;

      if (!title || !content) {
        return NextResponse.json({ error: "Missing required blog fields" }, { status: 400 });
      }

      const slug = slugify(title);
      
      const blog = await prisma.blogPost.upsert({
        where: { slug },
        update: {
          metaDescription: metaDescription || '',
          summary: summary || '',
          content,
          imageUrl: imageUrl || '',
          createdAt: new Date() // refresh date to bump to top
        },
        create: {
          title,
          slug,
          metaDescription: metaDescription || '',
          summary: summary || '',
          content,
          imageUrl: imageUrl || '',
        }
      });

      return NextResponse.json({ success: true, blog });
    }

    return NextResponse.json({ error: "Unknown action" }, { status: 400 });

  } catch (error: any) {
    console.error("Bot API Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
