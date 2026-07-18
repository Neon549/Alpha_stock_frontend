import streamlit as st
import requests
import re
import datetime
import pandas as pd
import plotly.graph_objects as go

API_BASE = "https://alphastock.cloud/api/v1"

st.set_page_config(
    page_title="AlphaStock",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_OPTIONS = {
    "fast": {"label": "快速", "desc": "DeepSeek V3", "icon": "⚡"},
    "smart": {"label": "精准", "desc": "DeepSeek R1", "icon": "🧠"},
    "strong": {"label": "强力", "desc": "R1 严格", "icon": "🔬"},
}

st.markdown(
    """
<style>
/* 字体覆盖但排除 Material 图标 */
*:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded):not(.material-symbols-outlined):not([class*="material-symbols"]):not(i){font-family:'Inter','PingFang SC',sans-serif;}
[data-testid="stIconMaterial"],.material-symbols-rounded,.material-symbols-outlined,[class*="material-symbols"]{font-family:'Material Symbols Rounded','Material Symbols Outlined'!important;}
#MainMenu,footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent!important;}
/* 展开按钮在stToolbar里，不能藏整个toolbar；只藏右侧动作菜单 */
[data-testid="stToolbarActions"],[data-testid="stMainMenu"]{visibility:hidden;}
[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapseButton"]{
    visibility:visible!important;display:flex!important;opacity:1!important;
}
.stApp,[data-testid="stAppViewContainer"]{background:#faf9f7!important;}
[data-testid="stSidebar"]{background:#f0eee9!important;border-right:1px solid #e5e2dc!important;}
[data-testid="stSidebar"] > div:first-child{padding-top:12px;}
/* 保护侧边栏折叠按钮，不被隐藏 */
[data-testid="stSidebarCollapseButton"]{display:flex!important;visibility:visible!important;}
button[kind="header"]{display:flex!important;visibility:visible!important;}

/* 主区域 */
.main .block-container{max-width:800px!important;padding:30px 20px 100px!important;}

/* 欢迎 */
.welcome{text-align:center;padding:100px 20px 30px;}
.welcome h1{font-size:26px;font-weight:600;color:#1a1a1a;letter-spacing:-.5px;margin-bottom:6px;}
.welcome p{font-size:13px;color:#9b9b93;}

/* 气泡 */
.bubble-u{display:flex;justify-content:flex-end;margin:8px 0 14px;}
.bubble-u div{background:#1a1a1a;color:white;border-radius:18px 18px 4px 18px;padding:10px 15px;max-width:62%;font-size:14px;line-height:1.6;}
.bubble-a{display:flex;gap:10px;margin:8px 0 18px;align-items:flex-start;}
.bubble-a .av{width:28px;height:28px;border-radius:50%;background:#1a1a1a;color:white;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;}
.bubble-a .txt{background:white;border:1px solid #ebe8e2;border-radius:4px 16px 16px 16px;padding:12px 16px;max-width:84%;font-size:14px;line-height:1.7;color:#1a1a1a;box-shadow:0 1px 3px rgba(0,0,0,.03);}
.badge{display:inline-flex;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600;}
.badge-buy{background:#fef2f2;color:#dc2626;border:1px solid #fecaca;}
.badge-hold{background:#fffbeb;color:#d97706;border:1px solid #fde68a;}
.badge-sell{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;}
.attach{display:inline-flex;gap:5px;padding:3px 9px;background:#f0f9ff;border:1px solid #bae6fd;border-radius:6px;font-size:11px;color:#0369a1;margin-bottom:5px;}

/* 侧栏元素 */
.sb-logo{display:flex;align-items:center;gap:8px;padding:4px 4px 12px;}
.sb-logo .ic{width:26px;height:26px;border-radius:7px;background:#1a1a1a;color:white;font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;}
.sb-logo .tx{font-size:15px;font-weight:600;color:#1a1a1a;}
.sb-user{background:white;border:1px solid #e5e2dc;border-radius:10px;padding:8px 10px;font-size:12px;color:#1a1a1a;margin-bottom:4px;}

/* chat_input 定制成Claude样式 */
[data-testid="stChatInput"]{background:white!important;border:1px solid #d8d4cc!important;border-radius:16px!important;box-shadow:0 2px 10px rgba(0,0,0,.06)!important;}
[data-testid="stChatInput"] textarea{font-size:14px!important;}
[data-testid="stChatInputSubmitButton"]{background:#e8490f!important;border-radius:50%!important;}

/* 按钮 */
.stButton>button{background:#f7f5f1!important;color:#3a3a3a!important;border:1px solid #e5e2dc!important;border-radius:8px!important;font-size:12px!important;font-weight:500!important;padding:6px 12px!important;}
.stButton>button:hover{background:#ebe8e2!important;}
.stTabs [data-baseweb="tab-list"]{border-bottom:1px solid #ebe8e2!important;}
.stTabs [data-baseweb="tab"]{color:#9b9b93!important;font-size:11px!important;padding:5px 12px!important;}
.stTabs [aria-selected="true"]{color:#1a1a1a!important;border-bottom:2px solid #1a1a1a!important;font-weight:600!important;}
/* label 只作用于非 select/slider 的场景 */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSlider"] label,
[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label,
[data-testid="stCaption"],
.stCaption{font-size:11px!important;color:#3a3a3a!important;}
/* selectbox 单独处理，保留原生样式 */
[data-testid="stSelectbox"] label{font-size:11px!important;color:#3a3a3a!important;}
[data-baseweb="select"]{border-radius:8px!important;}
[data-baseweb="select"] [data-baseweb="input"]{font-size:13px!important;}
[data-baseweb="popover"] li{font-size:13px!important;}
</style>
""",
    unsafe_allow_html=True,
)

# ── Session State ──────────────────────────────────────────────────────────
for k, v in {
    "conversations": {},
    "current_conv": None,
    "mode": "chat",
    "bt_result": None,
    "_pending": None,
    "model": "smart",
    "token": None,
    "username": None,
    "auth_page": "login",
    "up_file": None,
    "up_image": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

SECTORS = {
    "造船": {"600150": "中国船舶", "601989": "中国重工"},
    "CPO光模块": {"300308": "中际旭创", "002281": "光迅科技"},
    "AI算力": {"002261": "拓维信息", "688041": "海光信息"},
    "半导体": {"603501": "韦尔股份", "002371": "北方华创"},
    "军工": {"600760": "中航沈飞", "000768": "中航西飞"},
    "新能源": {"300750": "宁德时代", "002594": "比亚迪"},
    "有色金属": {"601899": "紫金矿业", "600362": "江西铜业"},
    "煤炭能源": {"601088": "中国神华", "601898": "中煤能源"},
}


def new_conv():
    cid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    st.session_state.conversations[cid] = {"title": "新对话", "messages": []}
    st.session_state.current_conv = cid
    st.session_state.mode = "chat"
    return cid


def get_msgs():
    cid = st.session_state.current_conv
    return (
        st.session_state.conversations.get(cid, {}).get("messages", []) if cid else []
    )


# ══════════════════════════════════════════════════════════════════════════
# 登录页（未登录时显示）
# ══════════════════════════════════════════════════════════════════════════
if not st.session_state.token:
    st.markdown(
        """
    <div style="text-align:center;padding:80px 20px 30px">
        <div style="width:56px;height:56px;border-radius:14px;background:#1a1a1a;color:white;
                    font-size:26px;font-weight:700;display:flex;align-items:center;justify-content:center;
                    margin:0 auto 16px">A</div>
        <div style="font-size:24px;font-weight:600;color:#1a1a1a">AlphaStock</div>
        <div style="font-size:13px;color:#9b9b93;margin-top:4px">智能投研助手 · 登录后开始使用</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        tab_login, tab_reg = st.tabs(["登录", "注册"])

        with tab_login:
            lu = st.text_input("用户名", key="login_user")
            lp = st.text_input("密码", type="password", key="login_pwd")
            if st.button("登录", use_container_width=True, key="do_login"):
                try:
                    r = requests.post(
                        f"{API_BASE}/auth/login",
                        json={"username": lu, "password": lp},
                        timeout=60,
                    )
                    if r.status_code == 200:
                        d = r.json()
                        st.session_state.token = d["token"]
                        st.session_state.username = d["username"]
                        st.rerun()
                    else:
                        st.error(r.json().get("detail", "登录失败"))
                except Exception as e:
                    st.error(f"连接失败：{e}")

        with tab_reg:
            ru = st.text_input("用户名", key="reg_user", help="至少2个字符")
            rp = st.text_input(
                "密码", type="password", key="reg_pwd", help="至少4个字符"
            )
            if st.button("注册", use_container_width=True, key="do_reg"):
                try:
                    r = requests.post(
                        f"{API_BASE}/auth/register",
                        json={"username": ru, "password": rp},
                        timeout=60,
                    )
                    if r.status_code == 200:
                        d = r.json()
                        st.session_state.token = d["token"]
                        st.session_state.username = d["username"]
                        st.rerun()
                    else:
                        st.error(r.json().get("detail", "注册失败"))
                except Exception as e:
                    st.error(f"连接失败：{e}")

    st.stop()  # 未登录时停在这里，不渲染主界面


# ══════════════════════════════════════════════════════════════════════════
# 已登录：主界面
# ══════════════════════════════════════════════════════════════════════════
try:
    backend_ok = requests.get(f"{API_BASE}/health", timeout=60).status_code == 200
except:
    backend_ok = False

# ── 侧栏 ──
with st.sidebar:
    st.markdown(
        """
    <div class="sb-logo"><div class="ic">A</div><div class="tx">AlphaStock</div></div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("＋　新对话", use_container_width=True, key="nc"):
        new_conv()
        st.rerun()

    # 模型选择
    st.caption("分析模型")
    mc1, mc2, mc3 = st.columns(3)
    for col, mk in zip([mc1, mc2, mc3], MODEL_OPTIONS.keys()):
        with col:
            mv = MODEL_OPTIONS[mk]
            is_cur = st.session_state.model == mk
            if st.button(
                f"{mv['icon']}",
                key=f"m_{mk}",
                use_container_width=True,
                help=f"{mv['label']} · {mv['desc']}",
            ):
                st.session_state.model = mk
                st.rerun()
    cur = MODEL_OPTIONS[st.session_state.model]
    st.markdown(
        f'<div style="font-size:11px;color:#9b9b93;text-align:center;margin:-4px 0 8px">{cur["icon"]} {cur["label"]} · {cur["desc"]}</div>',
        unsafe_allow_html=True,
    )

    st.caption("功能")
    for key, label in [
        ("chat", "💬 股票助手"),
        ("backtest", "📊 量化回测"),
        ("alpha", "🧮 Alpha选股"),
        ("scan", "🎯 今日买点"),
        ("filter", "🔍 板块筛选"),
    ]:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.mode = key
            st.rerun()

    st.caption("历史对话")
    convs = st.session_state.conversations
    if convs:
        for cid in sorted(convs.keys(), reverse=True)[:6]:
            if st.button(
                f"💬 {convs[cid]['title'][:14]}",
                key=f"h_{cid}",
                use_container_width=True,
            ):
                st.session_state.current_conv = cid
                st.session_state.mode = "chat"
                st.rerun()
    else:
        st.caption("暂无历史")

    # 底部：用户信息 + 登出
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        f'<div class="sb-user">👤 {st.session_state.username}</div>',
        unsafe_allow_html=True,
    )
    dot = "🟢 服务正常" if backend_ok else "🔴 服务异常"
    st.markdown(
        f'<div style="font-size:11px;color:#9b9b93;padding:2px 4px">{dot}</div>',
        unsafe_allow_html=True,
    )
    if st.button("登出", use_container_width=True, key="logout"):
        try:
            requests.post(
                f"{API_BASE}/auth/logout",
                json={"token": st.session_state.token},
                timeout=60,
            )
        except:
            pass
        st.session_state.token = None
        st.session_state.username = None
        st.rerun()

# ── 主区域 ──
mode = st.session_state.mode

if mode == "chat":
    msgs = get_msgs()
    if not msgs:
        st.markdown(
            """
        <div class="welcome">
            <h1>你好，我是 AlphaStock</h1>
            <p>输入股票代码开始分析，或上传财报截图</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        cc = st.columns(4)
        for col, (code, name) in zip(
            cc,
            [
                ("600150", "中国船舶"),
                ("300308", "中际旭创"),
                ("002261", "拓维信息"),
                ("601088", "中国神华"),
            ],
        ):
            with col:
                if st.button(
                    f"{code}\n{name}", key=f"chip_{code}", use_container_width=True
                ):
                    if not st.session_state.current_conv:
                        new_conv()
                    st.session_state._pending = code
                    st.rerun()

    # 渲染消息
    for m in msgs:
        if m["role"] == "user":
            pre = (
                f'<div class="attach">📎 {m.get("file_name","")}</div>'
                if m.get("has_file")
                else ""
            )
            st.markdown(
                f'{pre}<div class="bubble-u"><div>{m["content"]}</div></div>',
                unsafe_allow_html=True,
            )
        elif m["role"] == "assistant":
            if m.get("type") == "analysis":
                data = m.get("data", {})
                dtxt = data.get("decision", "")
                badge = (
                    '<span class="badge badge-buy">🔴 买入</span>'
                    if "买入" in dtxt
                    else (
                        '<span class="badge badge-sell">🟢 减仓</span>'
                        if ("减仓" in dtxt or "卖出" in dtxt)
                        else '<span class="badge badge-hold">🟡 观望</span>'
                    )
                )
                mi = MODEL_OPTIONS.get(m.get("model", "smart"), {})
                st.markdown(
                    f'<div class="bubble-a"><div class="av">A</div><div style="flex:1;min-width:0"><div style="font-size:10px;color:#9b9b93;margin-bottom:6px">{data.get("stock_code","")} &nbsp;{badge} &nbsp;<span style="padding:1px 6px;background:#f0eee9;border-radius:4px">{mi.get("icon","")} {mi.get("label","")}</span></div>',
                    unsafe_allow_html=True,
                )
                t1, t2, t3, t4, t5 = st.tabs(
                    ["💼 决策", "📊 基本面", "📈 技术面", "📰 情绪", "🔬 辩论"]
                )
                with t1:
                    st.markdown(dtxt or "暂无")
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
                    f'<div class="bubble-a"><div class="av">A</div><div class="txt">{m["content"]}</div></div>',
                    unsafe_allow_html=True,
                )

    # 处理待分析
    if st.session_state._pending:
        code = st.session_state._pending
        model = st.session_state.model
        st.session_state._pending = None
        if not st.session_state.current_conv:
            new_conv()
        cid = st.session_state.current_conv
        # 记录用户消息（如果还没记录）
        if not msgs or msgs[-1].get("content", "") != code:
            st.session_state.conversations[cid]["messages"].append(
                {"role": "user", "content": f"分析 {code}"}
            )
        with st.spinner(f"正在用「{MODEL_OPTIONS[model]['label']}」分析 {code}..."):
            try:
                r = requests.post(
                    f"{API_BASE}/analyze",
                    json={
                        "stock_code": code,
                        "model": model,
                        "token": st.session_state.token,
                    },
                    timeout=300,
                )
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.conversations[cid]["messages"].append(
                        {
                            "role": "assistant",
                            "type": "analysis",
                            "data": data,
                            "model": model,
                        }
                    )
                    d = data.get("decision", "")
                    act = "买入" if "买入" in d else ("减仓" if "减仓" in d else "观望")
                    st.session_state.conversations[cid]["title"] = f"{code}·{act}"
                else:
                    st.session_state.conversations[cid]["messages"].append(
                        {
                            "role": "assistant",
                            "type": "text",
                            "content": f"分析失败：{r.json().get('detail','重试')}",
                        }
                    )
            except Exception as e:
                st.session_state.conversations[cid]["messages"].append(
                    {"role": "assistant", "type": "text", "content": f"连接失败：{e}"}
                )
        st.rerun()

    # ── 多模态上传（+ 按钮）──
    with st.expander("📎 上传文件 / 图片", expanded=False):
        up_col1, up_col2 = st.columns(2)
        with up_col1:
            uploaded_img = st.file_uploader(
                "上传截图 / 财报图片",
                type=["png", "jpg", "jpeg", "webp"],
                key="uploader_img",
                label_visibility="collapsed",
            )
            if uploaded_img:
                st.session_state.up_image = uploaded_img
                st.image(uploaded_img, width=180)
                st.caption(f"📷 {uploaded_img.name}")
        with up_col2:
            uploaded_file = st.file_uploader(
                "上传 PDF / CSV",
                type=["pdf", "csv", "txt"],
                key="uploader_file",
                label_visibility="collapsed",
            )
            if uploaded_file:
                st.session_state.up_file = uploaded_file
                st.caption(f"📄 {uploaded_file.name} · 已就绪")
        if st.session_state.up_image or st.session_state.up_file:
            if st.button("🗑 清除附件", key="clear_attach"):
                st.session_state.up_image = None
                st.session_state.up_file = None
                st.rerun()

    # ── 原生chat_input（自动固定底部，Claude样式）──
    prompt = st.chat_input("输入股票代码（如 600150）或直接提问...")
    if prompt:
        if not st.session_state.current_conv:
            new_conv()
        cid = st.session_state.current_conv
        has_file = st.session_state.up_file is not None
        has_img = st.session_state.up_image is not None
        file_name = (
            st.session_state.up_image.name
            if has_img
            else (st.session_state.up_file.name if has_file else "")
        )
        st.session_state.conversations[cid]["messages"].append(
            {
                "role": "user",
                "content": prompt,
                "has_file": has_file or has_img,
                "file_name": file_name,
            }
        )
        # 发完清除附件
        st.session_state.up_file = None
        st.session_state.up_image = None
        codes = re.findall(r"\b\d{6}\b", prompt)
        if codes:
            st.session_state._pending = codes[0]
        else:
            st.session_state.conversations[cid]["messages"].append(
                {
                    "role": "assistant",
                    "type": "text",
                    "content": "请输入6位股票代码，例如 <b>600150</b>（中国船舶）",
                }
            )
        st.rerun()

elif mode == "backtest":
    st.markdown("### 量化回测")
    st.caption("KDJ / RSI / 布林带 · Backtrader")
    c1, c2, c3, c4 = st.columns([1.2, 1.5, 0.9, 0.9])
    with c1:
        code = st.text_input("股票代码", "600150")
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
                r = requests.post(
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
                if r.status_code == 200:
                    st.session_state.bt_result = r.json()
                    st.rerun()
                else:
                    st.error(f"回测失败：{r.json().get('detail','未知')}")
            except Exception as e:
                st.error(f"请求失败：{e}")
    bt = st.session_state.bt_result
    if bt:
        tr = bt["total_return"]
        cs = st.columns(5)
        for col, (l, v) in zip(
            cs,
            [
                ("总收益", f"{tr:+.2f}%"),
                ("夏普", str(bt["sharpe"])),
                ("回撤", f"-{bt['max_drawdown']:.2f}%"),
                ("交易", str(bt["trade_count"])),
                ("胜率", f"{bt['win_rate']}%"),
            ],
        ):
            with col:
                st.metric(l, v)
        if bt.get("returns_data") and bt.get("dates_data"):
            cum = (
                (1 + pd.Series(bt["returns_data"], index=bt["dates_data"])).cumprod()
                - 1
            ) * 100
            fig = go.Figure(
                go.Scatter(
                    x=cum.index,
                    y=cum.values,
                    mode="lines",
                    line=dict(color="#1a1a1a", width=1.6),
                    fill="tozeroy",
                    fillcolor="rgba(26,26,26,.04)",
                )
            )
            fig.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                height=220,
                margin=dict(l=44, r=16, t=8, b=32),
                showlegend=False,
                yaxis=dict(ticksuffix="%", gridcolor="#f5f5f3"),
                xaxis=dict(gridcolor="#f5f5f3"),
            )
            st.plotly_chart(fig, use_container_width=True)

elif mode == "alpha":
    st.markdown("### Alpha 因子选股")
    st.caption("五因子打分：KDJ · 成交量 · ROE · 市值 · 均线趋势 · 总分100")
    st.info("≥75分 ⭐⭐重点关注 · 60-74分 ⭐值得关注 · <60分 不推荐")
    ac1, ac2, ac3 = st.columns([2, 1, 1])
    with ac1:
        opts = ["全部（动态股票池）"] + list(SECTORS.keys())
        sector = st.selectbox("板块", opts)
    with ac2:
        ms = st.slider("最低分", 50, 90, 60)
    with ac3:
        tn = st.slider("数量", 5, 30, 15)
    if st.button("开始打分 →"):
        payload = {"min_score": ms, "top_n": tn}
        if sector != "全部（动态股票池）":
            payload["sector"] = sector
        with st.spinner("打分中（约2-5分钟）..."):
            try:
                r = requests.post(f"{API_BASE}/alpha/score", json=payload, timeout=600)
                if r.status_code == 200:
                    data = r.json()
                    results = data.get("results", [])
                    st.success(
                        f"完成 · {data['total_scored']}只 · {data['qualified']}只通过"
                    )
                    if results:
                        rows = []
                        for x in results:
                            f = x["factors"]
                            rows.append(
                                {
                                    "代码": x["stock_code"],
                                    "名称": x["stock_name"],
                                    "总分": x["total_score"],
                                    "评级": x["rating"],
                                    "KDJ": f["kdj"]["score"],
                                    "成交量": f["volume"]["score"],
                                    "ROE": f["roe"]["score"],
                                    "市值": f["market_cap"]["score"],
                                    "趋势": f["trend"]["score"],
                                }
                            )
                        st.dataframe(
                            pd.DataFrame(rows),
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "总分": st.column_config.ProgressColumn(
                                    "总分", min_value=0, max_value=100, format="%d"
                                )
                            },
                        )
                    else:
                        st.warning("无股票通过门槛")
                else:
                    st.error(f"失败：{r.json().get('detail','未知')}")
            except Exception as e:
                st.error(f"请求失败：{e}")

elif mode == "scan":
    st.markdown("### 今日买点")
    st.caption("全市场扫描 · KDJ超卖 · 市值≥300亿")
    sc1, sc2 = st.columns([2, 1])
    with sc1:
        bs = st.text_input("数据起始日期", "20230101")
    with sc2:
        tn = st.slider("最多显示", 5, 20, 10)
    if st.button("开始扫描 →"):
        with st.spinner("扫描中（约5分钟）..."):
            try:
                r = requests.post(
                    f"{API_BASE}/scan/today",
                    json={"base_start": bs, "top_n": tn},
                    timeout=600,
                )
                if r.status_code == 200:
                    data = r.json()
                    recs = data.get("recommendations", [])
                    st.success(
                        f"候选{data['total_candidates']}只 · 推荐{data['count']}只"
                    )
                    for x in recs:
                        ic = "🔴" if x["confidence"] == "高" else "🟡"
                        with st.expander(
                            f"{ic} {x['name']}（{x['code']}）— {x['decision']}"
                        ):
                            st.metric("当前价", f"¥{x['close']}")
                            st.markdown(x["report"])
                else:
                    st.error(f"扫描失败：{r.json().get('detail','未知')}")
            except Exception as e:
                st.error(f"扫描失败：{e}")

elif mode == "filter":
    st.markdown("### 板块筛选")
    st.caption("主题景气周期 · PE / ROE 多维评分")
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        sector = st.selectbox("板块", list(SECTORS.keys()))
    with fc2:
        ms = st.slider("最低评分", 50, 90, 65)
    with fc3:
        tn = st.slider("数量", 3, 10, 5)
    if st.button("开始筛选 →"):
        try:
            r = requests.post(
                f"{API_BASE}/filter",
                json={
                    "sector": sector,
                    "stocks": SECTORS.get(sector, {}),
                    "min_score": ms,
                    "top_n": tn,
                },
                timeout=60,
            )
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    df = pd.DataFrame(
                        [
                            {
                                "代码": x["code"],
                                "名称": x["name"],
                                "评分": x["score"],
                                "PE": f"{x['pe']:.1f}" if x.get("pe") else "N/A",
                                "ROE": f"{x['roe']:.1f}%" if x.get("roe") else "N/A",
                            }
                            for x in results
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
                    st.warning("无股票通过筛选")
            else:
                st.error("筛选失败")
        except Exception as e:
            st.error(f"筛选失败：{e}")
