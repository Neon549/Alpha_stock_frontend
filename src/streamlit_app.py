"""
streamlit_app.py  ──  入口 & 仿 TradeZella 着陆页
"""
import streamlit as st
import requests
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.common import API_BASE, init_session

st.set_page_config(
    page_title="AlphaStock · Meet Your AI Partner",
    page_icon="🦄",
    layout="wide", # 必须宽屏以支持左右布局
    initial_sidebar_state="collapsed",
)

init_session()

# 已登录 → 跳主界面
if st.session_state.token:
    st.switch_page("pages/1_chat.py")
    st.stop()

# ── CSS：全局样式与完全自定义的着陆页组件 ─────────────────────────
st.markdown("""
<style>
/* 1. 彻底隐藏所有的 Streamlit 默认导航、侧边栏和底栏 */
[data-testid="stSidebarNav"],
[data-testid="stSidebar"], 
[data-testid="collapsedControl"],
#MainMenu, header[data-testid="stHeader"], footer {
    display: none !important;
}

/* 2. 放宽主容器宽度限制并去掉多余 padding */
.block-container {
    max-width: 1300px !important;
    padding: 10px 40px 100px !important;
    margin: 0 auto !important;
}

/* 3. 背景：实现极其细腻的左白右紫渐变 (类似 TradeZella) */
.stApp {
    background: radial-gradient(circle at 85% 10%, #fef5ff 0%, #f3ebff 25%, #ffffff 60%) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* ================= HTML 顶层导航栏 (Navbar) ================= */
.tz-nav {
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 0; margin-bottom: 70px;
}
.tz-logo {
    font-size: 24px; font-weight: 800; color: #111827; letter-spacing: -0.5px;
    display: flex; align-items: center; gap: 8px; cursor: pointer;
}
.tz-menu {
    display: flex; gap: 32px; font-size: 15px; font-weight: 600; color: #374151;
}
.tz-item {
    display: flex; align-items: center; gap: 4px; cursor: pointer; transition: color 0.2s;
}
.tz-item:hover { color: #8B5CF6; }
.tz-chevron { font-size: 14px; font-weight: bold; transform: translateY(-1px); }
.tz-actions { display: flex; align-items: center; gap: 24px; }
.tz-login {
    text-decoration: none; color: #111827; font-weight: 600; font-size: 15px; transition: color 0.2s;
}
.tz-login:hover { color: #8B5CF6; }
.tz-start {
    text-decoration: none;
    background: linear-gradient(90deg, #6366f1, #d946ef); /* 紫红渐变按钮 */
    color: white; padding: 12px 24px; border-radius: 8px; font-weight: 600; font-size: 15px;
    box-shadow: 0 4px 14px rgba(217,70,239,0.3); transition: transform 0.2s;
}
.tz-start:hover { transform: translateY(-1px); color: white; }

/* ================= 右侧 Streamlit 表单的卡片化 ================= */
/* 选中第二个 column 并将其转换为浮雕玻璃卡片 */
[data-testid="column"]:nth-of-type(2) {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 24px;
    padding: 40px;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.1), 0 0 0 1px rgba(0,0,0,0.02);
}

/* 覆盖登录/注册的 Tab 和 Input 原生样式 */
.stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #e5e7eb; gap: 0; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #6b7280; font-weight: 600; border: none; padding: 12px 18px; }
.stTabs [aria-selected="true"] { color: #111827 !important; border-bottom: 2px solid #111827 !important; margin-bottom: -2px; }
[data-testid="stTextInput"] input {
    border-radius: 12px !important; border: 1px solid #e5e7eb !important;
    padding: 14px !important; background: #f9fafb !important; font-size: 14.5px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #6366F1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important; background: #ffffff !important;
}
[data-testid="stFormSubmitButton"] button, div.stButton > button {
    background: #111827 !important; color: white !important; border: none !important;
    border-radius: 12px !important; padding: 14px !important; font-weight: 600 !important; font-size: 15px !important;
}
[data-testid="stFormSubmitButton"] button:hover, div.stButton > button:hover {
    background: #374151 !important; transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

# ── 1. 自定义 HTML 导航栏 (包含悬浮菜单的视觉设计) ────────────────────
st.markdown("""
<div class="tz-nav">
    <div class="tz-logo">
        <span style="font-size:28px;">🦄</span> AlphaStock
    </div>
    <div class="tz-menu">
        <div class="tz-item">Products <span class="tz-chevron">⌄</span></div>
        <div class="tz-item">Solutions <span class="tz-chevron">⌄</span></div>
        <div class="tz-item">Supported Brokers</div>
        <div class="tz-item">Pricing</div>
        <div class="tz-item">Resources <span class="tz-chevron">⌄</span></div>
    </div>
    <div class="tz-actions">
        <!-- 锚点链接，点击后直接在页面内定位到右侧登录框 -->
        <a href="#auth-section" class="tz-login">Log In</a>
        <a href="#auth-section" class="tz-start">Get Started ></a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 2. 主视觉区 (左右分栏：左文案，右登录) ─────────────────────────
col_left, col_right = st.columns([1.2, 0.9], gap="large")

with col_left:
    # 纯正的海外 SaaS 文案排版
    st.markdown("""
    <div style="padding-top: 10px;">
        <h1 style="font-size: 72px; font-weight: 800; color: #0F172A; line-height: 1.05; letter-spacing: -2.5px; margin-bottom: 24px;">
            Meet Your AI<br>Trading Partner
        </h1>
        <p style="font-size: 20px; color: #475569; line-height: 1.6; margin-bottom: 35px; max-width: 85%;">
            The AI trading journal that knows your trades, builds your game plan, and reviews every session automatically while you focus on the next one.<br><br>
            <span style="color:#0F172A;">Trusted by <b>100K+</b> traders.</span>
        </p>
        
        <div style="display:flex; align-items:center; gap: 24px; margin-bottom: 50px;">
            <a href="#auth-section" style="background:#0F172A; color:white; padding:18px 36px; border-radius:30px; font-weight:600; font-size:16px; text-decoration:none; box-shadow:0 8px 20px rgba(0,0,0,0.15); transition:all 0.2s;">
                Get Started
            </a>
            <div style="display:flex; flex-direction:column; gap:4px;">
                <div style="font-size:15px; font-weight:700; color:#0F172A; display:flex; align-items:center; gap:6px;">
                    Excellent <span style="color:#00B67A; font-size:19px; letter-spacing:1px; transform:translateY(-1px);">★★★★★</span>
                </div>
                <div style="font-size:13px; text-decoration:underline; color:#475569; cursor:pointer;">
                    978 reviews on <span style="color:#00B67A; font-size:15px;">★</span> Trustpilot
                </div>
            </div>
        </div>
        
        <div style="font-size: 12px; font-weight: 700; color: #94A3B8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 16px;">
            Everything in one place · 6 Tools
        </div>
        
        <div style="display: flex; flex-wrap: wrap; gap: 12px;">
            <span style="padding:10px 18px; border-radius:24px; border:1px solid #E2E8F0; background:white; font-size:14px; font-weight:600; color:#475569; display:flex; align-items:center; gap:8px;">
                <span style="width:8px; height:8px; border-radius:50%; background:#8B5CF6;"></span> Automated Journaling
            </span>
            <span style="padding:10px 18px; border-radius:24px; border:1px solid #E2E8F0; background:white; font-size:14px; font-weight:600; color:#475569;">Backtesting</span>
            <span style="padding:10px 18px; border-radius:24px; border:1px solid #E2E8F0; background:white; font-size:14px; font-weight:600; color:#475569;">Trade Replay</span>
            <span style="padding:10px 18px; border-radius:24px; border:1px solid #E2E8F0; background:white; font-size:14px; font-weight:600; color:#475569;">AI Insights</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    # 这是提供给上方按钮跳转的锚点
    st.markdown('<div id="auth-section" style="position:relative; top:-80px;"></div>', unsafe_allow_html=True)

    # ── OAuth 第三方登录按钮 ──
    st.markdown("""
    <h3 style="margin-top:0; color:#0F172A; font-weight:800; font-size:26px; letter-spacing:-0.5px;">Start Your Journey</h3>
    <p style="color:#64748B; font-size:15px; margin-bottom:28px;">登入以体验全套智能投研工具</p>
    
    <div style="display:flex;gap:12px;margin-bottom:20px">
      <a href="https://alphastock.cloud/api/v1/auth/google"
         style="flex:1;display:flex;align-items:center;justify-content:center;gap:8px;
                border:1px solid #E2E8F0;border-radius:12px;padding:14px 8px;
                font-size:14.5px;font-weight:600;color:#334155;background:white;
                text-decoration:none;box-shadow:0 1px 2px rgba(0,0,0,0.02);transition:all 0.2s;">
        <svg width="18" height="18" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.31-8.16 2.31-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
        Google
      </a>
      <button onclick="alert('微信/QQ 登录接口开发中 🔧')"
              style="flex:1;display:flex;align-items:center;justify-content:center;gap:8px;
                     border:1px solid #E2E8F0;border-radius:12px;padding:14px 8px;
                     font-size:14.5px;font-weight:600;color:#334155;background:white;
                     cursor:pointer;box-shadow:0 1px 2px rgba(0,0,0,0.02);transition:all 0.2s;">
        <span style="font-size:18px;line-height:1">💬</span> WeChat
      </button>
    </div>
    <div style="display:flex;align-items:center;gap:12px;margin:24px 0 16px;color:#94A3B8;font-size:13px">
      <div style="flex:1;height:1px;background:#E2E8F0"></div>
      <span>或使用账号密码</span>
      <div style="flex:1;height:1px;background:#E2E8F0"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── 常规账号密码登录逻辑 (内嵌在卡片中) ──
    tab_login, tab_reg = st.tabs(["安全登录", "注册账号"])

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            # 取消 Label 以求极致极简，使用 placeholder 代替
            lu = st.text_input("用户名", placeholder="Username", label_visibility="collapsed")
            lp = st.text_input("密码", type="password", placeholder="Password", label_visibility="collapsed")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("进入系统", use_container_width=True)

        if submitted:
            if not lu or not lp:
                st.error("请输入用户名和密码")
            else:
                try:
                    r = requests.post(f"{API_BASE}/auth/login", json={"username": lu, "password": lp}, timeout=60)
                    if r.status_code == 200:
                        d = r.json()
                        st.session_state.token = d["token"]
                        st.session_state.username = d["username"]
                        st.switch_page("pages/1_chat.py")
                    else:
                        st.error(r.json().get("detail", "登录失败，请检查用户名或密码"))
                except Exception as e:
                    st.error(f"连接失败：{e}")

    with tab_reg:
        ru = st.text_input("用户名", key="reg_user", placeholder="Username (4-20 chars)", label_visibility="collapsed")
        rp = st.text_input("创建密码", type="password", key="reg_pwd", placeholder="Password (Min 8, Letters + Nums)", label_visibility="collapsed")
        if rp:
            items = [(len(rp)>=8,"8位以上"), (any(c.islower() for c in rp),"包含小写"), (any(c.isupper() for c in rp),"包含大写"), (any(c.isdigit() for c in rp),"包含数字")]
            checks = "".join(f'<div style="font-size:12px;font-weight:600;display:flex;gap:4px;color:{"#10B981" if ok else "#94A3B8"}">{"✓" if ok else "○"} {label}</div>' for ok, label in items)
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0;">{checks}</div>', unsafe_allow_html=True)

        if st.button("注册并进入", use_container_width=True, key="do_reg"):
            if not ru or not rp:
                st.error("请填写用户名和密码")
            elif len(rp) < 8:
                st.error("密码至少需要 8 位")
            else:
                try:
                    r = requests.post(f"{API_BASE}/auth/register", json={"username": ru, "password": rp}, timeout=60)
                    if r.status_code == 200:
                        d = r.json()
                        st.session_state.token = d.get("token")
                        st.session_state.username = d.get("username", ru)
                        st.switch_page("pages/1_chat.py")
                    else:
                        st.error(r.json().get("detail", "注册失败"))
                except Exception as e:
                    st.error(f"连接失败：{e}")