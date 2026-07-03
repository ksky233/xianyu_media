# 初始化 Vite React 项目

## 初始化目标

本次初始化的目标，是在 `xianyu_frontend` 这个空目录中创建一个基于 Vite 的 React 前端工程，并且选择 TypeScript 模板作为后续迁移的基础。当前项目使用 `pnpm create vite . --template react-ts` 创建，模板版本对应当前生成的 `Vite v8.1.3` 工程结构，代码检查工具选择 `Oxlint`。

在本项目中，前端目录只负责保存前端工程文件，后续统一的 Git 版本控制会放在 `xianyu_media` 根目录中处理，因此 Vite 初始化阶段只生成前端文件和 `.gitignore`，项目根目录的 Git 初始化可以之后单独执行。

## 初始化命令

进入前端目录：

```powershell
cd E:\AI_Projects\MyProjects\xianyu_media\xianyu_frontend
```

使用 Vite 脚手架创建 React TypeScript 项目：

```powershell
pnpm create vite . --template react-ts
```

这条命令可以拆开理解：`pnpm create vite` 表示使用 Vite 脚手架创建项目，`.` 表示把项目创建到当前目录，`--template react-ts` 表示选择 React + TypeScript 模板。执行过程中出现 linter 选择时，本项目选择 `Oxlint`，它是一个速度很快、配置较轻的新一代代码检查工具，适合在学习项目中体验现代前端工具链。

脚手架生成文件之后，安装依赖：

```powershell
pnpm install
```

依赖安装完成后，启动开发服务器：

```powershell
pnpm dev
```

当终端显示下面这样的内容时，说明 Vite 开发服务器已经成功启动：

```text
VITE v8.1.3  ready in 240 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

此时在浏览器中打开 `http://localhost:5173/`，能够看到 Vite 默认页面，就代表项目初始化阶段已经完成。

## 当前生成的目录结构

当前 `xianyu_frontend` 目录中的主要文件如下：

```text
xianyu_frontend/
  node_modules/
  public/
  src/
  .gitignore
  .oxlintrc.json
  index.html
  package.json
  pnpm-lock.yaml
  README.md
  tsconfig.app.json
  tsconfig.json
  tsconfig.node.json
  vite.config.ts
```

当前 `src` 目录中的主要文件如下：

```text
src/
  App.css
  App.tsx
  index.css
  main.tsx
  assets/
    hero.png
    react.svg
    vite.svg
```

`node_modules` 是依赖安装目录，`pnpm-lock.yaml` 是 pnpm 生成的依赖锁文件，`public` 用来放置可以直接被浏览器访问的静态资源，`src` 用来放置 React 应用源码，`.oxlintrc.json` 是 Oxlint 配置文件，`README.md` 是模板生成的说明文档，三个 `tsconfig` 文件共同组成 TypeScript 配置体系。

## package.json 与项目命令

当前 `package.json` 中的 scripts 是：

```json
{
  "dev": "vite",
  "build": "tsc -b && vite build",
  "lint": "oxlint",
  "preview": "vite preview"
}
```

执行 `pnpm dev` 时，pnpm 会读取 `dev` 脚本并运行 `vite` 来启动开发服务器；执行 `pnpm build` 时，会先通过 `tsc -b` 执行 TypeScript 构建检查，再通过 `vite build` 生成生产环境产物；执行 `pnpm lint` 时，会运行 Oxlint 检查代码；执行 `pnpm preview` 时，会在本地预览已经构建好的生产产物。

当前项目初始化后的核心依赖是 `react` 和 `react-dom`，开发依赖包含 `vite`、`typescript`、`@vitejs/plugin-react`、`oxlint`、`@types/react`、`@types/react-dom` 和 `@types/node`。这说明当前工程还处于干净的 React TypeScript 模板阶段，尚未引入 React Router、TanStack Query、Zustand、Zod 或 Tailwind CSS。

## index.html：HTML 加载入口

当前 `index.html` 的内容如下：

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>xianyu_frontend</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

这个文件提供浏览器加载页面时所需的基础 HTML 结构。`<div id="root"></div>` 是 React 应用挂载的位置，`<script type="module" src="/src/main.tsx"></script>` 负责加载前端应用的 TypeScript 入口文件。浏览器先读取这个 HTML 文件，然后通过 Vite 的模块加载能力进入 `src/main.tsx`，React 应用也从这里开始接管页面内容。

## main.tsx：React 应用启动入口

当前 `src/main.tsx` 的内容如下：

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

`main.tsx` 是 React 应用的启动文件。它导入 React 的 `StrictMode`、React DOM 的 `createRoot`、全局样式 `index.css` 以及根组件 `App`，然后通过 `document.getElementById('root')!` 获取 `index.html` 中的根节点，并使用 `createRoot(...).render(...)` 将 React 组件树渲染到页面中。

