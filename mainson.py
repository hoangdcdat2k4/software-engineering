import streamlit as st
import sqlite3
import hashlib  # Để mã hóa mật khẩu
from utils import database
import pandas as pd

from components import header, profile_card, task_management, achievements, attendance, dashboard_cards, training_performance

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Quản lý Nhân sự", page_icon=":office:", layout="wide")

# Load Font Awesome with a direct link to CSS file
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" integrity="sha512-1ycn6IcaQQ40/MKBW2W4Rhis/DbILU74C1vSrLJxCq57o941Ym01SwNsOMqvEBFlcgUa6xLiPY/NS5R+E6ztJQ==" crossorigin="anonymous" referrerpolicy="no-referrer" />
<style>
/* Fix to ensure Font Awesome icons display properly */
.fa, .fas, .far, .fal, .fab {
  font-family: "Font Awesome 5 Free", "Font Awesome 5 Brands" !important;
}
.fas, .fa {
  font-weight: 900 !important;
}
.far {
  font-weight: 400 !important;
}
</style>
""", unsafe_allow_html=True)

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- KẾT NỐI CƠ SỞ DỮ LIỆU ---
DATABASE_PATH = "data/quanlynhansu.db"  # Đường dẫn đến file database (đã sửa)

def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

conn = connect_db()
if conn:
    database.create_tables(conn) # Gọi hàm tạo bảng từ database.py
    conn.close()
    print("Đã tạo database và các bảng (nếu chưa tồn tại).") # Thêm dòng này
else:
    print("Không thể kết nối đến database.")

def close_db(conn):
    conn.close()

# --- HÀM MÃ HÓA MẬT KHẨU ---
def hash_password(password):
    """Mã hóa mật khẩu sử dụng SHA-256."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

# --- HÀM KIỂM TRA ĐĂNG NHẬP ---
def kiem_tra_dang_nhap(ten_dang_nhap, mat_khau):
    """Kiểm tra thông tin đăng nhập trong cơ sở dữ liệu."""
    conn = connect_db()
    cursor = conn.cursor()
    hashed_password = hash_password(mat_khau)  # Mã hóa mật khẩu người dùng nhập
    cursor.execute("SELECT * FROM TaiKhoan WHERE TenDangNhap = ? AND MatKhau = ?", (ten_dang_nhap, hashed_password))
    user = cursor.fetchone()
    close_db(conn)
    return user

# --- HÀM TẠO TÀI KHOẢN MỚI (CHỈ DÀNH CHO ADMIN) ---
def tao_tai_khoan(ten_dang_nhap, mat_khau, ma_nhan_vien, quyen_han):
  """Tạo tài khoản mới trong cơ sở dữ liệu."""
  conn = connect_db()
  cursor = conn.cursor()
  hashed_password = hash_password(mat_khau)
  try:
    cursor.execute("INSERT INTO TaiKhoan (TenDangNhap, MatKhau, MaNhanVien, QuyenHan) VALUES (?, ?, ?, ?)", (ten_dang_nhap, hashed_password, ma_nhan_vien, quyen_han))
    conn.commit()
    close_db(conn)
    return True # Tạo thành công
  except sqlite3.Error as e:
    print(f"Lỗi tạo tài khoản: {e}")
    close_db(conn)
    return False # Tạo thất bại

