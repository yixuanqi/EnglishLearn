# Vercel 前端部署指南

本指南将帮助您将 English Trainer 前端项目部署到 Vercel。

## 一、前期准备

### 1.1 账号准备

- **Vercel 账号**：使用 GitHub 注册
  - 访问：https://vercel.com/（免费额度足够个人使用）
  - 点击 "Sign Up" → 选择 "Continue with GitHub"
  - 完成注册和登录

- **TRAE 国际版客户端**（可选，用于 Solo 模式部署）
  - 下载安装：https://www.trae.ai/
  - 完成注册登录

### 1.2 账号授权准备

- 确保 Vercel 已绑定 GitHub 账号
- 后续一键授权即可

## 二、方式一：使用 TRAE Solo 模式部署（推荐）

### 2.1 进入 TRAE Solo 模式

1. 打开 TRAE IDE
2. 在左上角模式切换处选择 **Solo**
3. 进入 AI 主导的自动化开发模式

### 2.2 Solo 模式部署前端

在 Solo 对话栏输入需求：

```
帮我将 English Trainer 前端项目部署到 Vercel，项目位于 frontend 目录，使用 Vite 构建，需要配置 API 代理和环境变量
```

Solo 会自动：
- 分析项目结构
- 优化配置文件
- 准备部署环境

### 2.3 Solo 模式一键部署到 Vercel

#### 1. 打开部署面板

**方式 1**：点击 TRAE 右上角 **Deploy（部署）** 按钮

**方式 2**：左侧栏火箭图标 → 进入 Deploy 部署面板

#### 2. 首次授权 Vercel

1. 点击 **开始授权 / Authorize Vercel**
2. 自动跳转到浏览器，登录 Vercel 并授权 TRAE 访问
3. 授权成功后自动返回 TRAE

#### 3. 一键执行部署

1. 部署面板选择目标平台：**Vercel**
2. 点击 **Deploy Now / 重新部署**

Solo 自动完成：
- 初始化 Git（如果需要）
- 推送到 GitHub 仓库
- 自动配置构建命令
- 提交 Vercel 构建部署

#### 4. 获取上线地址

部署完成后，面板会直接生成：
- **Vercel 免费域名**：`xxx.vercel.app`
- 可直接复制分享、浏览器访问

### 2.4 更新网页→自动重新部署

1. 在 Solo 模式修改页面内容（自然语言指令即可）
2. 保存后再次点击 **Deploy / 重新部署**
3. Vercel 自动触发新版本构建，1 分钟内更新上线

## 三、方式二：手动部署到 Vercel

### 3.1 推送代码到 GitHub

```bash
# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "准备部署到 Vercel"

# 推送到 GitHub
git branch -M main
git remote add origin https://github.com/your-username/EnglishLearn.git
git push -u origin main
```

### 3.2 在 Vercel 创建新项目

1. 登录 Vercel Dashboard：https://vercel.com/dashboard
2. 点击 **"Add New..."** → **"Project"**
3. 选择 **"Import"** 从 GitHub 导入项目
4. 选择 `EnglishLearn` 仓库

### 3.3 配置项目设置

#### 构建配置

Vercel 会自动检测到 Vite 项目，配置如下：

- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

#### 环境变量

在 **Environment Variables** 部分添加：

```
VITE_API_URL=https://api.englishspeakingtrainer.com
```

### 3.4 部署项目

1. 点击 **"Deploy"** 按钮
2. 等待构建完成（通常 1-2 分钟）
3. 部署成功后会显示访问地址

### 3.5 配置自定义域名（可选）

1. 在项目设置中，点击 **"Domains"**
2. 点击 **"Add"** 添加自定义域名
3. 按照提示配置 DNS 记录

## 四、项目配置说明

### 4.1 Vercel 配置文件

项目已包含 `vercel.json` 配置文件：

```json
{
  "version": 2,
  "name": "english-trainer-frontend",
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/assets/(.*)",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      },
      "dest": "/assets/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install",
  "framework": "vite"
}
```

### 4.2 Vite 构建优化

`frontend/vite.config.js` 已优化：

- 生产环境自动配置 API URL
- 代码分割优化（vendor、ui、utils）
- Terser 压缩
- Source map 控制

### 4.3 环境变量

创建 `frontend/.env.production` 文件：

```
VITE_API_URL=https://api.englishspeakingtrainer.com
```

## 五、常见问题与排查

