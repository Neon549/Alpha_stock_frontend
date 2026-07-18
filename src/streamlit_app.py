import streamlit as st
import requests
import re
import datetime
import pandas as pd
import plotly.graph_objects as go
import base64

API_BASE = "https://neonzz-neon-stock-trading-agent.hf.space/api/v1"

st.set_page_config(
    page_title="AlphaStock",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 模型配置 ──────────────────────────────────────────────────────────────
MODEL_OPTIONS = {
    "fast": {"label": "快速", "desc": "DeepSeek V3 · 适合选股筛选", "icon": "⚡"},
    "smart": {"label": "精准", "desc": "DeepSeek R1 · 适合深度分析", "icon": "🧠"},
    "strong": {"label": "强力", "desc": "R1 + 多轮验证 · 适合量化回测", "icon": "🔬"},
}

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', 'PingFang SC', sans-serif !important; box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

.stApp, [data-testid="stAppViewContainer"], .main { background: #f5f5f3 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* 左栏 */
.logo-row { display:flex; align-items:center; gap:8px; padding:0 4px 14px; margin-bottom:6px; border-bottom:1px solid #e5e5e3; }
.logo-icon { width:26px; height:26px; border-radius:6px; background:linear-gradient(135deg,#1a1a1a,#333); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:12px; flex-shrink:0; }
.logo-text { font-size:14px; font-weight:600; color:#111; letter-spacing:-0.3px; }

.nav-section-title { font-size:10px; font-weight:600; color:#bbb; text-transform:uppercase; letter-spacing:0.08em; padding:10px 4px 4px; }

/* 模型选择器 */
.model-selector { background:white; border:1px solid #e5e7eb; border-radius:8px; padding:8px; margin:8px 0; }
.model-selector-label { font-size:10px; font-weight:600; color:#9ca3af; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px; }
.model-btn { display:flex; align-items:center; gap:6px; padding:6px 8px; border-radius:6px; cursor:pointer; margin-bottom:2px; transition:background 0.1s; }
.model-btn:hover { background:#f9fafb; }
.model-btn.active { background:#f0f9ff; border:1px solid #bae6fd; }
.model-icon { font-size:14px; }
.model-info { flex:1; }
.model-name { font-size:12px; font-weight:600; color:#111; }
.model-desc { font-size:10px; color:#9ca3af; margin-top:1px; }
.model-check { color:#0ea5e9; font-size:12px; }

/* 输入栏 */
.input-wrapper { border-top:1px solid #e5e5e3; background:#f9f9f8; padding:10px 20px 14px; }
.input-box { background:white; border:1px solid #d1d5db; border-radius:12px; padding:10px 14px; box-shadow:0 1px 4px rgba(0,0,0,0.06); }
.input-toolbar { display:flex; align-items:center; gap:6px; margin-top:8px; }
.toolbar-btn { display:flex; align-items:center; gap:4px; padding:4px 10px; border-radius:20px; border:1px solid #e5e7eb; background:white; font-size:11px; color:#6b7280; cursor:pointer; }
.toolbar-btn:hover { background:#f9fafb; color:#374151; }
.model-pill { display:flex; align-items:center; gap:4px; padding:3px 8px; border-radius:20px; background:#f0f9ff; border:1px solid #bae6fd; font-size:11px; color:#0369a1; font-weight:500; }

/* 气泡 */
.bubble-user { display:flex; justify-content:flex-end; margin:6px 0 12px; }
.bubble-user-inner { background:#111; color:white; border-radius:16px 16px 3px 16px; padding:9px 14px; max-width:65%; font-size:13px; line-height:1.6; }
.bubble-ai { display:flex; gap:9px; margin:6px 0 18px; align-items:flex-start; }
.ai-avatar { width:26px; height:26px; border-radius:50%; flex-shrink:0; background:linear-gradient(135deg,#1a1a1a,#333); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:11px; margin-top:2px; }
.bubble-ai-inner { background:white; border:1px solid #e5e7eb; border-radius:3px 16px 16px 16px; padding:12px 16px; max-width:84%; font-size:13px; line-height:1.7; color:#111; box-shadow:0 1px 3px rgba(0,0,0,0.04); }

/* 欢迎 */
.welcome { text-align:center; padding:70px 20px 40px; }
.welcome-title { font-size:22px; font-weight:600; color:#111; letter-spacing:-0.4px; margin-bottom:6px; }
.welcome-sub { font-size:13px; color:#9ca3af; }
.welcome-chips { display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-top:20px; }
.chip { padding:6px 14px; border-radius:20px; border:1px solid #e5e7eb; background:white; font-size:12px; color:#374151; cursor:pointer; }
.chip:hover { background:#f9fafb; }

/* badge */
.badge { display:inline-flex; align-items:center; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-buy { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.badge-sell { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.badge-hold { background:#fffbeb; color:#d97706; border:1px solid #fde68a; }

/* 回测 */
.page-title { font-size:18px; font-weight:600; color:#111; margin-bottom:3px; letter-spacing:-0.3px; }
.page-sub { font-size:12px; color:#9ca3af; margin-bottom:20px; }
.mini-metric { background:white; border:1px solid #e5e7eb; border-radius:8px; padding:10px 12px; text-align:center; }
.mini-metric-label { font-size:10px; color:#9ca3af; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; }
.mini-metric-value { font-size:17px; font-weight:700; color:#111; font-family:'JetBrains Mono',monospace; margin-top:2px; }
.mini-metric-value.up { color:#dc2626; }
.mini-metric-value.down { color:#10b981; }

/* status */
.status-pill { display:inline-flex; align-items:center; gap:5px; font-size:11px; padding:3px 8px; border-radius:20px; }
.status-online { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.status-offline { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }

/* 上传预览 */
.upload-preview { display:flex; align-items:center; gap:6px; padding:4px 10px; background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; font-size:11px; color:#0369a1; margin-bottom:6px; }

/* 覆盖Streamlit */
.stTextInput > div > div > input { background:transparent !important; border:none !important; box-shadow:none !important; font-size:13px !important; padding:0 !important; color:#111 !important; }
.stTextInput > div > div > input:focus { outline:none !important; box-shadow:none !important; border:none !important; }
.stTextInput > div { border:none !important; }
.stButton > button { background:#f3f4f6 !important; color:#374151 !important; border:1px solid #e5e7eb !important; border-radius:8px !important; font-weight:500 !important; font-size:12px !important; padding:7px 16px !important; }
.stButton > button:hover { background:#e5e7eb !important; }
/* 发送按钮单独样式 */
[data-testid="stButton"][aria-label="send_btn"] > button,
div[data-testid="column"]:last-child .stButton > button { background:#e8490f !important; color:white !important; border:none !important; border-radius:50% !important; width:36px !important; height:36px !important; padding:0 !important; font-size:16px !important; }
.stSelectbox > div > div { background:white !important; border:1px solid #e5e7eb !important; border-radius:7px !important; font-size:12px !important; }
.stTabs [data-baseweb="tab-list"] { background:transparent !important; border-bottom:1px solid #e5e7eb !important; gap:0 !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#9ca3af !important; font-size:11px !important; padding:6px 12px !important; }
.stTabs [aria-selected="true"] { color:#111 !important; border-bottom:2px solid #111 !important; font-weight:600 !important; }
label { color:#374151 !important; font-size:11px !important; font-weight:500 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Session State ─────────────────────────────────────────────────────────
defaults = {
    "conversations": {},
    "current_conv": None,
    "mode": "chat",
    "bt_result": None,
    "_pending_code": None,
    "selected_model": "smart",
    "uploaded_file": None,
    "uploaded_image": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

SECTORS = {
    "造船": {"600150": "中国船舶", "601989": "中国重工"},
    "CPO光模块": {"300308": "中际旭创", "002281": "光迅科技", "603068": "博通集成"},
    "AI算力": {"002261": "拓维信息", "688041": "海光信息", "688256": "寒武纪"},
    "半导体": {"603501": "韦尔股份", "002371": "北方华创", "688981": "中芯国际"},
    "军工": {"600760": "中航沈飞", "000768": "中航西飞", "600893": "航发动力"},
    "新能源": {"300750": "宁德时代", "002594": "比亚迪", "601012": "隆基绿能"},
    "有色金属": {"601899": "紫金矿业", "600362": "江西铜业", "000630": "铜陵有色"},
    "煤炭能源": {"601088": "中国神华", "601898": "中煤能源", "600188": "兖矿能源"},
}


def new_conv():
    cid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    st.session_state.conversations[cid] = {
        "title": "新对话",
        "messages": [],
        "time": datetime.datetime.now().strftime("%H:%M"),
    }
    st.session_state.current_conv = cid
    st.session_state.mode = "chat"
    st.session_state.uploaded_file = None
    st.session_state.uploaded_image = None
    return cid


def get_messages():
    cid = st.session_state.current_conv
    if cid and cid in st.session_state.conversations:
        return st.session_state.conversations[cid]["messages"]
    return []


try:
    _r = requests.get(f"{API_BASE}/health", timeout=2)
    backend_ok = _r.status_code == 200
except:
    backend_ok = False

# ══════════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns([1, 4.2])

# ── 左栏 ──────────────────────────────────────────────────────────────────
with col_left:
    st.markdown(
        """
    <div class="logo-row">
        <div class="logo-icon">A</div>
        <div class="logo-text">AlphaStock</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("＋  新对话", key="btn_new", use_container_width=True):
        new_conv()
        st.rerun()

    # 当前模型显示（简洁版，左栏只显示当前模型）
    cur_model = st.session_state.selected_model
    mv = MODEL_OPTIONS[cur_model]
    st.markdown(
        f"""
    <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;
                padding:6px 10px;margin:6px 0;font-size:11px;color:#374151">
        <span style="color:#9ca3af">当前模型</span><br>
        <b>{mv["icon"]} {mv["label"]}</b>
        <span style="color:#9ca3af;font-size:10px"> · {mv["desc"].split("·")[0].strip()}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-section-title">功能</div>', unsafe_allow_html=True)

    for nav_key, icon, label in [
        ("chat", "💬", "股票助手"),
        ("backtest", "📊", "量化回测"),
        ("alpha", "🧮", "Alpha选股"),
        ("scan", "🎯", "今日买点"),
        ("filter", "🔍", "板块筛选"),
    ]:
        if st.button(
            f"{icon}  {label}", key=f"navbtn_{nav_key}", use_container_width=True
        ):
            st.session_state.mode = nav_key
            st.rerun()

    st.markdown('<div class="nav-section-title">历史对话</div>', unsafe_allow_html=True)
    convs = st.session_state.conversations
    if convs:
        for cid in sorted(convs.keys(), reverse=True)[:8]:
            c = convs[cid]
            title = c["title"][:14] + ("…" if len(c["title"]) > 14 else "")
            if st.button(f"💬 {title}", key=f"conv_{cid}", use_container_width=True):
                st.session_state.current_conv = cid
                st.session_state.mode = "chat"
                st.rerun()
    else:
        st.markdown(
            '<div style="font-size:11px;color:#ccc;padding:4px">暂无历史</div>',
            unsafe_allow_html=True,
        )

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
                <div class="welcome-title">你好，我是 AlphaStock</div>
                <div class="welcome-sub">输入股票代码开始分析，或上传财报截图</div>
                <div class="welcome-chips">
                    <div class="chip">600150 中国船舶</div>
                    <div class="chip">300308 中际旭创</div>
                    <div class="chip">002261 拓维信息</div>
                    <div class="chip">601088 中国神华</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # 渲染对话历史
        for msg in messages:
            if msg["role"] == "user":
                content = msg["content"]
                # 如果有附件标注
                if msg.get("has_file"):
                    content = f"📎 {msg.get('file_name', '附件')}  \n{content}"
                st.markdown(
                    f'<div class="bubble-user"><div class="bubble-user-inner">{content}</div></div>',
                    unsafe_allow_html=True,
                )
            elif msg["role"] == "assistant":
                mtype = msg.get("type", "text")
                if mtype == "analysis":
                    data = msg.get("data", {})
                    dtxt = data.get("decision", "")
                    model_used = msg.get("model", "smart")
                    model_label = MODEL_OPTIONS.get(model_used, {}).get("label", "精准")

                    if "买入" in dtxt:
                        badge = '<span class="badge badge-buy">🔴 买入</span>'
                    elif "卖出" in dtxt or "减仓" in dtxt:
                        badge = '<span class="badge badge-sell">🟢 减仓</span>'
                    else:
                        badge = '<span class="badge badge-hold">🟡 观望</span>'

                    st.markdown(
                        f"""
                    <div class="bubble-ai">
                        <div class="ai-avatar">A</div>
                        <div style="flex:1;min-width:0">
                            <div style="font-size:10px;color:#9ca3af;margin-bottom:6px;display:flex;align-items:center;gap:8px">
                                {data.get('stock_code','')} &nbsp;{badge}
                                <span style="padding:2px 6px;background:#f5f5f3;border-radius:4px;font-size:10px;color:#9ca3af">
                                    {MODEL_OPTIONS.get(model_used,{}).get('icon','')} {model_label}模式
                                </span>
                            </div>
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
                        f'<div class="bubble-ai"><div class="ai-avatar">A</div><div class="bubble-ai-inner">{msg["content"]}</div></div>',
                        unsafe_allow_html=True,
                    )

        # 处理待分析
        if st.session_state._pending_code:
            code = st.session_state._pending_code
            model = st.session_state.selected_model
            st.session_state._pending_code = None
            with st.spinner(
                f"正在用「{MODEL_OPTIONS[model]['label']}」模式分析 {code}..."
            ):
                try:
                    resp = requests.post(
                        f"{API_BASE}/analyze",
                        json={"stock_code": code, "model": model},
                        timeout=300,
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
                                "model": model,
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

        # ── 输入区域（Claude风格）──
        st.markdown("<div style='height:16px'/>", unsafe_allow_html=True)

        # 上传预览条
        if st.session_state.uploaded_file or st.session_state.uploaded_image:
            fname = (
                st.session_state.uploaded_image.name
                if st.session_state.uploaded_image
                else st.session_state.uploaded_file.name
            )
            pc1, pc2 = st.columns([8, 1])
            with pc1:
                st.markdown(
                    f'<div class="upload-preview">📎 {fname}</div>',
                    unsafe_allow_html=True,
                )
            with pc2:
                if st.button("✕", key="clear_upload"):
                    st.session_state.uploaded_file = None
                    st.session_state.uploaded_image = None
                    st.rerun()

        # 主输入框容器
        cur_m = st.session_state.selected_model
        st.markdown(
            f"""
        <div style="background:white;border:1px solid #d1d5db;border-radius:14px;
                    padding:10px 14px 8px;box-shadow:0 1px 4px rgba(0,0,0,0.06);
                    max-width:760px;margin:0 auto">
        """,
            unsafe_allow_html=True,
        )

        # 文本输入
        user_input = st.text_input(
            "msg",
            label_visibility="collapsed",
            placeholder="输入股票代码（如 600584）或直接提问...",
            key="chat_input",
        )

        # 底部工具栏：+ 号 | 模型切换 | 发送
        bot_c1, bot_c2, bot_c3 = st.columns([1, 6, 1])

        with bot_c1:
            # + 号按钮，点击展开上传
            plus_clicked = st.button("＋", key="plus_btn", help="上传图片或文件")
            if plus_clicked:
                st.session_state["show_upload"] = not st.session_state.get(
                    "show_upload", False
                )
                st.rerun()

        with bot_c2:
            # 模型选择器（inline，点击切换）
            m_cols = st.columns(3)
            for idx, (mk, mv) in enumerate(MODEL_OPTIONS.items()):
                with m_cols[idx]:
                    is_cur = st.session_state.selected_model == mk
                    btn_style = (
                        "background:#f0f9ff;color:#0369a1;border:1px solid #bae6fd;"
                        if is_cur
                        else ""
                    )
                    st.markdown(
                        f"""
                    <div style="text-align:center;padding:3px 6px;border-radius:6px;
                                font-size:11px;{btn_style}cursor:pointer">
                        {mv['icon']} {mv['label']}
                    </div>""",
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        mv["label"], key=f"inline_model_{mk}", use_container_width=True
                    ):
                        st.session_state.selected_model = mk
                        st.rerun()

        with bot_c3:
            send = st.button("↑", key="send_btn")

        st.markdown("</div>", unsafe_allow_html=True)

        # 上传弹出区（点+号后展开）
        if st.session_state.get("show_upload", False):
            st.markdown(
                """
            <div style="background:white;border:1px solid #e5e7eb;border-radius:10px;
                        padding:12px;margin:6px auto;max-width:760px;
                        box-shadow:0 4px 12px rgba(0,0,0,0.08)">
                <div style="font-size:11px;color:#9ca3af;margin-bottom:8px;font-weight:600">
                    选择上传类型
                </div>
            </div>""",
                unsafe_allow_html=True,
            )

            up_c1, up_c2 = st.columns(2)
            with up_c1:
                st.markdown(
                    '<div style="font-size:12px;color:#374151;margin-bottom:4px">📷 图片（财报截图/K线图）</div>',
                    unsafe_allow_html=True,
                )
                uploaded_img = st.file_uploader(
                    "图片",
                    type=["png", "jpg", "jpeg", "webp"],
                    key="img_upload",
                    label_visibility="collapsed",
                )
                if uploaded_img:
                    st.session_state.uploaded_image = uploaded_img
                    st.session_state["show_upload"] = False
                    st.rerun()
            with up_c2:
                st.markdown(
                    '<div style="font-size:12px;color:#374151;margin-bottom:4px">📎 文件（PDF/Word/CSV）</div>',
                    unsafe_allow_html=True,
                )
                uploaded_file = st.file_uploader(
                    "文件",
                    type=["pdf", "txt", "csv", "xlsx"],
                    key="file_upload",
                    label_visibility="collapsed",
                )
                if uploaded_file:
                    st.session_state.uploaded_file = uploaded_file
                    st.session_state["show_upload"] = False
                    st.rerun()

        # 发送逻辑
        if send and user_input.strip():
            txt = user_input.strip()
            if not st.session_state.current_conv:
                new_conv()
            cid = st.session_state.current_conv
            has_file = bool(
                st.session_state.uploaded_file or st.session_state.uploaded_image
            )
            file_name = ""
            if st.session_state.uploaded_image:
                file_name = st.session_state.uploaded_image.name
            elif st.session_state.uploaded_file:
                file_name = st.session_state.uploaded_file.name

            st.session_state.conversations[cid]["messages"].append(
                {
                    "role": "user",
                    "content": txt,
                    "has_file": has_file,
                    "file_name": file_name,
                }
            )
            codes = re.findall(r"\b\d{6}\b", txt)
            if codes:
                st.session_state._pending_code = codes[0]
            else:
                st.session_state.conversations[cid]["messages"].append(
                    {
                        "role": "assistant",
                        "type": "text",
                        "content": "请输入6位股票代码进行分析，例如 <b>600150</b>（中国船舶）",
                    }
                )
            st.session_state.uploaded_file = None
            st.session_state.uploaded_image = None
            st.rerun()

    # ── 量化回测 ──
    elif mode == "backtest":
        cur_m = st.session_state.selected_model
        st.markdown(
            f"""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
            <div class="page-title">量化回测</div>
            <div class="model-pill">{MODEL_OPTIONS[cur_m]['icon']} {MODEL_OPTIONS[cur_m]['label']}模式</div>
        </div>
        <div class="page-sub">Backtrader · KDJ / RSI / 布林带 · 建议使用「强力」模式获取最深度解读</div>
        """,
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns([1.2, 1.5, 0.9, 0.9])
        with c1:
            code = st.text_input("股票代码", "600150", key="bt_code")
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
                        line=dict(color="#111827", width=1.6),
                        fill="tozeroy",
                        fillcolor="rgba(17,24,39,0.04)",
                    )
                )
                fig.add_hline(y=0, line_dash="dot", line_color="#e5e7eb")
                fig.update_layout(
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    font=dict(family="Inter", color="#9ca3af", size=11),
                    xaxis=dict(gridcolor="#f9fafb", linecolor="#e5e7eb"),
                    yaxis=dict(
                        gridcolor="#f9fafb", ticksuffix="%", linecolor="#e5e7eb"
                    ),
                    height=220,
                    margin=dict(l=44, r=16, t=8, b=32),
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
                '<div style="text-align:center;padding:50px;color:#9ca3af;font-size:13px">填写参数，点击「开始回测」</div>',
                unsafe_allow_html=True,
            )

    # ── 今日买点 ──
    elif mode == "scan":
        st.markdown('<div class="page-title">今日买点</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">全市场扫描 · KDJ超卖 + MA20趋势 · Agent验证 · 市值≥300亿</div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns([2, 1])
        with c1:
            bs = st.text_input("数据起始日期", "20230101")
        with c2:
            tn = st.slider("最多显示", 5, 20, 10)

        if st.button("开始扫描 →"):
            with st.spinner("扫描中（约5分钟）..."):
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

    # ── Alpha因子选股 ──
    elif mode == "alpha":
        cur_m = st.session_state.selected_model
        st.markdown(
            f"""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
            <div class="page-title">Alpha 因子选股</div>
            <div class="model-pill">{MODEL_OPTIONS[cur_m]["icon"]} {MODEL_OPTIONS[cur_m]["label"]}模式</div>
        </div>
        <div class="page-sub">五因子打分：KDJ反转 · 成交量 · ROE · 市值 · 均线趋势 · 总分100分</div>
        """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            sector_options = ["全部（动态股票池）"] + list(SECTORS.keys())
            sector = st.selectbox("板块", sector_options, key="alpha_sector")
        with c2:
            min_score = st.slider("最低分数", 50, 90, 60, key="alpha_min")
        with c3:
            top_n = st.slider("显示数量", 5, 30, 15, key="alpha_top")

        st.markdown(
            """
        <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:10px 14px;font-size:12px;color:#92400e;margin-bottom:16px">
            💡 <b>评级标准</b>：≥75分 ⭐⭐重点关注 · 60-74分 ⭐值得关注 · &lt;60分 不推荐
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("开始打分 →", key="alpha_btn"):
            payload = {"min_score": min_score, "top_n": top_n}
            if sector != "全部（动态股票池）":
                payload["sector"] = sector

            with st.spinner(
                f"正在对{'全部股票池' if sector == '全部（动态股票池）' else sector}打分（约2-5分钟）..."
            ):
                try:
                    resp = requests.post(
                        f"{API_BASE}/alpha/score",
                        json=payload,
                        timeout=600,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("results", [])
                        st.success(
                            f"打分完成 · 共{data['total_scored']}只 · {data['qualified']}只通过门槛"
                        )

                        if results:
                            # 汇总表格
                            rows = []
                            for r in results:
                                score = r["total_score"]
                                rating = r["rating"]
                                factors = r["factors"]
                                rows.append(
                                    {
                                        "代码": r["stock_code"],
                                        "名称": r["stock_name"],
                                        "总分": score,
                                        "评级": rating,
                                        "KDJ": factors["kdj"]["score"],
                                        "成交量": factors["volume"]["score"],
                                        "ROE": factors["roe"]["score"],
                                        "市值": factors["market_cap"]["score"],
                                        "趋势": factors["trend"]["score"],
                                    }
                                )
                            df = pd.DataFrame(rows)
                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "总分": st.column_config.ProgressColumn(
                                        "总分", min_value=0, max_value=100, format="%d"
                                    )
                                },
                            )

                            # 展开详情
                            st.markdown("### 因子详情")
                            for r in results[:10]:
                                score = r["total_score"]
                                icon = "⭐⭐" if score >= 75 else "⭐"
                                with st.expander(
                                    f"{icon} {r['stock_name']}（{r['stock_code']}）— {score:.0f}分"
                                ):
                                    factors = r["factors"]
                                    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
                                    for col, (fname, fkey) in zip(
                                        [fc1, fc2, fc3, fc4, fc5],
                                        [
                                            ("KDJ", "kdj"),
                                            ("成交量", "volume"),
                                            ("ROE", "roe"),
                                            ("市值", "market_cap"),
                                            ("趋势", "trend"),
                                        ],
                                    ):
                                        with col:
                                            fscore = factors[fkey]["score"]
                                            fdetail = factors[fkey]["detail"]
                                            color = (
                                                "#16a34a"
                                                if fscore >= 15
                                                else (
                                                    "#d97706"
                                                    if fscore >= 8
                                                    else "#dc2626"
                                                )
                                            )
                                            st.markdown(
                                                f"""
                                            <div style="text-align:center;padding:8px;background:white;border:1px solid #e5e7eb;border-radius:8px">
                                                <div style="font-size:10px;color:#9ca3af">{fname}</div>
                                                <div style="font-size:18px;font-weight:700;color:{color}">{fscore}</div>
                                                <div style="font-size:9px;color:#9ca3af">/20</div>
                                            </div>
                                            """,
                                                unsafe_allow_html=True,
                                            )
                                    st.caption(f"KDJ: {factors['kdj']['detail']}")
                                    st.caption(f"成交量: {factors['volume']['detail']}")
                                    st.caption(f"ROE: {factors['roe']['detail']}")
                                    st.caption(
                                        f"市值: {factors['market_cap']['detail']}"
                                    )
                                    st.caption(f"趋势: {factors['trend']['detail']}")

                                    # 一键分析
                                    if st.button(
                                        f"深度分析 {r['stock_code']} →",
                                        key=f"alpha_analyze_{r['stock_code']}",
                                    ):
                                        if not st.session_state.current_conv:
                                            new_conv()
                                        cid = st.session_state.current_conv
                                        st.session_state.conversations[cid][
                                            "messages"
                                        ].append(
                                            {
                                                "role": "user",
                                                "content": f"Alpha打分{score:.0f}分，深度分析{r['stock_code']}",
                                            }
                                        )
                                        st.session_state._pending_code = r["stock_code"]
                                        st.session_state.mode = "chat"
                                        st.rerun()
                        else:
                            st.warning("没有股票达到门槛，建议降低最低分数")
                    else:
                        st.error(f"打分失败：{resp.json().get('detail', '未知')}")
                except Exception as e:
                    st.error(f"请求失败：{e}")
        else:
            st.markdown(
                '<div style="text-align:center;padding:50px;color:#9ca3af;font-size:13px">选择板块，点击「开始打分」</div>',
                unsafe_allow_html=True,
            )

    # ── 板块筛选 ──
    elif mode == "filter":
        st.markdown('<div class="page-title">板块筛选</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">主题景气周期 · PE / ROE / 毛利率多维评分</div>',
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
                '<div style="text-align:center;padding:50px;color:#9ca3af;font-size:13px">选择板块，点击「开始筛选」</div>',
                unsafe_allow_html=True,
            )
