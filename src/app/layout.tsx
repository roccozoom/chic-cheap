import type { Metadata } from "next";
import { Playfair_Display, Lato } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import Script from "next/script";
import { ShoppingBag, Search, Menu } from "lucide-react";

const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair" });
const lato = Lato({ subsets: ["latin"], weight: ["300", "400", "700"], variable: "--font-lato" });

export const metadata: Metadata = {
  title: "Chic-Cheap | Curated Style. Smart Prices.",
  description: "Discover affordable fashion finds curated daily. Dresses, bags, shoes, and accessories — chic style at budget-friendly prices.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Google AdSense */}
        <Script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4267818870826080"
          crossOrigin="anonymous"
          strategy="afterInteractive"
        />
      </head>
      <body className={`${playfair.variable} ${lato.variable} font-sans antialiased bg-[#FAFAFA] text-zinc-900`}>
        
        {/* Navbar */}
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-zinc-100 h-16 flex items-center justify-between px-6 md:px-12">
          <Link href="/" className="font-playfair text-2xl font-bold tracking-tight">
            chic<span className="text-pink-500">-cheap</span>
          </Link>
          
          <div className="hidden md:flex gap-8 items-center text-sm font-bold uppercase tracking-wider text-zinc-700">
            <Link href="/shop" className="hover:text-pink-500 transition-colors">Shop</Link>
            <Link href="/blog" className="hover:text-pink-500 transition-colors">Style Blog</Link>
            <Link href="/#newsletter" className="hover:text-pink-500 transition-colors">Newsletter</Link>
          </div>

          <div className="flex gap-4 items-center">
            <a href="https://pinterest.com/chiccheapcom" target="_blank" className="hidden md:block text-xs font-bold uppercase tracking-widest text-zinc-500 hover:text-pink-500">Pinterest</a>
            <button className="md:hidden p-2 text-zinc-800"><Menu size={20}/></button>
          </div>
        </nav>

        {/* Main Content */}
        <main className="min-h-screen">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-zinc-950 text-zinc-400 py-16 px-6 md:px-12 mt-24">
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
            <div className="md:col-span-2">
              <Link href="/" className="font-playfair text-3xl font-bold tracking-tight text-white block mb-4">
                chic<span className="text-pink-500">-cheap</span>
              </Link>
              <p className="text-sm max-w-sm leading-relaxed">
                Your daily source for affordable, stylish fashion finds. Curated by style lovers, for style lovers.
              </p>
            </div>
            
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-widest mb-6">Shop</h4>
              <ul className="space-y-3 text-sm">
                <li><Link href="/shop?cat=dresses" className="hover:text-pink-400 transition">Dresses</Link></li>
                <li><Link href="/shop?cat=tops" className="hover:text-pink-400 transition">Tops & Blouses</Link></li>
                <li><Link href="/shop?cat=bags" className="hover:text-pink-400 transition">Bags</Link></li>
                <li><Link href="/shop?cat=shoes" className="hover:text-pink-400 transition">Shoes</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-widest mb-6">Discover</h4>
              <ul className="space-y-3 text-sm">
                <li><Link href="/blog" className="hover:text-pink-400 transition">Style Blog</Link></li>
                <li><Link href="/#newsletter" className="hover:text-pink-400 transition">Newsletter</Link></li>
              </ul>
            </div>
          </div>
          <div className="max-w-7xl mx-auto mt-16 pt-8 border-t border-zinc-800 flex justify-between items-center text-xs">
            <p>© 2026 Chic-Cheap. All rights reserved.</p>
            <p className="text-zinc-500">Affiliate Disclosure: We earn from qualifying purchases.</p>
          </div>
        </footer>

      </body>
    </html>
  );
}