### 5.1 部署失败

**检查项目根目录**：
- 确保 `frontend/package.json` 存在
- 确保 `frontend/vite.config.js` 配置正确

**检查构建日志**：
- 在 Vercel Dashboard 查看构建日志
- 检查依赖安装是否成功

### 5.2 404 错误

**检查路由配置**：
- `vercel.json` 已配置 SPA 路由重写
- 所有路由都应指向 `index.html`

**检查构建输出**：
- 确保 `frontend/dist` 目录包含 `index.html`

### 5.3 授权失败

- 退出 TRAE 重新登录
- 清理浏览器缓存后再次授权

### 5.4 部署后未更新

- 等待 1-2 分钟 Vercel CDN 刷新
- 清除浏览器缓存
- 检查是否正确推送了最新代码

### 5.5 API 请求失败

**检查环境变量**：
- 确保 `VITE_API_URL` 正确配置
- 检查后端 API 是否可访问

**检查 CORS 配置**：
- 确保后端允许前端域名访问

### 5.6 无 Deploy 按钮

- 确认处于 Solo 模式
- 重启 TRAE 即可恢复

## 六、更新和维护

### 6.1 更新前端代码

```bash
# 修改代码后提交
git add .
git commit -m "更新前端功能"
git push origin main
```

Vercel 会自动检测到推送并触发重新部署。

### 6.2 监控部署状态

- 在 Vercel Dashboard 查看部署历史
- 查看构建日志和错误信息
- 设置部署通知（Slack、Email 等）

### 6.3 回滚部署

1. 在 Vercel Dashboard 进入项目
2. 点击 **"Deployments"**
3. 找到要回滚的版本
4. 点击 **"..."** → **"Promote to Production"**

## 七、性能优化建议

### 7.1 启用 CDN 缓存

`vercel.json` 已配置静态资源缓存：

```json
{
  "src": "/assets/(.*)",
  "headers": {
    "cache-control": "public, max-age=31536000, immutable"
  }
}
```

### 7.2 图片优化

- 使用 WebP 格式
- 实现懒加载
- 使用响应式图片

### 7.3 代码分割

Vite 配置已启用代码分割：

```javascript
manualChunks: {
  vendor: ['react', 'react-dom', 'react-router-dom'],
  ui: ['framer-motion'],
  utils: ['axios']
}
```

### 7.4 预加载关键资源

在 `index.html` 中添加：

```html
<link rel="preload" href="/assets/main.js" as="script">
```

## 八、安全最佳实践

### 8.1 环境变量管理

- 不要在代码中硬编码敏感信息
- 使用 Vercel 环境变量管理 API 密钥
- 定期轮换密钥

### 8.2 HTTPS 强制

Vercel 默认启用 HTTPS，无需额外配置。

### 8.3 安全头部

在 `vercel.json` 中添加安全头部：

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ]
}
```

## 九、总结（Solo 部署核心流程）

1. 打开 TRAE → 切换 Solo 模式
2. 自然语言描述部署需求 → Solo 自动配置
3. 点 Deploy → 授权 Vercel
4. 一键部署 → 获取上线链接
5. 修改内容 → 重新部署自动更新

## 十、快速参考

### 部署命令

```bash
# 本地测试构建
cd frontend
npm install
npm run build

# 预览构建结果
npm run preview
```

### Vercel CLI

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录 Vercel
vercel login

# 部署项目
vercel --prod
```

### 有用的链接

- [Vercel 文档](https://vercel.com/docs)
- [Vite 部署指南](https://vitejs.dev/guide/build.html)
- [React Router 部署](https://reactrouter.com/en/main/start/overview#deploying)

## 十一、故障排查清单

部署前检查：

- [ ] `frontend/package.json` 存在且正确
- [ ] `frontend/vite.config.js` 配置正确
- [ ] `vercel.json` 配置正确
- [ ] 环境变量已配置
- [ ] 代码已推送到 GitHub
- [ ] 后端 API 可访问

部署后检查：

- [ ] 网站可正常访问
- [ ] 路由正常工作
- [ ] API 请求成功
- [ ] 静态资源加载正常
- [ ] 控制台无错误

---

**需要帮助？**

- 查看 [Vercel 文档](https://vercel.com/docs)
- 检查 [Vite 构建日志](https://vitejs.dev/guide/build.html)
- 联系技术支持

祝部署顺利！🚀
