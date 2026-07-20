"""
streamlit_app.py  ──  入口，直接跳主界面
登录在落地页完成，token 通过 URL 参数传入
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.common import API_BASE, init_session

st.set_page_config(
    page_title="AlphaStock",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

# 读取 URL 参数中的 token
params = st.query_params
if "token" in params:
    st.session_state.token    = params["token"]
    st.session_state.username = params.get("username", "用户")
    # 清除 URL 参数
    st.query_params.clear()

# 没有 token → 跳回落地页
if not st.session_state.token:
    st.markdown("""
    <meta http-equiv="refresh" content="0;url=https://alphastock.cloud">
    <p>请先登录...</p>
    """, unsafe_allow_html=True)
    st.stop()

# 有 token → 直接进聊天主界面
st.switch_page("pages/1_chat.py")
