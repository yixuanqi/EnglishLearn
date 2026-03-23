# English Trainer - Frontend Interface

高端精致的英语学习前端界面，采用奢华精致风格设计。

## 设计特色

### 视觉风格
- **奢华精致主题**：深色背景配合金色点缀，营造高端学习体验
- **优雅字体**：使用 Playfair Display 和 Source Sans 3 字体组合
- **精致动画**：流畅的过渡效果和微交互
- **响应式设计**：完美适配桌面和移动设备

### 核心功能
1. **用户认证**：登录/注册页面
2. **仪表板**：学习进度统计和最近练习
3. **场景列表**：按难度筛选的练习场景
4. **练习界面**：AI对话练习和实时反馈

## 快速开始

### 方式1：直接打开HTML文件（推荐）

最简单的方式是直接在浏览器中打开HTML文件：

```bash
# 在浏览器中打开
start frontend/index.html
```

或者双击 `frontend/index.html` 文件即可在浏览器中查看界面。

### 方式2：使用本地服务器

如果你有Python环境：

```bash
# 进入前端目录
cd frontend

# 使用Python启动简单HTTP服务器
python -m http.server 3000

# 或者使用Python 3
python3 -m http.server 3000
```

然后在浏览器中访问：`http://localhost:3000`

### 方式3：使用React开发服务器（需要Node.js）

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 界面预览

### 登录页面
- 优雅的渐变背景
- 金色品牌标识
- 流畅的表单交互

### 仪表板
- 学习统计卡片
- 进度趋势显示
- 最近练习记录

### 场景列表
- 网格布局展示
- 难度筛选功能
- 搜索功能
- Premium标识

### 练习界面
- 对话式学习
- 实时语音识别
- AI反馈系统

## 技术栈

### 纯HTML版本
- HTML5
- CSS3 (包含动画和响应式设计)
- JavaScript (ES6+)
- Google Fonts

### React版本（可选）
- React 18
- React Router
- Axios
- Framer Motion

## 设计系统

### 颜色变量
```css
--color-bg-primary: #0a0a0f;
--color-bg-secondary: #12121a;
--color-bg-tertiary: #1a1a24;
--color-gold: #d4af37;
--color-gold-light: #f4cf57;
```

### 字体
- **Display Font**: Playfair Display (标题和重要文本)
- **Body Font**: Source Sans 3 (正文和UI元素)

### 间距和圆角
- **小圆角**: 8px
- **中圆角**: 12px
- **大圆角**: 16px
- **超大圆角**: 24px

## 后端集成

前端已配置好与后端API的集成：

### API基础URL
```
http://localhost:8000/api/v1
```

### 主要端点
- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册
- `GET /scenarios` - 获取场景列表
- `POST /practice/start` - 开始练习会话
- `POST /practice/submit` - 提交练习结果

## 注意事项

1. **后端服务**：确保后端服务运行在 `http://localhost:8000`
2. **CORS配置**：后端需要配置CORS允许前端访问
3. **环境变量**：在生产环境中配置正确的API地址

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 开发说明

### 文件结构
```
frontend/
├── index.html              # 纯HTML版本（可直接打开）
├── package.json            # React版本依赖配置
├── vite.config.js         # Vite配置
└── src/
    ├── main.jsx           # React入口
    ├── App.jsx            # React主组件
    ├── index.css          # 全局样式
    ├── components/        # React组件
    ├── pages/            # 页面组件
    └── contexts/         # React Context
```

### 自定义样式

所有样式都使用CSS变量，可以轻松自定义主题：

```css
:root {
  --color-gold: #your-color;
  --font-display: 'Your Font';
}
```

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。