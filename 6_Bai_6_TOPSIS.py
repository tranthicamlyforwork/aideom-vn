import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Bài 6 - TOPSIS", layout="wide", page_icon="🗺️")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.sec{background:#1e2235;border-radius:10px;padding:16px 20px;margin:12px 0;border-left:4px solid #ff9800;}
</style>""", unsafe_allow_html=True)

st.title("🗺️ Bài 6 — TOPSIS Xếp Hạng 6 Vùng Kinh Tế Theo Ưu Tiên AI")
st.caption("Technique for Order of Preference by Similarity to Ideal Solution")

REGIONS=["Trung du MN Bắc","ĐB sông Hồng","Bắc TB+DH Trung","Tây Nguyên","Đông Nam Bộ","ĐB sông CL"]
X = np.array([
    [57.0,  3.5, 38, 22, 21.5, 0.18, 72, 0.405],
    [152.3,20.0, 78, 68, 36.8, 0.85, 92, 0.358],
    [87.5,  8.2, 55, 40, 27.5, 0.32, 84, 0.372],
    [68.9,  0.8, 32, 18, 18.2, 0.15, 68, 0.412],
    [158.9,18.5, 82, 75, 42.5, 0.78, 94, 0.385],
    [80.5,  2.1, 48, 30, 16.8, 0.22, 78, 0.392],
])
CRITERIA=["GRDP/người","FDI","Digital Index","AI Readiness","LĐ ĐT%","R&D/GRDP","Internet%","Gini"]
IS_BENEFIT=[True,True,True,True,True,True,True,False]

with st.sidebar:
    st.header("⚙️ Trọng số TOPSIS")
    w = []
    defaults=[0.10,0.10,0.15,0.20,0.15,0.15,0.05,0.10]
    for c,d in zip(CRITERIA,defaults):
        w.append(st.slider(c,0.01,0.40,d,0.01))
    w=np.array(w)
    w=w/w.sum()
    st.info(f"Tổng = {w.sum():.2f} (đã chuẩn hóa)")

def topsis(X,w,is_benefit):
    R=X/np.sqrt((X**2).sum(axis=0))
    V=R*w
    A_pos=np.where(is_benefit,V.max(0),V.min(0))
    A_neg=np.where(is_benefit,V.min(0),V.max(0))
    S_pos=np.sqrt(((V-A_pos)**2).sum(1))
    S_neg=np.sqrt(((V-A_neg)**2).sum(1))
    return S_neg/(S_pos+S_neg)

def entropy_weights(X):
    P=X/X.sum(axis=0)
    k=1.0/np.log(len(X))
    E=-k*np.nansum(P*np.log(P+1e-12),axis=0)
    d=1-E; return d/d.sum()

C_star = topsis(X,w,IS_BENEFIT)
w_ent  = entropy_weights(X)
C_ent  = topsis(X,w_ent,IS_BENEFIT)

tab1,tab2,tab3 = st.tabs(["🏆 Xếp hạng TOPSIS","🔢 Entropy Weights","📉 Độ nhạy"])

with tab1:
    df=pd.DataFrame({"Vùng":REGIONS,"TOPSIS (chuyên gia)":np.round(C_star,4),"Xếp hạng":pd.Series(C_star).rank(ascending=False).astype(int).values})
    df=df.sort_values("Xếp hạng")
    c_l,c_r=st.columns([2,3])
    with c_l:
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.markdown(f"""<div class='sec'>
        🥇 <b>{df.iloc[0]['Vùng']}</b> — Điểm {df.iloc[0]['TOPSIS (chuyên gia)']:.4f}<br>
        🥈 <b>{df.iloc[1]['Vùng']}</b> — Điểm {df.iloc[1]['TOPSIS (chuyên gia)']:.4f}<br>
        🥉 <b>{df.iloc[2]['Vùng']}</b> — Điểm {df.iloc[2]['TOPSIS (chuyên gia)']:.4f}
        </div>""",unsafe_allow_html=True)
    with c_r:
        fig=go.Figure(go.Bar(x=df["Vùng"],y=df["TOPSIS (chuyên gia)"],
            marker_color=["#ffd700","#c0c0c0","#cd7f32","#3949ab","#3949ab","#3949ab"],
            opacity=0.9,text=np.round(df["TOPSIS (chuyên gia)"].values,4),textposition="outside"))
        fig.update_layout(title="Điểm TOPSIS 6 vùng kinh tế",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=400,
            xaxis=dict(tickangle=-15,gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig,use_container_width=True)

with tab2:
    col1,col2=st.columns(2)
    with col1:
        st.markdown("**Trọng số Entropy (khách quan):**")
        df_ent=pd.DataFrame({"Tiêu chí":CRITERIA,"Entropy weight":np.round(w_ent,4),"Chuyên gia":np.round(w,4)})
        st.dataframe(df_ent,use_container_width=True,hide_index=True)
    with col2:
        df_cmp=pd.DataFrame({"Vùng":REGIONS,"Chuyên gia":np.round(C_star,4),"Entropy":np.round(C_ent,4)})
        df_cmp["Δ Hạng"]=pd.Series(C_star).rank(ascending=False).values-pd.Series(C_ent).rank(ascending=False).values
        df_cmp=df_cmp.sort_values("Entropy",ascending=False)
        st.markdown("**So sánh xếp hạng:**")
        st.dataframe(df_cmp,use_container_width=True,hide_index=True)

with tab3:
    st.subheader("Độ nhạy theo trọng số AI Readiness (w₄)")
    ai_vals=np.arange(0.05,0.45,0.05)
    scores_all=[]
    for ai_w in ai_vals:
        w2=w.copy(); w2[3]=ai_w; w2=w2/w2.sum()
        scores_all.append(topsis(X,w2,IS_BENEFIT))
    fig=go.Figure()
    colors=["#ff4b4b","#00c47a","#1565c0","#ff9800","#9c27b0","#37474f"]
    for i,(r,clr) in enumerate(zip(REGIONS,colors)):
        fig.add_trace(go.Scatter(x=ai_vals,y=[s[i] for s in scores_all],
            mode="lines+markers",name=r,line=dict(color=clr,width=2),marker=dict(size=7)))
    fig.update_layout(title="Điểm TOPSIS theo w(AI Readiness)",
        xaxis_title="w₄ (AI Readiness)",yaxis_title="TOPSIS Score",
        plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=420,
        xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
    st.plotly_chart(fig,use_container_width=True)
