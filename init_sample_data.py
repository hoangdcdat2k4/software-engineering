import sqlite3
from utils import database
import hashlib
from datetime import datetime, timedelta
import random

def create_sample_data():
    """
    Tạo dữ liệu mẫu cho các bảng mới: CongViec, ThanhTich, ChamCong
    """
    conn = database.connect_db()
    
    if not conn:
        print("Không thể kết nối đến cơ sở dữ liệu.")
        return
    
    try:
        cursor = conn.cursor()
        
        # 1. Thêm phòng ban nếu chưa có
        phong_ban_list = [
            ("Kỹ thuật", "Phòng phát triển sản phẩm và hỗ trợ kỹ thuật"),
            ("Marketing", "Phòng tiếp thị và quảng cáo"),
            ("Nhân sự", "Phòng quản lý nhân sự và tuyển dụng"),
            ("Tài chính", "Phòng quản lý tài chính và kế toán"),
            ("Kinh doanh", "Phòng kinh doanh và phát triển thị trường")
        ]
        
        for pb in phong_ban_list:
            cursor.execute("SELECT COUNT(*) FROM PhongBan WHERE TenPhongBan = ?", (pb[0],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO PhongBan (TenPhongBan, MoTa) VALUES (?, ?)", pb)
        
        # 2. Thêm vị trí công việc nếu chưa có
        vi_tri_list = [
            ("Giám đốc", "Quản lý cấp cao"),
            ("Trưởng phòng", "Quản lý cấp trung"),
            ("Nhân viên", "Nhân viên thông thường"),
            ("Kỹ sư", "Kỹ sư phát triển sản phẩm"),
            ("Thiết kế", "Nhân viên thiết kế"),
            ("Kế toán", "Nhân viên kế toán"),
            ("Nhân viên kinh doanh", "Nhân viên kinh doanh và bán hàng")
        ]
        
        for vt in vi_tri_list:
            cursor.execute("SELECT COUNT(*) FROM ViTri WHERE TenViTri = ?", (vt[0],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO ViTri (TenViTri, MoTa) VALUES (?, ?)", vt)
        
        # 3. Thêm nhân viên mẫu nếu chưa đủ
        cursor.execute("SELECT COUNT(*) FROM NhanVien")
        if cursor.fetchone()[0] < 5:
            # Lấy ID phòng ban và vị trí
            cursor.execute("SELECT PhongBanID FROM PhongBan")
            phong_ban_ids = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT ViTriID FROM ViTri")
            vi_tri_ids = [row[0] for row in cursor.fetchall()]
            
            # Tạo 10 nhân viên mẫu
            nhan_vien_list = [
                ("Nguyễn Văn A", "1985-05-15", "Nam", "Hà Nội", "0987654321", "nguyenvana@example.com", 
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2018-02-10", 15000000, "", "123456789"),
                ("Trần Thị B", "1990-08-20", "Nữ", "Hồ Chí Minh", "0912345678", "tranthib@example.com",
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2019-05-22", 12000000, "", "987654321"),
                ("Lê Văn C", "1988-12-03", "Nam", "Đà Nẵng", "0923456789", "levanc@example.com",
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2020-01-15", 13500000, "", "456789123"),
                ("Phạm Thị D", "1992-04-25", "Nữ", "Hải Phòng", "0934567891", "phamthid@example.com",
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2020-09-10", 11000000, "", "789123456"),
                ("Hoàng Văn E", "1987-11-08", "Nam", "Quảng Ninh", "0945678912", "hoangvane@example.com",
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2017-06-18", 14000000, "", "321654987"),
                ("Ngô Thị F", "1993-02-17", "Nữ", "Cần Thơ", "0956789123", "ngothif@example.com",
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2021-03-01", 10500000, "", "654987321"),
                ("Đặng Văn G", "1986-07-30", "Nam", "Huế", "0967891234", "dangvang@example.com",
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2019-11-05", 13000000, "", "987321654"),
                ("Vũ Thị H", "1991-09-12", "Nữ", "Đồng Nai", "0978912345", "vuthih@example.com",
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2018-08-15", 12500000, "", "321987654"),
                ("Bùi Văn I", "1989-01-05", "Nam", "Bình Dương", "0989123456", "buivani@example.com",
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2017-10-20", 14500000, "", "654321987"),
                ("Lý Thị K", "1994-06-28", "Nữ", "Long An", "0991234567", "lythik@example.com",
                 random.choice(phong_ban_ids), random.choice(vi_tri_ids), "2022-01-10", 10000000, "", "987654123")
            ]
            
            for nv in nhan_vien_list:
                # Kiểm tra email đã tồn tại chưa
                cursor.execute("SELECT COUNT(*) FROM NhanVien WHERE Email = ?", (nv[5],))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO NhanVien (HoTen, NgaySinh, GioiTinh, DiaChi, SoDienThoai, Email, 
                                            PhongBanID, ViTriID, NgayVaoCongTy, MucLuong, AnhDaiDien, SoCMND)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, nv)
        
        # 4. Thêm tài khoản cho nhân viên nếu chưa có
        cursor.execute("SELECT MaNhanVien, Email FROM NhanVien WHERE MaNhanVien NOT IN (SELECT MaNhanVien FROM TaiKhoan WHERE MaNhanVien IS NOT NULL)")
        nhan_vien_no_account = cursor.fetchall()
        
        for nv in nhan_vien_no_account:
            # Tạo tài khoản với tên đăng nhập là phần trước @ của email và mật khẩu là "password123"
            username = nv[1].split("@")[0]
            password = hashlib.sha256("password123".encode()).hexdigest()
            quyen_han = "nhanvien"  # Mặc định là quyền nhân viên
            
            cursor.execute("""
                INSERT INTO TaiKhoan (MaNhanVien, TenDangNhap, MatKhau, QuyenHan)
                VALUES (?, ?, ?, ?)
            """, (nv[0], username, password, quyen_han))
            
            print(f"Đã tạo tài khoản cho nhân viên {nv[0]} với tên đăng nhập: {username}")
        
        # 5. Thêm dữ liệu mẫu cho bảng CongViec
        cursor.execute("SELECT COUNT(*) FROM CongViec")
        if cursor.fetchone()[0] < 5:
            # Lấy danh sách mã nhân viên
            cursor.execute("SELECT MaNhanVien FROM NhanVien")
            ma_nhan_vien_list = [row[0] for row in cursor.fetchall()]
            
            # Tạo 20 công việc mẫu
            today = datetime.now()
            
            cong_viec_list = [
                ("Phân tích yêu cầu khách hàng", "Phân tích các yêu cầu từ khách hàng A và lập tài liệu đặc tả", 
                 (today - timedelta(days=10)).strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Cao", random.choice(ma_nhan_vien_list), 1),
                
                ("Thiết kế giao diện người dùng", "Thiết kế UI/UX cho ứng dụng di động", 
                 (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Bình thường", random.choice(ma_nhan_vien_list), 1),
                
                ("Phát triển backend API", "Xây dựng các API cho hệ thống quản lý nhân sự", 
                 (today - timedelta(days=15)).strftime("%Y-%m-%d"), (today - timedelta(days=2)).strftime("%Y-%m-%d"), 
                 "Đã hoàn thành", "Cao", random.choice(ma_nhan_vien_list), 1),
                
                ("Kiểm thử sản phẩm", "Thực hiện kiểm thử phần mềm theo kế hoạch", 
                 (today - timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=10)).strftime("%Y-%m-%d"), 
                 "Chưa hoàn thành", "Bình thường", random.choice(ma_nhan_vien_list), 1),
                
                ("Họp với khách hàng", "Trình bày tiến độ dự án với khách hàng", 
                 (today + timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=2)).strftime("%Y-%m-%d"), 
                 "Chưa hoàn thành", "Cao", random.choice(ma_nhan_vien_list), 1),
                
                ("Báo cáo kết quả kinh doanh", "Tổng hợp báo cáo kết quả kinh doanh quý II", 
                 (today - timedelta(days=20)).strftime("%Y-%m-%d"), (today - timedelta(days=10)).strftime("%Y-%m-%d"), 
                 "Đã hoàn thành", "Cao", random.choice(ma_nhan_vien_list), 1),
                
                ("Lập kế hoạch marketing", "Xây dựng kế hoạch marketing cho sản phẩm mới", 
                 (today - timedelta(days=8)).strftime("%Y-%m-%d"), (today + timedelta(days=12)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Bình thường", random.choice(ma_nhan_vien_list), 1),
                
                ("Đào tạo nhân viên mới", "Tổ chức đào tạo cho nhân viên mới về quy trình làm việc", 
                 (today + timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"), 
                 "Chưa hoàn thành", "Thấp", random.choice(ma_nhan_vien_list), 1),
                
                ("Cập nhật hệ thống", "Nâng cấp phiên bản phần mềm quản lý", 
                 (today - timedelta(days=3)).strftime("%Y-%m-%d"), (today + timedelta(days=1)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Cao", random.choice(ma_nhan_vien_list), 1),
                
                ("Phân tích dữ liệu khách hàng", "Phân tích hành vi khách hàng từ dữ liệu bán hàng", 
                 (today - timedelta(days=12)).strftime("%Y-%m-%d"), (today - timedelta(days=5)).strftime("%Y-%m-%d"), 
                 "Đã hoàn thành", "Bình thường", random.choice(ma_nhan_vien_list), 1),
                
                ("Tuyển dụng nhân sự", "Tổ chức phỏng vấn cho vị trí kỹ sư phát triển", 
                 (today - timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=15)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Bình thường", random.choice(ma_nhan_vien_list), 1),
                
                ("Nghiên cứu công nghệ mới", "Tìm hiểu và đánh giá công nghệ blockchain", 
                 (today - timedelta(days=30)).strftime("%Y-%m-%d"), (today + timedelta(days=30)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Thấp", random.choice(ma_nhan_vien_list), 1),
                
                ("Thiết kế logo", "Thiết kế logo cho dự án mới", 
                 (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today - timedelta(days=1)).strftime("%Y-%m-%d"), 
                 "Đã hoàn thành", "Bình thường", random.choice(ma_nhan_vien_list), 1),
                
                ("Chuẩn bị tài liệu đấu thầu", "Chuẩn bị hồ sơ tham gia gói thầu XYZ", 
                 (today - timedelta(days=10)).strftime("%Y-%m-%d"), (today + timedelta(days=3)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Cao", random.choice(ma_nhan_vien_list), 1),
                
                ("Tối ưu hóa website", "Tối ưu tốc độ và SEO cho website công ty", 
                 (today - timedelta(days=15)).strftime("%Y-%m-%d"), (today - timedelta(days=5)).strftime("%Y-%m-%d"), 
                 "Đã hoàn thành", "Bình thường", random.choice(ma_nhan_vien_list), 1),
                
                ("Lập báo cáo tài chính", "Tổng hợp báo cáo tài chính tháng 8", 
                 (today - timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=2)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Cao", random.choice(ma_nhan_vien_list), 1),
                
                ("Quản lý kho hàng", "Kiểm kê và cập nhật thông tin kho hàng", 
                 (today - timedelta(days=3)).strftime("%Y-%m-%d"), (today + timedelta(days=1)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Bình thường", random.choice(ma_nhan_vien_list), 1),
                
                ("Xây dựng quy trình làm việc", "Thiết lập quy trình làm việc cho nhóm phát triển", 
                 (today - timedelta(days=20)).strftime("%Y-%m-%d"), (today - timedelta(days=10)).strftime("%Y-%m-%d"), 
                 "Đã hoàn thành", "Cao", random.choice(ma_nhan_vien_list), 1),
                
                ("Khảo sát thị trường", "Thực hiện khảo sát thị trường về nhu cầu sản phẩm", 
                 (today - timedelta(days=8)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"), 
                 "Đang thực hiện", "Bình thường", random.choice(ma_nhan_vien_list), 1),
                
                ("Triển khai chiến dịch quảng cáo", "Thiết lập và triển khai chiến dịch quảng cáo Google Ads", 
                 (today + timedelta(days=1)).strftime("%Y-%m-%d"), (today + timedelta(days=15)).strftime("%Y-%m-%d"), 
                 "Chưa hoàn thành", "Bình thường", random.choice(ma_nhan_vien_list), 1)
            ]
            
            for cv in cong_viec_list:
                cursor.execute("""
                    INSERT INTO CongViec (TieuDe, MoTa, NgayBatDau, NgayKetThuc, TrangThai, MucDoUuTien, MaNhanVien, NguoiGiao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, cv)
            
            print(f"Đã thêm {len(cong_viec_list)} công việc mẫu.")
        
        # 6. Thêm dữ liệu mẫu cho bảng ThanhTich
        cursor.execute("SELECT COUNT(*) FROM ThanhTich")
        if cursor.fetchone()[0] < 5:
            # Tạo thành tích mẫu
            thanh_tich_list = [
                ("Nhân viên xuất sắc quý II/2023", "Hoàn thành xuất sắc các nhiệm vụ được giao", 
                 (today - timedelta(days=30)).strftime("%Y-%m-%d"), "Xuất sắc", random.choice(ma_nhan_vien_list)),
                
                ("Sáng kiến cải tiến quy trình", "Đề xuất cải tiến quy trình làm việc giúp tăng hiệu suất 20%", 
                 (today - timedelta(days=60)).strftime("%Y-%m-%d"), "Sáng tạo", random.choice(ma_nhan_vien_list)),
                
                ("Nhân viên chăm chỉ nhất tháng", "Có số giờ làm việc cao nhất trong tháng", 
                 (today - timedelta(days=15)).strftime("%Y-%m-%d"), "Chăm chỉ", random.choice(ma_nhan_vien_list)),
                
                ("Hoàn thành dự án trước thời hạn", "Hoàn thành dự án ABC trước thời hạn 1 tuần", 
                 (today - timedelta(days=45)).strftime("%Y-%m-%d"), "Hiệu quả", random.choice(ma_nhan_vien_list)),
                
                ("Tinh thần đồng đội", "Hỗ trợ đồng nghiệp tích cực, góp phần hoàn thành dự án", 
                 (today - timedelta(days=20)).strftime("%Y-%m-%d"), "Teamwork", random.choice(ma_nhan_vien_list)),
                
                ("Ý tưởng sáng tạo", "Đề xuất ý tưởng sáng tạo cho sản phẩm mới", 
                 (today - timedelta(days=75)).strftime("%Y-%m-%d"), "Sáng tạo", random.choice(ma_nhan_vien_list)),
                
                ("Nhân viên tiêu biểu", "Được khách hàng đánh giá cao về thái độ phục vụ", 
                 (today - timedelta(days=90)).strftime("%Y-%m-%d"), "Tiêu biểu", random.choice(ma_nhan_vien_list)),
                
                ("Kỹ năng chuyên môn xuất sắc", "Thể hiện kỹ năng chuyên môn cao trong dự án XYZ", 
                 (today - timedelta(days=50)).strftime("%Y-%m-%d"), "Kỹ năng", random.choice(ma_nhan_vien_list))
            ]
            
            for tt in thanh_tich_list:
                cursor.execute("""
                    INSERT INTO ThanhTich (TieuDe, MoTa, NgayDat, LoaiThanhTich, MaNhanVien)
                    VALUES (?, ?, ?, ?, ?)
                """, tt)
            
            print(f"Đã thêm {len(thanh_tich_list)} thành tích mẫu.")
        
        # 7. Thêm dữ liệu mẫu cho bảng ChamCong
        cursor.execute("SELECT COUNT(*) FROM ChamCong")
        if cursor.fetchone()[0] < 10:
            # Lấy danh sách nhân viên
            cursor.execute("SELECT MaNhanVien FROM NhanVien")
            nhan_vien_ids = [row[0] for row in cursor.fetchall()]
            
            # Tạo dữ liệu chấm công cho 30 ngày gần nhất
            for nv_id in nhan_vien_ids:
                for i in range(30):
                    work_date = (today - timedelta(days=i)).date()
                    
                    # Bỏ qua ngày cuối tuần (thứ 7, chủ nhật)
                    if work_date.weekday() >= 5:
                        continue
                    
                    # Một số nhân viên sẽ vắng mặt ngẫu nhiên
                    if random.random() < 0.1:  # 10% cơ hội nghỉ
                        trang_thai = random.choice(["Nghỉ phép", "Nghỉ không phép"])
                        gio_vao = None
                        gio_ra = None
                    else:
                        trang_thai = "Đi làm"
                        gio_vao_hour = random.randint(7, 9)
                        gio_vao_min = random.randint(0, 59)
                        gio_vao = f"{gio_vao_hour:02d}:{gio_vao_min:02d}:00"
                        
                        gio_ra_hour = random.randint(17, 19)
                        gio_ra_min = random.randint(0, 59)
                        gio_ra = f"{gio_ra_hour:02d}:{gio_ra_min:02d}:00"
                    
                    # Kiểm tra xem đã có bản ghi này chưa
                    cursor.execute(
                        "SELECT COUNT(*) FROM ChamCong WHERE MaNhanVien = ? AND NgayLamViec = ?", 
                        (nv_id, work_date.strftime("%Y-%m-%d"))
                    )
                    
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO ChamCong (MaNhanVien, NgayLamViec, GioVao, GioRa, TrangThai, GhiChu)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (nv_id, work_date.strftime("%Y-%m-%d"), gio_vao, gio_ra, trang_thai, ""))
            
            print("Đã thêm dữ liệu chấm công mẫu.")
        
        # Lưu thay đổi
        conn.commit()
        print("Đã tạo dữ liệu mẫu thành công.")
    
    except sqlite3.Error as e:
        print(f"Lỗi: {e}")
        conn.rollback()
    
    finally:
        database.close_db(conn)

if __name__ == "__main__":
    create_sample_data() 