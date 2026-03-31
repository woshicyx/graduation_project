# 智能电影推荐平台 - 前端

Next.js 14 (App Router) + TypeScript + Tailwind CSS + Shadcn/UI + Framer Motion。

## 目录结构

```
frontend/
├── app/                 # App Router 页面与布局
├── components/          # 通用业务组件
├── components/ui/       # Shadcn/UI 组件 (button, input, card, dialog, sheet, scroll-area, carousel)
├── lib/                 # 工具函数 (含 cn)
├── hooks/               # 自定义 React Hooks
├── types/               # 全局类型定义
└── public/
```

## 本地运行

确保已安装 Node.js 18+，在项目根目录执行：

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 [http://localhost:3000](http://localhost:3000)。

## 脚本

- `npm run dev` - 开发服务器
- `npm run build` - 生产构建
- `npm run start` - 启动生产服务
- `npm run lint` - ESLint 检查

## 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **组件**: Shadcn/UI (new-york 风格)
- **动画**: Framer Motion
- **图标**: Lucide React
