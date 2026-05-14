import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
      },
      {
        userAgent: ['Amazonbot', 'Applebot-Extended', 'Bytespider', 'CCBot', 'ClaudeBot', 'CloudflareBrowserRenderingCrawler', 'Google-Extended', 'GPTBot', 'meta-externalagent', 'ChatGPT-User', 'PerplexityBot', 'anthropic-ai', 'FacebookBot'],
        disallow: '/',
      },
    ],
    sitemap: 'https://chic-cheap.com/sitemap.xml',
  }
}
