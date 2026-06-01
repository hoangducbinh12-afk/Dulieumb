import streamlit as st
import json
import os

# Cấu hình giao diện chuẩn Mobile gọn gàng
st.set_page_config(page_title="Loto Pro V3.1", page_icon="📊", layout="centered")

# CSS tùy chỉnh để ép giao diện siêu gọn trên điện thoại (đã sửa lỗi tham số markdown)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 450px; }
    h3 { margin-bottom: 0.2rem; padding-bottom: 0px; }
    div[data-testid="stVerticalBlock"] > div { autocomplete: off; }
    .stNumberInput [data-testid="stMarkdownContainer"] p { font-size: 11px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data_master.json"

# Hàm tải dữ liệu gốc từ file json
def load_master_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

# Hàm lưu dữ liệu khi có cập nhật (Học Số)
def save_master_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# Khởi tạo trạng thái ứng dụng (Session State)
if 'master_data' not in st.session_state:
    st.session_state.master_data = load_master_data()
if 'history' not in st.session_state:
    st.session_state.history = []
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

st.title("🎯 LOTO SMART PRO V3.1")

# --- BƯỚC 1: QUẢN LÝ DỮ LIỆU Ở SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Cấu hình hệ thống")
    uploaded_file = st.file_uploader("Nạp đè file JSON mới", type=["json"])
    if uploaded_file is not None:
        try:
            st.session_state.master_data = json.load(uploaded_file)
            save_master_data(st.session_state.master_data)
            st.success("Đã đồng bộ kho dữ liệu!")
        except:
            st.error("File lỗi định dạng JSON!")
            
    if st.button("❌ XÓA SẠCH BỘ NHỚ", type="primary"):
        st.session_state.master_data = {}
        st.session_state.history = []
        st.session_state.prediction_result = None
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()

    # Nút bấm xuất dữ liệu dự phòng
    st.subheader("Sao lưu")
    json_string = json.dumps(st.session_state.master_data, ensure_ascii=False)
    st.download_button(
        label="📥 TẢI FILE DATA Master.json",
        data=json_string,
        file_name="data_master_updated.json",
        mime="application/json"
    )

# --- BƯỚC 2: NHẬP SỐ & SOI DÀN ---
st.subheader("📊 Phân tích Rank cầu")
col1, col2 = st.columns(2)
with col1:
    t2_input = st.text_input("Kỳ T-2 (Hệ số 10)", max_chars=2, placeholder="VD: 15")
with col2:
    t1_input = st.text_input("Kỳ T-1 (Hệ số 11)", max_chars=2, placeholder="VD: 88")

if st.button("🚀 SOI DÀN KẾT QUẢ KỲ T", use_container_width=True):
    if not t1_input or not t2_input:
        st.warning("Mày phải điền đủ cả số Kỳ T-1 và T-2!")
    else:
        pad_t1 = t1_input.zfill(2)
        pad_t2 = t2_input.zfill(2)
        
        # Khởi tạo bảng điểm cho 100 số
        scores = {str(i).zfill(2): {"score": 0, "hits": 0} for i in range(100)}
        
        # Tính điểm T-1 (Hệ số 11)
        if pad_t1 in st.session_state.master_data:
            for num, count in st.session_state.master_data[pad_t1].items():
                scores[num]["score"] += count * 11
                scores[num]["hits"] += count
                
        # Tính điểm T-2 (Hệ số 10)
        if pad_t2 in st.session_state.master_data:
            for num, count in st.session_state.master_data[pad_t2].items():
                scores[num]["score"] += count * 10
                scores[num]["hits"] += count
                
        # Sắp xếp Rank theo đúng luật: Điểm cao -> Tổng nổ lớn -> Số nhỏ ưu tiên hơn
        ranked = sorted(
            scores.keys(),
            key=lambda x: (-scores[x]["score"], -scores[x]["hits"], int(x))
        )
        
        st.session_state.prediction_result = {
            "t1": pad_t1,
            "t2": pad_t2,
            "ranked_list": ranked
        }

# --- HIỂN THỊ KẾT QUẢ DẠNG TEXT RÕ RÀNG ---
if st.session_state.prediction_result:
    ranked = st.session_state.prediction_result["ranked_list"]
    
    coti = ranked[0:9]
    ket = ranked[9:19]
    dep = ranked[19:39]
    tb = ranked[39:59]
    lot = ranked[59:79]
    loai = ranked[79:100]
    
    st.markdown(f"🔥 **DÀN CỐI:** {', '.join(coti)}")
    st.markdown(f"🎯 **DÀN KẾT:** {', '.join(ket)}")
    st.markdown(f"⭐ **DÀN ĐẸP:** {', '.join(dep)}")
    st.markdown(f"💎 **TRUNG BÌNH:** {', '.join(tb)}")
    st.markdown(f"🛡️ **XÉT LÓT:** {', '.join(lot)}")
    st.markdown(f"🚫 **DÀN LOẠI:** {', '.join(loai)}")
    st.write("---")

    # --- BƯỚC 3: GHI NHẬN KẾT QUẢ THỰC TẾ (HỌC SỐ CHỈ CỘNG T-1) ---
    st.subheader("📝 Ghi nhận Kỳ T thực tế")
    actual_input = st.text_input("Tối nay đài nổ con gì?", max_chars=2, placeholder="VD: 45")
    
    if st.button("💾 Ghi Nhận & Học Số", type="secondary"):
        if not actual_input:
            st.error("Chưa nhập số thực tế vừa về kìa mày!")
        else:
            act_num = actual_input.zfill(2)
            pred = st.session_state.prediction_result
            
            # Đối chiếu xem con số nổ rơi vào dàn nào
            idx = pred["ranked_list"].index(act_num)
            if idx <= 8: res = "DÀN CỐI"
            elif idx <= 18: res = "DÀN KẾT"
            elif idx <= 38: res = "DÀN ĐẸP"
            elif idx <= 58: res = "TRUNG BÌNH"
            elif idx <= 78: res = "XÉT LÓT"
            else: res = "DÀN LOẠI"
            
            # Chỉ cập nhật cộng +1 nhịp vào kho bạc nhớ của con Kỳ T-1
            t1 = pred["t1"]
            if t1 not in st.session_state.master_data:
                st.session_state.master_data[t1] = {}
            
            st.session_state.master_data[t1][act_num] = st.session_state.master_data[t1].get(act_num, 0) + 1
            
            # Lưu đè dữ liệu mới cập nhật vào file json trên máy chủ
            save_master_data(st.session_state.master_data)
            
            # Thêm thông tin vào danh sách nhật ký hiển thị công khai
            st.session_state.history.insert(0, {"num": act_num, "group": res})
            
            st.success(f"Ghi nhận thành công số {act_num} thuộc {res}! Bộ nhớ T-1 ({t1}) đã được cộng 1 nhịp.")
            
            # Xóa trạng thái dự đoán cũ và kích hoạt đảo số tự động cho ngày mai
            st.session_state.prediction_result = None
            st.rerun()

# --- BẢNG NHẬT KÝ NỔ DÀN ---
st.subheader("📋 Nhật ký nổ dàn")
if st.session_state.history:
    for idx, item in enumerate(st.session_state.history):
        st.text(f"Kỳ {len(st.session_state.history) - idx}: Số về {item['num']} ➔ {item['group']}")
else:
    st.caption("Chưa có nhật ký ghi nhận nào.")
