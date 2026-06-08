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
    .stButton>button:hover { border-color: #10B981; color: #10B981; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px; font-weight: bold; border-radius: 12px; }
    .result-card { background-color: white; padding: 12px; border-radius: 12px; border-left: 5px solid #4f46e5; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .group-label { font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 3px; }
    .number-text { font-size: 15px; font-weight: 600; color: #1e293b; line-height: 1.4; }
    
    /* CẤU TRÚC VIỀN VÀ NỀN MỚI CHO NHẬT KÝ NỔ CYBERPUNK */
    .history-item { padding: 10px; border-radius: 10px; margin-bottom: 6px; font-size: 13px; font-weight: bold; border-left: 5px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .hist-côi { background-color: #FEF2F2; border-left-color: #ef4444; color: #991b1b; }
    .hist-kết { background-color: #FFF7ED; border-left-color: #f97316; color: #9a3412; }
    .hist-đẹp { background-color: #FEFCE8; border-left-color: #eab308; color: #854d0e; }
    .hist-trungbinh { background-color: #F0FDF4; border-left-color: #22c55e; color: #166534; }
    .hist-xétlót { background-color: #EFF6FF; border-left-color: #3b82f6; color: #1e40af; }
    .hist-loại { background-color: #F8FAFC; border-left-color: #94a3b8; color: #475569; }
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
    actual_val = st.session_state.get("input_actual_key", "").strip()
    pred = st.session_state.prediction_result
    
    if actual_val and pred:
        act_num = actual_val.zfill(2)
        t1_key = pred["t1"]
        
        if t1_key not in st.session_state.master_data:
            st.session_state.master_data[t1_key] = {}
        
        current_count = st.session_state.master_data[t1_key].get(act_num, 0)
        st.session_state.master_data[t1_key][act_num] = current_count + 1
        
        idx = pred["list"].index(act_num) if act_num in pred["list"] else 99
        if idx <= 8: g = "DÀN CỐI"
        elif idx <= 18: g = "DÀN KẾT"
        elif idx <= 38: g = "DÀN ĐẸP"
        elif idx <= 58: g = "TRUNG BÌNH"
        elif idx <= 78: g = "XÉT LÓT"
        else: g = "DÀN LOẠI"
        
        st.session_state.history.insert(0, {"num": act_num, "group": g})
        save_all_data(st.session_state.master_data, st.session_state.history)
        
        st.session_state["widget_t2"] = t1_key
        st.session_state["widget_t1"] = act_num
        
        st.session_state["input_actual_key"] = "" 
        st.session_state.prediction_result = None 
        
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
        ("🛡️ XXét Lót", r[59:79], "#3b82f6"),
        ("🚫 DÀN LOẠI", r[79:100], "#94a3b8")
    ]
    st.write("---")
    for label, nums, color in groups:
        st.markdown(f"""<div class="result-card" style="border-left-color: {color}"><div class="group-label" style="color: {color}">{label}</div><div class="number-text">{', '.join(nums)}</div></div>""", unsafe_allow_html=True)

    st.write("---")
    st.write("**GHI NHẬN KẾT QUẢ THỰC TẾ**")
    st.text_input("Số về hôm nay là gì?", key="input_actual_key")
    st.button("💾 GHI NHẬN & HỌC SỐ", on_click=callback_hoc_so)

# --- NHẬT KÝ ĐÃ ĐƯỢC TÂN TRANG RỰC RỠ ---
st.write("---")
st.subheader("📋 Nhật ký nổ")
if st.session_state.history:
    for h in st.session_state.history[:15]:
        # Tự động nhận diện dàn để dán nhãn CSS và icon rực rỡ tương ứng
        if h['group'] == "DÀN CỐI":
            css_class, icon = "hist-côi", "🔥"
        elif h['group'] == "DÀN KẾT":
            css_class, icon = "hist-kết", "🎯"
        elif h['group'] == "DÀN ĐẸP":
            css_class, icon = "hist-đẹp", "⭐"
        elif h['group'] == "TRUNG BÌNH":
            css_class, icon = "hist-trungbinh", "💎"
        elif h['group'] == "XÉT LÓT":
            css_class, icon = "hist-xétlót", "🛡️"
        else:
            css_class, icon = "hist-loại", "🚫"
            
        # Xuất bản giao diện hộp nhật ký có màu nền rực rỡ riêng biệt
        st.markdown(f"""
            <div class="history-item {css_class}">
                🔢 Số về: <span style="font-size:16px;"><b>{h['num']}</b></span> ➔ {icon} {h['group']}
            </div>
        """, unsafe_allow_html=True)
