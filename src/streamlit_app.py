import streamlit as st
import requests
import re
import datetime
import pandas as pd
import plotly.graph_objects as go

API_BASE = "https://neonzz-neon-stock-trading-agent.hf.space/api/v1"

st.set_page_config(
    page_title="StockMind",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif !important; box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

/* 全局背景 */
.stApp, [data-testid="stAppViewContainer"], .main { background: #f5f5f3 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── 整体布局容器 ── */
.app-layout {
    display: flex;
    height: 100vh;
    overflow: hidden;
}

/* ── 左侧栏 ── */
.left-panel {
    width: 240px;
    min-width: 240px;
    background: #f9f9f8;
    border-right: 1px solid #e5e5e3;
    display: flex;
    flex-direction: column;
    padding: 16px 10px;
    overflow-y: auto;
    height: 100vh;
}
.logo-row {
    display: flex; align-items: center; gap: 9px;
    padding: 4px 4px 16px; margin-bottom: 8px;
    border-bottom: 1px solid #e5e5e3;
}
.logo-icon {
    width: 28px; height: 28px; border-radius: 7px;
    background: linear-gradient(135deg, #d97706, #f59e0b);
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 13px; flex-shrink: 0;
}
.logo-text { font-size: 15px; font-weight: 600; color: #111827; letter-spacing: -0.3px; }

.nav-section-title {
    font-size: 10px; font-weight: 600; color: #aaa;
    text-transform: uppercase; letter-spacing: 0.08em;
    padding: 12px 4px 5px;
}
.nav-item {
    display: flex; align-items: center; gap: 8px;
    padding: 7px 10px; border-radius: 7px;
    font-size: 13px; color: #374151; cursor: pointer;
    margin-bottom: 1px; transition: background 0.1s;
    text-decoration: none;
}
.nav-item:hover { background: #efeeec; }
.nav-item.active { background: #fff8ed; color: #d97706; font-weight: 600; }

.hist-item {
    display: flex; align-items: center; gap: 7px;
    padding: 6px 10px; border-radius: 7px;
    font-size: 12px; color: #6b7280; cursor: pointer;
    margin-bottom: 1px;
}
.hist-item:hover { background: #efeeec; color: #374151; }
.hist-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

.status-pill {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 11px; padding: 3px 8px; border-radius: 20px;
    margin-top: auto; margin-bottom: 4px;
}
.status-online { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.status-offline { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

/* ── 右侧主内容 ── */
.right-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    height: 100vh;
}
.chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 40px 0 20px;
}
.chat-inner {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 24px;
}

/* 欢迎 */
.welcome { text-align: center; padding: 80px 20px 48px; }
.welcome-title { font-size: 26px; font-weight: 600; color: #111827; letter-spacing: -0.5px; margin-bottom: 8px; }
.welcome-sub { font-size: 14px; color: #9ca3af; }

/* 气泡 */
.bubble-user { display: flex; justify-content: flex-end; margin: 6px 0 14px; }
.bubble-user-inner {
    background: #111827; color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 16px; max-width: 68%;
    font-size: 14px; line-height: 1.6;
}
.bubble-ai { display: flex; gap: 10px; margin: 6px 0 20px; align-items: flex-start; }
.ai-avatar {
    width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg,#d97706,#f59e0b);
    display:flex; align-items:center; justify-content:center;
    color:white; font-weight:700; font-size:13px; margin-top:2px;
}
.bubble-ai-inner {
    background: white; border: 1px solid #e5e7eb;
    border-radius: 4px 18px 18px 18px;
    padding: 14px 18px; max-width: 86%;
    font-size: 14px; line-height: 1.7; color: #111827;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* 输入栏 */
.input-bar {
    border-top: 1px solid #e5e5e3;
    background: #f9f9f8;
    padding: 14px 24px 18px;
}
.input-bar-inner {
    max-width: 720px; margin: 0 auto;
    display: flex; gap: 10px; align-items: center;
}

/* badge */
.badge { display:inline-flex; align-items:center; padding:2px 9px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-buy { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.badge-sell { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.badge-hold { background:#fffbeb; color:#d97706; border:1px solid #fde68a; }

/* 回测区域 */
.page-area { flex:1; overflow-y:auto; padding:32px 40px; }
.page-title { font-size:20px; font-weight:600; color:#111827; margin-bottom:4px; letter-spacing:-0.4px; }
.page-sub { font-size:13px; color:#9ca3af; margin-bottom:24px; }

.mini-metric { background:white; border:1px solid #e5e7eb; border-radius:10px; padding:12px 14px; text-align:center; }
.mini-metric-label { font-size:10px; color:#9ca3af; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; }
.mini-metric-value { font-size:19px; font-weight:700; color:#111827; font-family:'JetBrains Mono',monospace; margin-top:3px; }
.mini-metric-value.up { color:#dc2626; }
.mini-metric-value.down { color:#10b981; }

/* Streamlit元素覆盖 */
.stTextInput > div > div > input {
    background: white !important; border: 1px solid #d1d5db !important;
    color: #111827 !important; border-radius: 24px !important;
    font-size: 14px !important; padding: 10px 20px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
}
.stTextInput > div > div > input:focus {
    border-color: #d97706 !important;
    box-shadow: 0 0 0 3px rgba(217,119,6,0.08) !important;
}
.stButton > button {
    background: #111827 !important; color: white !important;
    border: none !important; border-radius: 24px !important;
    font-weight: 600 !important; font-size: 13px !important;
    padding: 10px 22px !important;
}
.stButton > button:hover { background: #1f2937 !important; }
.stSelectbox > div > div { background:white !important; border:1px solid #d1d5db !important; border-radius:8px !important; }
.stTabs [data-baseweb="tab-list"] { background:transparent !important; border-bottom:1px solid #e5e7eb !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#6b7280 !important; font-size:12px !important; }
.stTabs [aria-selected="true"] { color:#d97706 !important; border-bottom:2px solid #d97706 !important; }
label { color:#374151 !important; font-size:12px !important; font-weight:500 !important; }
hr { border-color:#e5e7eb !important; margin:10px 0 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── 数据 ──────────────────────────────────────────────────────────────────
SECTORS = {
    "半导体": {"603650": "彤程新材", "002222": "福晶科技", "002549": "凯美特气"},
    "CPO光模块": {"300308": "中际旭创", "002281": "光迅科技"},
    "新能源": {"002709": "天赐材料", "603876": "鼎盛新材"},
    "消费电子": {"000725": "京东方A", "002049": "紫光国微"},
    "军工": {"600893": "航发动力", "600760": "中航沈飞"},
}

# ── Session State ─────────────────────────────────────────────────────────
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "current_conv" not in st.session_state:
    st.session_state.current_conv = None
if "mode" not in st.session_state:
    st.session_state.mode = "chat"
if "bt_result" not in st.session_state:
    st.session_state.bt_result = None
if "_pending_code" not in st.session_state:
    st.session_state._pending_code = None


def new_conv():
    cid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    st.session_state.conversations[cid] = {
        "title": "新对话",
        "messages": [],
        "time": datetime.datetime.now().strftime("%H:%M"),
    }
    st.session_state.current_conv = cid
    st.session_state.mode = "chat"
    return cid


def get_messages():
    cid = st.session_state.current_conv
    if cid and cid in st.session_state.conversations:
        return st.session_state.conversations[cid]["messages"]
    return []


# 后端状态
try:
    _r = requests.get(f"{API_BASE}/health", timeout=2)
    backend_ok = _r.status_code == 200
except:
    backend_ok = False

# ══════════════════════════════════════════════════════════════════════════
# 布局：左栏 + 右栏（用columns实现，sidebar完全弃用）
# ══════════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns([1.1, 4.5])

# ── 左栏 ──────────────────────────────────────────────────────────────────
with col_left:
    st.markdown(
        """
    <div class="logo-row">
        <div class="logo-icon">S</div>
        <div class="logo-text">StockMind</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("＋  新对话", key="btn_new", use_container_width=True):
        new_conv()
        st.rerun()

    st.markdown('<div class="nav-section-title">功能</div>', unsafe_allow_html=True)

    for nav_key, icon, label in [
        ("chat", "💬", "股票助手"),
        ("backtest", "📊", "量化回测"),
        ("scan", "🎯", "今日买点"),
        ("filter", "🔍", "板块筛选"),
    ]:
        active = "active" if st.session_state.mode == nav_key else ""
        st.markdown(
            f'<div class="nav-item {active}" id="nav_{nav_key}">{icon}&nbsp;&nbsp;{label}</div>',
            unsafe_allow_html=True,
        )
        if st.button(label, key=f"navbtn_{nav_key}", use_container_width=True):
            st.session_state.mode = nav_key
            st.rerun()

    st.markdown('<div class="nav-section-title">历史对话</div>', unsafe_allow_html=True)

    convs = st.session_state.conversations
    if convs:
        for cid in sorted(convs.keys(), reverse=True):
            c = convs[cid]
            is_cur = cid == st.session_state.current_conv
            title = c["title"][:16] + ("…" if len(c["title"]) > 16 else "")
            label_md = f"**{title}**" if is_cur else title
            if st.button(f"💬 {title}", key=f"conv_{cid}", use_container_width=True):
                st.session_state.current_conv = cid
                st.session_state.mode = "chat"
                st.rerun()
    else:
        st.markdown(
            '<div style="font-size:12px;color:#ccc;padding:4px">暂无历史对话</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='flex:1'/>", unsafe_allow_html=True)
    st.markdown("---")
    pill_cls = "status-online" if backend_ok else "status-offline"
    pill_txt = "● 服务正常" if backend_ok else "● 服务异常"
    st.markdown(
        f'<div class="status-pill {pill_cls}">{pill_txt}</div>', unsafe_allow_html=True
    )

# ── 右栏 ──────────────────────────────────────────────────────────────────
with col_right:
    mode = st.session_state.mode

    # ── 股票助手 ──
    if mode == "chat":
        messages = get_messages()

        if not messages:
            st.markdown(
                """
            <div class="welcome">
                <div class="welcome-title">欢迎使用 StockMind</div>
                <div class="welcome-sub">你的 A 股智能分析助手，输入股票代码即可开始</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # 渲染对话历史
        for msg in messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="bubble-user"><div class="bubble-user-inner">{msg["content"]}</div></div>',
                    unsafe_allow_html=True,
                )
            elif msg["role"] == "assistant":
                mtype = msg.get("type", "text")
                if mtype == "analysis":
                    data = msg.get("data", {})
                    dtxt = data.get("decision", "")
                    if "买入" in dtxt:
                        badge = '<span class="badge badge-buy">🔴 买入</span>'
                    elif "卖出" in dtxt or "减仓" in dtxt:
                        badge = '<span class="badge badge-sell">🟢 减仓</span>'
                    else:
                        badge = '<span class="badge badge-hold">🟡 观望</span>'

                    st.markdown(
                        f"""
                    <div class="bubble-ai">
                        <div class="ai-avatar">S</div>
                        <div style="flex:1;min-width:0">
                            <div style="font-size:11px;color:#9ca3af;margin-bottom:8px">{data.get('stock_code','')} &nbsp;{badge}</div>
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
                else:
                    st.markdown(
                        f'<div class="bubble-ai"><div class="ai-avatar">S</div><div class="bubble-ai-inner">{msg["content"]}</div></div>',
                        unsafe_allow_html=True,
                    )

        # 处理待分析
        if st.session_state._pending_code:
            code = st.session_state._pending_code
            st.session_state._pending_code = None
            with st.spinner(f"正在分析 {code}，约30-90秒..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/analyze", json={"stock_code": code}, timeout=300
                    )
                    cid = st.session_state.current_conv
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.conversations[cid]["messages"].append(
                            {
                                "role": "assistant",
                                "type": "analysis",
                                "content": "",
                                "data": data,
                            }
                        )
                        d = data.get("decision", "")
                        action = (
                            "买入"
                            if "买入" in d
                            else ("减仓" if ("减仓" in d or "卖出" in d) else "观望")
                        )
                        st.session_state.conversations[cid][
                            "title"
                        ] = f"{code} · {action}"
                    else:
                        st.session_state.conversations[cid]["messages"].append(
                            {
                                "role": "assistant",
                                "type": "text",
                                "content": f"分析失败：{resp.json().get('detail','请稍后重试')}",
                            }
                        )
                except Exception as e:
                    cid = st.session_state.current_conv
                    st.session_state.conversations[cid]["messages"].append(
                        {
                            "role": "assistant",
                            "type": "text",
                            "content": f"连接失败：{e}",
                        }
                    )
            st.rerun()

        # 输入框
        st.markdown("<div style='height:20px'/>", unsafe_allow_html=True)
        inp_col, btn_col = st.columns([5, 1])
        with inp_col:
            user_input = st.text_input(
                "msg",
                label_visibility="collapsed",
                placeholder="输入股票代码（如 600584）或直接提问...",
                key="chat_input",
            )
        with btn_col:
            send = st.button("发送 →", key="send_btn", use_container_width=True)

        if send and user_input.strip():
            txt = user_input.strip()
            if not st.session_state.current_conv:
                new_conv()
            cid = st.session_state.current_conv
            st.session_state.conversations[cid]["messages"].append(
                {"role": "user", "content": txt}
            )
            codes = re.findall(r"\b\d{6}\b", txt)
            if codes:
                st.session_state._pending_code = codes[0]
            else:
                st.session_state.conversations[cid]["messages"].append(
                    {
                        "role": "assistant",
                        "type": "text",
                        "content": "请输入6位股票代码进行分析，例如 <b>600584</b>（长电科技）",
                    }
                )
            st.rerun()

    # ── 量化回测 ──
    elif mode == "backtest":
        st.markdown('<div class="page-title">量化回测</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">Backtrader 引擎 · KDJ / RSI / 布林带多策略历史回测</div>',
            unsafe_allow_html=True,
        )

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
            sd = st.text_input("开始", "20240101")
        with c4:
            ed = st.text_input("结束", "20260530")

        if st.button("开始回测 →"):
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
                    (
                        "胜率",
                        f"{bt['win_rate']}%",
                        "up" if bt["win_rate"] > 50 else "down",
                    ),
                ],
            ):
                with col:
                    st.markdown(
                        f'<div class="mini-metric"><div class="mini-metric-label">{lbl}</div><div class="mini-metric-value {cls}">{val}</div></div>',
                        unsafe_allow_html=True,
                    )

            if bt.get("returns_data") and bt.get("dates_data"):
                cum = (
                    (
                        1 + pd.Series(bt["returns_data"], index=bt["dates_data"])
                    ).cumprod()
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
                fig.add_hline(y=0, line_dash="dot", line_color="#e5e7eb")
                fig.update_layout(
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    font=dict(family="Inter", color="#6b7280", size=11),
                    xaxis=dict(gridcolor="#f9fafb", linecolor="#e5e7eb"),
                    yaxis=dict(
                        gridcolor="#f9fafb", ticksuffix="%", linecolor="#e5e7eb"
                    ),
                    height=240,
                    margin=dict(l=44, r=16, t=12, b=36),
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
                            "买入": buys.iloc[i]["date"],
                            f"买入价": f"¥{bp}",
                            "卖出": sells.iloc[i]["date"],
                            "卖出价": f"¥{sp}",
                            "盈亏": f"{pnl:+.2f}%",
                            "": ("✓" if pnl > 0 else "✗"),
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

    # ── 今日买点 ──
    elif mode == "scan":
        st.markdown('<div class="page-title">今日买点</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">全市场扫描 · KDJ超卖 + MA20趋势 · Agent验证</div>',
            unsafe_allow_html=True,
        )
        st.info("首次扫描约5分钟，之后约30秒（增量缓存）")

        c1, c2 = st.columns([2, 1])
        with c1:
            bs = st.text_input("数据起始日期", "20230101")
        with c2:
            tn = st.slider("最多显示", 5, 20, 10)

        if st.button("开始扫描 →"):
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

    # ── 板块筛选 ──
    elif mode == "filter":
        st.markdown('<div class="page-title">板块筛选</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">PE / ROE / 毛利率多维评分</div>',
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sector = st.selectbox("板块", list(SECTORS.keys()))
        with c2:
            min_score = st.slider("最低评分", 50, 90, 65)
        with c3:
            top_n = st.slider("数量", 3, 10, 5)

        if st.button("开始筛选 →"):
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
                                    "ROE": (
                                        f"{r['roe']:.1f}%" if r.get("roe") else "N/A"
                                    ),
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
                    st.error("筛选失败")
            except Exception as e:
                st.error(f"筛选失败：{e}")
        else:
            st.markdown(
                '<div style="text-align:center;padding:60px;color:#9ca3af;font-size:14px">选择板块，点击「开始筛选」</div>',
                unsafe_allow_html=True,
            )
