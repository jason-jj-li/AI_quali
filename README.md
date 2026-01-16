# 🔬 QualInsight - AI-Assisted Qualitative Research Platform v4.1

> 智能赋能研究，保持人文关怀 | Empowering Research, Maintaining Humanity

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-3.0-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📖 项目简介 / Project Introduction

### [中文] / Chinese

QualInsight 是一款功能完整的 AI 辅助质性研究平台，支持编码分析、主题识别、情感分析、话语分析、叙事分析等高级功能。专为单次分析设计，采用「上传→分析→下载」工作流程，无需数据库，数据隐私安全。

### English

QualInsight is a fully-featured AI-assisted qualitative research platform supporting coding analysis, theme identification, sentiment analysis, discourse analysis, narrative analysis, and more. Designed for single-session analysis with an "Upload → Analyze → Download" workflow, no database required, data privacy assured.

---

## ✨ 核心特性 / Key Features

| 功能 / Feature | 描述 / Description |
|----------------|---------------------|
| 🏷️ **AI 编码** | 演绎式/归纳式编码，层级结构，智能缓存 / Deductive/Inductive coding, hierarchical structure, smart caching |
| 🎯 **主题分析** | AI 主题识别，层级关系，跨案例分析 / AI theme identification, hierarchical relationships, cross-case analysis |
| 📊 **可视化** | 10+ 种图表类型 / 10+ chart types |
| 🔬 **高级分析** | 情感、话语、叙事分析，编码信度 / Sentiment, discourse, narrative analysis, coding reliability |
| 📝 **报告生成** | IMRAD 结构，双语支持 / IMRAD structure, bilingual support |
| 💾 **导出系统** | 多格式导出，项目打包 / Multi-format export, project packaging |
| ⚙️ **多 LLM** | OpenAI, Anthropic, Deepseek, LM Studio / Multiple LLM providers |

---

## 🚀 快速开始 / Quick Start

### 环境要求 / Requirements

- Python 3.9+
- pip

### 安装 / Installation

```bash
# 1. 进入项目目录 / Navigate to project directory
cd AI_quali

# 2. 安装依赖 / Install dependencies
pip install -r requirements.txt

# 3. 运行应用 / Run application
streamlit run app.py
```

应用将在 http://localhost:8501 启动

App will start at http://localhost:8501

### LLM 配置 / LLM Configuration

#### 默认选项 / Default: LM Studio (Local)

