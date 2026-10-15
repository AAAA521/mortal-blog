import type { CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'posts'>;

/**
 * 站点部署根路径（即 Astro 的 base）。
 * 部署在 https://<用户名>.github.io/mortal-blog/ 时为 '/mortal-blog'；
 * 部署在根域名（<用户名>.github.io 仓库）时为 ''。
 */
export const BASE = import.meta.env.BASE_URL.replace(/\/+$/, '');

/**
 * 给站内绝对路径补上 base 前缀：
 *   withBase('/about/')  -> '/mortal-blog/about/'
 * 外链、协议相对地址、锚点、相对路径都原样返回。
 */
export function withBase(path: string): string {
  if (!path.startsWith('/') || path.startsWith('//')) return path;
  return `${BASE}${path}`;
}

/** 日期格式化为 2026-10-15 */
export function formatDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** 文章按发布时间倒序 */
export function sortPosts(posts: Post[]): Post[] {
  return [...posts].sort((a, b) => b.data.published.valueOf() - a.data.published.valueOf());
}

/** 统计分类及篇数（按篇数降序、名称升序） */
export function countCategories(posts: Post[]): { name: string; count: number }[] {
  const map = new Map<string, number>();
  for (const p of posts) {
    const k = p.data.category || '随笔';
    map.set(k, (map.get(k) ?? 0) + 1);
  }
  return [...map.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'zh-CN'));
}

/** 统计标签及篇数 */
export function countTags(posts: Post[]): { name: string; count: number }[] {
  const map = new Map<string, number>();
  for (const p of posts) {
    for (const t of p.data.tags ?? []) {
      map.set(t, (map.get(t) ?? 0) + 1);
    }
  }
  return [...map.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'zh-CN'));
}

/** 估算阅读时长（分钟） */
export function readingTime(body: string): number {
  const chars = body.replace(/\s+/g, '').length;
  return Math.max(1, Math.round(chars / 400));
}

/** 估算正文字数 */
export function wordCount(body: string): number {
  return body.replace(/\s+/g, '').length;
}
