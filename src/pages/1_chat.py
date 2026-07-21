"""
pages/1_chat.py  ──  Alpha AI 对话界面
"""
import re
import streamlit as st
import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.common import API_BASE, init_session

@st.dialog("退出登录")
def logout_dialog():
    st.write("确定要退出登录吗？退出后将返回主页。")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ 确认退出", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.conversations = {}
            st.session_state.current_conv = None
            st.session_state._conv_loaded = False
            st.markdown('<meta http-equiv="refresh" content="0;url=https://alphastock.cloud?logout=1">',
                        unsafe_allow_html=True)
            st.stop()
    with c2:
        if st.button("❌ 取消", use_container_width=True):
            st.rerun()

@st.dialog("切换用户")
def switch_dialog():
    st.write("确定要切换用户吗？当前对话记录已保存，切换后将返回主页重新登录。")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ 确认切换", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.conversations = {}
            st.session_state.current_conv = None
            st.session_state._conv_loaded = False
            st.markdown('<meta http-equiv="refresh" content="0;url=https://alphastock.cloud?switch=1">',
                        unsafe_allow_html=True)
            st.stop()
    with c2:
        if st.button("❌ 取消", use_container_width=True):
            st.rerun()

st.set_page_config(
    page_title="Alpha AI · AlphaStock",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

# 从后端加载对话记录（首次加载）
if not st.session_state.get("_conv_loaded") and st.session_state.token:
    try:
        r = requests.get(f"{API_BASE}/conversations/{st.session_state.username}", timeout=5)
        if r.status_code == 200:
            convs = r.json().get("conversations", [])
            for c in convs:
                st.session_state.conversations[c["id"]] = {
                    "title": c["title"],
                    "messages": c["messages"]
                }
            if convs and not st.session_state.current_conv:
                st.session_state.current_conv = convs[0]["id"]
    except:
        pass
    st.session_state._conv_loaded = True

# 鉴权守卫
if not st.session_state.token:
    st.markdown('<meta http-equiv="refresh" content="0;url=https://alphastock.cloud">',
                unsafe_allow_html=True)
    st.stop()

st.markdown("""
<style>
[data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"],
[data-testid="stBreadcrumbs"], #MainMenu, footer { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
[data-testid="stToolbarActions"], [data-testid="stDecoration"] { display: none !important; }
.stApp { background: #F9FAFB !important; }
[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E5E7EB !important; }
.main .block-container { max-width: 900px !important; padding: 32px 30px 100px !important; }
.stButton > button { background: #FFFFFF !important; color: #374151 !important; border: 1px solid #E5E7EB !important; border-radius: 10px !important; }
.stButton > button:hover { border-color: #6366F1 !important; color: #6366F1 !important; }
.bubble-u { display:flex; justify-content:flex-end; margin:12px 0 20px; }
.bubble-u div { background:linear-gradient(135deg,#6366F1,#8B5CF6); color:white; border-radius:20px 20px 4px 20px; padding:12px 18px; max-width:65%; font-size:14px; }
.bubble-a { display:flex; gap:14px; margin:12px 0 24px; align-items:flex-start; }
.bubble-a .av { width:34px; height:34px; border-radius:8px; background:#111827; color:white; font-size:16px; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.bubble-a .txt { background:white; border:1px solid #E5E7EB; border-radius:4px 20px 20px 20px; padding:16px 20px; max-width:85%; font-size:14px; color:#1F2937; }
.terminal-box { background:#0F172A; color:#38BDF8; font-family:monospace; font-size:13px; padding:16px; border-radius:12px; }
</style>
""", unsafe_allow_html=True)

# ── 工具函数 ──────────────────────────────────────────────────────────
def init_conv():
    import datetime
    cid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    st.session_state.conversations[cid] = {"title": "新对话", "messages": []}
    st.session_state.current_conv = cid
    return cid

# ── 侧边栏 ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:9px;padding:4px 8px 20px;font-size:17px;font-weight:800">'
        '<div style="width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,#6366F1,#8B5CF6);'
        'color:white;font-size:14px;font-weight:900;display:flex;align-items:center;justify-content:center">A</div>'
        'Alpha AI</div>', unsafe_allow_html=True)

    if st.button("＋ 新的对话", use_container_width=True, key="nc"):
        init_conv()
        st.rerun()

    st.caption("历史记录")
    convs = st.session_state.conversations
    if convs:
        for cid in sorted(convs.keys(), reverse=True)[:10]:
            title = convs[cid]["title"][:16]
            col_h, col_d = st.columns([4,1])
            with col_h:
                if st.button(f"💬 {title}…", key=f"h_{cid}", use_container_width=True):
                    st.session_state.current_conv = cid
                    st.rerun()
            with col_d:
                if st.button("🗑", key=f"del_{cid}"):
                    try:
                        requests.delete(f"{API_BASE}/conversations/{cid}", timeout=3)
                    except: pass
                    del st.session_state.conversations[cid]
                    if st.session_state.current_conv == cid:
                        st.session_state.current_conv = None
                    st.rerun()
    else:
        st.markdown('<div style="font-size:12px;color:#9CA3AF;padding:4px 8px">暂无历史</div>',
                    unsafe_allow_html=True)

    # 用 JS 注入把底部元素真正贴底
    st.markdown("""
<script>
(function() {
    function fixBottom() {
        var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"] > div:first-child');
        if (!sidebar) { setTimeout(fixBottom, 200); return; }
        var bottom = window.parent.document.getElementById('sidebar-bottom');
        if (!bottom) { setTimeout(fixBottom, 200); return; }
        sidebar.style.position = 'relative';
        sidebar.style.minHeight = '100vh';
        bottom.style.position = 'absolute';
        bottom.style.bottom = '0';
        bottom.style.left = '0';
        bottom.style.right = '0';
        bottom.style.background = 'white';
        bottom.style.padding = '12px 14px 16px';
        bottom.style.borderTop = '1px solid #F3F4F6';
    }
    setTimeout(fixBottom, 500);
})();
</script>
""", unsafe_allow_html=True)
    st.markdown('<div id="sidebar-bottom">', unsafe_allow_html=True)
    st.divider()

    # 用户信息 + 按钮
    st.markdown(f'<div style="font-size:13px;color:#374151;font-weight:500;padding:4px 0 8px">👤 {st.session_state.username}</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 主页", use_container_width=True, key="home"):
            st.markdown('<meta http-equiv="refresh" content="0;url=https://alphastock.cloud">',
                        unsafe_allow_html=True)
            st.stop()
    with col2:
        if st.button("退出", use_container_width=True, key="logout"):
            logout_dialog()

    if st.button("⇄ 切换用户", use_container_width=True, key="switch"):
        switch_dialog()

    # 确认弹窗
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("_confirm"):
        action = st.session_state._confirm
        label = "退出登录" if action == "logout" else "切换用户"
        st.warning(f"确定要{label}吗？")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 确认", use_container_width=True, key="confirm_yes"):
                st.session_state._confirm = None
                st.session_state.token = None
                st.session_state.username = None
                st.session_state.conversations = {}
                st.session_state.current_conv = None
                url = "https://alphastock.cloud?switch=1" if action == "switch" else "https://alphastock.cloud"
                st.markdown(f'<meta http-equiv="refresh" content="0;url={url}">',
                            unsafe_allow_html=True)
                st.stop()
        with c2:
            if st.button("❌ 取消", use_container_width=True, key="confirm_no"):
                st.session_state._confirm = None
                st.rerun()

# ── 主内容 ────────────────────────────────────────────────────────────
cid = st.session_state.current_conv
msgs = st.session_state.conversations.get(cid, {}).get("messages", []) if cid else []

if not msgs:
    st.markdown("""
<div style="padding:40px 0 32px">
  <h1 style="font-size:40px;font-weight:800;color:#111827;line-height:1.1;letter-spacing:-1.5px;margin-bottom:14px">
    Meet Your AI<br>
    <span style="background:linear-gradient(90deg,#6366F1,#A855F7);-webkit-background-clip:text;-webkit-text-fill-color:transparent">
      Trading Partner
    </span>
  </h1>
  <p style="color:#6B7280;font-size:15px;margin-bottom:32px">输入 6 位股票代码，AI 从多个视角同时分析，给出明确的投资建议。</p>
</div>
""", unsafe_allow_html=True)
    st.caption("🔥 快速分析")
    cc = st.columns(4)
    for col, (code, name) in zip(cc, [("600150","中国船舶"),("300308","中际旭创"),("002261","拓维信息"),("601088","中国神华")]):
        with col:
            if st.button(f"{code}\n{name}", key=f"chip_{code}", use_container_width=True):
                if not st.session_state.current_conv:
                    init_conv()
                st.session_state._pending = code
                st.rerun()

for m in msgs:
    if m["role"] == "user":
        pre = f'<div style="font-size:11px;color:#6366F1;margin-bottom:4px;text-align:right">📎 {m.get("file_name","")}</div>' if m.get("has_file") else ""
        st.markdown(f'{pre}<div class="bubble-u"><div>{m["content"]}</div></div>', unsafe_allow_html=True)
    elif m["role"] == "assistant":
        if m.get("type") == "analysis":
            data = m.get("data", {})
            dtxt = data.get("decision", "")
            badge = "🔴 买入建议" if "买入" in dtxt else ("🟢 减仓提示" if ("减仓" in dtxt or "卖出" in dtxt) else "🟡 观望状态")
            st.markdown(f"""
<div class="bubble-a"><div class="av">A</div>
<div style="flex:1;min-width:0;background:white;border:1px solid #E5E7EB;border-radius:12px;padding:20px">
  <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #F3F4F6;padding-bottom:12px;margin-bottom:16px">
    <span style="font-size:18px;font-weight:700">{data.get("stock_code","标的")} {data.get("stock_name","")} 投研报告</span>
    <span style="font-size:13px;font-weight:700">{badge}</span>
  </div>
""", unsafe_allow_html=True)
            t1, t2, t3, t4, t5 = st.tabs(["💼 核心决策","📊 基本面","📈 技术面","📰 情绪","🔬 辩论日志"])
            with t1: st.markdown(dtxt or "等待生成…")
            with t2: st.markdown(data.get("fundamental_report","无数据"))
            with t3: st.markdown(data.get("technical_report","无数据"))
            with t4: st.markdown(data.get("sentiment_report","无数据"))
            with t5:
                debate = data.get("researcher_analysis","[System] 等待初始化…")
                st.markdown(debate)
            st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bubble-a"><div class="av">A</div><div class="txt">{m["content"]}</div></div>', unsafe_allow_html=True)

if st.session_state._pending:
    code = st.session_state._pending
    st.session_state._pending = None
    if not st.session_state.current_conv:
        init_conv()
    cid = st.session_state.current_conv
    msgs2 = st.session_state.conversations[cid]["messages"]
    if not msgs2 or msgs2[-1].get("content","") != code:
        msgs2.append({"role":"user","content":f"请针对标的 {code} 生成完整的研报及决策建议。"})
    with st.spinner(f"AI 正在分析 {code}，请稍候…"):
        try:
            r = requests.post(f"{API_BASE}/analyze",
                json={"stock_code":code,"model":"smart","token":st.session_state.token}, timeout=300)
            if r.status_code == 200:
                data = r.json()
                msgs2.append({"role":"assistant","type":"analysis","data":data})
                d = data.get("decision","")
                act = "买入" if "买入" in d else ("减仓" if "减仓" in d else "观望")
                st.session_state.conversations[cid]["title"] = f"{code} [{act}]"
                # 保存到后端
                try:
                    requests.post(f"{API_BASE}/conversations/save", json={
                        "id": cid,
                        "username": st.session_state.username,
                        "title": st.session_state.conversations[cid]["title"],
                        "messages": msgs2
                    }, timeout=5)
                except: pass
            else:
                msgs2.append({"role":"assistant","type":"text","content":f"请求失败：{r.json().get('detail','未知')}"})
        except Exception as e:
            msgs2.append({"role":"assistant","type":"text","content":f"网络异常：{e}"})
    st.rerun()

prompt = st.chat_input("输入股票代码（如 600150）或投资疑问…",
    accept_file="multiple", file_type=["png","jpg","jpeg","webp","pdf","csv","txt"])
if prompt:
    text = prompt.text or ""
    files = prompt.files or []
    if not st.session_state.current_conv:
        init_conv()
    cid = st.session_state.current_conv
    file_name = " / ".join(f.name for f in files) if files else ""
    st.session_state.conversations[cid]["messages"].append({
        "role":"user","content": text if text else f"（附件 {file_name}）",
        "has_file": bool(files),"file_name": file_name,
    })
    # 自动命名：用第一条消息内容作为标题
    user_msgs = [m for m in st.session_state.conversations[cid]["messages"] if m["role"]=="user"]
    if len(user_msgs) == 1:
        title = (text or file_name)[:16]
        st.session_state.conversations[cid]["title"] = title if title else "新对话"

    codes = re.findall(r"\b\d{6}\b", text)
    if codes:
        st.session_state._pending = codes[0]
    else:
        st.session_state.conversations[cid]["messages"].append({
            "role":"assistant","type":"text",
            "content":"请直接输入 6 位股票代码（例如 **600150**）即可触发分析。",
        })
    st.rerun()
