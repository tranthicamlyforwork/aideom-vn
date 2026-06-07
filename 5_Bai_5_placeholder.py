import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bài 5", layout="wide", page_icon="📊")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.coming{background:#1e2235;border-radius:12px;padding:40px;text-align:center;margin:40px 0;border:2px dashed #2a2d3e;}
</style>""", unsafe_allow_html=True)

import pulp
st.title("🎯 Bài 5 — MIP Lựa Chọn 15 Dự Án Chuyển Đổi Số")
st.caption("Bài toán knapsack nhị phân: max ΣBᵢ·yᵢ | Ngân sách 80.000 tỷ VND")

P=list(range(1,16))
C={1:12000,2:11500,3:18000,4:4500,5:3200,6:5800,7:6500,8:15000,9:2500,10:7200,11:4800,12:8500,13:20000,14:3800,15:1500}
C1={1:8500,2:7500,3:12000,4:3500,5:2500,6:4000,7:4500,8:9000,9:1800,10:5000,11:3500,12:5500,13:13000,14:2800,15:1200}
B={1:21500,2:20800,3:32500,4:9200,5:6800,6:11400,7:12200,8:28500,9:5800,10:13800,11:8500,12:16200,13:35000,14:7500,15:3800}
NAMES={1:"TTDL Hòa Lạc",2:"TTDL phía Nam",3:"5G toàn quốc",4:"VNeID 2.0",5:"Cổng DVC v3",
    6:"Y tế số",7:"Giáo dục số K-12",8:"Trung tâm AI QG",9:"Sandbox fintech",
    10:"Logistics thông minh",11:"Nông nghiệp số ĐBSCL",12:"Đào tạo 50k kỹ sư AI",
    13:"KCN bán dẫn Bắc Ninh",14:"An ninh mạng SOC",15:"Open Data QG"}

with st.sidebar:
    budget = st.slider("Ngân sách tổng (tỷ)", 60000, 120000, 80000, 1000)
    budget1 = st.slider("Ngân sách năm 1-2 (tỷ)", 30000, 60000, 40000, 1000)
    run = st.button("🚀 Giải MIP", type="primary")

col1,col2 = st.columns(2)
with col1:
    st.markdown("**📋 Danh sách 15 dự án**")
    df_proj = pd.DataFrame({"Mã":[f"P{i}" for i in P],"Tên":[NAMES[i] for i in P],
        "Chi phí (tỷ)":[C[i] for i in P],"Lợi ích NPV":[B[i] for i in P],
        "ROI":[round(B[i]/C[i],2) for i in P]})
    st.dataframe(df_proj, use_container_width=True, hide_index=True)
with col2:
    if run:
        with st.spinner("Đang giải MIP..."):
            m=pulp.LpProblem('VN_Projects',pulp.LpMaximize)
            y=pulp.LpVariable.dicts('y',P,cat='Binary')
            m+=pulp.lpSum(B[i]*y[i] for i in P)
            m+=pulp.lpSum(C[i]*y[i] for i in P)<=budget
            m+=pulp.lpSum(C1[i]*y[i] for i in P)<=budget1
            m+=y[1]+y[2]<=1; m+=y[8]<=y[12]; m+=y[13]<=y[12]
            m+=y[4]+y[5]>=1; m+=y[14]>=1
            m+=pulp.lpSum(y[i] for i in P)>=7; m+=pulp.lpSum(y[i] for i in P)<=11
            m.solve(pulp.PULP_CBC_CMD(msg=False))
        if pulp.LpStatus[m.status]=='Optimal':
            selected=[i for i in P if pulp.value(y[i])>0.5]
            Z=pulp.value(m.objective)
            st.success(f"✅ Z* = {Z:,.0f} tỷ VND | {len(selected)} dự án được chọn")
            st.metric("Tổng chi phí",f"{sum(C[i] for i in selected):,} tỷ")
            st.metric("ROI tổng hợp",f"{Z/sum(C[i] for i in selected):.3f}")
            df_sel=pd.DataFrame({"Mã":[f"P{i}" for i in selected],"Tên":[NAMES[i] for i in selected],
                "Chi phí":[C[i] for i in selected],"Lợi ích":[B[i] for i in selected]})
            st.dataframe(df_sel,use_container_width=True,hide_index=True)
            fig=go.Figure(go.Bar(x=[f"P{i}" for i in selected],y=[B[i] for i in selected],
                marker_color="#00c47a",opacity=0.85,text=[B[i] for i in selected],textposition="outside"))
            fig.update_layout(title="Lợi ích NPV các dự án được chọn",
                plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=350,
                xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
            st.plotly_chart(fig,use_container_width=True)
    else:
        st.info("👈 Click **Giải MIP** để tìm danh mục dự án tối ưu")
