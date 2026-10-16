// ── 站点基本信息 ──────────────────────────────────────────
export const SITE = {
  title: 'Mortal',
  subtitle: 'Little Steps of Growth',
  description: '网络安全学习者 / CTF 选手的学习记录',
  author: 'Mortal',
  lang: 'zh-CN',
  // 部署到 GitHub Pages 前改成你的真实地址（含仓库名）
  url: 'https://AAAA521.github.io/mortal-blog',
};

export const PROFILE = {
  name: 'Mortal',
  bio: 'web 安全学习中~，偶尔打打 CTF，欢迎各位师傅参观~',
  avatar: '/avatar.png',
  banner: '/banner.png',
};

// ── 每页文章数 ────────────────────────────────────────────
export const PAGE_SIZE = 10;

// ── 导航 ─────────────────────────────────────────────────
export const NAV_ITEMS = [
  { name: '友链', url: '/friends/' },
  { name: '主页', url: '/' },
  { name: '归档', url: '/archive/' },
  { name: '关于', url: '/about/' },
];

export const SOCIAL_LINKS = [
  { name: 'GitHub', url: 'https://github.com/AAAA521', icon: 'github', external: true },
  { name: 'RSS', url: '/rss.xml', icon: 'rss', external: false },
];

// ── 友链 ─────────────────────────────────────────────────
export const FRIEND_LINKS = [
  {
    name: 'yuanmuyan',
    url: 'https://yuanmuyan.github.io/',
    desc: 'web 手一枚，博客模板参考来源',
    // 原用 github.com/identicons/…（GitHub 早已下线该端点，取不到图）。
    // 换成对方友链页「我？」处公布的官方 icon
    avatar: 'https://yuanmuyan.github.io/favicon/avatar-180.png',
  },
  {
    name: 'Map1e-Suk1',
    url: 'https://map1e-suk1.github.io/',
    // 对方友链页公布的官方描述，直接用原文
    desc: 'Roam free, for life is wide.',
    avatar: 'https://map1e-suk1.github.io/avatar.webp',
  },
];
