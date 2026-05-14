import { MetadataRoute } from 'next';
import { PrismaClient } from '@prisma/client';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const prisma = new PrismaClient();
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://chic-cheap.com';

  try {
    // Get all products
    const products = await prisma.product.findMany({
      select: { id: true, updatedAt: true },
    });

    // Get all blog posts
    const blogPosts = await prisma.blogPost.findMany({
      select: { slug: true, updatedAt: true },
    });

    const productUrls = products.map((product) => ({
      url: `${baseUrl}/product/${product.id}`,
      lastModified: product.updatedAt,
      changeFrequency: 'weekly' as const,
      priority: 0.8,
    }));

    const blogUrls = blogPosts.map((post) => ({
      url: `${baseUrl}/blog/${post.slug}`,
      lastModified: post.updatedAt,
      changeFrequency: 'monthly' as const,
      priority: 0.6,
    }));

    const staticUrls = [
      {
        url: `${baseUrl}`,
        lastModified: new Date(),
        changeFrequency: 'daily' as const,
        priority: 1,
      },
      {
        url: `${baseUrl}/shop`,
        lastModified: new Date(),
        changeFrequency: 'daily' as const,
        priority: 0.9,
      },
      {
        url: `${baseUrl}/blog`,
        lastModified: new Date(),
        changeFrequency: 'daily' as const,
        priority: 0.7,
      },
    ];

    return [...staticUrls, ...productUrls, ...blogUrls];
  } catch (error) {
    console.error("Error generating sitemap:", error);
    // Fallback to static URLs if database fails
    return [
      {
        url: `${baseUrl}`,
        lastModified: new Date(),
        changeFrequency: 'daily' as const,
        priority: 1,
      }
    ];
  } finally {
    await prisma.$disconnect();
  }
}
