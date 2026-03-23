# 国内AI服务配置指南

## 支持的AI服务商

| 服务商 | 主要功能 | 推荐用途 |
|--------|----------|----------|
| **DeepSeek** | 对话生成、文本处理、代码能力 | 场景对话生成 |
| **MiniMax** | 对话生成、文本处理 | 场景对话生成 |
| **豆包 (Doubao)** | 对话生成、文本处理 | 场景对话生成 |
| **阿里云语音服务** | 语音合成(TTS)、语音识别(STT) | 发音练习 |

---

## 1. DeepSeek 配置

### 注册步骤
1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册账号
3. 进入控制台 → 创建 API Key
4. 复制 API Key

### 环境变量配置
```env
AI_PROVIDER=deepseek
AI_DEEPSEEK_API_KEY=your_deepseek_api_key
AI_DEEPSEEK_MODEL=deepseek-chat
```

---

## 2. MiniMax 配置

### 注册步骤
1. 访问 [MiniMax开放平台](https://platform.minimax.chat/)
2. 注册账号并完成实名认证
3. 进入控制台 → 创建应用
4. 复制 API Key

### 环境变量配置
```env
AI_PROVIDER=minimax
AI_MINIMAX_API_KEY=your_minimax_api_key
AI_MINIMAX_MODEL=abab6.5s-chat
```

---

## 3. 豆包 (Doubao) 配置

### 注册步骤
1. 访问 [火山引擎 (豆包)](https://www.volcengine.com/product/doubao)
2. 注册账号并开通服务
3. 进入控制台 → 创建应用
4. 复制 API Key

### 环境变量配置
```env
AI_PROVIDER=doubao
AI_DOUBAO_API_KEY=your_doubao_api_key
AI_DOUBAO_MODEL=doubao-pro
```

---

## 4. 阿里云语音服务配置

### 注册步骤
1. 访问 [阿里云语音服务](https://ai.console.aliyun.com/)
2. 开通语音合成和语音识别服务
3. 创建AccessKey并获取密钥

### 环境变量配置
```env
AI_AZURE_SPEECH_KEY=your_aliyun_access_key
AI_AZURE_SPEECH_REGION=cn-east-1
```

---

## 4. 统一配置示例 (.env)

```env
# AI服务提供商: openai / minimax / doubao / azure
AI_PROVIDER=minimax

# MiniMax配置
AI_MINIMAX_API_KEY=your_minimax_api_key
AI_MINIMAX_MODEL=abab6.5s-chat

# 豆包配置 (备选)
AI_DOUBAO_API_KEY=your_doubao_api_key
AI_DOUBAO_MODEL=doubao-pro

# 阿里云语音服务
AI_AZURE_SPEECH_KEY=your_aliyun_access_key
AI_AZURE_SPEECH_REGION=cn-east-1
```

---

## 5. 快速配置脚本

运行配置向导：
```bash
cd scripts
setup-api-keys.bat
```

---

## 6. 验证配置

测试AI服务连接：
```bash
cd backend
python -c "from app.ai.llm_client import LLMClient; print(LLMClient().provider)"
```

---

## 常见问题

### Q: MiniMax API调用失败
**A:** 检查：
1. API Key是否正确
2. 账户余额是否充足
3. 是否开通了对应服务

### Q: 语音服务无法使用
**A:** 阿里云语音服务需要开通"语音合成"和"语音识别"两个服务

### Q: 如何切换AI服务商？
**A:** 修改 `AI_PROVIDER` 环境变量值为 `deepseek`、`minimax`、`doubao` 或 `openai`
