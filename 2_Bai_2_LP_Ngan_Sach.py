import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import linprog

st.set_page_config(page_title="Bài 2 - LP Ngân sách", layout="wide", page_icon="💰")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.sec{background:#1e2235;border-radius:10px;padding:16px 20px;margin:12px 0;border-left:4px solid #f9a825;}
</style>""", unsafe_allow_html=True)

st.title("💰 Bài 2 — LP Phân Bổ Ngân Sách 4 Hạng Mục Đầu Tư Số")
st.caption("max Z = 0,85·x₁ + 1,20·x₂ + 0,95·x₃ + 1,35·x₄  |  Ngân sách: 100.000 tỷ VND")

with st.sidebar:
    st.header("⚙️ Tham số")
    budget = st.slider("Ngân sách tổng (nghìn tỷ)", 80, 200, 100, 5)
    min_I  = st.slider("Sàn hạ tầng số x₁ (≥)", 10, 40, 25, 1)
    min_AI = st.slider("Sàn AI & dữ liệu x₂ (≥)", 5, 30, 15, 1)
    min_H  = st.slider("Sàn nhân lực số x₃ (≥)", 10, 40, 20, 1)
    min_RD = st.slider("Sàn R&D x₄ (≥)", 5, 25, 10, 1)
    tech_ratio = st.slider("Tỷ trọng công nghệ CL (x₂+x₄ ≥ ?%)", 25, 50, 35, 1)/100

c = [-0.85, -1.20, -0.95, -1.35]
A_ub = [
    [1,1,1,1],
    [-1,0,0,0],
    [0,-1,0,0],
    [0,0,-1,0],
    [0,0,0,-1],
    [tech_ratio-1, -1+tech_ratio, tech_ratio, -1+tech_ratio]
]
b_ub = [budget, -min_I, -min_AI, -min_H, -min_RD, 0]
res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0,None)]*4, method='highs')

tab1, tab2, tab3 = st.tabs(["📊 Kết quả tối ưu", "📉 Phân tích độ nhạy", "💬 Thảo luận"])

with tab1:
    if res.success:
        x = res.x
        Z = -res.fun
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Z* GDP tăng thêm", f"{Z:.2f} ng.tỷ")
        c2.metric("NPV/Chi phí", f"{Z/budget:.4f}")
        c3.metric("Tổng đầu tư", f"{sum(x):.1f} ng.tỷ")
        c4.metric("Trạng thái", "✅ Khả thi")

        labels=["Hạ tầng số (x₁)","AI & Dữ liệu (x₂)","Nhân lực số (x₃)","R&D (x₄)"]
        colors=["#1565c0","#7b1fa2","#2e7d32","#e65100"]
        col_l, col_r = st.columns(2)
        with col_l:
            fig = go.Figure(go.Bar(x=labels, y=x, marker_color=colors, opacity=0.85,
                text=[f"{v:.1f}" for v in x], textposition="outside"))
            fig.update_layout(title="Phân bổ ngân sách tối ưu (nghìn tỷ VND)",
                plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=380,
                yaxis=dict(gridcolor="#2a2d3e"))
            st.plotly_chart(fig, use_container_width=True)
        with col_r:
            fig2 = go.Figure(go.Pie(labels=labels, values=x,
                marker=dict(colors=colors), hole=0.4,
                textinfo="label+percent"))
            fig2.update_layout(title="Tỷ trọng phân bổ",
                paper_bgcolor="#0f1117",font_color="white",height=380)
            st.plotly_chart(fig2, use_container_width=True)

        df = pd.DataFrame({"Hạng mục":labels,
            "Phân bổ (ng.tỷ)":np.round(x,2),
            "Tỷ trọng (%)":[f"{v/budget*100:.1f}%" for v in x],
            "Hệ số tác động":[0.85,1.20,0.95,1.35],
            "GDP tăng thêm":np.round(x*np.array([0.85,1.20,0.95,1.35]),2)})
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.info(f"**Shadow price ngân sách:** Mỗi nghìn tỷ VND tăng thêm → GDP kỳ vọng tăng **~{Z/budget:.4f} nghìn tỷ VND**")
    else:
        st.error("❌ Bài toán không khả thi! Hãy giảm ràng buộc tối thiểu.")

with tab2:
    st.subheader("Phân tích độ nhạy — Tăng ngân sách")
    budgets = list(range(80, 201, 5))
    Zs = []
    for b in budgets:
        b_ub2 = [b,-min_I,-min_AI,-min_H,-min_RD,0]
        r2 = linprog(c, A_ub=A_ub, b_ub=b_ub2, bounds=[(0,None)]*4, method='highs')
        Zs.append(-r2.fun if r2.success else None)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=budgets, y=Zs, mode="lines+markers",
        line=dict(color="#ff9800",width=3), marker=dict(size=7), name="Z*(B)"))
    fig.add_vline(x=budget, line_dash="dash", line_color="#ff4b4b",
        annotation_text=f"B={budget}", annotation_font_color="white")
    fig.update_layout(title="Đường cong Z*(B) — GDP tăng theo ngân sách",
        xaxis_title="Ngân sách (nghìn tỷ VND)", yaxis_title="Z* (GDP tăng thêm)",
        plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=400,
        xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("""<div class="sec">
<b>💬 Thảo luận chính sách</b><br><br>
<b>a)</b> Shadow price ngân sách: mỗi nghìn tỷ VND tăng thêm → GDP kỳ vọng tăng theo hệ số tác động biên của hạng mục được bổ sung. Đây là cận trên hợp lý của chi phí cơ hội vốn công.<br><br>
<b>b)</b> R&D có hệ số cao nhất (1,35) nhưng ràng buộc tối thiểu thấp nhất (10 ng.tỷ) vì: tác động lan tỏa dài hạn nhưng hấp thụ vốn chậm, cần thời gian nghiên cứu, không thể "đổ tiền" nhanh.<br><br>
<b>c)</b> Tỷ lệ 35% công nghệ chiến lược (AI + R&D) thách thức trong thực tiễn 2025 khi ngân sách ưu tiên hạ tầng giao thông và an sinh. Cần cơ chế PPP để bù đắp phần thiếu hụt từ ngân sách nhà nước.
</div>""", unsafe_allow_html=True)
