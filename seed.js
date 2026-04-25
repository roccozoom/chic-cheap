const { PrismaClient } = require('@prisma/client');
const fs = require('fs');

const prisma = new PrismaClient({
  datasourceUrl: process.env.DATABASE_URL || "file:./dev.db"
});

function slugify(text) {
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

async function main() {
  console.log('Migrating data...');

  // 1. Read website_data.json
  let websiteData = {};
  try {
    const rawWebsite = fs.readFileSync('./temp_data/website_data.json', 'utf8');
    websiteData = JSON.parse(rawWebsite);
  } catch (e) {
    console.log('Could not read website_data.json', e);
  }

  // 2. Read blog_archive.json
  let blogArchive = [];
  try {
    const rawArchive = fs.readFileSync('./temp_data/blog_archive.json', 'utf8');
    blogArchive = JSON.parse(rawArchive);
  } catch (e) {
    console.log('Could not read blog_archive.json', e);
  }

  // Categories and Products
  if (websiteData.products) {
    for (const prod of websiteData.products) {
      const catName = prod.category || 'Uncategorized';
      let category = await prisma.category.findUnique({
        where: { name: catName }
      });

      if (!category) {
        category = await prisma.category.create({
          data: {
            name: catName,
            slug: slugify(catName)
          }
        });
      }

      await prisma.product.create({
        data: {
          title: prod.title,
          price: prod.price || 'N/A',
          categoryId: category.id,
          imageUrl: prod.image_url || '',
          link: prod.link || '#',
          reviewText: prod.review_text || '',
          stylingTip: prod.styling_tip || '',
          aiScore: prod.ai_score || 90,
          rating: prod.rating || '4.5',
          reviewCount: prod.review_count || '100+',
          isFeatured: false
        }
      });
    }
    console.log(`Imported ${websiteData.products.length} products.`);
  }

  // Blogs from website_data.json (current featured blog)
  if (websiteData.blog && websiteData.blog.title) {
    await prisma.blogPost.create({
      data: {
        title: websiteData.blog.title,
        slug: websiteData.blog.slug || slugify(websiteData.blog.title),
        metaDescription: websiteData.blog.meta_description || '',
        summary: websiteData.blog.summary || '',
        content: websiteData.blog.content || '',
        imageUrl: websiteData.blog.image_url || 'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?q=80&w=900',
      }
    });
    console.log(`Imported featured blog.`);
  }

  // Archived blogs
  for (const b of blogArchive) {
    const existing = await prisma.blogPost.findUnique({
      where: { slug: b.slug || slugify(b.title) }
    });
    if (!existing && b.title) {
      await prisma.blogPost.create({
        data: {
          title: b.title,
          slug: b.slug || slugify(b.title),
          metaDescription: b.summary || '',
          summary: b.summary || '',
          content: `<p>${b.summary}</p>`, // Archive didn't have full content usually
          imageUrl: 'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?q=80&w=900',
        }
      });
    }
  }
  console.log(`Imported ${blogArchive.length} archived blogs.`);

  console.log('Migration complete!');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