# --- GIAO DIỆN ĐĂNG NHẬP ---
def trang_dang_nhap():
    # Use columns to center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and title with styles applied directly
        st.markdown("<div style='text-align: center; margin-bottom: 30px; margin-top: 50px;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 48px; font-weight: 700; color: #333; margin-bottom: 20px; letter-spacing: -1px;'>PTIT Telecom<span style='color: #6c7ae0;'>.</span></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 24px; font-weight: 500; color: #333;'>Đăng nhập</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Create login form with modern styling
        with st.form("login_form", clear_on_submit=False):
            # Apply custom style to form
            st.markdown(
                """
                <style>
                div[data-testid="stForm"] {
                    background-color: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                }
                div.stButton > button {
                    width: 100%;
                    margin-top: 10px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            ten_dang_nhap = st.text_input("Tên đăng nhập")
            mat_khau = st.text_input("Mật khẩu", type="password")
            
            submit_button = st.form_submit_button("Đăng nhập")
            
            if submit_button:
                user = kiem_tra_dang_nhap(ten_dang_nhap, mat_khau)
                if user:
                    # Lưu thông tin người dùng vào session state
                    st.session_state.dang_nhap = True
                    st.session_state.ten_nguoi_dung = ten_dang_nhap # hoặc lấy từ CSDL nếu có HoTen
                    st.session_state.quyen_han = user[4] # Lấy quyền hạn từ CSDL (cột 4)
                    st.session_state.user_id = user[1]  # Lưu MaNhanVien
                    st.success(f"Đăng nhập thành công! Chào mừng {ten_dang_nhap}.")
                    st.rerun() # Tải lại trang để hiển thị giao diện sau đăng nhập
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không đúng.")
        
        # Add demo credentials
        st.markdown("<div style='text-align: center; margin-top: 20px; font-size: 14px; color: #666;'>Tài khoản demo: <strong>admin</strong> / Mật khẩu: <strong>admin</strong></div>", unsafe_allow_html=True)

# --- GIAO DIỆN TRANG CHỦ (SAU KHI ĐĂNG NHẬP) ---
def trang_chu():
     #Hiển thị header
    header.header(st.session_state.ten_nguoi_dung, st.session_state.quyen_han)

   # --- SIDEBAR ---
    with st.sidebar:
        # Add sidebar logo
        st.markdown("<div style='padding: 20px 0; margin-bottom: 20px; border-bottom: 1px solid #f0f0f0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 24px; font-weight: 700; color: #333; text-align: center; letter-spacing: -0.5px;'>acme<span style='color: #6c7ae0;'>.</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- DANH SÁCH CÁC MODULE ---
        modules = ["Dashboard", "Thông tin cá nhân", "Công việc", "Thành tích", "Chấm công", "Đào tạo & Đánh giá"]  # Modules for all users
        
        if st.session_state.quyen_han == "admin":
            modules.extend(["Quản lý hệ thống", "Quản lý Nhân viên", "Báo cáo"]) # Admin modules
            
        # Custom styling for sidebar menu
        st.markdown(
            """
            <style>
            div[data-testid="stRadio"] > div {
                display: flex;
                flex-direction: column;
            }
            div[data-testid="stRadio"] > div > label {
                padding: 10px 15px;
                border-radius: 8px;
                margin-bottom: 5px;
                transition: all 0.3s;
            }
            div[data-testid="stRadio"] > div > label:hover {
                background-color: #f5f7f9;
            }
            div[data-testid="stRadio"] > div > label[data-baseweb="radio"] > div:first-child {
                background-color: #6c7ae0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
            
        selected_module = st.radio("", modules)
        
        # Log out button at the bottom of sidebar
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        if st.button("Đăng xuất", key="logout_btn"):
            st.session_state.dang_nhap = False
            st.session_state.ten_nguoi_dung = None
            st.session_state.quyen_han = None
            st.session_state.user_id = None
            st.rerun()

    # --- NỘI DUNG CHÍNH TÙY THEO MODULE VÀ QUYỀN HẠN ---
    if st.session_state.dang_nhap:
        # Check if user is admin
        is_admin = st.session_state.quyen_han == "admin"
        
        if selected_module == "Dashboard":
            # --- DASHBOARD PAGE ---
            st.header("Dashboard")
            
            # Add employee info at the top
            conn = database.connect_db()
            if conn:
                nhan_vien = database.lay_nhan_vien_theo_id(conn, st.session_state.user_id)
                database.close_db(conn)
                
                if nhan_vien:
                    employee_name = nhan_vien[1]
                    
                    # Create welcome banner with native Streamlit elements
                    st.info(f"Xin chào, {employee_name}! Chào mừng quay trở lại với hệ thống quản lý nhân sự.")
            
            # Leave information dashboard
            dashboard_cards.employee_leave_dashboard(st.session_state.user_id)
            
            # Time tracking statistics
            dashboard_cards.time_tracking_stats(st.session_state.user_id)
            
            # Requests and upcoming events
            col1, col2 = st.columns([3, 1])
            
            with col1:
                dashboard_cards.request_list(st.session_state.user_id)
            
            with col2:
                dashboard_cards.upcoming_events()
                
        elif selected_module == "Thông tin cá nhân":
            # --- HIỂN THỊ THÔNG TIN CÁ NHÂN ---
            st.header("Thông tin cá nhân")
            
            conn = database.connect_db()
            if conn:
                tai_khoan = database.lay_tai_khoan_theo_ten_dang_nhap(conn, st.session_state.ten_nguoi_dung)
                if tai_khoan:
                    ma_nhan_vien = tai_khoan[1]  # Lấy MaNhanVien từ bảng TaiKhoan
                    nhan_vien = database.lay_nhan_vien_theo_id(conn, ma_nhan_vien)  # Lấy thông tin nhân viên
                    database.close_db(conn)

                    if nhan_vien:
                        profile_card.profile_card(nhan_vien) #Hiển thị profile card
                    else:
                        st.warning("Không tìm thấy thông tin nhân viên.")
                else:
                    st.warning("Không tìm thấy thông tin tài khoản.")
                database.close_db(conn)
            else:
                st.error("Không thể kết nối đến cơ sở dữ liệu.")
        
        elif selected_module == "Công việc":
            # Display task management component
            task_management.task_management(st.session_state.user_id, is_admin)
            
        elif selected_module == "Thành tích":
            # Display achievements component
            achievements.achievements(st.session_state.user_id, is_admin)
            
        elif selected_module == "Chấm công":
            # Display attendance component
            attendance.attendance(st.session_state.user_id, is_admin)

        elif selected_module == "Đào tạo & Đánh giá":
            # Display training and performance evaluation component
            training_performance.training_performance(st.session_state.user_id, is_admin)

        elif selected_module == "Quản lý hệ thống" and is_admin:
             # --- QUẢN LÝ HỆ THỐNG (CHỈ ADMIN) ---
            st.header("Quản lý hệ thống")
            st.write("Bạn có quyền truy cập đầy đủ vào hệ thống.")

            # --- FORM TẠO TÀI KHOẢN (CHỈ ADMIN MỚI THẤY) ---
            with st.expander("Tạo tài khoản mới (chỉ Admin)"):
              ten_dang_nhap_moi = st.text_input("Tên đăng nhập mới")
              mat_khau_moi = st.text_input("Mật khẩu mới", type="password")
              ma_nhan_vien_moi = st.number_input("Mã nhân viên", min_value=1, step=1)
              quyen_han_moi = st.selectbox("Quyền hạn", ["nhanvien", "truongphong", "admin"])

              if st.button("Tạo tài khoản", key="tao_tk"):
                conn = database.connect_db() # Kết nối DB
                if conn: # Kiểm tra kết nối thành công
                  if database.tao_tai_khoan(conn, ten_dang_nhap_moi, mat_khau_moi, ma_nhan_vien_moi, quyen_han_moi):
                    st.success("Tạo tài khoản thành công!")
                  else:
                    st.error("Tạo tài khoản thất bại. Vui lòng kiểm tra lại.")
                  database.close_db(conn) # Đóng kết nối
                else:
                  st.error("Không thể kết nối đến cơ sở dữ liệu.") # Thông báo lỗi nếu không kết nối được

        elif selected_module == "Quản lý Nhân viên" and is_admin:
            # --- QUẢN LÝ NHÂN VIÊN (CHỈ ADMIN) ---
            st.header("Quản lý Nhân viên")
            if st.button("Xem danh sách nhân viên", key="xem_dsnv"):
                conn = database.connect_db()
                if conn:
                    danh_sach_nhan_vien = database.lay_danh_sach_nhan_vien(conn)
                    database.close_db(conn)

                    if danh_sach_nhan_vien:
                        st.dataframe(danh_sach_nhan_vien)
                    else:
                        st.warning("Không có nhân viên nào trong hệ thống.")
                else:
                    st.error("Không thể kết nối đến cơ sở dữ liệu.")

        elif selected_module == "Báo cáo" and is_admin:
            # --- BÁO CÁO (CHỈ ADMIN) ---
            st.subheader("Báo cáo")
            # --- CHỌN LOẠI BÁO CÁO ---
            loai_bao_cao = st.selectbox(
                "Chọn loại báo cáo",
                ["Số lượng nhân viên theo phòng ban", "Số lượng nhân viên theo vị trí", "Danh sách nhân viên có thâm niên trên X năm"],
            )

            if loai_bao_cao == "Số lượng nhân viên theo phòng ban":
                # --- TẠO BÁO CÁO SỐ LƯỢNG NHÂN VIÊN THEO PHÒNG BAN ---
                if st.button("Tạo báo cáo", key="tao_bao_cao_pb"):
                    conn = database.connect_db()
                    if conn:
                        # Lấy dữ liệu từ database
                        try:
                            cursor = conn.cursor()
                            cursor.execute("""
                                SELECT PhongBan.TenPhongBan, COUNT(NhanVien.MaNhanVien)
                                FROM NhanVien
                                JOIN PhongBan ON NhanVien.PhongBanID = PhongBan.PhongBanID
                                GROUP BY PhongBan.TenPhongBan
                            """)
                            data = cursor.fetchall()

                            # Tạo DataFrame từ dữ liệu
                            df = pd.DataFrame(data, columns=["Phòng ban", "Số lượng nhân viên"])

                            # Hiển thị DataFrame bằng Streamlit
                            st.dataframe(df)

                            # (Tùy chọn) Tạo biểu đồ
                            st.bar_chart(data=df, x="Phòng ban", y="Số lượng nhân viên")

                        except sqlite3.Error as e:
                            st.error(f"Lỗi truy vấn cơ sở dữ liệu: {e}")
                        finally:
                            database.close_db(conn)
                    else:
                        st.error("Không thể kết nối đến cơ sở dữ liệu.")

            elif loai_bao_cao == "Số lượng nhân viên theo vị trí":
                # --- TẠO BÁO CÁO SỐ LƯỢNG NHÂN VIÊN THEO VỊ TRÍ ---
                if st.button("Tạo báo cáo", key="tao_bao_cao_vt"):
                    conn = database.connect_db()
                    if conn:
                        # Lấy dữ liệu từ database
                        try:
                            cursor = conn.cursor()
                            cursor.execute("""
                                SELECT ViTri.TenViTri, COUNT(NhanVien.MaNhanVien)
                                FROM NhanVien
                                JOIN ViTri ON NhanVien.ViTriID = ViTri.ViTriID
                                GROUP BY ViTri.TenViTri
                            """)
                            data = cursor.fetchall()

                            # Tạo DataFrame từ dữ liệu
                            df = pd.DataFrame(data, columns=["Vị trí", "Số lượng nhân viên"])

                            # Hiển thị DataFrame bằng Streamlit
                            st.dataframe(df)

                            # (Tùy chọn) Tạo biểu đồ
                            st.bar_chart(data=df, x="Vị trí", y="Số lượng nhân viên")

                        except sqlite3.Error as e:
                            st.error(f"Lỗi truy vấn cơ sở dữ liệu: {e}")
                        finally:
                            database.close_db(conn)
                    else:
                        st.error("Không thể kết nối đến cơ sở dữ liệu.")

            elif loai_bao_cao == "Danh sách nhân viên có thâm niên trên X năm":
                # --- TẠO BÁO CÁO DANH SÁCH NHÂN VIÊN CÓ THÂM NIÊN TRÊN X NĂM ---
                tham_nien = st.number_input("Nhập số năm thâm niên", min_value=0, value=5, step=1)
                if st.button("Tạo báo cáo", key="tao_bao_cao_tn"):
                    conn = database.connect_db()
                    if conn:
                        # Lấy dữ liệu từ database
                        try:
                            cursor = conn.cursor()
                            sql = """
                                SELECT MaNhanVien, HoTen, NgayVaoCongTy
                                FROM NhanVien
                                WHERE STRFTIME('%Y', 'now') - STRFTIME('%Y', NgayVaoCongTy) >= ?
                            """
                            cursor.execute(sql, (tham_nien,))  # Truyền tham số vào câu SQL
                            data = cursor.fetchall()

                            # Tạo DataFrame từ dữ liệu
                            df = pd.DataFrame(data, columns=["Mã NV", "Họ tên", "Ngày vào công ty"])

                            # Hiển thị DataFrame bằng Streamlit
                            st.dataframe(df)

                        except sqlite3.Error as e:
                            st.error(f"Lỗi truy vấn cơ sở dữ liệu: {e}")
                        finally:
                            database.close_db(conn)
                    else:
                        st.error("Không thể kết nối đến cơ sở dữ liệu.")

        elif st.session_state.quyen_han == "truongphong":
            st.subheader("Quản lý phòng ban")
            st.write("Bạn có quyền quản lý thông tin nhân viên trong phòng ban của mình.")

# --- KHỞI TẠO SESSION STATE ---
if "dang_nhap" not in st.session_state:
    st.session_state.dang_nhap = False
if "ten_nguoi_dung" not in st.session_state:
    st.session_state.ten_nguoi_dung = None
if "quyen_han" not in st.session_state:
    st.session_state.quyen_han = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
# ***THÊM DÒNG NÀY ĐỂ KHỞI TẠO nhan_vien_data***
if "nhan_vien_data" not in st.session_state:
    st.session_state.nhan_vien_data = None
# Initialize session states for components
if "selected_task" not in st.session_state:
    st.session_state.selected_task = None
    
# --- ĐIỀU HƯỚNG TRANG ---
if not st.session_state.dang_nhap:
    trang_dang_nhap()
else:
    trang_chu()

