# Mortal Blog

个人博客，基于 **Astro** 构建，Fuwari 风格主题（顶部 Banner + 侧栏名片 + 卡片式文章列表 + 明暗双主题）。

## 本地开发

### 方式一：双击（推荐，不需要装 Node.js）

| 双击这个 | 作用 |
|---|---|
| **`启动博客.bat`** | 启动本地预览 http://localhost:4321，改文章自动刷新。关窗口即停止 |
| **`构建博客.bat`** | 生成静态站点到 `dist/`，完成后可回车本地预览 |
| **`打开终端.bat`** | 打开一个已配好环境的终端，可自己敲命令 |

> 脚本会先把 Node.js 目录加进 PATH，所以即使系统 PATH 出问题也能跑。
> 本机 Node.js 装在 **`D:\node-js`**；如果以后换了安装位置，改三个 bat 里的这一行：
> ```bat
> set "NODE_DIR=D:\node-js"
> ```

### 方式二：手动敲命令

前提是系统 PATH 里能找到 `node` / `npm`。在终端里先切到项目目录，再执行：

```bash
cd /d D:\mortal-blog   # PowerShell 用 cd D:\mortal-blog（不带 /d）
npm install            # 首次安装依赖
npm run dev            # 启动开发服务器  http://localhost:4321
npm run build          # 构建到 dist/
npm run preview        # 预览构建产物
```

### ⚠️ 改完 bat 要重新编码

`.bat` 含中文时必须是 **GBK 编码 + CRLF 行尾**，否则 cmd 会解析错乱（表现为行首字符被吞、报「不是内部或外部命令」）。
如果用编辑器改了任何 `.bat`，跑一次这个重新编码：

```bash
python _to_gbk.py
```

## 环境备忘（本机，2026-10-15 配置）

| 项 | 值 |
|---|---|
| Node.js | **v24.22.0**，装在 `D:\node-js`，已加入用户 PATH |
| npm | 11.19.1（随 Node.js 自带） |
| PowerShell 执行策略 | CurrentUser = `RemoteSigned` |

配置过程中踩过的两个坑，换机器时要注意：

1. **Node.js 的 MSI 安装包不会自动把安装目录加进 PATH**——它只加了全局包目录
   `%APPDATA%\npm`。装完在终端敲 `npm` 依然报「不是内部或外部命令」。
   解决：手动把 `D:\node-js` 写入用户环境变量 Path。
2. **PowerShell 默认执行策略是 `Restricted`**，会把 `npm.ps1` 当未签名脚本拦掉，
   报「无法加载文件 npm.ps1，因为在此系统上禁止运行脚本」。
   解决：`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`。

> 两项改完都必须**关掉终端重新开**才生效（已开的窗口不会刷新环境）。

## 目录结构

```
mortal-blog/
├── astro.config.mjs            # 站点配置（site / base / 语法高亮）
├── public/                     # 静态资源（banner / avatar / favicon / 图片）
├── src/
│   ├── consts.ts               # 站点信息、导航、友链 —— 改这里最快
│   ├── content.config.ts       # 文章 frontmatter 校验规则
│   ├── content/posts/*.md      # 文章（Markdown）
│   ├── components/             # Navbar / Footer / Sidebar / PostCard / PostList
│   ├── layouts/BaseLayout.astro
│   ├── pages/
│   │   ├── index.astro         # 首页（第 1 页）
│   │   ├── page/[page].astro   # 分页
│   │   ├── posts/[...id].astro # 文章详情
│   │   ├── archive.astro       # 归档（支持分类/标签筛选）
│   │   ├── about.astro         # 关于
│   │   ├── friends.astro       # 友链
│   │   ├── rss.xml.js          # RSS
│   │   └── 404.astro
│   ├── styles/global.css       # 全部样式与主题变量
│   └── utils.ts                # 日期 / 统计 / 字数工具
└── .github/workflows/deploy.yml # 自动部署到 GitHub Pages
```

## 写一篇新文章

在 `src/content/posts/` 下新建 `.md` 文件，开头写 frontmatter：

```markdown
---
title: 文章标题
published: 2026-10-15
description: 一句话摘要，会显示在列表里
category: 随笔
tags: [标签1, 标签2]
pinned: false
---

正文……
```

字段说明：

| 字段 | 必填 | 说明 |
|---|---|---|
| `title` | ✅ | 标题 |
| `published` | ✅ | 发布日期，决定排序 |
| `description` | — | 列表页摘要 |
| `category` | — | 分类，默认「随笔」 |
| `tags` | — | 标签数组 |
| `pinned` | — | 置顶（显示「置顶」徽章） |
| `draft` | — | `true` 则该文章不发布 |
| `updated` | — | 更新日期 |

## 改站点信息

编辑 `src/consts.ts`：

```ts
export const SITE = { title: 'Mortal', subtitle: '...', url: 'https://...' };
export const PROFILE = { name: 'Mortal', bio: '...', avatar: '/avatar.png' };
export const NAV_ITEMS = [...];
export const FRIEND_LINKS = [...];
```

## 换个主题色

编辑 `src/styles/global.css` 顶部的 `--hue`：

```css
:root { --hue: 215; }   /* 215 = 蓝，160 = 青绿，280 = 紫，350 = 红 */
```

## 替换 Banner / 头像

- `public/banner.png`（建议 1600×450）
- `public/avatar.png`（正方形）
- 也可以重新生成：`python _gen_assets.py`

## 部署到 GitHub Pages

**方式一：双击脚本（推荐）**

1. 在 GitHub 网页新建仓库：选 **Public**、**不要**勾 README / .gitignore，
   建好后复制页面上 `.git` 结尾的地址；
2. 双击 **`部署.bat`**，粘贴地址回车。首次运行会问你的名字和 GitHub 邮箱；
   推送时浏览器会弹登录窗口，登录即可（**不需要自己搞 token**）；
3. 仓库 **Settings → Pages → Build and deployment → Source** 选 **GitHub Actions**；
4. 打开仓库的 Actions 页面等绿勾（约 1 分钟），地址就是
   `https://用户名.github.io/仓库名`。

**方式二：自己敲命令**

```bash
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/用户名/仓库名.git
git push -u origin main
```

之后的步骤同方式一的 3、4。

**方式三：本地构建后手动上传**

```bash
npm run build      # 产物在 dist/
```

把 `dist/` 内容传到 `gh-pages` 分支即可。

### ⚠️ 部署前必改

如果仓库**不是** `用户名.github.io`，而是 `用户名/repo` 这种形式，必须改 `astro.config.mjs`：

```js
export default defineConfig({
  site: 'https://你的用户名.github.io',
  base: '/你的仓库名',        // ← 仓库名形式才需要；用户名.github.io 则保持 '/'
});
```

同时把 `src/consts.ts` 里的 `SITE.url` 改成真实地址。

## 许可

文章内容版权归作者所有，主题代码可自由参考。
