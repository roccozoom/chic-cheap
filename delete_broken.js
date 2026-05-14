const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient();

async function main() {
  const titlesToDelete = [
    "Women's Boho Chic Maxi Dress",
    "Women's Gold Plated Bar Necklace",
    "Women's Oversized Blazer"
  ];
  
  const result = await p.product.deleteMany({
    where: {
      title: {
        in: titlesToDelete
      }
    }
  });
  
  console.log(`Silinen urun sayisi: ${result.count}`);
}

main()
  .catch(e => console.error(e))
  .finally(async () => {
    await p.$disconnect();
  });
