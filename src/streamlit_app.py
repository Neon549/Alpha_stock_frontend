import streamlit as st
import requests
import time
import datetime
import pandas as pd
import plotly.graph_objects as go

API_BASE = "https://neonzz-neon-stock-trading-agent.hf.space/api/v1"

st.set_page_config(
    page_title="StockMind",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 20px !important; padding-bottom: 40px !important; max-width: 860px !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #f9f9f8 !important; border-right: 1px solid #e5e5e3 !important; }
[data-testid="stSidebar"] .block-container { padding: 16px 12px !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* 侧边栏按钮统一样式 */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #374151 !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 7px 10px !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: background 0.12s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #efefed !important;
    color: #111827 !important;
}

/* 主区域 */
.stApp { background: #f5f5f3 !important; }
[data-testid="stAppViewContainer"] { background: #f5f5f3 !important; }
.main { background: #f5f5f3 !important; }

/* 聊天消息 */
.chat-msg-user {
    display: flex; justify-content: flex-end; margin-bottom: 14px;
}
.chat-msg-user-bubble {
    background: #111827; color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 11px 16px; max-width: 70%;
    font-size: 14px; line-height: 1.6;
}
.chat-msg-ai {
    display: flex; align-items: flex-start; gap: 10px; margin-bottom: 20px;
}
.chat-msg-ai-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg, #d97706, #f59e0b);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0; margin-top: 2px;
    color: white; font-weight: 700;
}
.chat-msg-ai-content {
    background: white; border: 1px solid #e5e7eb;
    border-radius: 4px 18px 18px 18px;
    padding: 14px 18px; max-width: 85%;
    font-size: 14px; line-height: 1.7; color: #111827;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* 输入框区域 */
.input-wrap {
    position: sticky; bottom: 0;
    background: linear-gradient(to top, #f5f5f3 85%, transparent);
    padding: 16px 0 8px;
}
.input-box {
    background: white; border: 1px solid #d1d5db;
    border-radius: 16px; padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    display: flex; align-items: center; gap: 10px;
}

/* 分析结果面板 */
.result-card {
    background: white; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 18px 20px;
    margin: 10px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.result-card-title { font-size: 12px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; }

.badge { display: inline-flex; align-items: center; gap: 4px; padding: 2px 9px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-buy { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.badge-sell { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.badge-hold { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }

/* metric卡片 */
.mini-metric { display: inline-block; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px 14px; margin: 4px; }
.mini-metric-label { font-size: 10px; color: #9ca3af; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.mini-metric-value { font-size: 17px; font-weight: 700; color: #111827; font-family: 'JetBrains Mono', monospace; margin-top: 2px; }
.mini-metric-value.up { color: #dc2626; }
.mini-metric-value.down { color: #10b981; }

/* 侧边栏历史条目 */
.hist-entry {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 10px; border-radius: 7px;
    font-size: 12px; color: #6b7280;
    margin-bottom: 1px;
}
.hist-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.hist-dot.buy { background: #ef4444; }
.hist-dot.sell { background: #10b981; }
.hist-dot.hold { background: #f59e0b; }

/* 主输入框覆盖 */
.stTextInput > div > div > input {
    background: white !important; border: 1px solid #d1d5db !important;
    color: #111827 !important; border-radius: 12px !important;
    font-size: 14px !important; padding: 10px 14px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}
.stTextInput > div > div > input:focus { border-color: #d97706 !important; box-shadow: 0 0 0 3px rgba(217,119,6,0.08) !important; }

.stButton > button {
    background: #111827 !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 13px !important;
}
.stButton > button:hover { background: #1f2937 !important; }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #e5e7eb !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #6b7280 !important; font-size: 12px !important; }
.stTabs [aria-selected="true"] { color: #d97706 !important; border-bottom: 2px solid #d97706 !important; }

label { color: #374151 !important; font-size: 12px !important; font-weight: 500 !important; }
hr { border-color: #e5e7eb !important; margin: 10px 0 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── 板块数据 ───────────────────────────────────────────────────────────────
SECTORS = {
    "半导体": {"603650": "彤程新材", "002222": "福晶科技", "002549": "凯美特气"},
    "CPO光模块": {"300308": "中际旭创", "002281": "光迅科技", "300281": "金信诺"},
    "新能源": {"002709": "天赐材料", "603876": "鼎盛新材"},
    "消费电子": {"000725": "京东方A", "002049": "紫光国微"},
    "军工": {"600893": "航发动力", "600760": "中航沈飞"},
}

# ── Session State ──────────────────────────────────────────────────────────
defaults = {
    "mode": "chat",  # chat / backtest / scan / filter
    "chat_messages": [],  # [{role, content, type, data}]
    "history_list": [],  # [{code, decision, time}]
    "bt_result": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── 后端状态 ───────────────────────────────────────────────────────────────
try:
    r = requests.get(f"{API_BASE}/health", timeout=2)
    backend_ok = r.status_code == 200
except:
    backend_ok = False

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown(
        """
    <div style="display:flex;align-items:center;gap:10px;padding:4px 4px 18px;border-bottom:1px solid #e5e5e3;margin-bottom:14px">
        <div style="width:30px;height:30px;background:linear-gradient(135deg,#d97706,#f59e0b);border-radius:7px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:14px">S</div>
        <span style="font-size:15px;font-weight:600;color:#111827;letter-spacing:-0.3px">StockMind</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 新对话按钮
    if st.button("＋  新对话", key="new_chat", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.mode = "chat"
        st.rerun()

    st.markdown(
        '<div style="font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.08em;padding:14px 4px 6px">功能</div>',
        unsafe_allow_html=True,
    )

    # 功能导航
    nav_items = [
        ("chat", "🤖", "AI 股票分析"),
        ("backtest", "📊", "量化回测"),
        ("scan", "🎯", "今日买点"),
        ("filter", "🔍", "板块筛选"),
    ]
    for key, icon, label in nav_items:
        is_active = st.session_state.mode == key
        btn_label = f"**{icon}  {label}**" if is_active else f"{icon}  {label}"
        if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
            st.session_state.mode = key
            st.rerun()

    st.markdown("---")

    # 后端状态
    if backend_ok:
        st.markdown(
            '<div style="display:inline-flex;align-items:center;gap:5px;font-size:11px;color:#16a34a;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:20px;padding:3px 8px">● 后端在线</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="display:inline-flex;align-items:center;gap:5px;font-size:11px;color:#dc2626;background:#fef2f2;border:1px solid #fecaca;border-radius:20px;padding:3px 8px">● 后端离线</div>',
            unsafe_allow_html=True,
        )

    # 历史记录
    if st.session_state.history_list:
        st.markdown(
            '<div style="font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.08em;padding:14px 4px 6px">最近分析</div>',
            unsafe_allow_html=True,
        )
        for item in reversed(st.session_state.history_list[-8:]):
            d = item.get("decision", "")
            dot = (
                "buy"
                if "买入" in d
                else ("sell" if ("卖出" in d or "减仓" in d) else "hold")
            )
            color = (
                "#ef4444"
                if dot == "buy"
                else ("#10b981" if dot == "sell" else "#f59e0b")
            )
            st.markdown(
                f"""
            <div class="hist-entry">
                <div class="hist-dot {dot}" style="background:{color}"></div>
                <span style="font-weight:500;color:#374151">{item['code']}</span>
                <span style="margin-left:auto;font-size:10px;color:#d1d5db">{item.get('time','')}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

mode = st.session_state.mode

# ══════════════════════════════════════════════════════════════════════════
# 主区域：AI 对话分析
# ══════════════════════════════════════════════════════════════════════════
if mode == "chat":

    # 欢迎界面（无消息时）
    if not st.session_state.chat_messages:
        st.markdown(
            """
        <div style="text-align:center;padding:60px 20px 40px;max-width:560px;margin:0 auto">
            <div style="font-size:30px;font-weight:700;color:#111827;letter-spacing:-1px;margin-bottom:10px">
                你好，<span style="color:#d97706">开始分析</span>
            </div>
            <div style="font-size:14px;color:#6b7280;line-height:1.7">
                输入股票代码或名称，获取<br>基本面 · 技术面 · 情绪面三维综合分析
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 快捷建议
        st.markdown(
            '<div style="max-width:560px;margin:0 auto">', unsafe_allow_html=True
        )
        suggestions = [
            ("分析 600584 长电科技", "600584"),
            ("分析 000725 京东方A", "000725"),
            ("分析 603650 彤程新材", "603650"),
            ("分析 002222 福晶科技", "002222"),
        ]
        c1, c2 = st.columns(2)
        for i, (label, code) in enumerate(suggestions):
            col = c1 if i % 2 == 0 else c2
            with col:
                if st.button(label, key=f"sug_{code}", use_container_width=True):
                    st.session_state.chat_messages.append(
                        {"role": "user", "content": label}
                    )
                    st.session_state["_pending_code"] = code
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 渲染历史消息
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(
                f"""
            <div class="chat-msg-user">
                <div class="chat-msg-user-bubble">{msg["content"]}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        elif msg["role"] == "assistant":
            mtype = msg.get("type", "text")

            if mtype == "analysis":
                data = msg.get("data", {})
                dtxt = data.get("decision", "")
                if "买入" in dtxt:
                    badge = '<span class="badge badge-buy">🔴 买入信号</span>'
                elif "卖出" in dtxt or "减仓" in dtxt:
                    badge = '<span class="badge badge-sell">🟢 减仓/卖出</span>'
                else:
                    badge = '<span class="badge badge-hold">🟡 持有观望</span>'

                st.markdown(
                    f"""
                <div class="chat-msg-ai">
                    <div class="chat-msg-ai-avatar">S</div>
                    <div style="flex:1">
                        <div style="font-size:11px;color:#9ca3af;margin-bottom:6px">{data.get('stock_code','')} · AI综合分析 {badge}</div>
                """,
                    unsafe_allow_html=True,
                )

                t1, t2, t3, t4, t5 = st.tabs(
                    ["💼 决策", "📊 基本面", "📈 技术面", "📰 情绪", "🔬 辩论"]
                )
                with t1:
                    st.markdown(dtxt)
                with t2:
                    st.markdown(data.get("fundamental_report", "暂无"))
                with t3:
                    st.markdown(data.get("technical_report", "暂无"))
                with t4:
                    st.markdown(data.get("sentiment_report", "暂无"))
                with t5:
                    st.markdown(data.get("researcher_analysis", "暂无"))

                st.markdown("</div></div>", unsafe_allow_html=True)

            elif mtype == "error":
                st.markdown(
                    f"""
                <div class="chat-msg-ai">
                    <div class="chat-msg-ai-avatar">S</div>
                    <div class="chat-msg-ai-content" style="color:#dc2626">{msg["content"]}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            else:
                st.markdown(
                    f"""
                <div class="chat-msg-ai">
                    <div class="chat-msg-ai-avatar">S</div>
                    <div class="chat-msg-ai-content">{msg["content"]}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # 处理pending分析（快捷建议触发）
    if "_pending_code" in st.session_state:
        code = st.session_state.pop("_pending_code")
        with st.spinner(f"分析 {code} 中，约30-60秒..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/analyze", json={"stock_code": code}, timeout=300
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "type": "analysis",
                            "content": "",
                            "data": data,
                        }
                    )
                    st.session_state.history_list.append(
                        {
                            "code": code,
                            "decision": data.get("decision", ""),
                            "time": datetime.datetime.now().strftime("%H:%M"),
                        }
                    )
                else:
                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "type": "error",
                            "content": f"分析失败：{resp.json().get('detail','未知错误')}",
                        }
                    )
            except Exception as e:
                st.session_state.chat_messages.append(
                    {"role": "assistant", "type": "error", "content": f"请求失败：{e}"}
                )
        st.rerun()

    # 输入框
    st.markdown("<div style='height:20px'/>", unsafe_allow_html=True)
    col_input, col_btn = st.columns([6, 1])
    with col_input:
        user_input = st.text_input(
            "input",
            label_visibility="collapsed",
            placeholder="输入股票代码（如 600584）或问题...",
            key="chat_input",
        )
    with col_btn:
        send_btn = st.button("发送", key="send_btn", use_container_width=True)

    if send_btn and user_input.strip():
        msg = user_input.strip()
        st.session_state.chat_messages.append({"role": "user", "content": msg})

        # 提取股票代码（6位数字）
        import re

        codes = re.findall(r"\b\d{6}\b", msg)
        if codes:
            code = codes[0]
            st.session_state["_pending_code"] = code
        else:
            # 非股票代码问题，返回提示
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "type": "text",
                    "content": "请输入6位股票代码进行分析，例如：<b>分析 600584</b> 或直接输入 <b>600584</b>",
                }
            )
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# 量化回测
# ══════════════════════════════════════════════════════════════════════════
elif mode == "backtest":
    st.markdown("#### 量化回测")
    st.caption("Backtrader 引擎 · KDJ / RSI / 布林带多策略历史回测")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns([1.2, 1.4, 0.9, 0.9])
    with c1:
        code = st.text_input("股票代码", "600584", key="bt_code")
    with c2:
        strat = st.selectbox(
            "策略",
            ["kdj_oversold", "j_extreme", "rsi", "boll", "kdj_macd"],
            format_func=lambda x: {
                "kdj_oversold": "KDJ超卖",
                "j_extreme": "J极值",
                "rsi": "RSI超卖",
                "boll": "布林带",
                "kdj_macd": "KDJ+MACD",
            }[x],
        )
    with c3:
        sd = st.text_input("开始日期", "20240101")
    with c4:
        ed = st.text_input("结束日期", "20260530")

    if st.button("📊 开始回测"):
        with st.spinner("回测中..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/backtest",
                    json={
                        "stock_code": code,
                        "strategy": strat,
                        "start_date": sd,
                        "end_date": ed,
                        "initial_cash": 100000,
                    },
                    timeout=120,
                )
                if resp.status_code == 200:
                    st.session_state.bt_result = resp.json()
                    st.rerun()
                else:
                    st.error(f"回测失败：{resp.json().get('detail','未知')}")
            except Exception as e:
                st.error(f"请求失败：{e}")

    bt = st.session_state.bt_result
    if bt:
        tr = bt["total_return"]
        cols = st.columns(5)
        for col, (lbl, val, cls) in zip(
            cols,
            [
                ("总收益率", f"{tr:+.2f}%", "up" if tr > 0 else "down"),
                ("夏普比率", str(bt["sharpe"]), ""),
                ("最大回撤", f"-{bt['max_drawdown']:.2f}%", "down"),
                ("交易次数", str(bt["trade_count"]), ""),
                ("胜率", f"{bt['win_rate']}%", "up" if bt["win_rate"] > 50 else "down"),
            ],
        ):
            with col:
                st.markdown(
                    f'<div class="mini-metric"><div class="mini-metric-label">{lbl}</div><div class="mini-metric-value {cls}">{val}</div></div>',
                    unsafe_allow_html=True,
                )

        if bt.get("returns_data") and bt.get("dates_data"):
            cum = (
                (1 + pd.Series(bt["returns_data"], index=bt["dates_data"])).cumprod()
                - 1
            ) * 100
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=cum.index,
                    y=cum.values,
                    mode="lines",
                    line=dict(color="#d97706", width=1.8),
                    fill="tozeroy",
                    fillcolor="rgba(217,119,6,0.06)",
                )
            )
            fig.add_hline(y=0, line_dash="dot", line_color="#e5e7eb", line_width=1)
            fig.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(family="Inter", color="#6b7280", size=11),
                xaxis=dict(
                    gridcolor="#f9fafb", tickcolor="#e5e7eb", linecolor="#e5e7eb"
                ),
                yaxis=dict(gridcolor="#f9fafb", ticksuffix="%"),
                height=260,
                margin=dict(l=44, r=16, t=16, b=36),
                hovermode="x unified",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        if bt.get("trade_records"):
            df = pd.DataFrame(bt["trade_records"])
            buys = df[df["type"] == "买入"].reset_index(drop=True)
            sells = df[df["type"] == "卖出"].reset_index(drop=True)
            pairs = []
            for i in range(min(len(buys), len(sells))):
                bp, sp = buys.iloc[i]["price"], sells.iloc[i]["price"]
                pnl = (sp - bp) / bp * 100
                pairs.append(
                    {
                        "#": i + 1,
                        "买入日期": buys.iloc[i]["date"],
                        "买入价": f"¥{bp}",
                        "卖出日期": sells.iloc[i]["date"],
                        "卖出价": f"¥{sp}",
                        "盈亏": f"{pnl:+.2f}%",
                        "结果": "✓" if pnl > 0 else "✗",
                    }
                )
            if pairs:
                st.dataframe(
                    pd.DataFrame(pairs), use_container_width=True, hide_index=True
                )
        st.caption(bt.get("report_text", ""))
    else:
        st.markdown(
            '<div style="text-align:center;padding:60px;color:#9ca3af;font-size:14px">填写参数，点击「开始回测」</div>',
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════
# 今日买点
# ══════════════════════════════════════════════════════════════════════════
elif mode == "scan":
    st.markdown("#### 今日买点扫描")
    st.caption("全市场扫描 · KDJ超卖 + MA20趋势 · 4 Agent验证")
    st.markdown("---")
    st.info("💡 首次扫描约5分钟，此后约30秒（增量缓存）")

    c1, c2 = st.columns([2, 1])
    with c1:
        bs = st.text_input("数据起始日期", "20230101")
    with c2:
        tn = st.slider("最多显示", 5, 20, 10)

    if st.button("🎯 开始扫描"):
        with st.spinner("扫描中..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/scan/today",
                    json={"base_start": bs, "top_n": tn},
                    timeout=600,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    recs = data.get("recommendations", [])
                    st.success(
                        f"扫描完成 · 候选 {data['total_candidates']} 只 · 推荐 {data['count']} 只"
                    )
                    for r in recs:
                        icon = "🔴" if r["confidence"] == "高" else "🟡"
                        with st.expander(
                            f"{icon} {r['name']}（{r['code']}）— {r['decision']} · 置信度:{r['confidence']}"
                        ):
                            ca, cb = st.columns([1, 2])
                            with ca:
                                st.metric("当前价", f"¥{r['close']}")
                            with cb:
                                st.markdown(r["report"])
                else:
                    st.error(f"扫描失败：{resp.json().get('detail','未知')}")
            except Exception as e:
                st.error(f"扫描失败：{e}")

# ══════════════════════════════════════════════════════════════════════════
# 板块筛选
# ══════════════════════════════════════════════════════════════════════════
elif mode == "filter":
    st.markdown("#### 板块基本面筛选")
    st.caption("PE / ROE / 毛利率多维评分")
    st.markdown("---")

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        sector = st.selectbox("板块", list(SECTORS.keys()))
    with c2:
        min_score = st.slider("最低评分", 50, 90, 65)
    with c3:
        top_n = st.slider("显示数量", 3, 10, 5)

    if st.button("🔍 开始筛选"):
        try:
            stocks = SECTORS.get(sector, {})
            resp = requests.post(
                f"{API_BASE}/filter",
                json={
                    "sector": sector,
                    "stocks": stocks,
                    "min_score": min_score,
                    "top_n": top_n,
                },
                timeout=60,
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    df = pd.DataFrame(
                        [
                            {
                                "代码": r["code"],
                                "名称": r["name"],
                                "评分": r["score"],
                                "PE": f"{r['pe']:.1f}" if r.get("pe") else "N/A",
                                "ROE": f"{r['roe']:.1f}%" if r.get("roe") else "N/A",
                                "毛利率": (
                                    f"{r['gross_margin']:.1f}%"
                                    if r.get("gross_margin")
                                    else "N/A"
                                ),
                            }
                            for r in results
                        ]
                    )
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "评分": st.column_config.ProgressColumn(
                                "评分", min_value=0, max_value=100
                            )
                        },
                    )
                else:
                    st.warning("没有股票通过筛选条件")
            else:
                st.error(f"筛选失败")
        except Exception as e:
            st.error(f"筛选失败：{e}")
    else:
        st.markdown(
            '<div style="text-align:center;padding:60px;color:#9ca3af;font-size:14px">选择板块，点击「开始筛选」</div>',
            unsafe_allow_html=True,
        )
