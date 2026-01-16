# 🔬 QualInsight - AI 辅助质性研究平台 v4.1

> 智能赋能研究，保持人文关怀

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-3.0-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📖 项目简介

**QualInsight** 是一款功能完整的 AI 辅助质性研究平台，支持编码分析、主题识别、情感分析、话语分析、叙事分析等高级功能。专为单次分析设计，采用「上传→分析→下载」工作流程，无需数据库，数据隐私安全。

---

## ✨ 核心特性

| 功能 | 描述 |
|----------------|---------------------|
| 🏷️ **AI 编码** | 演绎式/归纳式编码，层级结构，智能缓存 |
| 🎯 **主题分析** | AI 主题识别，层级关系，跨案例分析 |
| 📊 **可视化** | 10+ 种图表类型 |
| 🔬 **高级分析** | 情感、话语、叙事分析，编码信度 |
| 📝 **报告生成** | IMRAD 结构，双语支持 |
| 💾 **导出系统** | 多格式导出，项目打包 |
| ⚙️ **多 LLM** | OpenAI, Anthropic, Deepseek, LM Studio |

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- pip

### 安装

```bash
# 1. 进入项目目录
cd AI_quali

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行应用
streamlit run app.py
```

应用将在 http://localhost:8501 启动

### LLM 配置

#### 默认选项：LM Studio (本地)

1. 下载 [LM Studio](https://lmstudio.ai/)
2. 启动本地服务器（默认端口 1234）
3. 无需 API 密钥

#### 云服务（可选）

- **OpenAI**: 以 `sk-` 开头的 API 密钥
- **Deepseek**: 从平台获取 API 密钥
- **Anthropic**: 以 `sk-ant-` 开头的 API 密钥

---

## 📖 使用指南

### 工作流程

```text
1. 🏠 主页 → 配置 LLM
2. 📋 数据准备 → 输入文本
3. 🏷️ AI 编码 → 分析编码
4. 🎯 主题分析 → 识别主题
5. 📊 可视化 → 查看图表
6. 🔬 深度分析 → 高级功能
7. 📑 报告生成 → 生成报告
8. 💾 导出下载 → 保存结果
```

### 页面导航

| 页面 | 功能 |
|-------------|----------------|
| 🏠 主页 | 项目介绍、LLM 配置、教程 |
| 📋 数据准备 | 研究问题、文本输入 |
| 🏷️ AI 编码 | 演绎/归纳式编码 |
| 🎯 主题分析 | 主题识别、层级结构 |
| 📊 可视化 | 热力图、网络图等 |
| 🔬 深度分析 | 情感、话语、叙事 |
| 📑 报告生成 | IMRAD 学术报告 |
| 💾 导出下载 | 导出数据 |

---

## 🏗️ 项目结构

```
AI_quali/
├── app.py                 # Streamlit 主应用
├── config.py              # 项目配置
├── requirements.txt       # Python 依赖
│
├── pages/                 # 页面模块
│   ├── 1_data_preparation.py
│   ├── 2_coding.py
│   ├── 3_theme_analysis.py
│   ├── 4_visualization.py
│   ├── 5_deep_analysis.py
│   ├── 6_report.py
│   ├── 7_export.py
│   └── 9_settings.py
│
├── services/              # 业务逻辑
│   ├── coding_service.py
│   ├── theme_service.py
│   └── report_service.py
│
├── src/                   # 核心模块
│   ├── llm/              # LLM 接口
│   │   ├── base.py
│   │   ├── openai.py
│   │   ├── lm_studio.py
│   │   ├── deepseek.py
│   │   ├── coding_assistant.py
│   │   ├── theme_assistant.py
│   │   └── report_assistant.py
│   │
│   ├── report/           # 报告生成
│   ├── coding.py
│   └── theme.py
│
├── prompts/              # AI 提示词
│   ├── coding.txt
│   ├── theme.txt
│   └── report.txt
│
├── i18n/                # 国际化
│   ├── translator.py
│   └── translations/
│       ├── zh_CN.json
│       └── en_US.json
│
└── utils/              # 工具函数
    ├── cache.py
    ├── exceptions.py
    ├── validators.py
    └── performance.py
```

---

## 🛠️ 技术栈

| 组件 | 技术 |
|-----------------|-------------------|
| 前端 | Streamlit 3.0 |
| 后端 | Python 3.9+ |
| LLM 接口 | OpenAI, Anthropic, Deepseek, LM Studio |
| 可视化 | Plotly |
| 数据处理 | NumPy, Pandas |

---

## 💡 最佳实践

### 编码建议

1. **多次迭代**: 先 AI 编码，后人工审核
2. **层级结构**: 建立 3 层结构
3. **定期保存**: 每添加 10 个编码保存一次
4. **多编码者**: 计算信度确保可靠性

### API 费用控制

- 优先使用本地模型
- 关键分析才用 GPT-4o
- 利用缓存减少调用

---

## ❓ 常见问题

### Q: 数据保存在哪里？

**A:** 数据保存在浏览器 Session 中
- 关闭窗口会丢失
- 务必使用「导出下载」保存

### Q: 本地模型 vs 在线模型？

| 特性 | 本地 | 在线 |
|----------------|-------------|-------------|
| 费用 | 免费 | 付费 |
| 隐私 | 本地 | 云端 |
| 效果 | 依赖模型 | 通常更好 |

**推荐**: 学习用本地，正式研究用在线

---

## 📄 许可证

本项目采用 MIT 许可证

---

## 🤝 贡献

欢迎贡献！

1. Fork 项目
2. 创建分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add feature'`)
4. 推送分支 (`git push origin feature`)
5. 开启 PR

---

## 📧 联系方式

- 提交 Issue
- 发送邮件: support@qualinsight.com

---

**QualInsight v4.1** - 让 AI 成为您的助手，不是替代品

🏗️ [项目结构](#-项目结构) | 🚀 [快速开始](#-快速开始) | 💡 [使用指南](#-使用指南)
