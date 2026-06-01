import streamlit as st
import json
import os

# 1. Cấu hình giao diện
st.set_page_config(page_title="Loto Pro V3.5", page_icon="🎯", layout="centered")

# 2. CSS làm đẹp
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3rem; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px; font-weight: bold; border-radius: 12px; }
    .result-card { background-color: white; padding: 12px; border-radius: 12px; border-left: 5px solid #4f46e5; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .group-label { font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 3px; }
    .number-text { font-size: 15px; font-weight: 600; color: #1e293b; line-height: 1.4; word-wrap: break-word; }
    .history-item { background: white; padding: 8px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #e5e7eb; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data_master.json"

# --- HÀM XỬ LÝ DỮ LIỆU ---
def load_all_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                full_data = json.load(f)
                master = full_data.get("master_data", full_data)
                history = full_data.get("history", [])
                return master, history
            except: return {}, []
    return {}, []

def save_all_data(master, history):
    full_data = {"master_data": master, "history": history}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False)

# --- KHỞI TẠO SESSION STATE ---
if 'master_data' not in st.session_state:
    m, h = load_all_data()
    st.session_state.master_data = m
    st.session_state.history = h

if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

# Hàm xử lý Học số (Callback) - ĐÂY LÀ CHÌA KHÓA FIX LỖI
def handle_learning():
    # Lấy dữ liệu từ Widget thông qua Key
    actual_val = st.session_state.get("actual_input_widget", "").strip()
    pred = st.session_state.prediction_result
    
    if actual_val and pred:
        act_num = actual_val.zfill(2)
        t1_key = pred["t1"]
        
        # 1. Cập nhật Bạc nhớ
        if t1_key not in st.session_state.master_data:
            st.session_state.master_data[t1_key] = {}
        st.session_state.master_data[t1_key][act_num] = st.session_state.master_data[t1_key].get(act_num, 0) + 1
        
        # 2. Lưu lịch sử
        idx = pred["list"].index(act_num) if act_num in pred["list"] else 99
        if idx <= 8: g = "DÀN CỐI"
        elif idx <= 18: g = "DÀN KẾT"
        elif idx <= 38: g = "DÀN ĐẸP"
        elif idx <= 58: g = "TRUNG BÌNH"
        elif idx <= 78: g = "XÉT LÓT"
        else: g = "DÀN LOẠI"
        st.session_state.history.insert(0, {"num": act_num, "group": g})
        
        # 3. Lưu file
        save_all_data(st.session_state.master_data, st.session_state.history)
        
        # 4. ĐẢO SỐ TỰ ĐỘNG (Ghi đè trực tiếp vào Widget State)
        st.session_state["t2_input_key"] = t1_key
        st.session_state["t1_input_key"] = act_num
        
        # 5. Reset các ô khác
        st.session_state["actual_input_widget"] = ""
        st.session_state.prediction_result = None
        st.toast(f"Đã học số {act_num} thành công!", icon="✅")

st.title("🎯 LOTO SMART V3.5")

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
            st.success("Đã nạp xong!")
        except: st.error("File lỗi!")

    if st.button("❌ RESET ALL"):
        for key in st.session_state.keys(): del st.session_state[key]
        if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
        st.rerun()
    
    st.subheader("Sao lưu")
    out_json = json.dumps({"master_data": st.session_state.master_data, "history": st.session_state.history}, ensure_ascii=False)
    st.download_button("📥 TẢI DỮ LIỆU VỀ", out_json, "loto_master.json", "application/json")

# --- NHẬP LIỆU SOI CẦU ---
st.write("**PHÂN TÍCH RANK**")
col1, col2 = st.columns(2)
with col1:
    st.text_input("Kỳ T-2", placeholder="Hệ số 10", key="t2_input_key")
with col2:
    st.text_input("Kỳ T-1", placeholder="Hệ số 11", key="t1_input_key")

if st.button("🚀 SOI DÀN DỰ ĐOÁN", type="primary"):
    t1 = st.session_state.get("t1_input_key", "").strip()
    t2 = st.session_state.get("t2_input_key", "").strip()
    
    if t1 and t2:
        p_t1, p_t2 = t1.zfill(2), t2.zfill(2)
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
        st.session_state.prediction_result = {"t1": p_t1, "t2": p_t2, "list": ranked_list}
    else:
        st.warning("Nhập đủ 2 kỳ đi mày!")

# --- HIỂN THỊ KẾT QUẢ ---
if st.session_state.prediction_result:
    r = st.session_state.prediction_result.get("list", [])
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
        st.markdown(f"""<div class="result-card" style="border-left-color: {color}"><div class="group-label" style="color: {color}">{label}</div><div class="number-text">{', '.join(nums)}</div></div>""", unsafe_allow_html=True)

    # --- HỌC SỐ & TỰ NHẢY SỐ ---
    st.write("---")
    st.write("**GHI NHẬN KẾT QUẢ THỰC TẾ**")
    st.text_input("Số về hôm nay là gì?", key="actual_input_widget")
    
    # Dùng On_Click để gọi hàm Callback giúp fix lỗi StreamlitAPIException
    st.button("💾 GHI NHẬN & HỌC SỐ", on_click=handle_learning)

# --- NHẬT KÝ ---
st.write("---")
st.subheader("📋 Nhật ký nổ")
if st.session_state.history:
    for h in st.session_state.history[:15]:
        badge = "color:#ef4444; font-weight:bold;" if h['group'] == "DÀN CỐI" else "color:#1e293b;"
        st.markdown(f"""<div class="history-item">Số về: <b>{h['num']}</b> ➔ <span style="{badge}">{h['group']}</span></div>""", unsafe_allow_html=True)
