#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: yulin
@created: 2026/7/19 16:34
@updated: 2026/7/19 16:34
@version: 1.0
@description:
"""

"""
utils/common.py
公共常量、CSS、守卫函数 —— 所有页面 import 这里
"""
import streamlit as st

API_BASE = "https://alphastock.cloud/api/v1"

MODEL_OPTIONS = {
    "fast": {"label": "快速", "desc": "DeepSeek V3", "icon": "⚡"},
    "smart": {"label": "精准", "desc": "DeepSeek R1", "icon": "🧠"},
    "strong": {"label": "强力", "desc": "R1 严格", "icon": "🔬"},
}

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

# ── Session State 初始化（每个页面顶部调用一次） ──────────────────────
DEFAULTS = {
    "conversations": {},
    "current_conv": None,
    "mode": "chat",
    "bt_result": None,
    "_pending": None,
    "model": "smart",
    "token": None,
    "username": None,
    "up_file": None,
}


def init_session():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── 鉴权守卫：没有 token 就踢回登录页 ───────────────────────────────
def require_auth():
    init_session()
    if not st.session_state.token:
        st.switch_page("streamlit_app.py")
        st.stop()


# ── 全局 CSS（主界面用） ─────────────────────────────────────────────
MAIN_CSS = """
<style>
[data-testid="stSidebarNav"] { display: none !important; }
body, p, div, span, h1, h2, h3, h4, button, input, select, textarea {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif !important;
}
[data-testid="stIconMaterial"],
.material-icons,
[class*="material-symbols"],
[class*="MaterialIcon"] {
    font-family: "Material Icons", "Material Icons Outlined", "Material Symbols Rounded" !important;
}
#MainMenu, footer { visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbarActions"], [data-testid="stMainMenu"] { visibility: hidden; }
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important; display: flex !important; opacity: 1 !important;
}
.stApp, [data-testid="stAppViewContainer"] { background: #F9FAFB !important; }
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E5E7EB !important;
    box-shadow: 2px 0 10px rgba(0,0,0,0.02);
}
.bubble-u { display:flex; justify-content:flex-end; margin:12px 0 20px; }
.bubble-u div { background:linear-gradient(135deg,#6366F1,#8B5CF6); color:white; border-radius:20px 20px 4px 20px; padding:12px 18px; max-width:65%; font-size:14px; box-shadow:0 4px 12px rgba(99,102,241,0.2); }
.bubble-a { display:flex; gap:14px; margin:12px 0 24px; align-items:flex-start; }
.bubble-a .av { width:34px; height:34px; border-radius:8px; background:#111827; color:white; font-size:16px; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.bubble-a .txt { background:white; border:1px solid #E5E7EB; border-radius:4px 20px 20px 20px; padding:16px 20px; max-width:85%; font-size:14px; color:#1F2937; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05); }
.terminal-box { background:#0F172A; color:#38BDF8; font-family:monospace; font-size:13px; padding:16px; border-radius:12px; }
.main .block-container { max-width:900px !important; padding:40px 30px 100px !important; }
.stButton>button { background:#FFFFFF !important; color:#374151 !important; border:1px solid #E5E7EB !important; border-radius:10px !important; }
.stButton>button:hover { border-color:#8B5CF6 !important; color:#8B5CF6 !important; }
</style>
"""


# ── 侧边栏（所有主页面共用） ─────────────────────────────────────────
def render_sidebar():
    import requests

    try:
        backend_ok = requests.get(f"{API_BASE}/health", timeout=5).status_code == 200
    except:
        backend_ok = False

    with st.sidebar:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:9px;padding:4px 8px 18px;'
            'font-size:17px;font-weight:800">'
            '<div style="width:28px;height:28px;border-radius:8px;'
            "background:linear-gradient(135deg,#6366F1,#8B5CF6);color:white;"
            "font-size:14px;font-weight:900;display:flex;align-items:center;"
            'justify-content:center">A</div>AlphaStock</div>',
            unsafe_allow_html=True,
        )

        if st.button("＋ 新的投研对话", use_container_width=True, key="nc"):
            from utils.common import new_conv

            new_conv()
            st.switch_page("pages/1_chat.py")

        st.caption("推理引擎")
        mc1, mc2, mc3 = st.columns(3)
        for col, mk in zip([mc1, mc2, mc3], MODEL_OPTIONS.keys()):
            with col:
                mv = MODEL_OPTIONS[mk]
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
            f'<div style="font-size:12px;color:#6B7280;text-align:center;margin:-4px 0 16px">'
            f'{cur["icon"]} {cur["label"]} ({cur["desc"]})</div>',
            unsafe_allow_html=True,
        )

        st.caption("功能")
        nav_map = {
            "pages/1_chat.py": "🤖 AI 股票助手",
            "pages/2_backtest.py": "📊 量化回测",
            "pages/3_alpha.py": "✨ Alpha 选股",
            "pages/4_scan.py": "🎯 今日买点",
            "pages/5_filter.py": "🔍 板块筛选",
        }
        for path, label in nav_map.items():
            if st.button(label, key=f"nav_{path}", use_container_width=True):
                st.switch_page(path)

        st.caption("历史记录")
        convs = st.session_state.conversations
        if convs:
            for cid in sorted(convs.keys(), reverse=True)[:5]:
                if st.button(
                    f"💬 {convs[cid]['title'][:12]}…",
                    key=f"h_{cid}",
                    use_container_width=True,
                ):
                    st.session_state.current_conv = cid
                    st.switch_page("pages/1_chat.py")
        else:
            st.markdown(
                '<div style="font-size:12px;color:#9CA3AF;padding:4px 8px">暂无历史</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='flex:1;min-height:60px'></div>", unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="font-size:13px;padding:6px 8px">👤 {st.session_state.username}</div>',
            unsafe_allow_html=True,
        )
        dot = "🟢 服务正常" if backend_ok else "🔴 后端未响应"
        st.markdown(
            f'<div style="font-size:11px;color:#9CA3AF;padding:2px 8px 8px">{dot}</div>',
            unsafe_allow_html=True,
        )
        if st.button("🏠 返回主页", use_container_width=True, key="sb_home"):
            import webbrowser
            st.markdown('<meta http-equiv="refresh" content="0;url=https://alphastock.cloud">', unsafe_allow_html=True)
        if st.button("退出登录", use_container_width=True, key="logout"):
            import requests as req

            try:
                req.post(
                    f"{API_BASE}/auth/logout",
                    json={"token": st.session_state.token},
                    timeout=5,
                )
            except:
                pass
            st.session_state.token = None
            st.session_state.username = None
            st.switch_page("streamlit_app.py")


# ── 对话辅助函数 ─────────────────────────────────────────────────────
def new_conv():
    import datetime

    cid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    st.session_state.conversations[cid] = {"title": "新对话", "messages": []}
    st.session_state.current_conv = cid
    return cid


def get_msgs():
    cid = st.session_state.current_conv
    return (
        st.session_state.conversations.get(cid, {}).get("messages", []) if cid else []
    )
