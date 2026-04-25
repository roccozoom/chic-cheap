#!/bin/bash
echo "🚀 Chic-Cheap Kurulumu Başlıyor..."

# 1. Gerekli bağımlılıkları yükle
echo "📦 Paketler yükleniyor..."
npm install

# 2. Veritabanı şemasını oluştur (Eğer daha önce oluşturulmadıysa)
echo "🗄️ Veritabanı kontrolü..."
npx prisma generate
# npx prisma db push # Bu komutu sildim çünkü halihazırda veritabanını oluşturduk. Sadece generate yeterli.

# 3. Next.js projesini derle (Build)
echo "🏗️ Proje derleniyor (Build)..."
npm run build

# 4. Eğer PM2'de zaten çalışıyorsa durdur ve sil
pm2 delete chiccheap 2>/dev/null

# 5. PM2 ile projeyi başlat (Port 3001)
echo "🟢 Proje PM2 ile başlatılıyor (Port: 3001)..."
PORT=3001 pm2 start npm --name "chiccheap" -- start

# 6. PM2 ayarlarını kaydet ki sunucu yeniden başladığında otomatik çalışsın
pm2 save

echo "✅ Chic-Cheap başarıyla 3001 portunda yayına alındı!"
