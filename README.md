# 🔬 QualInsight - AI-Assisted Qualitative Research Platform v4.1

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md) [![中文](https://img.shields.io/badge/lang-中文-red.svg)](README.zh-Hans.md)

> Empowering Research, Maintaining Humanity

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-3.0-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📖 Project Introduction

**QualInsight** is a fully-featured AI-assisted qualitative research platform supporting coding analysis, theme identification, sentiment analysis, discourse analysis, narrative analysis, and more. Designed for single-session analysis with an "Upload → Analyze → Download" workflow, no database required, data privacy assured.

---

## ✨ Key Features

| Feature | Description |
|----------------|---------------------|
| 🏷️ **AI Coding** | Deductive/Inductive coding, hierarchical structure, smart caching |
| 🎯 **Theme Analysis** | AI theme identification, hierarchical relationships, cross-case analysis |
| 📊 **Visualization** | 10+ chart types |
| 🔬 **Advanced Analysis** | Sentiment, discourse, narrative analysis, coding reliability |
| 📝 **Report Generation** | IMRAD structure, bilingual support |
| 💾 **Export System** | Multi-format export, project packaging |
| ⚙️ **Multiple LLMs** | OpenAI, Anthropic, Deepseek, LM Studio |

---

## 🚀 Quick Start

### Requirements

- Python 3.9+
- pip

### Installation

```bash
# 1. Navigate to project directory
cd AI_quali

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
streamlit run app.py
```

App will start at http://localhost:8501

### LLM Configuration

#### Default Option: LM Studio (Local)

1. Download [LM Studio](https://lmstudio.ai/)
2. Start local server (default port 1234)
3. No API key required

#### Cloud Services (Optional)

- **OpenAI**: API key starting with `sk-`
- **Deepseek**: Get API key from platform
- **Anthropic**: API key starting with `sk-ant-`

---

## 📖 User Guide

### Workflow

```text
1. 🏠 Home → Configure LLM
2. 📋 Data Preparation → Input text
3. 🏷️ AI Coding → Analyze codes
4. 🎯 Theme Analysis → Identify themes
5. 📊 Visualization → View charts
6. 🔬 Advanced Analysis → Advanced features
7. 📑 Report Generation → Generate report
8. 💾 Export → Save results
```

### Page Navigation

| Page | Function |
|-------------|----------------|
| 🏠 Home | Intro, LLM config, tutorial |
| 📋 Data Preparation | Research question, text input |
| 🏷️ AI Coding | Deductive/Inductive coding |
| 🎯 Theme Analysis | Theme identification, hierarchy |
| 📊 Visualization | Heatmaps, network graphs |
| 🔬 Advanced Analysis | Sentiment, discourse, narrative |
| 📑 Report Generation | Academic report |
| 💾 Export | Export data |

---

## 🏗️ Project Structure

```
AI_quali/
├── app.py                 # Main Streamlit app
├── config.py              # Project configuration
├── requirements.txt       # Python dependencies
│
├── pages/                 # Page modules
│   ├── 1_data_preparation.py
│   ├── 2_coding.py
│   ├── 3_theme_analysis.py
│   ├── 4_visualization.py
│   ├── 5_deep_analysis.py
│   ├── 6_report.py
│   ├── 7_export.py
│   └── 9_settings.py
│
├── services/              # Business logic
│   ├── coding_service.py
│   ├── theme_service.py
│   └── report_service.py
│
├── src/                   # Core modules
│   ├── llm/              # LLM interfaces
│   │   ├── base.py
│   │   ├── openai.py
│   │   ├── lm_studio.py
│   │   ├── deepseek.py
│   │   ├── coding_assistant.py
│   │   ├── theme_assistant.py
│   │   └── report_assistant.py
│   │
│   ├── report/           # Report generation
│   ├── coding.py
│   └── theme.py
│
├── prompts/              # AI prompts
│   ├── coding.txt
│   ├── theme.txt
│   └── report.txt
│
├── i18n/                # Internationalization
│   ├── translator.py
│   └── translations/
│       ├── zh_CN.json
│       └── en_US.json
│
└── utils/              # Utilities
    ├── cache.py
    ├── exceptions.py
    ├── validators.py
    └── performance.py
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------------|-------------------|
| Frontend | Streamlit 3.0 |
| Backend | Python 3.9+ |
| LLM Interface | OpenAI, Anthropic, Deepseek, LM Studio |
| Visualization | Plotly |
| Data Processing | NumPy, Pandas |

---

## 💡 Best Practices

### Coding Tips

1. **Multiple Iterations**: AI coding first, human review second
2. **Hierarchical Structure**: Build 3-layer structure
3. **Save Regularly**: Save every 10 codes
4. **Multiple Coders**: Calculate reliability to ensure consistency

### API Cost Control

- Use local models first
- Use GPT-4o only for critical analysis
- Use caching to reduce calls

---

## ❓ FAQ

### Q: Where is data stored?

**A:** Data is stored in browser session
- Lost on window close
- Must use "Export" to save

### Q: Local vs Cloud models?

| Feature | Local | Cloud |
|----------------|-------------|-------------|
| Cost | Free | Paid |
| Privacy | Local | Cloud |
| Quality | Depends on model | Usually better |

**Recommendation**: Local for learning, cloud for research

---

## 📄 License

This project is licensed under MIT License

---

## 🤝 Contributing

Welcome to contribute!

1. Fork the project
2. Create branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add feature'`)
4. Push (`git push origin feature`)
5. Open PR

---

## 📧 Contact

- Submit Issue
- Email: support@qualinsight.com

---

**QualInsight v4.1** - Let AI be your assistant, not replacement

🏗️ [Project Structure](#-project-structure) | 🚀 [Quick Start](#-quick-start) | 💡 [User Guide](#-user-guide)
