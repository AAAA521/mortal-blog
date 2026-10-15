import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 部署到 GitHub Pages 时把 site / base 改成你的仓库地址：
//   site: 'https://<用户名>.github.io',
//   base: '/<仓库名>',
export default defineConfig({
  site: 'https://AAAA521.github.io',
  base: '/mortal-blog',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      theme: 'github-dark',
      wrap: true,
    },
  },
});
