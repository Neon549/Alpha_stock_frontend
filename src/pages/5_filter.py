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
pages/5_filter.py  ──  🔍 板块筛选
"""
import streamlit as st
import requests
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.common import API_BASE, SECTORS, MAIN_CSS, require_auth, render_sidebar

st.set_page_config(
    page_title="AlphaStock · 板块筛选",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()
st.markdown(MAIN_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown("### 细分板块多维筛查")
st.caption("基于景气周期及 PE / ROE 估值的综合优选")

fc1, fc2, fc3 = st.columns([2, 1, 1])
with fc1:
    sector = st.selectbox("监控板块", list(SECTORS.keys()))
with fc2:
    ms = st.slider("及格线", 50, 90, 65)
with fc3:
    tn = st.slider("优选席位", 3, 10, 5)

if st.button("🔍 执行板块过滤", use_container_width=True):
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
                            "综合分": x["score"],
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
                        "综合分": st.column_config.ProgressColumn(
                            "综合分", min_value=0, max_value=100
                        )
                    },
                )
            else:
                st.warning("暂无标的达到评级")
        else:
            st.error("接口异常")
    except Exception as e:
        st.error(f"连接失败：{e}")
