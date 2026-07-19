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
pages/3_alpha.py  ──  ✨ Alpha 多因子选股
"""
import streamlit as st
import requests
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.common import API_BASE, SECTORS, MAIN_CSS, require_auth, render_sidebar

st.set_page_config(
    page_title="AlphaStock · Alpha选股",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()
st.markdown(MAIN_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown("### Alpha 多因子打分模型")
st.caption("总分 100 · ≥75 重点配置 · 60-74 跟踪观察 · <60 规避")

ac1, ac2, ac3 = st.columns([2, 1, 1])
with ac1:
    sector = st.selectbox("资产池", ["全部（A股动态池）"] + list(SECTORS.keys()))
with ac2:
    ms = st.slider("最低分", 50, 90, 60)
with ac3:
    tn = st.slider("最大数量", 5, 30, 15)

if st.button("⚡ 提交多因子运算", use_container_width=True):
    payload = {"min_score": ms, "top_n": tn}
    if sector != "全部（A股动态池）":
        payload["sector"] = sector
    with st.spinner("并行打分中（约 2-5 分钟）…"):
        try:
            r = requests.post(f"{API_BASE}/alpha/score", json=payload, timeout=600)
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                st.success(
                    f"遍历 {data['total_scored']} 支 · 符合 {data['qualified']} 支"
                )
                if results:
                    rows = [
                        {
                            "代码": x["stock_code"],
                            "名称": x["stock_name"],
                            "总分": x["total_score"],
                            "评级": x["rating"],
                            "KDJ": x["factors"]["kdj"]["score"],
                            "量能": x["factors"]["volume"]["score"],
                            "ROE": x["factors"]["roe"]["score"],
                            "市值": x["factors"]["market_cap"]["score"],
                            "趋势": x["factors"]["trend"]["score"],
                        }
                        for x in results
                    ]
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
                    st.warning("无标的通过门槛")
            else:
                st.error(r.json().get("detail", "未知"))
        except Exception as e:
            st.error(f"通信异常：{e}")
