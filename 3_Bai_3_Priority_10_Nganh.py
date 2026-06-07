import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Bài 3 - Priority 10 ngành", layout="wide", page_icon="🏭")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.sec{background:#1e2235;border-radius:10px;padding:16px 20px;margin:12px 0;border-left:4px solid #00c47a;}
</style>""", unsafe_allow_html=True)

st.title("🏭 Bài 3 — Chỉ Số Ưu Tiên Ngành cho 10 Ngành Việt Nam")
st.caption("Priorityᵢ = a₁·Growth + a₂·Productivity + a₃·Spillover + a₄·Export + a₅·Employment + a₆·AIReadiness − a₇·Risk")

SECTORS = ["Nông-Lâm-Thủy sản","CN chế biến chế tạo","Xây dựng","Khai khoáng",
           "Bán buôn-bán lẻ","Tài chính-Ngân hàng","Logistics-Vận tải",
           "CNTT-Truyền thông","Giáo dục-Đào tạo","Y tế"]
data = {
    "growth":    [3.27,9.64,7.45,-1.20,7.10,7.36,9.93,7.85,6.42,6.85],
    "prod":      [103.4,241.2,168.8,1290.5,145.3,1072.4,321.4,713.8,205.7,437.1],
    "spillover": [0.35,0.78,0.42,0.30,0.55,0.85,0.72,0.92,0.65,0.60],
    "export":    [40.5,290.9,2.5,8.2,5.5,1.2,3.1,178.0,0.0,0.0],
    "employ":    [13.20,11.50,4.80,0.30,7.80,0.55,1.95,0.62,2.15,0.75],
    "ai_ready":  [15,55,20,30,48,72,42,88,38,45],
    "risk":      [18,42,25,55,38,52,35,28,22,18],
}
df = pd.DataFrame(data, index=SECTORS)

with st.sidebar:
    st.header("⚙️ Trọng số")
    a1 = st.slider("a₁ Tăng trưởng", 0.05, 0.40, 0.15, 0.01)
    a2 = st.slider("a₂ Năng suất",   0.05, 0.40, 0.15, 0.01)
    a3 = st.slider("a₃ Lan tỏa",     0.05, 0.40, 0.20, 0.01)
    a4 = st.slider("a₄ Xuất khẩu",   0.05, 0.40, 0.15, 0.01)
    a5 = st.slider("a₅ Việc làm",    0.05, 0.30, 0.10, 0.01)
    a6 = st.slider("a₆ AI Readiness",0.05, 0.40, 0.20, 0.01)
    a7 = st.slider("a₇ Rủi ro TĐH", 0.05, 0.30, 0.15, 0.01)
    total = round(a1+a2+a3+a4+a5+a6+a7,2)
    st.info(f"Tổng trọng số = {total:.2f}")

def norm_good(x): return (x-x.min())/(x.max()-x.min()) if x.max()!=x.min() else x*0
def norm_bad(x):  return (x.max()-x)/(x.max()-x.min()) if x.max()!=x.min() else x*0

Xg = df[["growth","prod","spillover","export","employ","ai_ready"]].apply(norm_good)
Xb = norm_bad(df["risk"])
w  = np.array([a1,a2,a3,a4,a5,a6])
priority = Xg.values @ w - a7*Xb.values
df["Priority"] = priority
df_sorted = df.sort_values("Priority", ascending=False)

tab1, tab2, tab3 = st.tabs(["🏆 Xếp hạng","🔥 Heatmap độ nhạy","🆚 So sánh chiến lược"])

with tab1:
    c_l, c_r = st.columns([3,2])
    with c_l:
        colors_bar = ["#ffd700" if i<3 else "#3949ab" for i in range(10)]
        fig = go.Figure(go.Bar(
            x=df_sorted["Priority"].values, y=df_sorted.index,
            orientation="h", marker_color=colors_bar, opacity=0.9,
            text=[f"{v:.3f}" for v in df_sorted["Priority"].values], textposition="outside"))
        fig.update_layout(title="Chỉ số ưu tiên ngành (Priority)",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=450,
            xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig, use_container_width=True)
    with c_r:
        st.markdown("**🥇 Top 3 ngành ưu tiên**")
        for i,(idx,row) in enumerate(df_sorted.head(3).iterrows()):
            medal=["🥇","🥈","🥉"][i]
            st.markdown(f"""<div style='background:#1e2235;padding:12px;border-radius:8px;margin:6px 0;border-left:4px solid #ffd700'>
            <b>{medal} {idx}</b><br>
            <span style='color:#ffd700;font-size:20px;font-weight:700'>{row['Priority']:.4f}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("**📋 Bảng xếp hạng đầy đủ**")
        df_display = pd.DataFrame({"Ngành":df_sorted.index,"Priority":np.round(df_sorted["Priority"],4),"Hạng":range(1,11)})
        st.dataframe(df_display, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Độ nhạy theo trọng số a₆ (AI Readiness)")
    a6_vals = np.arange(0.05,0.45,0.05)
    ranks = []
    for a6v in a6_vals:
        rem = 1.0 - a6v
        scale = rem/sum([a1,a2,a3,a4,a5,a7])
        w2 = np.array([a1,a2,a3,a4,a5,a6v])*scale; w2[5]=a6v
        a7v = a7*scale
        p2 = Xg.values @ w2[:6] - a7v*Xb.values
        order = np.argsort(-p2)
        ranks.append([SECTORS[o] for o in order[:5]])
    df_rank = pd.DataFrame(ranks, columns=[f"Top{i+1}" for i in range(5)],
                           index=[f"a₆={v:.2f}" for v in a6_vals])
    st.markdown("**Top 5 ngành theo từng mức a₆ (AI Readiness):**")
    st.dataframe(df_rank, use_container_width=True)

with tab3:
    st.subheader("So sánh 2 bộ trọng số chính sách")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📈 Định hướng Tăng trưởng**")
        w_growth = np.array([0.25,0.20,0.10,0.25,0.05,0.05])
        p_growth = Xg.values @ w_growth - 0.10*Xb.values
        df["P_growth"] = p_growth
        top3_g = df.sort_values("P_growth",ascending=False).head(3).index.tolist()
        for s in top3_g: st.markdown(f"• **{s}**")
    with col2:
        st.markdown("**🤝 Định hướng Bao trùm**")
        w_incl = np.array([0.10,0.05,0.25,0.05,0.25,0.10])
        p_incl = Xg.values @ w_incl - 0.20*Xb.values
        df["P_incl"] = p_incl
        top3_i = df.sort_values("P_incl",ascending=False).head(3).index.tolist()
        for s in top3_i: st.markdown(f"• **{s}**")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=SECTORS,y=df["P_growth"],mode="lines+markers",name="Tăng trưởng",
        line=dict(color="#ff9800",width=2),marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=SECTORS,y=df["P_incl"],mode="lines+markers",name="Bao trùm",
        line=dict(color="#00c47a",width=2),marker=dict(size=8)))
    fig.update_layout(title="So sánh Priority: Tăng trưởng vs Bao trùm",
        plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=380,
        xaxis=dict(tickangle=-30,gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""<div class="sec">
<b>💬 Thảo luận chính sách</b><br><br>
<b>a)</b> CNTT-Truyền thông, Logistics và Tài chính-Ngân hàng thường dẫn đầu — phù hợp với Nghị quyết 57-NQ/TW ưu tiên hạ tầng số và chuyển đổi số doanh nghiệp.<br><br>
<b>b)</b> Khai khoáng có năng suất rất cao nhưng không nằm trong top vì: AI Readiness thấp (30), rủi ro tự động hóa cao (55%), lan tỏa thấp (0,30), và không phải định hướng chiến lược tương lai.<br><br>
<b>c)</b> Bộ trọng số nên do hội đồng chính sách đa bên quyết định — không chỉ chuyên gia kỹ thuật — để đảm bảo tính chính danh và phản ánh ưu tiên xã hội thực sự.
</div>""", unsafe_allow_html=True)
