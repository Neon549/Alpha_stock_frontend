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
pages/4_scan.py  ──  🎯 今日买点扫描
"""
import streamlit as st
import requests
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.common import API_BASE, MAIN_CSS, require_auth, render_sidebar

st.set_page_config(
    page_title="AlphaStock · 今日买点",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()
st.markdown(MAIN_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown("### 市场今日异动扫描")
st.caption("全市场技术面超卖买点 · 市值 ≥ 300 亿")

sc1, sc2 = st.columns([2, 1])
with sc1:
    bs = st.text_input("扫描起始日期", "20230101")
with sc2:
    tn = st.slider("结果上限", 5, 20, 10)

if st.button("📡 发射扫描探针", use_container_width=True):
    with st.spinner("全市场扫描中（约 5 分钟）…"):
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
                    f"筛选池 {data['total_candidates']} 支 · 触发 {data['count']} 支"
                )
                for x in recs:
                    ic = "🔴" if x["confidence"] == "高" else "🟡"
                    with st.expander(
                        f"{ic} {x['name']} ({x['code']}) — {x['decision']}"
                    ):
                        st.metric("触发日价格", f"¥{x['close']}")
                        st.markdown(
                            f'<div class="terminal-box">{x["report"]}</div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.error(r.json().get("detail", "未知"))
        except Exception as e:
            st.error(f"探针离线：{e}")
