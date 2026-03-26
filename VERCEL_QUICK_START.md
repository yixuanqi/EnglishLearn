# Vercel 部署快速指南

## 当前状态

✅ GitHub 仓库：https://github.com/yixuanqi/EnglishLearn
✅ 代码已推送到 main 分支
✅ Vercel 配置文件已就绪

---

## Vercel 部署步骤

### 第一步：登录 Vercel

1. 访问 https://vercel.com/login
2. 使用 GitHub 账号登录
3. 授权 Vercel 访问您的 GitHub 仓库

### 第二步：导入项目

1. 登录后，点击 **"Add New..."** → **"Project"**
2. 在 **"Import Git Repository"** 部分
3. 找到并选择 **`yixuanqi/EnglishLearn`** 仓库
4. 点击 **"Import"**

### 第三步：配置项目设置

Vercel 会自动检测到 Vite 项目，确认以下配置：

#### 构建配置

```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

#### 环境变量

在 **Environment Variables** 部分添加：

```
Name: VITE_API_URL
Value: https://api.englishspeakingtrainer.com
Environment: Production, Preview, Development
```

**注意**：如果您的后端 API 地址不同，请相应修改 `Value`。

### 第四步：部署

1. 检查所有配置是否正确
2. 点击 **"Deploy"** 按钮
3. 等待构建完成（通常 1-2 分钟）

### 第五步：获取访问地址

部署成功后，Vercel 会显示：
- **预览地址**：`english-learn-xxx.vercel.app`
- **生产地址**：`english-learn.vercel.app`（如果配置了自定义域名）

---

## 部署后验证

### 1. 检查部署状态

在 Vercel Dashboard 中：
- 进入项目页面
- 查看 **Deployments** 标签
- 确认最新部署状态为 **Ready**

### 2. 测试网站

访问部署地址，检查：
- [ ] 页面正常加载
- [ ] 路由正常工作
- [ ] 样式正确显示
- [ ] 控制台无错误

### 3. 测试 API 连接

打开浏览器控制台（F12），检查：
- [ ] API 请求正常
- [ ] 无 CORS 错误
- [ ] 响应数据正确

---

## 常见问题

### 问题 1：构建失败

**可能原因**：
- 依赖安装失败
- 构建命令错误
- 环境变量缺失

**解决方法**：
1. 查看 Vercel 构建日志
2. 检查 `frontend/package.json` 中的脚本
3. 确认所有依赖都在 `package.json` 中

### 问题 2：页面 404

**可能原因**：
- SPA 路由未正确配置
- 构建输出目录错误

**解决方法**：
1. 确认 `vercel.json` 中的 `outputDirectory` 为 `frontend/dist`
2. 检查 `rewrites` 配置是否正确

### 问题 3：API 请求失败

**可能原因**：
- 环境变量未设置
- CORS 配置错误
- 后端 API 不可访问

**解决方法**：
1. 确认 `VITE_API_URL` 环境变量已设置
2. 检查后端 CORS 配置
3. 验证后端 API 是否可访问

### 问题 4：样式加载异常

**可能原因**：
- 静态资源路径错误
- CSS 文件未正确构建

**解决方法**：
1. 检查 `vite.config.js` 中的 `base` 配置
2. 确认 CSS 文件在 `dist` 目录中

---

## 更新部署

### 修改代码后自动部署

1. 在本地修改代码
2. 提交并推送到 GitHub：
   ```bash
   git add .
   git commit -m "更新功能"
   git push origin main
   ```
3. Vercel 会自动检测到推送并触发部署

### 手动触发部署

1. 访问 Vercel Dashboard
2. 进入项目页面
3. 点击 **Deployments** 标签
4. 找到要重新部署的版本
5. 点击 **"..."** → **"Redeploy"**

---

## 自定义域名（可选）

### 添加自定义域名

1. 在 Vercel Dashboard 中进入项目
2. 点击 **Settings** → **Domains**
3. 点击 **Add** 添加域名
4. 按照提示配置 DNS 记录

### DNS 配置

```
Type: CNAME
Name: @
Value: cname.vercel-dns.com
```

---

## 监控和日志

### 查看构建日志

1. 进入 Vercel Dashboard
2. 点击项目
3. 查看 **Deployments** 标签
4. 点击具体的部署查看详细日志

### 查看实时日志

1. 进入项目页面
2. 点击 **Logs** 标签
3. 查看实时日志和错误信息

---

## 性能优化

### 启用缓存

Vercel 默认启用 CDN 缓存，静态资源会自动缓存。

### 图片优化

1. 使用 WebP 格式
2. 实现懒加载
3. 使用响应式图片

### 代码分割

Vite 已配置代码分割，无需额外配置。

---

## 安全建议

### 环境变量管理

- 不要在代码中硬编码敏感信息
- 使用 Vercel 环境变量管理 API 密钥
- 定期轮换密钥

### HTTPS

Vercel 默认启用 HTTPS，无需额外配置。

---

## 需要帮助？

- [Vercel 文档](https://vercel.com/docs)
- [Vite 部署指南](https://vitejs.dev/guide/build.html)
- [项目仓库](https://github.com/yixuanqi/EnglishLearn)

---

**祝部署顺利！🚀**
