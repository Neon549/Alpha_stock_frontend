import streamlit as st
import requests
import time
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

/* 隐藏默认顶栏 */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 24px !important; padding-bottom: 40px !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #f9f9f8 !important;
    border-right: 1px solid #e8e8e5 !important;
    width: 260px !important;
}
[data-testid="stSidebar"] .block-container { padding: 16px 12px !important; }

/* sidebar logo区域 */
.sidebar-logo {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 4px 20px;
    border-bottom: 1px solid #e8e8e5;
    margin-bottom: 16px;
}
.sidebar-logo-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; color: white; font-weight: 700;
}
.sidebar-logo-name { font-size: 16px; font-weight: 600; color: #1a1a1a; letter-spacing: -0.3px; }

/* sidebar section标题 */
.sidebar-section { font-size: 10px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.08em; padding: 12px 4px 6px; }

/* sidebar nav item */
.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 10px; border-radius: 8px;
    font-size: 13px; font-weight: 500; color: #374151;
    cursor: pointer; margin-bottom: 2px;
    transition: background 0.12s;
}
.nav-item:hover { background: #f0f0ec; }
.nav-item.active { background: #fff8ed; color: #d97706; font-weight: 600; }
.nav-item-icon { font-size: 15px; width: 20px; text-align: center; }

/* 历史记录条目 */
.hist-item {
    display: flex; align-items: center; gap: 8px;
    padding: 7px 10px; border-radius: 7px;
    font-size: 12px; color: #6b7280; cursor: pointer;
    margin-bottom: 1px;
}
.hist-item:hover { background: #f0f0ec; color: #374151; }
.hist-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.hist-dot.buy { background: #ef4444; }
.hist-dot.sell { background: #10b981; }
.hist-dot.hold { background: #f59e0b; }

/* status badge */
.status-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 8px; border-radius: 20px;
    font-size: 11px; font-weight: 500;
    background: #f0fdf4; color: #16a34a;
    border: 1px solid #bbf7d0;
    margin-top: 8px;
}
.status-badge.offline { background: #fef2f2; color: #dc2626; border-color: #fecaca; }
.status-dot-sm { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }

/* ── 主区域 ── */
.main-hero {
    text-align: center;
    padding: 48px 20px 40px;
    max-width: 600px;
    margin: 0 auto;
}
.main-hero-title {
    font-size: 28px; font-weight: 700; color: #111827;
    letter-spacing: -0.8px; margin-bottom: 10px;
}
.main-hero-title span { color: #d97706; }
.main-hero-desc { font-size: 14px; color: #6b7280; line-height: 1.6; margin-bottom: 32px; }

/* 功能卡片 */
.feature-cards { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 40px; }
.feature-card {
    background: white; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 16px 20px;
    text-align: left; width: 160px;
    cursor: pointer; transition: all 0.15s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.feature-card:hover { border-color: #d97706; box-shadow: 0 4px 12px rgba(217,119,6,0.1); transform: translateY(-1px); }
.feature-card-icon { font-size: 22px; margin-bottom: 8px; }
.feature-card-title { font-size: 13px; font-weight: 600; color: #111827; margin-bottom: 3px; }
.feature-card-desc { font-size: 11px; color: #9ca3af; }

/* 分析面板 */
.analysis-panel {
    background: white; border: 1px solid #e5e7eb;
    border-radius: 14px; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}
.analysis-panel-header {
    padding: 14px 20px; border-bottom: 1px solid #f3f4f6;
    display: flex; align-items: center; justify-content: space-between;
    background: #fafaf9;
}
.analysis-panel-title { font-size: 13px; font-weight: 600; color: #374151; display: flex; align-items: center; gap: 8px; }
.analysis-panel-body { padding: 20px; }

/* 决策badge */
.decision-badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-buy { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.badge-sell { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.badge-hold { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }

/* Agent步骤 */
.agent-step { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f9fafb; }
.agent-step:last-child { border-bottom: none; }
.agent-step-icon { width: 32px; height: 32px; border-radius: 8px; background: #f3f4f6; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; margin-top: 1px; }
.agent-step-icon.active { background: #fff8ed; }
.agent-step-name { font-size: 13px; font-weight: 500; color: #374151; }
.agent-step-name.active { color: #111827; }
.agent-step-sub { font-size: 11px; color: #9ca3af; margin-top: 1px; }
.agent-step-status { font-size: 11px; color: #d1d5db; margin-left: auto; padding-top: 2px; }
.agent-step-status.done { color: #10b981; }

/* 指标卡 */
.metric-row { display: flex; gap: 10px; margin-bottom: 16px; }
.metric-card { flex: 1; background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; }
.metric-label { font-size: 10px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 5px; }
.metric-value { font-size: 20px; font-weight: 700; color: #111827; font-family: 'JetBrains Mono', monospace; }
.metric-value.up { color: #dc2626; }
.metric-value.down { color: #10b981; }

/* 空状态 */
.empty-state { text-align: center; padding: 48px 20px; }
.empty-icon { font-size: 36px; margin-bottom: 12px; opacity: 0.25; }
.empty-text { font-size: 14px; color: #9ca3af; line-height: 1.6; }

/* 输入框、按钮覆盖 */
.stTextInput > div > div > input {
    background: white !important; border: 1px solid #d1d5db !important;
    color: #111827 !important; border-radius: 8px !important;
    font-size: 13px !important; padding: 8px 12px !important;
}
.stTextInput > div > div > input:focus { border-color: #d97706 !important; box-shadow: 0 0 0 3px rgba(217,119,6,0.1) !important; }

.stSelectbox > div > div { background: white !important; border: 1px solid #d1d5db !important; border-radius: 8px !important; color: #111827 !important; }

.stButton > button {
    background: #111827 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 13px !important;
    transition: background 0.15s !important;
}
.stButton > button:hover { background: #1f2937 !important; }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #e5e7eb !important; gap: 0 !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #6b7280 !important; font-size: 12px !important; font-weight: 500 !important; padding: 8px 14px !important; }
.stTabs [aria-selected="true"] { color: #d97706 !important; border-bottom: 2px solid #d97706 !important; }

label { color: #374151 !important; font-size: 12px !important; font-weight: 500 !important; }
hr { border-color: #f3f4f6 !important; }
.stApp { background: #f5f5f3 !important; }
[data-testid="stAppViewContainer"] { background: #f5f5f3 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── 板块数据（hardcode，不依赖后端） ──────────────────────────────────────
SECTORS = {
    "半导体": {
        "603650": "彤程新材",
        "002222": "福晶科技",
        "002549": "凯美特气",
        "688012": "中微公司",
    },
    "CPO光模块": {"300308": "中际旭创", "002281": "光迅科技", "300281": "金信诺"},
    "新能源": {"002709": "天赐材料", "603876": "鼎盛新材", "300750": "宁德时代"},
    "消费电子": {"000725": "京东方A", "002049": "紫光国微"},
    "军工": {"600893": "航发动力", "600760": "中航沈飞"},
    "自定义": {},
}

# ── Session State ─────────────────────────────────────────────────────────
for k, v in {
    "active_mode": "home",
    "selected_code": "",
    "analysis_result": None,
    "backtest_result": None,
    "history_list": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── 后端状态检测 ──────────────────────────────────────────────────────────
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
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">S</div>
        <div class="sidebar-logo-name">StockMind</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 导航
    st.markdown('<div class="sidebar-section">功能</div>', unsafe_allow_html=True)

    nav_items = [
        ("home", "🏠", "主页"),
        ("ai", "🤖", "AI 智能分析"),
        ("backtest", "📊", "量化回测"),
        ("scan", "🎯", "今日买点"),
        ("filter", "🔍", "板块筛选"),
    ]
    for key, icon, label in nav_items:
        active = "active" if st.session_state.active_mode == key else ""
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.active_mode = key
            st.rerun()

    st.markdown("---")

    # 后端状态
    if backend_ok:
        st.markdown(
            '<div class="status-badge"><span class="status-dot-sm"></span>后端在线</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-badge offline"><span class="status-dot-sm"></span>后端离线</div>',
            unsafe_allow_html=True,
        )

    # 历史记录
    if st.session_state.history_list:
        st.markdown(
            '<div class="sidebar-section">最近分析</div>', unsafe_allow_html=True
        )
        for item in st.session_state.history_list[-8:][::-1]:
            decision = item.get("decision", "")
            dot = (
                "buy"
                if "买入" in decision
                else ("sell" if "卖出" in decision or "减仓" in decision else "hold")
            )
            st.markdown(
                f"""
            <div class="hist-item">
                <div class="hist-dot {dot}"></div>
                <span>{item['code']}</span>
                <span style="margin-left:auto;color:#d1d5db;font-size:11px">{item.get('time','')}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

mode = st.session_state.active_mode

# ══════════════════════════════════════════════════════════════════════════
# 主页
# ══════════════════════════════════════════════════════════════════════════
if mode == "home":
    st.markdown(
        """
    <div class="main-hero">
        <div class="main-hero-title">你好，<span>开始分析</span></div>
        <div class="main-hero-desc">
            基于 LangGraph Multi-Agent 工作流<br>
            综合基本面 · 技术面 · 情绪面，给出专业A股交易决策
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, (key, icon, title, desc) in zip(
        [c1, c2, c3, c4],
        [
            ("ai", "🤖", "AI 分析", "多Agent协同分析"),
            ("backtest", "📊", "量化回测", "KDJ/RSI策略验证"),
            ("scan", "🎯", "今日买点", "全市场买点扫描"),
            ("filter", "🔍", "板块筛选", "基本面多维评分"),
        ],
    ):
        with col:
            if st.button(
                f"{icon}\n\n**{title}**\n\n{desc}",
                key=f"home_{key}",
                use_container_width=True,
            ):
                st.session_state.active_mode = key
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# AI 分析
# ══════════════════════════════════════════════════════════════════════════
elif mode == "ai":
    left, right = st.columns([1, 2.2])

    with left:
        st.markdown("#### 分析设置")

        sector = st.selectbox("板块", list(SECTORS.keys()))
        stocks = SECTORS.get(sector, {})
        opts = {"— 自定义输入 —": ""} | {f"{n}（{c}）": c for c, n in stocks.items()}
        sel = st.selectbox("快速选股", list(opts.keys()))
        if sel != "— 自定义输入 —" and opts[sel]:
            st.session_state.selected_code = opts[sel]

        code = st.text_input(
            "股票代码", value=st.session_state.selected_code, placeholder="如 600584"
        )
        st.session_state.selected_code = code

        analyze_btn = st.button("🚀 开始AI分析", use_container_width=True)
        history_btn = st.button("📋 查看历史决策", use_container_width=True)

        st.markdown("---")

        # Agent工作流面板
        st.markdown("**Agent 工作流**")
        done = st.session_state.analysis_result is not None
        for icon, name, sub in [
            ("📊", "基本面分析师", "财务数据 · 估值"),
            ("📈", "技术面分析师", "KDJ · MACD"),
            ("📰", "情绪分析师", "新闻 · RAG"),
            ("🔬", "研究员", "多空辩论"),
            ("💼", "交易员", "最终决策"),
        ]:
            ac = "active" if done else ""
            st.markdown(
                f"""
            <div class="agent-step">
                <div class="agent-step-icon {ac}">{icon}</div>
                <div style="flex:1">
                    <div class="agent-step-name {ac}">{name}</div>
                    <div class="agent-step-sub">{sub}</div>
                </div>
                <div class="agent-step-status {'done' if done else ''}">{'✓' if done else '·'}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with right:
        if analyze_btn and code:
            st.session_state.analysis_result = None
            prog = st.progress(0)
            ph = st.empty()
            for i, s in enumerate(
                ["基本面分析", "技术面分析", "情绪分析", "研究员辩论", "交易员决策"]
            ):
                ph.caption(f"⏳ {s}中...")
                prog.progress((i + 1) / 5 * 0.8)
                time.sleep(0.3)
            ph.caption("🤖 AI综合分析中，约30-90秒...")
            try:
                resp = requests.post(
                    f"{API_BASE}/analyze", json={"stock_code": code}, timeout=300
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.analysis_result = data
                    prog.progress(1.0)
                    ph.caption("✅ 分析完成")
                    # 记录历史
                    import datetime

                    st.session_state.history_list.append(
                        {
                            "code": code,
                            "decision": data.get("decision", ""),
                            "time": datetime.datetime.now().strftime("%H:%M"),
                        }
                    )
                    st.rerun()
                else:
                    st.error(f"分析失败：{resp.json().get('detail','未知错误')}")
            except Exception as e:
                st.error(f"请求失败：{e}")

        if history_btn and code:
            try:
                r = requests.get(f"{API_BASE}/history/{code}", timeout=10)
                if r.status_code == 200:
                    hist = r.json().get("history", "暂无历史记录")
                    with st.expander(f"📋 {code} 历史决策", expanded=True):
                        st.text(hist)
            except Exception as e:
                st.error(f"获取失败：{e}")

        result = st.session_state.analysis_result
        if result:
            dtxt = result.get("decision", "")
            if "买入" in dtxt:
                badge = '<span class="decision-badge badge-buy">🔴 买入信号</span>'
            elif "卖出" in dtxt or "减仓" in dtxt:
                badge = '<span class="decision-badge badge-sell">🟢 减仓/卖出</span>'
            else:
                badge = '<span class="decision-badge badge-hold">🟡 持有观望</span>'

            st.markdown(
                f"""
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
                <span style="font-size:16px;font-weight:700;color:#111827">{result['stock_code']} · 分析结果</span>
                {badge}
            </div>
            """,
                unsafe_allow_html=True,
            )

            t1, t2, t3, t4, t5 = st.tabs(
                ["💼 最终决策", "📊 基本面", "📈 技术面", "📰 情绪", "🔬 多空辩论"]
            )
            with t1:
                st.markdown(dtxt)
            with t2:
                st.markdown(result.get("fundamental_report", "暂无"))
            with t3:
                st.markdown(result.get("technical_report", "暂无"))
            with t4:
                st.markdown(result.get("sentiment_report", "暂无"))
            with t5:
                st.markdown(result.get("researcher_analysis", "暂无"))

        elif not analyze_btn:
            st.markdown(
                """
            <div class="empty-state">
                <div class="empty-icon">📈</div>
                <div class="empty-text">从左侧选择股票<br>点击「开始AI分析」</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════════
# 量化回测
# ══════════════════════════════════════════════════════════════════════════
elif mode == "backtest":
    st.markdown("#### 量化回测")
    st.caption("Backtrader 引擎 · KDJ / RSI / 布林带多策略历史回测")

    c1, c2, c3, c4 = st.columns([1.2, 1.3, 0.9, 0.9])
    with c1:
        code = st.text_input(
            "股票代码", value=st.session_state.selected_code or "600584", key="bt_code"
        )
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

    if st.button("📊 开始回测", use_container_width=False):
        with st.spinner("回测计算中..."):
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
                    st.session_state.backtest_result = resp.json()
                    st.rerun()
                else:
                    st.error(f"回测失败：{resp.json().get('detail','未知')}")
            except Exception as e:
                st.error(f"请求失败：{e}")

    bt = st.session_state.backtest_result
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
                    f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value {cls}">{val}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:12px'/>", unsafe_allow_html=True)

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
                yaxis=dict(
                    gridcolor="#f9fafb",
                    ticksuffix="%",
                    tickcolor="#e5e7eb",
                    linecolor="#e5e7eb",
                ),
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
                        "买入": buys.iloc[i]["date"],
                        "买入价": f"¥{bp}",
                        "卖出": sells.iloc[i]["date"],
                        "卖出价": f"¥{sp}",
                        "盈亏": f"{pnl:+.2f}%",
                        "": "✓" if pnl > 0 else "✗",
                    }
                )
            if pairs:
                st.dataframe(
                    pd.DataFrame(pairs), use_container_width=True, hide_index=True
                )
        st.caption(bt.get("report_text", ""))
    else:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">📊</div><div class="empty-text">输入股票代码和策略参数<br>点击「开始回测」</div></div>',
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════
# 今日买点
# ══════════════════════════════════════════════════════════════════════════
elif mode == "scan":
    st.markdown("#### 今日买点扫描")
    st.caption("全市场扫描 · KDJ超卖 + MA20趋势过滤 · 4 Agent二次验证")

    c1, c2, c3 = st.columns([1.5, 1, 0.8])
    with c1:
        bs = st.text_input("数据起始日期", "20230101")
    with c2:
        tn = st.slider("最多显示", 5, 20, 10)
    with c3:
        st.markdown("<div style='height:26px'/>", unsafe_allow_html=True)
        scan_btn = st.button("🎯 开始扫描")

    st.info("💡 首次扫描约5分钟（拉取历史数据），此后约30秒（增量更新缓存）")

    if scan_btn:
        with st.spinner("全市场扫描中..."):
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
    st.caption("PE / ROE / 毛利率多维度评分 · 快速锁定优质标的")

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        sector = st.selectbox("选择板块", list(SECTORS.keys()))
    with c2:
        min_score = st.slider("最低评分", 50, 90, 65)
    with c3:
        top_n = st.slider("显示数量", 3, 10, 5)

    if st.button("🔍 开始筛选"):
        try:
            stocks = SECTORS.get(sector, {})
            payload = {
                "sector": sector,
                "stocks": stocks,
                "min_score": min_score,
                "top_n": top_n,
            }
            resp = requests.post(f"{API_BASE}/filter", json=payload, timeout=60)
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
                st.error(f"筛选失败：{resp.json().get('detail','未知')}")
        except Exception as e:
            st.error(f"筛选失败：{e}")
    else:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">🔍</div><div class="empty-text">选择板块，点击「开始筛选」</div></div>',
            unsafe_allow_html=True,
        )
