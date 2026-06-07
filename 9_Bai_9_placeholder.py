import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bài 9", layout="wide", page_icon="📊")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.sec{background:#1e2235;border-radius:10px;padding:20px;margin:12px 0;border-left:4px solid #7b1fa2;}
</style>""", unsafe_allow_html=True)
st.title("👷 Bài 9 — Tác Động AI Tới Thị Trường Lao Động")
st.caption("NetJobᵢ = NewJobᴬᴵᵢ + UpgradeJobᵢ − DisplacedJobᵢ ≥ 0 ∀i")

SECTORS=["Nông-Lâm-TS","CN chế biến","Xây dựng","Bán buôn-lẻ","Tài chính-NH","Logistics","CNTT","Giáo dục"]
L=np.array([13.20,11.50,4.80,7.80,0.55,1.95,0.62,2.15])
risk=np.array([18,42,25,38,52,35,28,22])/100
a1_=np.array([8.5,32.5,12.8,22.4,45.8,28.5,62.5,18.5])
b1=np.array([45,28,35,32,22,30,20,55])
c1_=np.array([5.2,62.4,18.5,48.2,72.5,42.8,32.5,12.5])
d1=np.array([50,32,42,38,26,36,24,62])

with st.sidebar:
    budget=st.slider("Ngân sách tổng (tỷ VND)",10000,50000,30000,1000)
    run=st.button("🚀 Tối ưu hóa",type="primary")

if run:
    try:
        import cvxpy as cp
        N=8
        x_AI=cp.Variable(N,nonneg=True); x_H=cp.Variable(N,nonneg=True)
        NewJob=cp.multiply(a1_,x_AI); Upgrade=cp.multiply(b1,x_H)
        Displaced=cp.multiply(cp.multiply(c1_,risk),x_AI)
        RetrainCap=cp.multiply(d1,x_H)
        NetJob=NewJob+Upgrade-Displaced
        constraints=[cp.sum(x_AI+x_H)<=budget, NetJob>=0, Displaced<=RetrainCap]
        prob=cp.Problem(cp.Maximize(cp.sum(NetJob)),constraints)
        prob.solve()
        if prob.status=="optimal":
            st.success(f"✅ Tổng NetJob = {prob.value:,.0f} việc làm ròng")
            df=pd.DataFrame({"Ngành":SECTORS,
                "x_AI (tỷ)":np.round(x_AI.value,1),"x_H (tỷ)":np.round(x_H.value,1),
                "NewJob":np.round((a1_*x_AI.value),0).astype(int),
                "Displaced":np.round((c1_*risk*x_AI.value),0).astype(int),
                "NetJob":np.round(NetJob.value,0).astype(int)})
            st.dataframe(df,use_container_width=True,hide_index=True)
            fig=go.Figure()
            fig.add_trace(go.Bar(name="NewJob",x=SECTORS,y=(a1_*x_AI.value),marker_color="#00c47a",opacity=0.85))
            fig.add_trace(go.Bar(name="Upgrade",x=SECTORS,y=(b1*x_H.value),marker_color="#1565c0",opacity=0.85))
            fig.add_trace(go.Bar(name="Displaced",x=SECTORS,y=-(c1_*risk*x_AI.value),marker_color="#c62828",opacity=0.85))
            fig.update_layout(barmode="relative",title="Luồng việc làm theo ngành",
                plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=420,
                xaxis=dict(tickangle=-20,gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e",zeroline=True,zerolinecolor="#555"))
            st.plotly_chart(fig,use_container_width=True)
    except Exception as e:
        st.error(f"Lỗi: {e}")
else:
    st.info("👈 Click **Tối ưu hóa** để chạy mô hình lao động")
    cols=st.columns(4)
    for i,(s,r) in enumerate(zip(SECTORS,risk)):
        cols[i%4].metric(s,f"Risk: {r*100:.0f}%")
