import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITE } from '../consts';
import { sortPosts, BASE } from '../utils';

export async function GET(context) {
  const posts = sortPosts(await getCollection('posts', ({ data }) => !data.draft));
  return rss({
    title: `${SITE.title} - ${SITE.subtitle}`,
    description: SITE.description,
    // 频道地址要带上 base，否则订阅者会跳到站点根目录
    site: new URL(`${BASE}/`, context.site ?? SITE.url).toString(),
    items: posts.map((p) => ({
      title: p.data.title,
      pubDate: p.data.published,
      description: p.data.description ?? '',
      categories: [p.data.category, ...(p.data.tags ?? [])],
      link: `${BASE}/posts/${p.id}/`,
    })),
    customData: '<language>zh-CN</language>',
  });
}
