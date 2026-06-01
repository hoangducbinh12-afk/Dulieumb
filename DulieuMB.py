import streamlit as st
import json
import os

# 1. Cấu hình giao diện chuẩn Mobile
st.set_page_config(page_title="Loto Intelligence Fix", page_icon="🎯", layout="centered")

# 2. CSS làm đẹp giao diện
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3rem; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px; font-weight: bold; border-radius: 12px; }
    .result-card { background-color: white; padding: 15px; border-radius: 15px; border-left: 5px solid #4f46e5; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .group-label { font-size: 12px; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }
    .number-text { font-size: 16px; font-weight: 600; color: #1e293b; line-height: 1.5; word-wrap: break-word; }
    .history-item { background: white; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #e5e7eb; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data_master.json"

# 3. Hàm xử lý dữ liệu (Load/Save)
def load_all_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                full_data = json.load(f)
                master = full_data.get("master_data", full_data)
                history = full_data.get("history", [])
                return master, history
            except:
                return {}, []
    return {}, []

def save_all_data(master, history):
    full_data = {"master_data": master, "history": history}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False)

# 4. Khởi tạo Session State
if 'master_data' not in st.session_state:
    m, h = load_all_data()
    st.session_state.master_data = m
    st.session_state.history = h

if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

# Giao diện chính
st.title("🎯 LOTO SMART V3.3")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Hệ thống")
    uploaded_file = st.file_uploader("Nạp file JSON", type=["json"])
    if uploaded_file:
        try:
            temp_data = json.load(uploaded_file)
            st.session_state.master_data = temp_data.get("master_data", temp_data)
            st.session_state.history = temp_data.get("history", [])
            save_all_data(st.session_state.master_data, st.session_state.history)
            st.success("Đã đồng bộ!")
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

# --- PHẦN 1: FORM NHẬP LIỆU SOI CẦU ---
with st.container():
    st.write("**PHÂN TÍCH RANK**")
    # Tự lấy giá trị từ session_state để điền vào ô nhập (Tự nhảy số)
    val_t2_default = st.session_state.get('next_t2', '')
    val_t1_default = st.session_state.get('next_t1', '')
    
    col1, col2 = st.columns(2)
    with col1:
        t2_in = st.text_input("Kỳ T-2", value=val_t2_default, placeholder="Hệ số 10", key="t2_input")
    with col2:
        t1_in = st.text_input("Kỳ T-1", value=val_t1_default, placeholder="Hệ số 11", key="t1_input")

    if st.button("🚀 SOI DÀN DỰ ĐOÁN", type="primary"):
        if t1_in and t2_in:
            p_t1, p_t2 = t1_in.zfill(2), t2_in.zfill(2)
            scores = {str(i).zfill(2): {"s": 0, "h": 0} for i in range(100)}
            
            m = st.session_state.master_data
            if p_t1 in m:
                for n, c in m[p_t1].items():
                    scores[n]["s"] += c * 11
                    scores[n]["h"] += c
            if p_t2 in m:
                for n, c in m[p_t2].items():
                    scores[n]["s"] += c * 10
                    scores[n]["h"] += c
            
            ranked_list = sorted(scores.keys(), key=lambda x: (-scores[x]["s"], -scores[x]["h"], int(x)))
            # Lưu vào session để không bị mất khi thao tác tiếp theo
            st.session_state.prediction_result = {"t1": p_t1, "t2": p_t2, "list": ranked_list}
        else:
            st.warning("Nhập đủ 2 kỳ!")

# --- PHẦN 2: HIỂN THỊ KẾT QUẢ ---
# Sử dụng kiểm tra 'list' in để tránh KeyError
if st.session_state.prediction_result and "list" in st.session_state.prediction_result:
    r = st.session_state.prediction_result["list"]
    
    res_groups = [
        ("🔥 DÀN CỐI", r[0:9], "#ef4444"),
        ("🎯 DÀN KẾT", r[9:19], "#f97316"),
        ("⭐ DÀN ĐẸP", r[19:39], "#eab308"),
        ("💎 TRUNG BÌNH", r[39:59], "#22c55e"),
        ("🛡️ XÉT LÓT", r[59:79], "#3b82f6"),
        ("🚫 DÀN LOẠI", r[79:100], "#94a3b8")
    ]
    
    st.write("---")
    for label, nums, color in res_groups:
        st.markdown(f"""
            <div class="result-card" style="border-left-color: {color}">
                <div class="group-label" style="color: {color}">{label}</div>
                <div class="number-text">{', '.join(nums)}</div>
            </div>
        """, unsafe_allow_html=True)

    # --- PHẦN 3: HỌC SỐ & TỰ NHẢY SỐ ---
    st.write("---")
    st.write("**CẬP NHẬT KẾT QUẢ THỰC TẾ**")
    actual = st.text_input("Con số vừa nổ Kỳ T là gì?", placeholder="VD: 45", key="actual_in")
    
    if st.button("💾 GHI NHẬN & HỌC SỐ"):
        if actual:
            act_num = actual.zfill(2)
            pred = st.session_state.prediction_result
            
            # Tính toán xem rơi vào dàn nào
            idx = pred["list"].index(act_num)
            if idx <= 8: g = "DÀN CỐI"
            elif idx <= 18: g = "DÀN KẾT"
            elif idx <= 38: g = "DÀN ĐẸP"
            elif idx <= 58: g = "TRUNG BÌNH"
            elif idx <= 78: g = "XÉT LÓT"
            else: g = "DÀN LOẠI"
            
            # Cập nhật Master (Chỉ cộng T-1)
            t1_key = pred["t1"]
            if t1_key not in st.session_state.master_data:
                st.session_state.master_data[t1_key] = {}
            st.session_state.master_data[t1_key][act_num] = st.session_state.master_data[t1_key].get(act_num, 0) + 1
            
            # Cập nhật Lịch sử
            st.session_state.history.insert(0, {"num": act_num, "group": g})
            
            # ĐẢO SỐ TỰ ĐỘNG: Gán giá trị vào session_state để lần sau load lên ô input
            st.session_state.next_t2 = t1_key # T-1 cũ thành T-2 mới
            st.session_state.next_t1 = act_num # Số vừa nổ thành T-1 mới
            
            save_all_data(st.session_state.master_data, st.session_state.history)
            st.session_state.prediction_result = None # Xóa dàn cũ
            st.success(f"Đã học số {act_num}. Kỳ mới đã sẵn sàng!")
            st.rerun()

# --- PHẦN 4: NHẬT KÝ ---
st.write("---")
st.subheader("📋 Nhật ký nổ")
if st.session_state.history:
    for h in st.session_state.history[:20]:
        badge_style = "color:#ef4444; font-weight:bold;" if h['group'] == "DÀN CỐI" else "color:#1e293b;"
        st.markdown(f"""
            <div class="history-item">
                Số về: <b>{h['num']}</b> ➔ <span style="{badge_style}">{h['group']}</span>
            </div>
        """, unsafe_allow_html=True)
else:
    st.caption("Chưa có lịch sử.")
