import streamlit as st

st.set_page_config(
    page_title="AIDEOM-VN",
    page_icon="🇻🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"] { background: #1a1d2e; }
.main-title { font-size:42px; font-weight:800; color:#ffffff; margin-bottom:4px; }
.main-sub { font-size:20px; font-style:italic; color:#aaaaaa; margin-bottom:24px; }
.main-desc { font-size:14px; color:#888; margin-bottom:32px; }
.kpi-box { background:#1e2235; border-radius:12px; padding:20px 24px; border:1px solid #2a2d3e; }
.kpi-val { font-size:32px; font-weight:700; color:#ff4b4b; margin:6px 0 4px 0; }
.kpi-lbl { font-size:13px; color:#888; }
.kpi-tag { font-size:12px; color:#00c47a; background:#0d2e1f; padding:2px 8px; border-radius:10px; display:inline-block; margin-top:4px; }
.section-title { font-size:22px; font-weight:700; color:#ffffff; margin:32px 0 16px 0; }
.level-box { background:#1e2235; border-radius:10px; padding:16px 20px; margin-bottom:8px; border-left:4px solid; }
.level-easy   { border-color:#00c47a; }
.level-medium { border-color:#ffa500; }
.level-hard2  { border-color:#ff6b6b; }
.level-hard   { border-color:#cc00ff; }
.bai-row { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #2a2d3e; }
.bai-name { font-size:14px; color:#ffffff; font-weight:600; }
.bai-desc { font-size:12px; color:#888; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🇻🇳 AIDEOM-VN</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">AI-Driven Decision Optimization Model for Vietnam</div>', unsafe_allow_html=True)
st.markdown('<div class="main-desc">Web app giải 12 bài toán mô hình ra quyết định phát triển kinh tế Việt Nam trong kỉ nguyên AI — dữ liệu thực 2020-2025.</div>', unsafe_allow_html=True)

# ── KPI ───────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('''<div class="kpi-box">
        <div class="kpi-lbl">GDP 2025</div>
        <div class="kpi-val">514,0 tỷ USD</div>
        <span class="kpi-tag">↑ +8,02%</span>
    </div>''', unsafe_allow_html=True)
with c2:
    st.markdown('''<div class="kpi-box">
        <div class="kpi-lbl">Kinh tế số / GDP</div>
        <div class="kpi-val">≈19,5%</div>
        <span class="kpi-tag">↑ +1,2 dpt</span>
    </div>''', unsafe_allow_html=True)
with c3:
    st.markdown('''<div class="kpi-box">
        <div class="kpi-lbl">FDI giải ngân 2025</div>
        <div class="kpi-val">27,6 tỷ USD</div>
        <span class="kpi-tag">↑ +8,9%</span>
    </div>''', unsafe_allow_html=True)
with c4:
    st.markdown('''<div class="kpi-box">
        <div class="kpi-lbl">GDP/người 2025</div>
        <div class="kpi-val">5.026 USD</div>
        <span class="kpi-tag">↑ +6,9%</span>
    </div>''', unsafe_allow_html=True)

st.markdown("---")

# ── 12 BÀI THEO CẤP ĐỘ ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">📚 12 bài toán theo 4 cấp độ</div>', unsafe_allow_html=True)

levels = [
    ("🟢 Cấp độ DỄ — Làm quen mô hình", "level-easy", [
        ("Bài 1", "Hàm sản xuất Cobb-Douglas mở rộng + AI", "Growth accounting, dự báo GDP 2030"),
        ("Bài 2", "LP phân bổ ngân sách 4 hạng mục", "scipy.optimize, shadow price"),
        ("Bài 3", "Chỉ số ưu tiên 10 ngành", "Min-max norm, weighted scoring, sensitivity"),
    ]),
    ("🟡 Cấp độ TRUNG BÌNH — Tối ưu cố điển", "level-medium", [
        ("Bài 4", "LP ngành-vùng 24 biến quyết định", "PuLP, CVXPY, ràng buộc công bằng"),
        ("Bài 5", "MIP lựa chọn 15 dự án số quốc gia", "Binary variables, precedence constraints"),
        ("Bài 6", "TOPSIS xếp hạng 6 vùng kinh tế", "Entropy weights, ideal solution"),
    ]),
    ("🔴 Cấp độ KHÁ KHÓ — Tối ưu nâng cao", "level-hard2", [
        ("Bài 7", "NSGA-II Pareto đa mục tiêu", "pymoo, 4 objectives, Pareto front 3D"),
        ("Bài 8", "Tối ưu động 2026-2035", "CVXPY, capital accumulation, TFP endogenous"),
        ("Bài 9", "Mô phỏng lao động & AI", "NetJob, retraining capacity, Sankey"),
    ]),
    ("🟣 Cấp độ KHÓ — Hệ thống tích hợp", "level-hard", [
        ("Bài 10", "Stochastic LP 2 giai đoạn", "Pyomo, VSS, EVPI, 4 kịch bản"),
        ("Bài 11", "Q-learning chính sách kinh tế", "MDP, epsilon-greedy, learning curve"),
        ("Bài 12", "AIDEOM-VN tích hợp", "6 modules, 5 kịch bản chính sách"),
    ]),
]

for title, cls, bais in levels:
    with st.expander(title, expanded=True):
        for code, name, desc in bais:
            st.markdown(f'''
            <div class="bai-row">
                <div>
                    <span class="bai-name">{code} — {name}</span><br>
                    <span class="bai-desc">{desc}</span>
                </div>
            </div>''', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p style="color:#555;font-size:12px;text-align:center">📊 Dữ liệu: NSO, MoST, MIC, MPI, WB, GII 2025 | Mô hình AIDEOM-VN</p>', unsafe_allow_html=True)
