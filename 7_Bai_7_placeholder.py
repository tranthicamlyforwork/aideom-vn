import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bài 7", layout="wide", page_icon="📊")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.sec{background:#1e2235;border-radius:10px;padding:20px;margin:12px 0;border-left:4px solid #7b1fa2;}
</style>""", unsafe_allow_html=True)
st.title("🔬 Bài 7 — NSGA-II Tối Ưu Đa Mục Tiêu Pareto")
st.caption("4 mục tiêu xung đột: Tăng trưởng GDP, Bao trùm xã hội, Môi trường, An ninh dữ liệu")

try:
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.optimize import minimize as pymoo_min
    PYMOO_OK = True
except: PYMOO_OK = False

with st.sidebar:
    st.header("⚙️ Tham số NSGA-II")
    pop_size = st.slider("Kích thước quần thể", 20, 100, 50, 10)
    n_gen    = st.slider("Số thế hệ", 20, 200, 50, 10)
    w_gdp    = st.slider("Trọng số Tăng trưởng", 0.1, 0.6, 0.40, 0.05)
    w_eq     = st.slider("Trọng số Bao trùm",    0.1, 0.5, 0.25, 0.05)
    w_env    = st.slider("Trọng số Môi trường",  0.1, 0.4, 0.20, 0.05)
    w_sec    = st.slider("Trọng số An ninh",     0.05,0.3, 0.15, 0.05)
    run = st.button("🚀 Chạy NSGA-II", type="primary")

beta = np.array([[1.15,0.85,0.55,1.30],[0.95,1.25,1.40,1.05],[1.05,0.95,0.85,1.15],
                 [1.20,0.75,0.45,1.35],[0.90,1.30,1.55,1.00],[1.10,0.85,0.65,1.25]])
e   = np.array([0.42,0.55,0.48,0.32,0.62,0.38])
rho = np.array([0.18,0.45,0.28,0.12,0.52,0.22])
sig = np.array([0.32,0.28,0.30,0.35,0.25,0.30])

if run and PYMOO_OK:
    with st.spinner(f"Đang chạy NSGA-II ({n_gen} thế hệ)..."):
        class VNProblem(ElementwiseProblem):
            def __init__(self):
                super().__init__(n_var=24,n_obj=4,n_ieq_constr=3,xl=np.zeros(24),xu=np.ones(24)*12000)
            def _evaluate(self,x,out,*a,**kw):
                X=x.reshape(6,4)
                f1=-(beta*X).sum()
                f2=np.abs(X.sum(1)-X.sum(1).mean()).mean()
                f3=(e*(X[:,0]+X[:,2])).sum()
                f4=(rho*X[:,2]).sum()-(sig*X[:,3]).sum()
                g1=X.sum()-50000; g2=-(X.sum(1)-5000).min(); g3=(X.sum(1)-12000).max()
                out['F']=[f1,f2,f3,f4]; out['G']=[g1,g2,g3]
        res=pymoo_min(VNProblem(),NSGA2(pop_size=pop_size),('n_gen',n_gen),seed=42,verbose=False)
    F=res.F
    st.success(f"✅ Tìm được {len(F)} nghiệm Pareto")
    col1,col2=st.columns(2)
    with col1:
        fig=go.Figure(go.Scatter3d(x=-F[:,0],y=F[:,1],z=F[:,2],mode='markers',
            marker=dict(size=4,color=F[:,3],colorscale='Plasma',showscale=True,colorbar=dict(title="An ninh"))))
        fig.update_layout(title="Pareto Front 3D",scene=dict(
            xaxis_title="GDP gain",yaxis_title="Bất bình đẳng",zaxis_title="Phát thải"),
            paper_bgcolor="#0f1117",font_color="white",height=500)
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        weights=np.array([w_gdp,w_eq,w_env,w_sec])
        F_n=(F-F.min(0))/(F.max(0)-F.min(0)+1e-9)
        F_n[:,0]=1-F_n[:,0]
        scores=F_n@weights
        best=np.argmax(scores)
        st.markdown(f"**Nghiệm thỏa hiệp TOPSIS:**")
        st.metric("GDP gain",f"{-F[best,0]:,.0f} tỷ")
        st.metric("Bất bình đẳng",f"{F[best,1]:.1f}")
        st.metric("Phát thải",f"{F[best,2]:.1f}")
        st.metric("Rủi ro an ninh",f"{F[best,3]:.1f}")
        fig2=go.Figure()
        labels=["Tăng trưởng","Bao trùm","Môi trường","An ninh"]
        for i,(lbl,clr) in enumerate(zip(labels,["#00c47a","#ff9800","#1565c0","#ff4b4b"])):
            fig2.add_trace(go.Scatter(x=np.arange(len(F)),y=F_n[:,i],mode='lines',
                name=lbl,line=dict(color=clr,width=1.5),opacity=0.7))
        fig2.update_layout(title="Parallel coords — tập Pareto",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=350,
            xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig2,use_container_width=True)
elif run and not PYMOO_OK:
    st.error("⚠️ pymoo chưa được cài. Vui lòng thêm pymoo vào requirements.txt")
else:
    st.info("👈 Điều chỉnh tham số rồi click **Chạy NSGA-II**")
    st.markdown("""<div class="sec">
    <b>📐 Mô hình 4 mục tiêu:</b><br>
    • <b>f₁:</b> max GDP gain = ΣΣ βⱼᵣ·xⱼᵣ<br>
    • <b>f₂:</b> min Bất bình đẳng = Gini xấp xỉ (MAD ngân sách vùng)<br>
    • <b>f₃:</b> min Phát thải = Σ eᵣ·(xᴵᵣ + xᴬᴵᵣ)<br>
    • <b>f₄:</b> min Rủi ro an ninh = Σ ρᵣ·xᴬᴵᵣ − Σ σᵣ·xᴴᵣ
    </div>""",unsafe_allow_html=True)
