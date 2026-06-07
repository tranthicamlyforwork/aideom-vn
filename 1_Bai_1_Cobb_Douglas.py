import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Bài 1 - Cobb-Douglas", layout="wide", page_icon="📈")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.block-container{padding-top:2rem;}
.sec{background:#1e2235;border-radius:10px;padding:16px 20px;margin:12px 0;border-left:4px solid #3949ab;}
.kv{font-size:28px;font-weight:700;color:#ff4b4b;}
.kl{font-size:12px;color:#888;margin-top:4px;}
</style>""", unsafe_allow_html=True)

st.title("📈 Bài 1 — Hàm Sản Xuất Cobb-Douglas Mở Rộng")
st.caption("Yₜ = Aₜ · Kₜᵅ · Lₜᵝ · Dₜᵞ · AIₜᵟ · Hₜᶿ  |  Dữ liệu Việt Nam 2020–2025")

# Sidebar
with st.sidebar:
    st.header("⚙️ Tham số")
    alpha = st.slider("α — Vốn K", 0.10, 0.60, 0.33, 0.01)
    beta  = st.slider("β — Lao động L", 0.10, 0.60, 0.42, 0.01)
    gamma = st.slider("γ — Số hóa D", 0.01, 0.30, 0.10, 0.01)
    delta = st.slider("δ — AI", 0.01, 0.20, 0.08, 0.01)
    theta = st.slider("θ — Nhân lực H", 0.01, 0.20, 0.07, 0.01)
    total = round(alpha+beta+gamma+delta+theta, 2)
    if abs(total-1.0) < 0.01: st.success(f"✅ Tổng = {total:.2f}")
    else: st.error(f"❌ Tổng = {total:.2f} ≠ 1.00")
    st.divider()
    st.markdown("**Kịch bản 2030**")
    D30  = st.slider("Kinh tế số (%)", 20.0, 40.0, 30.0, 0.5)
    AI30 = st.slider("DN số (nghìn)", 80.0, 150.0, 100.0, 1.0)
    H30  = st.slider("LĐ qua ĐT (%)", 29.0, 45.0, 35.0, 0.5)
    gKL  = st.slider("Tăng K,L (%/năm)", 3.0, 10.0, 6.0, 0.5)/100
    gTFP = st.slider("Tăng TFP (%/năm)", 0.5, 3.0, 1.2, 0.1)/100

years = np.array([2020,2021,2022,2023,2024,2025])
Y  = np.array([8044.4,8487.5,9513.3,10221.8,11511.9,12847.6])
K  = np.array([16500,17800,19600,21300,23500,25900])
L  = np.array([53.6,50.5,51.7,52.4,52.9,53.4])
D  = np.array([12.0,12.7,14.3,16.5,18.3,19.5])
AI = np.array([55.6,60.2,65.4,67.0,73.8,80.1])
H  = np.array([24.1,26.1,26.2,27.0,28.4,29.2])

A = Y / (K**alpha * L**beta * D**gamma * AI**delta * H**theta)
A_mean = np.mean(A)
Y_hat = A_mean * (K**alpha)*(L**beta)*(D**gamma)*(AI**delta)*(H**theta)
mape = float(np.mean(np.abs((Y-Y_hat)/Y))*100)

tab1,tab2,tab3,tab4 = st.tabs(["1️⃣ TFP","2️⃣ Dự báo & MAPE","3️⃣ Phân rã tăng trưởng","4️⃣ Dự báo 2030"])

with tab1:
    st.subheader("Câu 1.4.1 — TFP theo năm")
    c1,c2,c3 = st.columns(3)
    c1.metric("TFP 2020", f"{A[0]:.3f}")
    c2.metric("TFP 2025", f"{A[-1]:.3f}")
    c3.metric("Thay đổi", f"{(A[-1]-A[0])/A[0]*100:+.2f}%")
    fig = go.Figure(go.Scatter(x=years, y=A, mode="lines+markers+text",
        line=dict(color="#3949ab",width=3), marker=dict(size=10),
        text=[f"{a:.3f}" for a in A], textposition="top center",
        fill="tozeroy", fillcolor="rgba(57,73,171,0.1)"))
    fig.update_layout(title="TFP (Aₜ) — Việt Nam 2020–2025",
        plot_bgcolor="#1e2235", paper_bgcolor="#0f1117",
        font_color="white", height=380,
        xaxis=dict(tickvals=years.tolist(), gridcolor="#2a2d3e"),
        yaxis=dict(gridcolor="#2a2d3e"))
    st.plotly_chart(fig, use_container_width=True)
    df_t = pd.DataFrame({"Năm":years,"GDP (nghìn tỷ)":Y,"TFP":np.round(A,4),
        "Tăng TFP":["—"]+[f"{(A[i]-A[i-1])/A[i-1]*100:+.2f}%" for i in range(1,6)]})
    st.dataframe(df_t, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Câu 1.4.2 — Dự báo GDP & MAPE")
    c1,c2 = st.columns(2)
    c1.metric("A̅ trung bình", f"{A_mean:.4f}")
    c2.metric("MAPE", f"{mape:.2f}%", "Tốt ✅" if mape<5 else ("Khá 🟡" if mape<10 else "Chưa tốt ❌"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years,y=Y,mode="lines+markers",name="Thực tế",
        line=dict(color="#1565c0",width=3),marker=dict(size=9)))
    fig.add_trace(go.Scatter(x=years,y=Y_hat,mode="lines+markers",name="Dự báo",
        line=dict(color="#c62828",width=2.5,dash="dash"),marker=dict(size=9,symbol="triangle-up")))
    fig.update_layout(title=f"GDP Thực tế vs Dự báo — MAPE={mape:.2f}%",
        plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=380,
        xaxis=dict(tickvals=years.tolist(),gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
    st.plotly_chart(fig, use_container_width=True)
    df_fc = pd.DataFrame({"Năm":years,"Thực tế":np.round(Y,1),"Dự báo":np.round(Y_hat,1),
        "Sai số (%)":np.round(np.abs((Y-Y_hat)/Y)*100,2)})
    st.dataframe(df_fc, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Câu 1.4.3 — Phân rã tăng trưởng 2020–2025")
    def gr(x): return np.diff(np.log(x))
    gY=gr(Y);gK=gr(K);gL=gr(L);gD=gr(D);gAI=gr(AI);gH=gr(H);gA=gr(A)
    cK=alpha*gK;cL=beta*gL;cD=gamma*gD;cAI=delta*gAI;cH=theta*gH;cTFP=gA
    periods=[f"{years[i]}→{years[i+1]}" for i in range(5)]
    avgs={"TFP":float(np.mean(cTFP)*100),"Vốn K":float(np.mean(cK)*100),
          "Số hóa D":float(np.mean(cD)*100),"AI":float(np.mean(cAI)*100),
          "Nhân lực H":float(np.mean(cH)*100),"Lao động L":float(np.mean(cL)*100)}
    colors=["#00c47a","#1565c0","#ff9800","#9c27b0","#f44336","#607d8b"]
    fig=go.Figure()
    for arr,lbl,clr in zip([cTFP,cK,cD,cAI,cH,cL],list(avgs.keys()),colors):
        fig.add_trace(go.Bar(x=periods,y=arr*100,name=lbl,marker_color=clr,opacity=0.85))
    fig.add_trace(go.Scatter(x=periods,y=gY*100,mode="lines+markers",
        line=dict(color="white",width=2),marker=dict(size=8),name="GDP growth"))
    fig.update_layout(barmode="relative",title="Phân rã tăng trưởng GDP (%)",
        plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=420,
        xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e",zeroline=True,zerolinecolor="#555"),
        legend=dict(orientation="h",y=-0.25))
    st.plotly_chart(fig, use_container_width=True)
    df_avg=pd.DataFrame({"Nhân tố":list(avgs.keys()),
        "Đóng góp TB (%/năm)":[round(v,3) for v in avgs.values()],
        "Tỷ trọng (%)":[round(v/float(np.mean(gY)*100)*100,1) for v in avgs.values()]})
    st.dataframe(df_avg, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Câu 1.4.4 — Dự báo GDP 2030")
    n=5; K25=K[-1]; L25=L[-1]; A25=A[-1]
    ty=[Y[-1]]
    for t in range(1,n+1):
        Kt=K25*(1+gKL)**t; Lt=L25*(1+gKL)**t; At=A25*(1+gTFP)**t
        Dt=D[-1]+(D30-D[-1])/n*t; AIt=AI[-1]+(AI30-AI[-1])/n*t; Ht=H[-1]+(H30-H[-1])/n*t
        ty.append(At*(Kt**alpha)*(Lt**beta)*(Dt**gamma)*(AIt**delta)*(Ht**theta))
    Y30=ty[-1]; gr_avg=(Y30/Y[-1])**(1/n)-1
    c1,c2,c3 = st.columns(3)
    c1.metric("GDP 2025",f"{Y[-1]:,.0f} ng.tỷ")
    c2.metric("GDP 2030 dự báo",f"{Y30:,.0f} ng.tỷ")
    c3.metric("Tăng trưởng TB",f"{gr_avg*100:.2f}%/năm")
    ty_years=list(range(2025,2031))
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=list(years),y=list(Y),mode="lines+markers",name="Thực tế 2020–2025",
        line=dict(color="#1565c0",width=3),marker=dict(size=9)))
    fig.add_trace(go.Scatter(x=ty_years,y=ty,mode="lines+markers",name="Dự báo 2025–2030",
        line=dict(color="#c62828",width=3,dash="dot"),marker=dict(size=9,symbol="triangle-up")))
    fig.add_vline(x=2025,line_dash="dash",line_color="#555")
    fig.update_layout(title="Quỹ đạo GDP Việt Nam 2020–2030",
        plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=420,
        xaxis=dict(tickvals=list(range(2020,2031)),gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("""<div class="sec">
<b>💬 Thảo luận chính sách</b><br><br>
<b>a)</b> TFP tăng +25,83% → chất lượng tăng trưởng cải thiện, nhưng vốn K vẫn chiếm 31,8% → chưa thoát khỏi tăng trưởng chiều rộng.<br>
<b>b)</b> Số hóa D đóng góp nhiều nhất (10,4%) trong 3 yếu tố mới. Nhân lực H là điểm nghẽn (chỉ 2,9%).<br>
<b>c)</b> Mục tiêu 30% kinh tế số/GDP 2030 KHẢ THI nhưng cần ưu tiên đào tạo nhân lực số và cải cách thể chế.
</div>""", unsafe_allow_html=True)
