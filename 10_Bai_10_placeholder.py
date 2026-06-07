import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bài 10", layout="wide", page_icon="📊")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.sec{background:#1e2235;border-radius:10px;padding:20px;margin:12px 0;border-left:4px solid #7b1fa2;}
</style>""", unsafe_allow_html=True)
st.title("🎲 Bài 10 — Quy Hoạch Ngẫu Nhiên Hai Giai Đoạn")
st.caption("Two-stage stochastic LP: min c'x + Σpₛ·Q(x,s) | 4 kịch bản kinh tế toàn cầu")

SCENARIOS={"s1 Lạc quan":{"p":0.30,"coef":{"I":1.25,"D":1.35,"AI":1.55,"H":1.05}},
            "s2 Cơ sở":   {"p":0.45,"coef":{"I":1.00,"D":1.10,"AI":1.25,"H":0.95}},
            "s3 Bi quan": {"p":0.20,"coef":{"I":0.75,"D":0.85,"AI":0.90,"H":1.00}},
            "s4 Khủng hoảng":{"p":0.05,"coef":{"I":0.40,"D":0.50,"AI":0.55,"H":1.10}}}
ITEMS=["I","D","AI","H"]; beta0={"I":1.00,"D":1.10,"AI":1.25,"H":0.95}

with st.sidebar:
    b1s=st.slider("Ngân sách giai đoạn 1 (tỷ)",40000,80000,65000,1000)
    b2s=st.slider("Dự phòng giai đoạn 2 (tỷ)",5000,30000,15000,1000)
    run=st.button("🚀 Giải Stochastic LP",type="primary")

if run:
    try:
        import pulp as pl
        m=pl.LpProblem("SP",pl.LpMaximize)
        x={j:pl.LpVariable(f"x_{j}",lowBound=0) for j in ITEMS}
        y={s:{j:pl.LpVariable(f"y_{s}_{j}",lowBound=0) for j in ITEMS} for s in SCENARIOS}
        obj=pl.lpSum(beta0[j]*x[j] for j in ITEMS)
        for s,sv in SCENARIOS.items():
            obj+=sv["p"]*pl.lpSum(sv["coef"][j]*y[s][j] for j in ITEMS)
        m+=obj
        m+=pl.lpSum(x[j] for j in ITEMS)<=b1s
        for s,sv in SCENARIOS.items():
            m+=pl.lpSum(y[s][j] for j in ITEMS)<=b2s
            m+=y[s]["AI"]<=0.5*x["H"]
        m.solve(pl.PULP_CBC_CMD(msg=False))
        Z=pl.value(m.objective)
        st.success(f"✅ Z* kỳ vọng = {Z:,.2f} tỷ VND")
        x_vals={j:pl.value(x[j]) for j in ITEMS}
        c1,c2=st.columns(2)
        with c1:
            st.markdown("**Quyết định giai đoạn 1 (x):**")
            df_x=pd.DataFrame({"Hạng mục":ITEMS,"Phân bổ (tỷ)":[round(x_vals[j],1) for j in ITEMS],"β₀":[beta0[j] for j in ITEMS]})
            st.dataframe(df_x,use_container_width=True,hide_index=True)
        with c2:
            rows2=[]
            for s,sv in SCENARIOS.items():
                r={"Kịch bản":s,"p":sv["p"]}
                for j in ITEMS: r[j]=round(pl.value(y[s][j]),1)
                rows2.append(r)
            st.markdown("**Điều chỉnh giai đoạn 2 (y):**")
            st.dataframe(pd.DataFrame(rows2),use_container_width=True,hide_index=True)
        fig=go.Figure(go.Bar(x=ITEMS,y=[x_vals[j] for j in ITEMS],marker_color=["#1565c0","#7b1fa2","#2e7d32","#e65100"],opacity=0.85,text=[round(x_vals[j],1) for j in ITEMS],textposition="outside"))
        fig.update_layout(title="Phân bổ tối ưu giai đoạn 1",plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=350,yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig,use_container_width=True)
    except Exception as e:
        st.error(f"Lỗi: {e}")
else:
    cols=st.columns(4)
    for i,(s,sv) in enumerate(SCENARIOS.items()):
        cols[i].metric(s,f"p={sv['p']}")
    st.info("👈 Click **Giải Stochastic LP**")
