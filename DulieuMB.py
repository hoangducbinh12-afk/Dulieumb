import streamlit as st
import json
import os

# Cấu hình giao diện chuẩn Mobile chuyên nghiệp
st.set_page_config(page_title="Loto Intelligence", page_icon="🎯", layout="centered")

# CSS tùy chỉnh để làm giao diện cực đẹp trên iPhone
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3rem; transition: all 0.3s; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px; font-weight: bold; border-radius: 12px; border: 2px solid #dee2e6; }
    .result-card { background-color: white; padding: 15px; border-radius: 15px; border-left: 5px solid #4f46e5; shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 10px; }
    .group-label { font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
    .number-text { font-size: 16px; font-weight: 600; color: #1e293b; line-height: 1.5; }
    .history-item { background: white; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #e5e7eb; font-size: 13px; }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data_master.json"

# --- HÀM XỬ LÝ DỮ LIỆU ---
def load_all_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                full_data = json.load(f)
                # Tách biệt master_data và history nếu có
                master = full_data.get("master_data", full_data) # Hỗ trợ cả file cũ và mới
                history = full_data.get("history", [])
                return master, history
            except:
                return {}, []
    return {}, []

def save_all_data(master, history):
    full_data = {
        "master_data": master,
        "history": history
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False)

# --- KHỞI TẠO SESSION STATE ---
if 'master_data' not in st.session_state or 'history' not in st.session_state:
    m, h = load_all_data()
    st.session_state.master_data = m
    st.session_state.history = h

if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

# Giao diện chính
st.title("🎯 LOTO SMART V3.2")

# --- SIDEBAR: CÀI ĐẶT ---
with st.sidebar:
    st.header("⚙️ Hệ thống")
    uploaded_file = st.file_uploader("Nạp file JSON", type=["json"])
    if uploaded_file:
        try:
            temp_data = json.load(uploaded_file)
            st.session_state.master_data = temp_data.get("master_data", temp_data)
            st.session_state.history = temp_data.get("history", [])
            save_all_data(st.session_state.master_data, st.session_state.history)
            st.success("Đã đồng bộ Dữ liệu & Lịch sử!")
        except:
            st.error("Lỗi file!")

    if st.button("❌ RESET ALL"):
        st.session_state.master_data = {}
        st.session_state.history = []
        if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
        st.rerun()

    st.subheader("Sao lưu")
    out_json = json.dumps({"master_data": st.session_state.master_data, "history": st.session_state.history}, ensure_ascii=False)
    st.download_button("📥 TẢI FILE DATA (.json)", out_json, "loto_backup.json", "application/json")

# --- NHẬP LIỆU ---
with st.container():
    st.markdown('<p style="font-size:12px; font-weight:bold; color:gray; margin-bottom:5px;">PHÂN TÍCH RANK</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        # Sử dụng key để có thể thay đổi giá trị từ code
        t2_val = st.text_input("Kỳ T-2", value=st.session_state.get('input_t2', ''), placeholder="Hệ số 10", key="t2_ui")
    with c2:
        t1_val = st.text_input("Kỳ T-1", value=st.session_state.get('input_t1', ''), placeholder="Hệ số 11", key="t1_ui")

if st.button("🚀 SOI DÀN DỰ ĐOÁN", type="primary"):
    if t1_val and t2_val:
        p_t1, p_t2 = t1_val.zfill(2), t2_val.zfill(2)
        
        scores = {str(i).zfill(2): {"s": 0, "h": 0} for i in range(100)}
        
        # Tính điểm
        m = st.session_state.master_data
        if p_t1 in m:
            for n, c in m[p_t1].items():
                scores[n]["s"] += c * 11
                scores[n]["h"] += c
        if p_t2 in m:
            for n, c in m[p_t2].items():
                scores[n]["s"] += c * 10
                scores[n]["h"] += c
                
        ranked = sorted(scores.keys(), key=lambda x: (-scores[x]["s"], -scores[x]["h"], int(x)))
        st.session_state.prediction_result = {"t1": p_t1, "t2": p_t2, "list": ranked}
    else:
        st.warning("Nhập đủ 2 kỳ đi mày!")

# --- HIỂN THỊ DÀN ---
if st.session_state.prediction_result:
    r = st.session_state.prediction_result["list"]
    groups = [
        ("🔥 DÀN CỐI", r[0:9], "#ef4444"),
        ("🎯 DÀN KẾT", r[9:19], "#f97316"),
        ("⭐ DÀN ĐẸP", r[19:39], "#eab308"),
        ("💎 TRUNG BÌNH", r[39:59], "#22c55e"),
        ("🛡️ XÉT LÓT", r[59:79], "#3b82f6"),
        ("🚫 DÀN LOẠI", r[79:100], "#94a3b8")
    ]
    
    for label, nums, color in groups:
        st.markdown(f"""
            <div class="result-card" style="border-left-color: {color}">
                <div class="group-label" style="color: {color}">{label}</div>
                <div class="number-text">{', '.join(nums)}</div>
            </div>
        """, unsafe_allow_html=True)

    # --- HỌC SỐ & TỰ NHẢY KỲ ---
    st.write("---")
    st.markdown('<p style="font-size:12px; font-weight:bold; color:gray; margin-bottom:5px;">CẬP NHẬT KẾT QUẢ THỰC TẾ</p>', unsafe_allow_html=True)
    actual = st.text_input("Con số vừa nổ là gì?", placeholder="Nhập số Kỳ T")
    
    if st.button("💾 HỌC SỐ & TIẾP TỤC"):
        if actual:
            act_num = actual.zfill(2)
            pred = st.session_state.prediction_result
            
            # Lưu lịch sử
            idx = pred["list"].index(act_num)
            if idx <= 8: res = "CỐI"
            elif idx <= 18: res = "KẾT"
            elif idx <= 38: res = "ĐẸP"
            elif idx <= 58: res = "TRUNG BÌNH"
            elif idx <= 78: res = "LÓT"
            else: res = "LOẠI"
            
            st.session_state.history.insert(0, {"num": act_num, "group": res})
            
            # Cập nhật Master Data (Chỉ T-1)
            t1 = pred["t1"]
            if t1 not in st.session_state.master_data: st.session_state.master_data[t1] = {}
            st.session_state.master_data[t1][act_num] = st.session_state.master_data[t1].get(act_num, 0) + 1
            
            # QUAN TRỌNG: TỰ ĐỘNG NHẢY KỲ CHO NGÀY MAI
            st.session_state.input_t2 = t1 # T-1 cũ nhảy sang T-2
            st.session_state.input_t1 = act_num # Số vừa về nhảy vào T-1
            
            save_all_data(st.session_state.master_data, st.session_state.history)
            st.session_state.prediction_result = None
            st.success(f"Đã học số {act_num}. Kỳ mới đã sẵn sàng!")
            st.rerun()

# --- NHẬT KÝ ---
st.write("---")
st.subheader("📋 Nhật ký nổ")
for h in st.session_state.history[:20]: # Hiển thị 20 kỳ gần nhất
    color = "#ef4444" if h['group'] == "CỐI" else "#1e293b"
    st.markdown(f"""
        <div class="history-item">
            Số về: <b>{h['num']}</b> ➔ <span style="color:{color}; font-weight:bold;">{h['group']}</span>
        </div>
    """, unsafe_allow_html=True)
