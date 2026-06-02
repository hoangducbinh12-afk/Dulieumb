import streamlit as st
import json
import os
import time

# 1. Cấu hình giao diện
st.set_page_config(page_title="Loto Pro V3.6", page_icon="🎯", layout="centered")

# 2. CSS Giao diện
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3rem; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px; font-weight: bold; border-radius: 12px; }
    .result-card { background-color: white; padding: 12px; border-radius: 12px; border-left: 5px solid #4f46e5; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .group-label { font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 3px; }
    .number-text { font-size: 15px; font-weight: 600; color: #1e293b; line-height: 1.4; }
    .history-item { background: white; padding: 8px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #e5e7eb; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data_master.json"

# --- HÀM XỬ LÝ DỮ LIỆU ---
def load_all_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                full_data = json.load(f)
                master = full_data.get("master_data", full_data)
                history = full_data.get("history", [])
                return master, history
        except Exception as e:
            return {}, []
    return {}, []

def save_all_data(master, history):
    try:
        full_data = {"master_data": master, "history": history}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(full_data, f, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Lỗi ghi file: {e}")
        return False

# --- KHỞI TẠO SESSION STATE ---
if 'master_data' not in st.session_state:
    m, h = load_all_data()
    st.session_state.master_data = m
    st.session_state.history = h

if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

# --- HÀM CALLBACK: XỬ LÝ HỌC SỐ & TỰ NHẢY KỲ ---
def callback_hoc_so():
    # 1. Lấy dữ liệu từ Widget thông qua Key
    actual_val = st.session_state.get("input_actual_key", "").strip()
    pred = st.session_state.prediction_result
    
    if actual_val and pred:
        act_num = actual_val.zfill(2)
        t1_key = pred["t1"]
        
        # 2. Cập nhật Bạc nhớ (Master Data)
        if t1_key not in st.session_state.master_data:
            st.session_state.master_data[t1_key] = {}
        
        current_count = st.session_state.master_data[t1_key].get(act_num, 0)
        st.session_state.master_data[t1_key][act_num] = current_count + 1
        
        # 3. Tính toán dàn nổ để lưu lịch sử
        idx = pred["list"].index(act_num) if act_num in pred["list"] else 99
        if idx <= 8: g = "DÀN CỐI"
        elif idx <= 18: g = "DÀN KẾT"
        elif idx <= 38: g = "DÀN ĐẸP"
        elif idx <= 58: g = "TRUNG BÌNH"
        elif idx <= 78: g = "XÉT LÓT"
        else: g = "DÀN LOẠI"
        
        st.session_state.history.insert(0, {"num": act_num, "group": g})
        
        # 4. Ghi đè vào file vật lý
        save_all_data(st.session_state.master_data, st.session_state.history)
        
        # 5. ĐẢO SỐ TỰ ĐỘNG (Ép Widget nhận giá trị mới)
        st.session_state["widget_t2"] = t1_key
        st.session_state["widget_t1"] = act_num
        
        # 6. Dọn dẹp trạng thái
        st.session_state["input_actual_key"] = "" # Xóa ô nhập số về
        st.session_state.prediction_result = None # Ẩn dàn dự đoán cũ
        
        # Thông báo thành công kiểu Toast (hiện góc màn hình)
        st.toast(f"Đã học số {act_num} (Nhịp sau {t1_key}). Đã nhảy kỳ mới!", icon="✅")

# --- GIAO DIỆN CHÍNH ---
st.title("🎯 LOTO SMART V3.6")

with st.sidebar:
    st.header("⚙️ Hệ thống")
    uploaded_file = st.file_uploader("Nạp file JSON dự phòng", type=["json"])
    if uploaded_file:
        temp = json.load(uploaded_file)
        st.session_state.master_data = temp.get("master_data", temp)
        st.session_state.history = temp.get("history", [])
        save_all_data(st.session_state.master_data, st.session_state.history)
        st.success("Đã đồng bộ!")

    if st.button("❌ RESET ALL DATA"):
        for k in st.session_state.keys(): del st.session_state[k]
        if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
        st.rerun()
    
    st.subheader("Sao lưu")
    out_json = json.dumps({"master_data": st.session_state.master_data, "history": st.session_state.history}, ensure_ascii=False)
    st.download_button("📥 TẢI DỮ LIỆU VỀ", out_json, "loto_master.json", "application/json")

# --- PHẦN NHẬP SOI CẦU ---
st.write("**PHÂN TÍCH RANK**")
col1, col2 = st.columns(2)
with col1:
    st.text_input("Kỳ T-2", placeholder="Hệ số 10", key="widget_t2")
with col2:
    st.text_input("Kỳ T-1", placeholder="Hệ số 11", key="widget_t1")

if st.button("🚀 SOI DÀN DỰ ĐOÁN", type="primary"):
    t1 = st.session_state.get("widget_t1", "").strip()
    t2 = st.session_state.get("widget_t2", "").strip()
    
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
        st.warning("Điền đủ T-1 và T-2!")

# --- HIỂN THỊ DÀN ---
if st.session_state.prediction_result:
    r = st.session_state.prediction_result.get("list", [])
    groups = [
        ("🔥 DÀN CỐI", r[0:9], "#ef4444"),
        ("🎯 DÀN KẾT", r[9:19], "#f97316"),
        ("⭐ DÀN ĐẸP", r[19:39], "#eab308"),
        ("💎 TRUNG BÌNH", r[39:59], "#22c55e"),
        ("🛡️ XÉT LÓT", r[59:79], "#3b82f6"),
        ("🚫 DÀN LOẠI", r[79:100], "#94a3b8")
    ]
    st.write("---")
    for label, nums, color in groups:
        st.markdown(f"""<div class="result-card" style="border-left-color: {color}"><div class="group-label" style="color: {color}">{label}</div><div class="number-text">{', '.join(nums)}</div></div>""", unsafe_allow_html=True)

    # --- HỌC SỐ ---
    st.write("---")
    st.write("**GHI NHẬN KẾT QUẢ THỰC TẾ**")
    st.text_input("Số về hôm nay là gì?", key="input_actual_key")
    
    # Dùng on_click để xử lý logic Đảo số và Ghi nhớ ngay khi bấm nút
    st.button("💾 GHI NHẬN & HỌC SỐ", on_click=callback_hoc_so)

# --- NHẬT KÝ ---
st.write("---")
st.subheader("📋 Nhật ký nổ")
if st.session_state.history:
    for h in st.session_state.history[:15]:
        b = "color:#ef4444; font-weight:bold;" if h['group'] == "DÀN CỐI" else "color:#1e293b;"
        st.markdown(f"""<div class="history-item">Số về: <b>{h['num']}</b> ➔ <span style="{b}">{h['group']}</span></div>""", unsafe_allow_html=True)
