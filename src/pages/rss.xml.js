import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITE } from '../consts';
import { sortPosts } from '../utils';

export async function GET(context) {
  const posts = sortPosts(await getCollection('posts', ({ data }) => !data.draft));
  return rss({
    title: `${SITE.title} - ${SITE.subtitle}`,
    description: SITE.description,
    site: context.site,
    items: posts.map((p) => ({
      title: p.data.title,
      pubDate: p.data.published,
      description: p.data.description ?? '',
      categories: [p.data.category, ...(p.data.tags ?? [])],
      link: `/posts/${p.id}/`,
    })),
    customData: '<language>zh-CN</language>',
  });
}
