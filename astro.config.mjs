import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { unified } from '@astrojs/markdown-remark';

// ── 部署地址（换仓库时只改这两行）──────────────────────────
// 仓库名是 <用户名>.github.io 时，BASE 写 '/'；
// 仓库名是别的（例如 mortal-blog）时，BASE 必须是 '/仓库名'。
const SITE = 'https://AAAA521.github.io';
const BASE = '/mortal-blog';

/**
 * 给 Markdown 正文里的站内绝对链接 / 图片补上 base 前缀。
 * Astro 只会改写它自己生成的资源路径，.md 里手写的 `/xxx` 不会自动加前缀。
 *   ![图](/a.png)      -> /mortal-blog/a.png
 *   [文](/posts/b/)    -> /mortal-blog/posts/b/
 */
function rehypeBasePath() {
  const isInternal = (v) => typeof v === 'string' && v.startsWith('/') && !v.startsWith('//');
  const walk = (node) => {
    if (node && node.type === 'element') {
      const p = node.properties || {};
      if (node.tagName === 'a' && isInternal(p.href)) p.href = BASE + p.href;
      if (node.tagName === 'img' && isInternal(p.src)) p.src = BASE + p.src;
    }
    if (node && Array.isArray(node.children)) node.children.forEach(walk);
  };
  return (tree) => walk(tree);
}

export default defineConfig({
  site: SITE,
  base: BASE,
  integrations: [sitemap()],
  markdown: {
    processor: unified({ rehypePlugins: [rehypeBasePath] }),
    shikiConfig: {
      theme: 'github-dark',
      wrap: true,
    },
  },
});
