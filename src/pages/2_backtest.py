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
pages/2_backtest.py  ──  📊 量化回测
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.common import API_BASE, MAIN_CSS, require_auth, render_sidebar

st.set_page_config(
    page_title="AlphaStock · 量化回测",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()
st.markdown(MAIN_CSS, unsafe_allow_html=True)
render_sidebar()

# ── 页面内容 ─────────────────────────────────────────────────────────
st.markdown("### 智能量化回测引擎")
st.caption("基于 Backtrader 框架 · KDJ / RSI / 布林带 / MACD 五种策略")

c1, c2, c3, c4 = st.columns([1.2, 1.5, 0.9, 0.9])
with c1:
    code = st.text_input("目标标的代码", "600150")
with c2:
    strat = st.selectbox(
        "核心运行策略",
        ["kdj_oversold", "j_extreme", "rsi", "boll", "kdj_macd"],
        format_func=lambda x: {
            "kdj_oversold": "KDJ 超卖反弹",
            "j_extreme": "J线极值反转",
            "rsi": "RSI 相对强弱",
            "boll": "布林带突破",
            "kdj_macd": "KDJ+MACD 共振",
        }[x],
    )
with c3:
    sd = st.text_input("回测起点", "20240101")
with c4:
    ed = st.text_input("回测终点", "20260530")

if st.button("🚀 启动回测", use_container_width=True):
    with st.spinner("调取历史 K 线数据进行回测…"):
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
            st.error(f"引擎请求失败：{e}")

bt = st.session_state.get("bt_result")
if bt:
    st.markdown("#### 🎯 回测结果")
    tr = bt["total_return"]
    cs = st.columns(5)
    for col, (l, v) in zip(
        cs,
        [
            ("总收益", f"{tr:+.2f}%"),
            ("夏普比率", str(bt["sharpe"])),
            ("最大回撤", f"-{bt['max_drawdown']:.2f}%"),
            ("交易次数", str(bt["trade_count"])),
            ("胜率", f"{bt['win_rate']}%"),
        ],
    ):
        with col:
            st.metric(l, v)

    if bt.get("returns_data") and bt.get("dates_data"):
        cum = (
            (1 + pd.Series(bt["returns_data"], index=bt["dates_data"])).cumprod() - 1
        ) * 100
        fig = go.Figure(
            go.Scatter(
                x=cum.index,
                y=cum.values,
                mode="lines",
                line=dict(color="#8B5CF6", width=2),
                fill="tozeroy",
                fillcolor="rgba(139,92,246,0.1)",
            )
        )
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            height=300,
            margin=dict(l=40, r=20, t=20, b=40),
            showlegend=False,
            yaxis=dict(ticksuffix="%", gridcolor="#F3F4F6"),
            xaxis=dict(gridcolor="#F3F4F6"),
        )
        st.plotly_chart(fig, use_container_width=True)
