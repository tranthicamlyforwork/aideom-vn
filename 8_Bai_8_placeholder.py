import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bài 8", layout="wide", page_icon="📊")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.sec{background:#1e2235;border-radius:10px;padding:20px;margin:12px 0;border-left:4px solid #7b1fa2;}
</style>""", unsafe_allow_html=True)
st.title("⏳ Bài 8 — Tối Ưu Động Phân Bổ 2026-2035")
st.caption("Tối ưu hóa liên thời gian 10 năm: max Σ ρᵗ·U(Cₜ) | Cobb-Douglas + tích lũy vốn")

with st.sidebar:
    st.header("⚙️ Tham số")
    rho  = st.slider("ρ hệ số chiết khấu", 0.85, 0.99, 0.97, 0.01)
    dK   = st.slider("δK khấu hao vốn", 0.03, 0.10, 0.05, 0.01)
    dD   = st.slider("δD khấu hao số hóa", 0.05, 0.20, 0.12, 0.01)
    dAI  = st.slider("δAI khấu hao AI", 0.08, 0.25, 0.15, 0.01)
    phi1 = st.slider("φ₁ Số hóa→TFP", 0.001, 0.008, 0.003, 0.001)
    phi2 = st.slider("φ₂ AI→TFP", 0.001, 0.006, 0.002, 0.001)
    phi3 = st.slider("φ₃ NL→TFP", 0.001, 0.008, 0.004, 0.001)

T=10; years=list(range(2026,2036))
K0,D0_,AI0,H0,A0=27500,20.3,86,30,34.91
alpha,beta_,gamma,delta,theta=0.33,0.42,0.10,0.08,0.07
theta_H,mu=0.8,0.02

Ks=[K0]; Ds=[D0_]; AIs=[AI0]; Hs=[H0]; As=[A0]
Ys=[]; Cs=[]
budget_annual=1200

for t in range(T):
    Kt,Dt,AIt,Ht,At=Ks[-1],Ds[-1],AIs[-1],Hs[-1],As[-1]
    iK=budget_annual*0.35; iD=budget_annual*0.25; iAI=budget_annual*0.20; iH=budget_annual*0.20
    Yt=At*(Kt**alpha)*(54.0**beta_)*(Dt**gamma)*(AIt**delta)*(Ht**theta)
    Ct=Yt-iK-iD-iAI-iH
    Ys.append(Yt); Cs.append(max(Ct,0))
    Ks.append((1-dK)*Kt+iK); Ds.append((1-dD)*Dt+iD/100)
    AIs.append((1-dAI)*AIt+iAI/20); Hs.append(Ht+theta_H*iH/200-mu*Ht)
    As.append(At*(1+phi1*Dt+phi2*AIt+phi3*Ht))

welfare=sum(rho**t*np.log(max(c,1)) for t,c in enumerate(Cs))

c1,c2,c3=st.columns(3)
c1.metric("GDP 2035 (dự báo)",f"{Ys[-1]:,.0f} ng.tỷ")
c2.metric("Welfare tổng",f"{welfare:.2f}")
c3.metric("TFP 2035",f"{As[-1]:.3f}")

fig=go.Figure()
for vals,name,clr in [(Ys,"GDP",  "#00c47a"),(Cs,"Tiêu dùng","#ff9800"),
                      (Ks[:T],"Vốn K","#1565c0")]:
    fig.add_trace(go.Scatter(x=years[:len(vals)],y=vals,mode="lines+markers",
        name=name,line=dict(color=clr,width=2),marker=dict(size=7)))
fig.update_layout(title="Quỹ đạo tối ưu 2026–2035",
    plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=420,
    xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
st.plotly_chart(fig,use_container_width=True)

fig2=go.Figure()
for vals,name,clr in [(Ds[:T],"Số hóa D","#ff9800"),(AIs[:T],"AI capacity","#9c27b0"),
                      (Hs[:T],"Nhân lực H","#c62828")]:
    fig2.add_trace(go.Scatter(x=years[:len(vals)],y=vals,mode="lines+markers",
        name=name,line=dict(color=clr,width=2),marker=dict(size=7)))
fig2.update_layout(title="Tích lũy vốn số 2026–2035",
    plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=350,
    xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
st.plotly_chart(fig2,use_container_width=True)