`StrictMode` 是 React 提供的开发辅助组件，它会在开发环境中帮助发现潜在问题，使组件写法更符合 React 的推荐实践。由于 `index.css` 在这里被导入，所以它会作为全局样式影响整个应用。

## App.tsx：应用根组件

当前 `src/App.tsx` 是模板生成的应用根组件，它导入了 `useState`、三个资源文件和 `App.css`：

```tsx
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
```

这个组件中包含一个 `count` 状态，并通过按钮点击事件更新计数：

```tsx
const [count, setCount] = useState(0)
```

页面主体展示了 Vite 默认欢迎区域、React 和 Vite 的 Logo、示例图片、文档链接和社交链接。这个文件的作用是展示 React 组件、状态、事件、CSS 文件和静态资源导入方式如何协同工作。后续迁移闲鱼媒体后台时，`App.tsx` 可以逐步替换为本项目自己的应用外壳，例如承接路由入口、全局 Provider、布局组件和页面容器。

## App.css：根组件样式

当前 `src/App.css` 是 `App.tsx` 专用的样式文件，它通过 `import './App.css'` 被根组件导入。模板页面中的 `.hero`、`.base`、`.framework`、`.vite`、`.counter`、`#center`、`#next-steps` 等样式主要来自这个文件。

这个文件体现了组件级样式的一种组织方式：组件文件负责结构和交互，CSS 文件负责该组件的展示细节。后续迁移到业务项目时，可以选择保留这种普通 CSS 写法，也可以逐步切换到 Tailwind CSS 或组件库样式。

## index.css：全局样式入口

当前 `src/index.css` 是全局样式文件，它由 `main.tsx` 直接导入，因此会影响整个 React 应用。当前模板在这里定义了全局 CSS 变量、亮色和暗色主题颜色、根节点布局、基础字体、标题、段落、代码块和计数按钮的基础样式。

例如当前文件中定义了 `:root` 下的颜色变量：

```css
:root {
  --text: #6b6375;
  --text-h: #08060d;
  --bg: #fff;
  --border: #e5e4e7;
}
```

同时也定义了 `#root` 的页面容器样式：

```css
#root {
  width: 1126px;
  max-width: 100%;
  margin: 0 auto;
  text-align: center;
  border-inline: 1px solid var(--border);
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}
```

这说明当前模板页面并不是一个空白 React 应用，而是一个带有完整默认演示样式的 Vite 欢迎页。后续整理模板时，可以先清理这些演示样式，再建立本项目自己的全局样式入口。

## vite.config.ts：Vite 配置入口

当前 `vite.config.ts` 的内容如下：

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})
```

这个文件负责配置 Vite 的开发服务器和构建行为。当前配置只启用了 React 插件，说明项目仍处于初始化模板状态。后续项目开发中，这个文件可以继续扩展，例如配置 `@` 路径别名、设置开发服务器端口、配置后端 API 代理、接入 Tailwind 的 Vite 插件等。

## TypeScript 配置文件

当前模板生成了三个 TypeScript 配置文件：`tsconfig.json`、`tsconfig.app.json` 和 `tsconfig.node.json`。其中 `tsconfig.json` 是配置入口，它通过 references 指向应用侧配置和 Node/Vite 配置；`tsconfig.app.json` 负责 `src` 目录中的前端代码类型检查；`tsconfig.node.json` 负责 `vite.config.ts` 这类运行在 Node 环境中的配置文件类型检查。

这种拆分方式可以让浏览器端代码和工具配置代码使用不同的类型环境，避免把 DOM、Node、构建配置混在同一个 TypeScript 上下文里。

## 模板启动链路

当前 Vite React 模板的启动链路可以概括为：

```text
index.html
  -> src/main.tsx
    -> src/App.tsx
      -> src/App.css
      -> src/assets/*
```

浏览器首先加载 `index.html`，这个 HTML 文件提供 `root` 节点并加载 `src/main.tsx`；`main.tsx` 创建 React 根节点、导入全局样式，并渲染 `App.tsx`；`App.tsx` 作为应用根组件组织默认页面内容，同时导入组件样式 `App.css` 和图片资源。理解这条链路之后，后续接入路由、状态管理、请求缓存、表单校验和 UI 组件库，本质上都是在这条启动链路上逐层扩展应用能力。

## 本阶段完成标准

当以下几项都完成时，可以认为 Vite 初始化阶段结束：

```text
已在 xianyu_frontend 中生成 Vite React TypeScript 模板
已选择 Oxlint 作为代码检查工具
已执行 pnpm install 安装依赖
已执行 pnpm dev 启动开发服务器
浏览器可以访问 http://localhost:5173/
已理解 index.html、main.tsx、App.tsx、App.css、index.css、vite.config.ts、package.json 和 TypeScript 配置文件的基本职责
```

初始化阶段结束后，下一步可以开始整理模板默认代码，建立本项目自己的目录结构，再逐步引入 React Router、TanStack Query、Zustand、Zod、Tailwind CSS 等实际业务所需的前端能力。
