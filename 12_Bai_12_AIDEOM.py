import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Bài 12 - AIDEOM-VN", layout="wide", page_icon="🇻🇳")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.kpi{background:#1e2235;border-radius:10px;padding:14px 18px;border:1px solid #2a2d3e;}
.kv{font-size:26px;font-weight:700;color:#ff4b4b;}
.kl{font-size:12px;color:#888;}
.sec{background:#1e2235;border-radius:10px;padding:16px 20px;margin:10px 0;border-left:4px solid #7b1fa2;}
.mod{background:#16213e;border-radius:8px;padding:12px 16px;margin:6px 0;border:1px solid #2a2d3e;}
</style>""", unsafe_allow_html=True)

st.title("🇻🇳 Bài 12 — AIDEOM-VN Hệ Thống Tích Hợp")
st.caption("AI-Driven Decision Optimization Model for Vietnam | 6 Modules | 5 Kịch bản chính sách")

# ── DỮ LIỆU CHUNG ────────────────────────────────────────────────────────────
years = np.array([2020,2021,2022,2023,2024,2025])
Y  = np.array([8044.4,8487.5,9513.3,10221.8,11511.9,12847.6])
K  = np.array([16500,17800,19600,21300,23500,25900])
L  = np.array([53.6,50.5,51.7,52.4,52.9,53.4])
D  = np.array([12.0,12.7,14.3,16.5,18.3,19.5])
AI = np.array([55.6,60.2,65.4,67.0,73.8,80.1])
H  = np.array([24.1,26.1,26.2,27.0,28.4,29.2])
alpha,beta,gamma,delta,theta = 0.33,0.42,0.10,0.08,0.07
A = Y/(K**alpha*L**beta*D**gamma*AI**delta*H**theta)

REGIONS=["Trung du MN Bắc","ĐB sông Hồng","Bắc TB+DH Trung","Tây Nguyên","Đông Nam Bộ","ĐB sông CL"]
SECTORS=["Nông-Lâm-TS","CN chế biến","Xây dựng","Bán buôn-lẻ","Tài chính-NH","Logistics","CNTT","Giáo dục"]

# 5 kịch bản
SCENARIOS = {
    "S1 — Truyền thống":   {"K":0.70,"D":0.10,"AI":0.10,"H":0.10,"color":"#607d8b","icon":"🏗️"},
    "S2 — Số hóa nhanh":   {"K":0.25,"D":0.45,"AI":0.15,"H":0.15,"color":"#1565c0","icon":"💻"},
    "S3 — AI dẫn dắt":     {"K":0.20,"D":0.20,"AI":0.45,"H":0.15,"color":"#7b1fa2","icon":"🤖"},
    "S4 — Bao trùm số":    {"K":0.30,"D":0.20,"AI":0.10,"H":0.40,"color":"#2e7d32","icon":"🤝"},
    "S5 — Tối ưu cân bằng":{"K":0.35,"D":0.25,"AI":0.20,"H":0.20,"color":"#ff6f00","icon":"⚖️"},
}

with st.sidebar:
    st.header("⚙️ Tham số hệ thống")
    budget_total = st.slider("Ngân sách tổng (tỷ VND)", 30000, 150000, 80000, 5000)
    n_years_proj = st.slider("Thời gian dự báo (năm)", 3, 10, 5, 1)
    gTFP = st.slider("Tăng trưởng TFP (%/năm)", 0.5, 3.0, 1.2, 0.1)/100
    gKL  = st.slider("Tăng K & L (%/năm)", 3.0, 10.0, 6.0, 0.5)/100
    D_target  = st.slider("Mục tiêu kinh tế số (%)", 20.0, 40.0, 30.0, 0.5)
    AI_target = st.slider("Mục tiêu DN số (nghìn)", 80.0, 150.0, 100.0, 2.0)
    H_target  = st.slider("Mục tiêu NL qua ĐT (%)", 29.0, 45.0, 35.0, 0.5)
    st.divider()
    selected_s = st.selectbox("Xem chi tiết kịch bản:", list(SCENARIOS.keys()))

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "📊 Tổng quan (M1-M2)",
    "💰 Phân bổ (M3)",
    "⚖️ 5 Kịch bản (M6)",
    "⚠️ Cảnh báo rủi ro (M4-M5)",
    "📋 Bảng tổng hợp KPI",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — TỔNG QUAN M1 + M2
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### M1 — Dự báo kinh tế (Cobb-Douglas)")
    if st.button("▶ Chạy M1", type="primary"):
        st.session_state["m1_run"] = True

    A_mean = np.mean(A)
    Y_hat  = A_mean*(K**alpha)*(L**beta)*(D**gamma)*(AI**delta)*(H**theta)
    mape   = float(np.mean(np.abs((Y-Y_hat)/Y))*100)

    # Dự báo theo kịch bản được chọn
    sc = SCENARIOS[selected_s]
    K25,L25,A25 = K[-1],L[-1],A[-1]
    traj_y=[Y[-1]]; n=n_years_proj
    for t in range(1,n+1):
        Kt=K25*(1+gKL)**t; Lt=L25*(1+gKL)**t; At=A25*(1+gTFP)**t
        Dt=D[-1]+(D_target-D[-1])/n*t; AIt=AI[-1]+(AI_target-AI[-1])/n*t; Ht=H[-1]+(H_target-H[-1])/n*t
        # Điều chỉnh theo kịch bản
        boost = 1 + sc["D"]*0.05 + sc["AI"]*0.08 + sc["H"]*0.04
        Yt=At*(Kt**alpha)*(Lt**beta)*(Dt**gamma)*(AIt**delta)*(Ht**theta)*boost
        traj_y.append(Yt)
    Y_end = traj_y[-1]
    gr_avg = (Y_end/Y[-1])**(1/n)-1

    c1,c2,c3 = st.columns(3)
    c1.markdown(f'<div class="kpi"><div class="kl">MAPE (Cobb-Douglas)</div><div class="kv">{mape:.2f}%</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi"><div class="kl">Ā trung bình TFP</div><div class="kv">{A_mean:.4f}</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi"><div class="kl">Y {2025+n} dự báo</div><div class="kv">{Y_end:,.0f} ng.tỷ</div></div>',unsafe_allow_html=True)

    st.markdown("---")
    col_l,col_r = st.columns(2)
    with col_l:
        # Phân rã tăng trưởng
        def gr(x): return np.diff(np.log(x))
        gY=gr(Y);gK=gr(K);gL=gr(L);gD=gr(D);gAI_=gr(AI);gH=gr(H);gA=gr(A)
        avgs={"TFP":float(np.mean(gA)*100),"Vốn K":float(np.mean(alpha*gK)*100),
              "Số hóa D":float(np.mean(gamma*gD)*100),"AI":float(np.mean(delta*gAI_)*100),
              "NL số H":float(np.mean(theta*gH)*100),"Lao động L":float(np.mean(beta*gL)*100)}
        clrs=["#00c47a","#1565c0","#ff9800","#9c27b0","#c62828","#607d8b"]
        fig=go.Figure(go.Bar(x=list(avgs.keys()),y=list(avgs.values()),
            marker_color=clrs,opacity=0.85,
            text=[f"{v:.2f}%" for v in avgs.values()],textposition="outside"))
        fig.update_layout(title="Phân rã đóng góp tăng trưởng 2020-2025",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=340,
            yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig,use_container_width=True)

    with col_r:
        # Quỹ đạo GDP
        proj_years=list(range(2025,2026+n))
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=list(years),y=list(Y),mode="lines+markers",name="Thực tế",
            line=dict(color="#1565c0",width=3),marker=dict(size=8)))
        fig.add_trace(go.Scatter(x=proj_years,y=traj_y,mode="lines+markers",
            name=f"{selected_s}",line=dict(color=sc["color"],width=3,dash="dot"),
            marker=dict(size=8,symbol="triangle-up")))
        fig.add_vline(x=2025,line_dash="dash",line_color="#555")
        fig.update_layout(title=f"Dự báo GDP — {selected_s}",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=340,
            xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig,use_container_width=True)

    st.markdown("### M2 — Đánh giá sẵn sàng số (TOPSIS)")
    X_r=np.array([[57.0,3.5,38,22,21.5,0.18,72,0.405],[152.3,20.0,78,68,36.8,0.85,92,0.358],
                  [87.5,8.2,55,40,27.5,0.32,84,0.372],[68.9,0.8,32,18,18.2,0.15,68,0.412],
                  [158.9,18.5,82,75,42.5,0.78,94,0.385],[80.5,2.1,48,30,16.8,0.22,78,0.392]])
    w_t=np.array([0.10,0.10,0.15,0.20,0.15,0.15,0.05,0.10])
    is_b=[True,True,True,True,True,True,True,False]
    R=X_r/np.sqrt((X_r**2).sum(0)); V=R*w_t
    Ap=np.where(is_b,V.max(0),V.min(0)); An=np.where(is_b,V.min(0),V.max(0))
    Sp=np.sqrt(((V-Ap)**2).sum(1)); Sn=np.sqrt(((V-An)**2).sum(1))
    C_star=Sn/(Sp+Sn)
    fig=go.Figure(go.Bar(x=REGIONS,y=C_star,
        marker_color=["#ffd700" if i==np.argmax(C_star) else "#3949ab" for i in range(6)],
        opacity=0.85,text=np.round(C_star,4),textposition="outside"))
    fig.update_layout(title="TOPSIS — Mức độ sẵn sàng AI theo vùng",
        plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=320,
        xaxis=dict(tickangle=-15,gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
    st.plotly_chart(fig,use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — PHÂN BỔ M3
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### M3 — Tối ưu phân bổ ngân sách")
    sc = SCENARIOS[selected_s]
    alloc = {k: budget_total*v for k,v in sc.items() if k in ["K","D","AI","H"]}

    c1,c2,c3,c4 = st.columns(4)
    labels_alloc=["Vốn K","Số hóa D","AI","Nhân lực H"]
    vals_alloc=[alloc["K"],alloc["D"],alloc["AI"],alloc["H"]]
    clr_alloc=["#1565c0","#ff9800","#7b1fa2","#2e7d32"]
    for col,lbl,val,clr in zip([c1,c2,c3,c4],labels_alloc,vals_alloc,clr_alloc):
        col.markdown(f'<div class="kpi"><div class="kl">{lbl}</div><div class="kv" style="color:{clr}">{val:,.0f} tỷ</div></div>',unsafe_allow_html=True)

    st.markdown("---")
    col_l,col_r=st.columns(2)
    with col_l:
        fig=go.Figure(go.Pie(labels=labels_alloc,values=vals_alloc,
            marker=dict(colors=clr_alloc),hole=0.45,
            textinfo="label+percent",textfont=dict(size=13)))
        fig.update_layout(title=f"Phân bổ — {selected_s}",
            paper_bgcolor="#0f1117",font_color="white",height=380)
        st.plotly_chart(fig,use_container_width=True)
    with col_r:
        # Phân bổ theo vùng (đơn giản hóa dựa trên TOPSIS)
        vung_w=C_star/C_star.sum()
        vung_alloc=budget_total*vung_w
        fig=go.Figure(go.Bar(x=REGIONS,y=vung_alloc,marker_color="#3949ab",opacity=0.85,
            text=[f"{v:,.0f}" for v in vung_alloc],textposition="outside"))
        fig.update_layout(title="Phân bổ theo vùng (dựa TOPSIS)",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=380,
            xaxis=dict(tickangle=-15,gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig,use_container_width=True)

    # Bảng ngành
    st.markdown("**📋 Phân bổ theo ngành (M3 — LP)**")
    risk_s=np.array([18,42,25,38,52,35,28,22])/100
    ai_share=np.array([0.05,0.25,0.08,0.12,0.10,0.12,0.18,0.10])
    h_share =np.array([0.18,0.14,0.10,0.12,0.06,0.10,0.08,0.22])
    df_sec=pd.DataFrame({"Ngành":SECTORS,
        "Ngân sách AI (tỷ)":np.round(alloc["AI"]*ai_share,0).astype(int),
        "Ngân sách H (tỷ)":np.round(alloc["H"]*h_share,0).astype(int),
        "Rủi ro TĐH (%)":(risk_s*100).astype(int)})
    st.dataframe(df_sec,use_container_width=True,hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — 5 KỊCH BẢN
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### M6 — So sánh 5 Kịch bản Chính sách")

    results={}
    for sname,sc_data in SCENARIOS.items():
        boost=1+sc_data["D"]*0.05+sc_data["AI"]*0.08+sc_data["H"]*0.04
        traj=[Y[-1]]
        for t in range(1,n_years_proj+1):
            Kt=K[-1]*(1+gKL)**t; Lt=L[-1]*(1+gKL)**t; At=A[-1]*(1+gTFP)**t
            Dt=D[-1]+(D_target-D[-1])/n_years_proj*t
            AIt=AI[-1]+(AI_target-AI[-1])/n_years_proj*t
            Ht=H[-1]+(H_target-H[-1])/n_years_proj*t
            Yt=At*(Kt**alpha)*(Lt**beta)*(Dt**gamma)*(AIt**delta)*(Ht**theta)*boost
            traj.append(Yt)
        # Tính các KPI
        Y_proj=traj[-1]
        gdp_growth=(Y_proj/Y[-1])**(1/n_years_proj)-1
        digital_idx=D_target*sc_data["D"]/0.10+18
        netjob_est=sc_data["H"]*budget_total*0.05-sc_data["AI"]*budget_total*0.02
        risk_score=sc_data["AI"]*0.6-sc_data["H"]*0.4
        env_score=sc_data["K"]*0.5+sc_data["AI"]*0.3
        results[sname]={
            "GDP cuối kỳ":round(Y_proj,0),"Tăng trưởng TB":round(gdp_growth*100,2),
            "Digital Index":round(digital_idx,1),"NetJob (nghìn)":round(netjob_est/1000,0),
            "Rủi ro AN":round(risk_score,3),"Phát thải":round(env_score,3),
            "color":sc_data["color"],"icon":sc_data["icon"]
        }

    # KPI cards
    cols=st.columns(5)
    for col,(sname,res) in zip(cols,results.items()):
        col.markdown(f"""<div class='kpi' style='border-left:4px solid {res['color']}'>
        <div class='kl'>{res['icon']} {sname.split('—')[1].strip()}</div>
        <div class='kv' style='font-size:18px;color:{res['color']}'>{res['GDP cuối kỳ']:,.0f}</div>
        <div class='kl'>ng.tỷ VND | {res['Tăng trưởng TB']}%/năm</div>
        </div>""",unsafe_allow_html=True)

    st.markdown("---")
    col_l,col_r=st.columns(2)
    with col_l:
        # Biểu đồ GDP theo kịch bản
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=list(years),y=list(Y),mode="lines",name="Thực tế 2020-2025",
            line=dict(color="white",width=2)))
        for sname,sc_data in SCENARIOS.items():
            boost=1+sc_data["D"]*0.05+sc_data["AI"]*0.08+sc_data["H"]*0.04
            traj=[Y[-1]]
            for t in range(1,n_years_proj+1):
                Kt=K[-1]*(1+gKL)**t; Lt=L[-1]*(1+gKL)**t; At=A[-1]*(1+gTFP)**t
                Dt=D[-1]+(D_target-D[-1])/n_years_proj*t
                AIt=AI[-1]+(AI_target-AI[-1])/n_years_proj*t
                Ht=H[-1]+(H_target-H[-1])/n_years_proj*t
                traj.append(At*(Kt**alpha)*(Lt**beta)*(Dt**gamma)*(AIt**delta)*(Ht**theta)*boost)
            proj_yrs=list(range(2025,2026+n_years_proj))
            fig.add_trace(go.Scatter(x=proj_yrs,y=traj,mode="lines+markers",
                name=sname,line=dict(color=sc_data["color"],width=2,dash="dot"),
                marker=dict(size=6)))
        fig.add_vline(x=2025,line_dash="dash",line_color="#555")
        fig.update_layout(title="Quỹ đạo GDP 5 kịch bản",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=400,
            xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"),
            legend=dict(orientation="h",y=-0.3,font=dict(size=10)))
        st.plotly_chart(fig,use_container_width=True)

    with col_r:
        # Radar chart so sánh
        cats=["GDP growth","Digital","NetJob","An ninh (inv)","Môi trường (inv)"]
        fig=go.Figure()
        for sname,res in results.items():
            vals=[res["Tăng trưởng TB"]/10,res["Digital Index"]/40,
                  min(1,max(0,res["NetJob (nghìn)"]/500)),
                  1-res["Rủi ro AN"],1-res["Phát thải"]]
            vals+=vals[:1]
            fig.add_trace(go.Scatterpolar(r=vals,theta=cats+[cats[0]],
                fill="toself",name=sname.split("—")[1].strip(),
                line=dict(color=res["color"],width=2),opacity=0.6))
        fig.update_layout(polar=dict(
            radialaxis=dict(visible=True,range=[0,1],gridcolor="#2a2d3e"),
            angularaxis=dict(gridcolor="#2a2d3e"),bgcolor="#1e2235"),
            title="Radar — So sánh đa chiều 5 kịch bản",
            paper_bgcolor="#0f1117",font_color="white",height=400,
            legend=dict(orientation="h",y=-0.2,font=dict(size=10)))
        st.plotly_chart(fig,use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — CẢNH BÁO RỦI RO M4-M5
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### M4 — Mô phỏng lao động | M5 — Đánh giá rủi ro")
    col1,col2=st.columns(2)

    with col1:
        st.markdown("**⚠️ Rủi ro tự động hóa theo ngành**")
        risk_data=np.array([18,42,25,38,52,35,28,22])
        clr_risk=["#c62828" if r>40 else "#ff9800" if r>25 else "#2e7d32" for r in risk_data]
        fig=go.Figure(go.Bar(x=SECTORS,y=risk_data,marker_color=clr_risk,opacity=0.85,
            text=[f"{r}%" for r in risk_data],textposition="outside"))
        fig.add_hline(y=35,line_dash="dash",line_color="white",opacity=0.5,
            annotation_text="Ngưỡng cảnh báo 35%",annotation_font_color="white")
        fig.update_layout(title="Rủi ro tự động hóa (%) theo ngành",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=380,
            xaxis=dict(tickangle=-20,gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig,use_container_width=True)

        # Cảnh báo
        high_risk=[s for s,r in zip(SECTORS,risk_data) if r>40]
        mid_risk=[s for s,r in zip(SECTORS,risk_data) if 25<r<=40]
        if high_risk:
            st.error(f"🔴 **Rủi ro cao (>40%):** {', '.join(high_risk)}")
        if mid_risk:
            st.warning(f"🟡 **Rủi ro trung bình (25-40%):** {', '.join(mid_risk)}")
        safe=[s for s,r in zip(SECTORS,risk_data) if r<=25]
        if safe:
            st.success(f"🟢 **Rủi ro thấp (≤25%):** {', '.join(safe)}")

    with col2:
        st.markdown("**🔐 Rủi ro an ninh & môi trường theo vùng**")
        rho_r=np.array([0.18,0.45,0.28,0.12,0.52,0.22])
        e_r  =np.array([0.42,0.55,0.48,0.32,0.62,0.38])
        fig=make_subplots(rows=1,cols=2,subplot_titles=["Rủi ro an ninh","Cường độ phát thải"])
        fig.add_trace(go.Bar(x=REGIONS,y=rho_r,marker_color="#9c27b0",opacity=0.85,name="An ninh"),row=1,col=1)
        fig.add_trace(go.Bar(x=REGIONS,y=e_r,marker_color="#ff6f00",opacity=0.85,name="Phát thải"),row=1,col=2)
        fig.update_layout(plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",
            height=340,showlegend=False)
        fig.update_xaxes(tickangle=-20,gridcolor="#2a2d3e")
        fig.update_yaxes(gridcolor="#2a2d3e")
        st.plotly_chart(fig,use_container_width=True)

        st.markdown("**🎲 4 kịch bản kinh tế toàn cầu (Bài 10)**")
        sc_data_sp={"Lạc quan":{"p":0.30,"GDP":3.5},"Cơ sở":{"p":0.45,"GDP":2.8},
                    "Bi quan":{"p":0.20,"GDP":1.5},"Khủng hoảng":{"p":0.05,"GDP":0.2}}
        df_sp=pd.DataFrame({"Kịch bản":list(sc_data_sp.keys()),
            "Xác suất":[f"{v['p']:.0%}" for v in sc_data_sp.values()],
            "TT TG (%)":[v["GDP"] for v in sc_data_sp.values()]})
        st.dataframe(df_sp,use_container_width=True,hide_index=True)
        exp_gdp=sum(v["p"]*v["GDP"] for v in sc_data_sp.values())
        st.metric("Tăng trưởng toàn cầu kỳ vọng",f"{exp_gdp:.2f}%")

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — BẢNG TỔNG HỢP KPI
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 📋 Bảng tổng hợp KPI — 5 Kịch bản đến 2030")

    df_kpi=pd.DataFrame({
        "Kịch bản":[f"{v['icon']} {k.split('—')[1].strip()}" for k,v in results.items()],
        "GDP cuối kỳ (ng.tỷ)":[f"{v['GDP cuối kỳ']:,.0f}" for v in results.values()],
        "Tăng trưởng TB (%/năm)":[v["Tăng trưởng TB"] for v in results.values()],
        "Digital Index":[v["Digital Index"] for v in results.values()],
        "NetJob (nghìn)":[v["NetJob (nghìn)"] for v in results.values()],
        "Rủi ro AN":[round(v["Rủi ro AN"],3) for v in results.values()],
        "Phát thải":[round(v["Phát thải"],3) for v in results.values()],
    })
    st.dataframe(df_kpi,use_container_width=True,hide_index=True)

    st.markdown("---")
    st.markdown("### 🏆 Khuyến nghị chính sách")

    best_gdp=max(results.items(),key=lambda x:x[1]["Tăng trưởng TB"])[0]
    best_safe=min(results.items(),key=lambda x:x[1]["Rủi ro AN"])[0]
    best_env =min(results.items(),key=lambda x:x[1]["Phát thải"])[0]
    best_job =max(results.items(),key=lambda x:x[1]["NetJob (nghìn)"])[0]

    c1,c2,c3,c4=st.columns(4)
    c1.markdown(f"""<div class='sec' style='border-color:#00c47a'>
    📈 <b>Tăng trưởng cao nhất</b><br>{best_gdp.split('—')[1].strip()}</div>""",unsafe_allow_html=True)
    c2.markdown(f"""<div class='sec' style='border-color:#1565c0'>
    🔐 <b>An ninh tốt nhất</b><br>{best_safe.split('—')[1].strip()}</div>""",unsafe_allow_html=True)
    c3.markdown(f"""<div class='sec' style='border-color:#2e7d32'>
    🌱 <b>Môi trường tốt nhất</b><br>{best_env.split('—')[1].strip()}</div>""",unsafe_allow_html=True)
    c4.markdown(f"""<div class='sec' style='border-color:#ff9800'>
    👷 <b>Việc làm tốt nhất</b><br>{best_job.split('—')[1].strip()}</div>""",unsafe_allow_html=True)

    st.markdown("""<div class='sec'>
    <b>💡 Khuyến nghị tích hợp AIDEOM-VN:</b><br><br>
    Không có kịch bản nào tối ưu trên tất cả các chiều. Kịch bản <b>S5 — Tối ưu cân bằng</b>
    được mô hình khuyến nghị vì đạt điểm Pareto tốt nhất khi xét đồng thời tăng trưởng,
    bao trùm xã hội, an ninh số và môi trường.<br><br>
    Giai đoạn 2026–2028: ưu tiên <b>hạ tầng số + nhân lực</b> (S2/S4) để tạo nền tảng.<br>
    Giai đoạn 2029–2030: chuyển sang <b>AI dẫn dắt</b> (S3) khi năng lực hấp thụ đã sẵn sàng.
    </div>""",unsafe_allow_html=True)

    st.markdown("---")
    st.caption("📊 Nguồn dữ liệu: NSO/GSO (2026), MoST (2026), MIC (2025), WB, GII 2025 | Mô hình AIDEOM-VN")
