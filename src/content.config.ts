import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    published: z.coerce.date(),
    updated: z.coerce.date().optional(),
    draft: z.boolean().default(false),
    description: z.string().default(''),
    category: z.string().default('随笔'),
    tags: z.array(z.string()).default([]),
    pinned: z.boolean().default(false),
  }),
});

export const collections = { posts };
