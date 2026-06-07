import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bài 11", layout="wide", page_icon="📊")
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stSidebar"]{background:#1a1d2e;}
.sec{background:#1e2235;border-radius:10px;padding:20px;margin:12px 0;border-left:4px solid #7b1fa2;}
</style>""", unsafe_allow_html=True)
st.title("🤖 Bài 11 — Q-Learning Chính Sách Kinh Tế Thích Nghi")
st.caption("Tabular Q-learning: π*(s) = argmaxₐ Q(s,a) | MDP nền kinh tế Việt Nam")

ACTIONS=["Truyền thống","Cân bằng","Số hóa nhanh","AI dẫn dắt","Bao trùm"]
ALLOC=np.array([[0.70,0.10,0.10,0.10],[0.40,0.25,0.15,0.20],
                [0.25,0.45,0.15,0.15],[0.20,0.20,0.45,0.15],[0.30,0.20,0.10,0.40]])
STATE_NAMES=["GDP growth","Digital","AI cap","Unemployment"]
LEVEL_NAMES=["Thấp","Trung bình","Cao"]
w_rew=np.array([0.40,0.25,0.20,0.15])

with st.sidebar:
    st.header("⚙️ Tham số Q-learning")
    n_ep=st.slider("Số episodes",1000,20000,8000,1000)
    lr=st.slider("Learning rate α",0.05,0.30,0.10,0.01)
    gamma_rl=st.slider("Discount γ",0.80,0.99,0.95,0.01)
    run=st.button("🚀 Huấn luyện Q-learning",type="primary")
    st.divider()
    st.markdown("**Trạng thái khởi đầu VN 2026:**")
    s0=st.selectbox("GDP growth",[0,1,2],index=1,format_func=lambda x:LEVEL_NAMES[x])
    s1=st.selectbox("Digital",[0,1,2],index=1,format_func=lambda x:LEVEL_NAMES[x])
    s2=st.selectbox("AI capacity",[0,1,2],index=0,format_func=lambda x:LEVEL_NAMES[x])
    s3=st.selectbox("Unemployment",[0,1,2],index=1,format_func=lambda x:LEVEL_NAMES[x])

if run:
    Q=np.zeros((3,3,3,3,5))
    rewards_ep=[]
    rng=np.random.default_rng(42)
    for ep in range(n_ep):
        s=np.array([1,1,0,1]); t_reward=0; eps=max(0.05,1.0-ep/int(n_ep*0.6))
        for _ in range(10):
            a=rng.integers(5) if rng.random()<eps else int(np.argmax(Q[tuple(s)]))
            alloc=ALLOC[a]
            ns=s.copy()
            ns[0]=min(2,max(0,s[0]+(1 if alloc[0]<0.4 else -1 if alloc[0]>0.6 else 0)+rng.integers(-1,2)))
            ns[1]=min(2,max(0,s[1]+(1 if alloc[1]>0.3 else 0)))
            ns[2]=min(2,max(0,s[2]+(1 if alloc[2]>0.3 else 0)))
            ns[3]=min(2,max(0,s[3]-(1 if alloc[3]>0.3 else 0)+rng.integers(0,2)))
            r_gdp=alloc@np.array([0.3,0.5,0.8,1.0])
            r_unemp=-0.5 if ns[3]==2 else 0.2 if ns[3]==0 else 0
            r_cyber=-0.3*alloc[2]; r_env=-0.2*alloc[0]
            reward=w_rew[0]*r_gdp+w_rew[1]*r_unemp+w_rew[2]*r_cyber+w_rew[3]*r_env
            Q[tuple(s)+(a,)]+=lr*(reward+gamma_rl*Q[tuple(ns)].max()-Q[tuple(s)+(a,)])
            s=ns; t_reward+=reward
        rewards_ep.append(t_reward)
    st.success("✅ Huấn luyện hoàn thành!")
    init_state=(s0,s1,s2,s3)
    best_a=int(np.argmax(Q[init_state]))
    c1,c2,c3=st.columns(3)
    c1.metric("Hành động tối ưu π*(s)",ACTIONS[best_a])
    c2.metric("Q-value cao nhất",f"{Q[init_state].max():.4f}")
    c3.metric("Episodes",f"{n_ep:,}")
    col1,col2=st.columns(2)
    with col1:
        window=max(1,n_ep//50)
        smooth=[np.mean(rewards_ep[max(0,i-window):i+1]) for i in range(len(rewards_ep))]
        fig=go.Figure(go.Scatter(x=list(range(n_ep)),y=smooth,mode="lines",
            line=dict(color="#00c47a",width=2),name="Reward TB"))
        fig.update_layout(title="Learning Curve",xaxis_title="Episode",yaxis_title="Reward",
            plot_bgcolor="#1e2235",paper_bgcolor="#0f1117",font_color="white",height=350,
            xaxis=dict(gridcolor="#2a2d3e"),yaxis=dict(gridcolor="#2a2d3e"))
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        st.markdown("**Chính sách π*(s) theo trạng thái:**")
        rows=[]
        for g in range(3):
            for d in range(3):
                a_opt=int(np.argmax(Q[g,d,s2,s3]))
                rows.append({"GDP":LEVEL_NAMES[g],"Digital":LEVEL_NAMES[d],"Hành động tốt nhất":ACTIONS[a_opt]})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
else:
    st.info("👈 Click **Huấn luyện Q-learning** để tìm chính sách tối ưu")
    st.markdown("**5 hành động:**")
    for i,(a,alloc) in enumerate(zip(ACTIONS,ALLOC)):
        st.markdown(f"**a{i}: {a}** — K:{alloc[0]*100:.0f}% D:{alloc[1]*100:.0f}% AI:{alloc[2]*100:.0f}% H:{alloc[3]*100:.0f}%")