1. 下载 [LM Studio](https://lmstudio.ai/) / Download [LM Studio](https://lmstudio.ai/)
2. 启动本地服务器（默认端口 1234） / Start local server (default port 1234)
3. 无需 API 密钥 / No API key required

#### 云服务 / Cloud Services (Optional)

- **OpenAI**: API key starting with `sk-`
- **Deepseek**: Get API key from platform
- **Anthropic**: API key starting with `sk-ant-`

---

## 📖 使用指南 / User Guide

### 工作流程 / Workflow

```text
1. 🏠 主页 / Home → 配置 LLM / Configure LLM
2. 📋 数据准备 / Data Preparation → 输入文本 / Input text
3. 🏷️ AI 编码 / AI Coding → 分析编码 / Analyze codes
4. 🎯 主题分析 / Theme Analysis → 识别主题 / Identify themes
5. 📊 可视化 / Visualization → 查看图表 / View charts
6. 🔬 深度分析 / Advanced Analysis → 高级功能 / Advanced features
7. 📑 报告生成 / Report Generation → 生成报告 / Generate report
8. 💾 导出下载 / Export → 保存结果 / Save results
```

### 页面导航 / Page Navigation

| 页面 / Page | 功能 / Function |
|-------------|----------------|
| 🏠 主页 / Home | 项目介绍、LLM 配置、教程 / Intro, LLM config, tutorial |
| 📋 数据准备 / Data Prep | 研究问题、文本输入 / Research question, text input |
| 🏷️ AI 编码 / AI Coding | 演绎/归纳式编码 / Deductive/Inductive coding |
| 🎯 主题分析 / Theme Analysis | 主题识别、层级结构 / Theme identification, hierarchy |
| 📊 可视化 / Visualization | 热力图、网络图等 / Heatmaps, network graphs |
| 🔬 深度分析 / Advanced Analysis | 情感、话语、叙事 / Sentiment, discourse, narrative |
| 📑 报告生成 / Report Generation | IMRAD 学术报告 / Academic report |
| 💾 导出下载 / Export | 导出数据 / Export data |

---

## 🏗️ 项目结构 / Project Structure

```
AI_quali/
├── app.py                 # Streamlit 主应用 / Main app
├── config.py              # 项目配置 / Project config
├── requirements.txt       # Python 依赖 / Dependencies
│
├── pages/                 # 页面模块 / Page modules
│   ├── 1_data_preparation.py
│   ├── 2_coding.py
│   ├── 3_theme_analysis.py
│   ├── 4_visualization.py
│   ├── 5_deep_analysis.py
│   ├── 6_report.py
│   ├── 7_export.py
│   └── 9_settings.py
│
├── services/              # 业务逻辑 / Business logic
│   ├── coding_service.py
│   ├── theme_service.py
│   └── report_service.py
│
├── src/                   # 核心模块 / Core modules
│   ├── llm/              # LLM 接口 / LLM interfaces
│   │   ├── base.py
│   │   ├── openai.py
│   │   ├── lm_studio.py
│   │   ├── deepseek.py
│   │   ├── coding_assistant.py
│   │   ├── theme_assistant.py
│   │   └── report_assistant.py
│   │
│   ├── report/           # 报告生成 / Report generation
│   ├── coding.py
│   └── theme.py
│
├── prompts/              # AI 提示词 / AI prompts
│   ├── coding.txt
│   ├── theme.txt
│   └── report.txt
│
├── i18n/                # 国际化 / i18n
│   ├── translator.py
│   └── translations/
│       ├── zh_CN.json
│       └── en_US.json
│
└── utils/              # 工具函数 / Utilities
    ├── cache.py
    ├── exceptions.py
    ├── validators.py
    └── performance.py
```

---

## 🛠️ 技术栈 / Tech Stack

| 组件 / Component | 技术 / Technology |
|-----------------|-------------------|
| 前端 / Frontend | Streamlit 3.0 |
| 后端 / Backend | Python 3.9+ |
| LLM 接口 / LLM | OpenAI, Anthropic, Deepseek, LM Studio |
| 可视化 / Visualization | Plotly |
| 数据处理 / Data Processing | NumPy, Pandas |

---

## 💡 最佳实践 / Best Practices

### 编码建议 / Coding Tips

1. **多次迭代 / Multiple Iterations**: 先 AI 编码，后人工审核 / AI coding first, human review second
2. **层级结构 / Hierarchical Structure**: 建立 3 层结构 / Build 3-layer structure
3. **定期保存 / Save Regularly**: 每添加 10 个编码保存一次 / Save every 10 codes
4. **多编码者 / Multiple Coders**: 计算信度确保可靠性 / Calculate reliability

### API 费用控制 / Cost Control

- 优先使用本地模型 / Use local models first
- 关键分析才用 GPT-4o / Use GPT-4o for critical analysis
- 利用缓存减少调用 / Use caching to reduce calls

---

## ❓ 常见问题 / FAQ

### Q: 数据保存在哪里？ / Where is data stored?

**A:** 数据保存在浏览器 Session 中 / Data stored in browser session
- 关闭窗口会丢失 / Lost on window close
- 务必使用「导出下载」保存 / Must use "Export" to save

### Q: 本地模型 vs 在线模型？/ Local vs Cloud models?

| 特性 / Feature | 本地 / Local | 在线 / Cloud |
|----------------|-------------|-------------|
| 费用 / Cost | 免费 / Free | 付费 / Paid |
| 隐私 / Privacy | 本地 / Local | 云端 / Cloud |
| 效果 / Quality | 依赖模型 / Depends on model | 通常更好 / Usually better |

**推荐 / Recommendation**: 学习用本地，正式研究用在线 / Local for learning, cloud for research

---

## 📄 许可证 / License

本项目采用 MIT 许可证 / This project is licensed under MIT License

---

## 🤝 贡献 / Contributing

欢迎贡献！/ Welcome to contribute!

1. Fork 项目 / Fork the project
2. 创建分支 / Create branch (`git checkout -b feature/AmazingFeature`)
3. 提交更改 / Commit (`git commit -m 'Add feature'`)
4. 推送分支 / Push (`git push origin feature`)
5. 开启 PR / Open PR

---

## 📧 联系方式 / Contact

- 提交 Issue / Submit Issue
- 发送邮件 / Email: support@qualinsight.com

---

**QualInsight v4.1** - 让 AI 成为您的助手 / Let AI be your assistant, not replacement

🏗️ [项目结构](#-项目结构--project-structure) | 🚀 [快速开始](#-快速开始--quick-start) | 💡 [使用指南](#-使用指南--user-guide)
