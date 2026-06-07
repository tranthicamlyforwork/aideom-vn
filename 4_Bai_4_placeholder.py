import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bài 4", layout="wide", page_icon="📊")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.coming{background:#1e2235;border-radius:12px;padding:40px;text-align:center;margin:40px 0;border:2px dashed #2a2d3e;}
</style>""", unsafe_allow_html=True)

import pulp
st.title("📊 Bài 4 — LP Phân Bổ Ngân Sách Ngành-Vùng")
st.caption("24 biến quyết định, 6 vùng × 4 hạng mục | Ràng buộc công bằng vùng miền")

with st.sidebar:
    st.header("⚙️ Tham số")
    budget = st.slider("Ngân sách tổng (tỷ VND)", 30000, 80000, 50000, 1000)
    floor = st.slider("Sàn mỗi vùng (tỷ VND)", 2000, 8000, 5000, 500)
    ceil = st.slider("Trần mỗi vùng (tỷ VND)", 8000, 20000, 12000, 500)
    h_floor = st.slider("Sàn nhân lực số (%)", 15, 35, 24, 1)
    lam = st.slider("λ công bằng vùng", 0.5, 0.9, 0.7, 0.05)
    run = st.button("🚀 Giải tối ưu", type="primary")

regions = ['Trung du MN Bắc','ĐB sông Hồng','Bắc TB + DH Trung','Tây Nguyên','Đông Nam Bộ','ĐB sông CL']
items = ['I','D','AI','H']
beta = {
    ('Trung du MN Bắc','I'):1.15,('Trung du MN Bắc','D'):0.85,('Trung du MN Bắc','AI'):0.55,('Trung du MN Bắc','H'):1.30,
    ('ĐB sông Hồng','I'):0.95,('ĐB sông Hồng','D'):1.25,('ĐB sông Hồng','AI'):1.40,('ĐB sông Hồng','H'):1.05,
    ('Bắc TB + DH Trung','I'):1.05,('Bắc TB + DH Trung','D'):0.95,('Bắc TB + DH Trung','AI'):0.85,('Bắc TB + DH Trung','H'):1.15,
    ('Tây Nguyên','I'):1.20,('Tây Nguyên','D'):0.75,('Tây Nguyên','AI'):0.45,('Tây Nguyên','H'):1.35,
    ('Đông Nam Bộ','I'):0.90,('Đông Nam Bộ','D'):1.30,('Đông Nam Bộ','AI'):1.55,('Đông Nam Bộ','H'):1.00,
    ('ĐB sông CL','I'):1.10,('ĐB sông CL','D'):0.85,('ĐB sông CL','AI'):0.65,('ĐB sông CL','H'):1.25,
}
D0 = {'Trung du MN Bắc':38,'ĐB sông Hồng':78,'Bắc TB + DH Trung':55,'Tây Nguyên':32,'Đông Nam Bộ':82,'ĐB sông CL':48}

if run:
    with st.spinner("Đang giải tối ưu LP..."):
        m = pulp.LpProblem('VN_Budget', pulp.LpMaximize)
        x = pulp.LpVariable.dicts('x', (regions,items), lowBound=0)
        m += pulp.lpSum(beta[(r,j)]*x[r][j] for r in regions for j in items)
        m += pulp.lpSum(x[r][j] for r in regions for j in items) <= budget
        for r in regions:
            m += pulp.lpSum(x[r][j] for j in items) >= floor
            m += pulp.lpSum(x[r][j] for j in items) <= ceil
        m += pulp.lpSum(x[r]['H'] for r in regions) >= budget*h_floor/100
        M = pulp.LpVariable('Dmax')
        gamma = 0.002
        for r in regions:
            m += D0[r] + gamma*x[r]['D'] <= M
            m += D0[r] + gamma*x[r]['D'] >= lam*M
        m.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[m.status] == 'Optimal':
        Z = pulp.value(m.objective)
        st.success(f"✅ Z* = {Z:,.2f} tỷ VND GDP tăng thêm")
        rows = []
        for r in regions:
            row = {"Vùng":r}
            for j in items: row[j] = round(pulp.value(x[r][j]),1)
            row["Tổng"] = round(sum(pulp.value(x[r][j]) for j in items),1)
            rows.append(row)
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        fig = go.Figure()
        for j,clr in zip(items,["#1565c0","#7b1fa2","#2e7d32","#e65100"]):
            fig.add_trace(go.Bar(name=j, x=[r["Vùng"] for r in rows],
                y=[r[j] for r in rows], marker_color=clr, opacity=0.85))
        fig.update_layout(barmode="stack", title="Phân bổ tối ưu theo vùng và hạng mục",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=420,
            xaxis=dict(tickangle=-20,gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("❌ Không tìm được nghiệm tối ưu. Hãy nới lỏng ràng buộc.")
else:
    st.info("👈 Điều chỉnh tham số bên sidebar rồi click **Giải tối ưu**")
