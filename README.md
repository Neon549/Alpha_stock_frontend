# AlphaStock 🦄

> **Meet Your AI Trading Partner** — 基于 LangGraph 多智能体与 DeepSeek R1 深度推理的下一代 A 股智能投研平台

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-purple)](https://github.com/langchain-ai/langgraph)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-R1%20%7C%20V3-orange)](https://deepseek.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

🌐 **Live Demo**: [alphastock.cloud](https://alphastock.cloud)

---

## 📌 项目简介

AlphaStock 是一个全栈 A 股智能投研系统，核心采用 **LangGraph StateGraph** 构建多智能体辩论架构，通过多个 AI Agent 并行分析基本面、技术面与市场情绪，最终通过多空辩论网络达成投资决策。

系统同时提供量化回测、Alpha 多因子选股、全市场买点扫描、板块筛选等六大工具，并通过 FastAPI 后端 + Streamlit 前端 + Nginx 静态落地页的三层架构部署于腾讯云服务器。

---

## 🏗️ 系统架构

```
alphastock.cloud/          → 静态落地页 (Nginx)
alphastock.cloud/app       → Streamlit AI 功能界面
alphastock.cloud/api/v1    → FastAPI 后端
```

### 多智能体架构

```
用户输入股票代码
      ↓
┌─────────────────────────────────┐
│         LangGraph StateGraph     │
│                                  │
│  ┌──────────┐  ┌──────────────┐ │
│  │基本面Agent│  │ 技术面 Agent │ │  ← 并行 (ThreadPoolExecutor)
│  └──────────┘  └──────────────┘ │
│        ┌──────────────┐         │
│        │ 情绪面 Agent │         │
│        └──────────────┘         │
│              ↓                  │
│  ┌─────────────────────────┐   │
│  │  多空辩论 (Bull vs Bear) │   │
│  └─────────────────────────┘   │
│              ↓                  │
│     ┌──────────────────┐       │
│     │  Trader 决策节点  │       │
│     └──────────────────┘       │
└─────────────────────────────────┘
      ↓
  买入 / 观望 / 减仓 + 完整研报
```

---

## ✨ 功能模块

| 模块 | 描述 |
|------|------|
| 🤖 **AI 股票助手** | 输入股票代码，多 Agent 并行分析，生成完整投研报告 |
| 📊 **量化回测** | Backtrader 框架，KDJ / RSI / 布林带 / MACD 五种策略 |
| ✨ **Alpha 选股** | 全市场五维因子（KDJ · 量能 · ROE · 市值 · 趋势）打分 |
| 🎯 **今日买点** | 全市场技术面超卖信号扫描，市值 ≥300 亿过滤 |
| 🔍 **板块筛选** | 基于景气周期与 PE/ROE 估值的细分板块优选 |
| 📎 **财报解析** | 上传财报截图 / PDF，AI 自动提取关键指标纳入分析 |

---

## 🛠️ 技术栈

**AI / Agent**
- LangGraph StateGraph — 多智能体编排
- DeepSeek R1 / V3 — 深度推理 LLM
- RAG (ChromaDB) — 检索增强生成，Recall@5: 91.2%
- TechLens-1.5B — 自研微调技术分析模型（本地优先 + DeepSeek fallback）

**后端**
- FastAPI — REST API
- SQLite — 对话记忆模块
- akshare / yfinance — A 股实时行情数据
- Backtrader — 量化回测引擎

**前端**
- Streamlit — AI 功能界面（多页面架构）
- HTML / CSS / JS — 静态落地页

**部署**
- 腾讯云 CVM — Ubuntu 24.04
- Nginx — 反向代理 + 静态托管
- Let's Encrypt — HTTPS

---

## 📁 项目结构

```
Alpha_stock_frontend/
├── web/
│   └── alphastock.html        # 静态落地页
├── src/
│   ├── streamlit_app.py       # 入口 & 登录页
│   ├── pages/
│   │   ├── 1_chat.py          # 🤖 AI 股票助手
│   │   ├── 2_backtest.py      # 📊 量化回测
│   │   ├── 3_alpha.py         # ✨ Alpha 选股
│   │   ├── 4_scan.py          # 🎯 今日买点
│   │   └── 5_filter.py        # 🔍 板块筛选
│   └── utils/
│       └── common.py          # 公共常量 / CSS / 侧边栏 / 鉴权
├── requirements.txt
└── Dockerfile
```

---

## 🚀 本地运行

```bash
# 克隆仓库
git clone https://github.com/Neon549/Alpha_stock_frontend
cd Alpha_stock_frontend

# 安装依赖
pip install -r requirements.txt

# 启动 Streamlit
cd src
streamlit run streamlit_app.py
```

> 需要配置 `.env` 文件，包含 `DEEPSEEK_API_KEY` 等环境变量，参考后端仓库 [Alpha_stock](https://github.com/Neon549/Alpha_stock)

---

## 🔗 相关仓库

| 仓库 | 描述 |
|------|------|
| [Alpha_stock](https://github.com/Neon549/Alpha_stock) | 后端 FastAPI + LangGraph Agent |
| [Alpha_stock_frontend](https://github.com/Neon549/Alpha_stock_frontend) | 本仓库，前端 Streamlit + 落地页 |
| [TechLens-1.5B](https://github.com/Neon549/TechLens-1.5B) | 自研技术分析微调模型 |
| [xhs-planting-agent](https://github.com/Neon549/xhs-planting-agent) | RAG 多智能体内容系统 |

---

## 📬 联系

- **Email**: yulingyu08@gmail.com
- **GitHub**: [@Neon549](https://github.com/Neon549)
- **Live**: [alphastock.cloud](https://alphastock.cloud)

---

## ⚠️ 免责声明

本项目所有分析结果仅供参考，不构成任何投资建议。股市有风险，投资需谨慎。

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/Neon549">Neon549</a></sub>
</div>