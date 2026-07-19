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
pages/1_chat.py  ──  🤖 AI 股票助手
"""
import re
import streamlit as st
import requests
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.common import (
    API_BASE,
    MODEL_OPTIONS,
    MAIN_CSS,
    require_auth,
    render_sidebar,
    new_conv,
    get_msgs,
)
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AlphaStock · AI助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# 侧边栏展开脚本
components.html(
    """<script>
const doc = window.parent.document;
let tries = 0;
const t = setInterval(() => {
    tries++;
    const sidebar = doc.querySelector('[data-testid="stSidebar"]');
    const btn     = doc.querySelector('[data-testid="stExpandSidebarButton"]');
    if (sidebar && sidebar.getAttribute('aria-expanded') !== 'false') { clearInterval(t); return; }
    if (btn) { btn.click(); clearInterval(t); return; }
    if (tries > 20) clearInterval(t);
}, 150);
</script>""",
    height=0,
)

render_sidebar()

# ── 空状态欢迎屏 ────────────────────────────────────────────────────
msgs = get_msgs()
if not msgs:
    st.markdown(
        """
<div style="padding:20px 0 40px">
  <h1 style="font-size:46px;font-weight:800;color:#111827;line-height:1.2;letter-spacing:-1px">
    Meet Your AI<br>
    <span style="background:linear-gradient(90deg,#6366F1,#A855F7);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent">
      Trading Partner
    </span>
  </h1>
  <p style="margin-top:12px;color:#6B7280">
    基于 LangGraph 多智能体与 DeepSeek R1 深度推理的下一代智能投研助手。
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.caption("🔥 快速分析热门标的")
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

# ── 渲染历史消息 ─────────────────────────────────────────────────────
for m in msgs:
    if m["role"] == "user":
        pre = (
            f'<div style="font-size:11px;color:#6366F1;margin-bottom:4px;text-align:right">'
            f'📎 {m.get("file_name","")}</div>'
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
                "🔴 买入建议"
                if "买入" in dtxt
                else (
                    "🟢 减仓提示"
                    if ("减仓" in dtxt or "卖出" in dtxt)
                    else "🟡 观望状态"
                )
            )
            mi = MODEL_OPTIONS.get(m.get("model", "smart"), {})
            st.markdown(
                f"""
<div class="bubble-a">
  <div class="av">A</div>
  <div style="flex:1;min-width:0;background:white;border:1px solid #E5E7EB;
              border-radius:12px;padding:20px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05)">
    <div style="display:flex;justify-content:space-between;align-items:center;
                border-bottom:1px solid #F3F4F6;padding-bottom:12px;margin-bottom:16px">
      <div>
        <span style="font-size:18px;font-weight:700;color:#111827">
          {data.get("stock_code","标的")} 投研报告
        </span><br>
        <span style="font-size:12px;color:#6B7280;font-family:monospace">
          Engine: {mi.get("desc","")} · Agent: Active
        </span>
      </div>
      <span style="font-size:13px;font-weight:700">{badge}</span>
    </div>
""",
                unsafe_allow_html=True,
            )
            t1, t2, t3, t4, t5 = st.tabs(
                ["💼 核心决策", "📊 基本面", "📈 技术面", "📰 情绪", "🔬 辩论日志"]
            )
            with t1:
                st.markdown(dtxt or "等待生成…")
            with t2:
                st.markdown(data.get("fundamental_report", "无数据"))
            with t3:
                st.markdown(data.get("technical_report", "无数据"))
            with t4:
                st.markdown(data.get("sentiment_report", "无数据"))
            with t5:
                st.markdown(
                    f'<div class="terminal-box">'
                    f'{data.get("researcher_analysis","[System] 等待辩论网络初始化…")}'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="bubble-a"><div class="av">A</div>'
                f'<div class="txt">{m["content"]}</div></div>',
                unsafe_allow_html=True,
            )

# ── 触发分析 ─────────────────────────────────────────────────────────
if st.session_state._pending:
    code = st.session_state._pending
    model = st.session_state.model
    st.session_state._pending = None
    if not st.session_state.current_conv:
        new_conv()
    cid = st.session_state.current_conv
    msgs2 = st.session_state.conversations[cid]["messages"]
    if not msgs2 or msgs2[-1].get("content", "") != code:
        msgs2.append(
            {"role": "user", "content": f"请针对标的 {code} 生成完整的研报及决策建议。"}
        )
    with st.spinner(
        f"AlphaStock Agent 正在调用 {MODEL_OPTIONS[model]['desc']} 分析 {code}…"
    ):
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
                msgs2.append(
                    {
                        "role": "assistant",
                        "type": "analysis",
                        "data": data,
                        "model": model,
                    }
                )
                d = data.get("decision", "")
                act = "买入" if "买入" in d else ("减仓" if "减仓" in d else "观望")
                st.session_state.conversations[cid]["title"] = f"分析 {code} [{act}]"
            else:
                msgs2.append(
                    {
                        "role": "assistant",
                        "type": "text",
                        "content": f"请求被拒绝：{r.json().get('detail','未知')}",
                    }
                )
        except Exception as e:
            msgs2.append(
                {"role": "assistant", "type": "text", "content": f"网络异常：{e}"}
            )
    st.rerun()

# ── 输入框 ────────────────────────────────────────────────────────────
prompt = st.chat_input(
    "输入股票代码（如 600150）或粘贴财报截图、输入投资疑问…",
    accept_file="multiple",
    file_type=["png", "jpg", "jpeg", "webp", "pdf", "csv", "txt"],
)
if prompt:
    text = prompt.text or ""
    files = prompt.files or []
    if not st.session_state.current_conv:
        new_conv()
    cid = st.session_state.current_conv
    file_name = " / ".join(f.name for f in files) if files else ""
    st.session_state.up_file = files[0] if files else None
    st.session_state.conversations[cid]["messages"].append(
        {
            "role": "user",
            "content": text if text else f"（附件 {file_name}）",
            "has_file": bool(files),
            "file_name": file_name,
        }
    )
    codes = re.findall(r"\b\d{6}\b", text)
    if codes:
        st.session_state._pending = codes[0]
    else:
        st.session_state.conversations[cid]["messages"].append(
            {
                "role": "assistant",
                "type": "text",
                "content": "请直接输入 6 位股票代码（例如 **600150**）即可触发分析。",
            }
        )
    st.rerun()
