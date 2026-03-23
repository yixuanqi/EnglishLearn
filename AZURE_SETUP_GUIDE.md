# Azure AI Services 配置指南

## 需要的 Azure 资源

### 1. Azure OpenAI Service (对话生成)

#### 注册步骤：
1. 访问 https://portal.azure.com 并登录
2. 搜索 "Azure OpenAI"
3. 点击 "创建"
4. 选择订阅和资源组
5. 选择区域（推荐：eastus）
6. 选择定价层（S0）
7. 点击 "创建"
8. 等待部署完成（约 5-10 分钟）
9. 在资源中点击 "Keys and Endpoint"
10. 复制 Key 和 Endpoint

#### 获取 API Key：
- Portal -> Azure OpenAI -> 资源 -> Keys and Endpoint
- 或者访问 https://oai.azure.com -> API Keys

### 2. Azure Speech Services (TTS + STT + 发音评测)

#### 创建 Speech Service：
1. 在 Azure Portal 搜索 "Speech"
2. 点击 "Create Speech resource"
3. 配置：
   - Name: english-trainer-speech
   - Pricing tier: Free (F0) or Standard (S0)
   - Region: eastus (推荐)
4. 点击 "Create"
5. 等待部署完成后，获取 Key 和 Region

#### 获取凭据：
- Azure Portal -> Your Speech Resource -> Keys and Endpoint
- 需要： SPEECH_KEY 和 SPEECH_REGION

### 3. 获取 OpenAI API Key (备选)

如果不想用 Azure OpenAI，可以用原生 OpenAI：
1. 访问 https://platform.openai.com
2. 注册/登录账号
3. 点击右上角头像 -> API Keys
4. 创建新 API Key
5. 注意：需要充值或使用免费额度

## 环境变量配置

在 `.env` 文件中配置以下内容：

```bash
# Azure OpenAI (对话生成)
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4

# 或者使用原生 OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Azure Speech (TTS/STT/发音评测)
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=eastus

# LLM 提供者选择
# 使用 Azure OpenAI: "azure"
# 使用原生 OpenAI: "openai"
LLM_PROVIDER=azure
```

## 免费额度

| 服务 | 免费额度 | 链接 |
|------|----------|------|
| Azure OpenAI | $0 (需申请) | https://ai.azure.com |
| Azure Speech | $0 (F0 tier) | 5000请求/月 |
| OpenAI | $5 免费credit | https://platform.openai.com |

## 验证配置

配置完成后，运行验证脚本：
```bash
python scripts/test-ai-services.py
```
