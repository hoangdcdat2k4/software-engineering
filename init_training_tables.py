import sqlite3
from utils import database

def create_training_tables(conn):
    """Tạo các bảng cho module Đào tạo & Đánh giá Hiệu suất."""
    cursor = conn.cursor()
    
    # Bảng Kế hoạch Đào tạo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS KeHoachDaoTao (
        KeHoachID INTEGER PRIMARY KEY AUTOINCREMENT,
        TenKeHoach TEXT NOT NULL,
        MoTa TEXT,
        NgayBatDau DATE,
        NgayKetThuc DATE,
        TrangThai TEXT CHECK(TrangThai IN ('Chờ duyệt', 'Đã duyệt', 'Đang thực hiện', 'Hoàn thành', 'Hủy')),
        NguoiTaoID INTEGER,
        FOREIGN KEY (NguoiTaoID) REFERENCES NhanVien(MaNhanVien)
    )
    """)
    
    # Bảng Khóa học
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS KhoaHoc (
        KhoaHocID INTEGER PRIMARY KEY AUTOINCREMENT,
        TenKhoaHoc TEXT NOT NULL,
        MoTa TEXT,
        LoaiHoc TEXT CHECK(LoaiHoc IN ('Online', 'Offline')),
        ThoiLuong INTEGER,  -- Thời lượng tính bằng giờ
        GiaTien DECIMAL(10,2),
        KeHoachID INTEGER,
        FOREIGN KEY (KeHoachID) REFERENCES KeHoachDaoTao(KeHoachID)
    )
    """)
    
    # Bảng Đăng ký Khóa học
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DangKyKhoaHoc (
        DangKyID INTEGER PRIMARY KEY AUTOINCREMENT,
        KhoaHocID INTEGER,
        NhanVienID INTEGER,
        NgayDangKy DATE,
        TrangThai TEXT CHECK(TrangThai IN ('Chờ duyệt', 'Đã duyệt', 'Đang học', 'Hoàn thành', 'Hủy')),
        DiemSo DECIMAL(4,2),
        GhiChu TEXT,
        FOREIGN KEY (KhoaHocID) REFERENCES KhoaHoc(KhoaHocID),
        FOREIGN KEY (NhanVienID) REFERENCES NhanVien(MaNhanVien)
    )
    """)
    
    # Bảng Chỉ số KPI
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ChiSoKPI (
        KPIID INTEGER PRIMARY KEY AUTOINCREMENT,
        TenKPI TEXT NOT NULL,
        MoTa TEXT,
        DonVi TEXT,
        MucTieu DECIMAL(10,2),
        TrongSo DECIMAL(3,2),
        PhongBanID INTEGER,
        FOREIGN KEY (PhongBanID) REFERENCES PhongBan(PhongBanID)
    )
    """)
    
    # Bảng Đánh giá Hiệu suất
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DanhGiaHieuSuat (
        DanhGiaID INTEGER PRIMARY KEY AUTOINCREMENT,
        NhanVienID INTEGER,
        KyDanhGia TEXT,  -- Ví dụ: "Q1-2024"
        NgayDanhGia DATE,
        NguoiDanhGiaID INTEGER,
        TongDiem DECIMAL(4,2),
        XepLoai TEXT CHECK(XepLoai IN ('Xuất sắc', 'Tốt', 'Đạt', 'Cần cải thiện', 'Không đạt')),
        NhanXet TEXT,
        FOREIGN KEY (NhanVienID) REFERENCES NhanVien(MaNhanVien),
        FOREIGN KEY (NguoiDanhGiaID) REFERENCES NhanVien(MaNhanVien)
    )
    """)
    
    # Bảng Chi tiết Đánh giá KPI
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ChiTietDanhGiaKPI (
        ChiTietID INTEGER PRIMARY KEY AUTOINCREMENT,
        DanhGiaID INTEGER,
        KPIID INTEGER,
        KetQua DECIMAL(10,2),
        DiemSo DECIMAL(4,2),
        NhanXet TEXT,
        FOREIGN KEY (DanhGiaID) REFERENCES DanhGiaHieuSuat(DanhGiaID),
        FOREIGN KEY (KPIID) REFERENCES ChiSoKPI(KPIID)
    )
    """)
    
    # Bảng Phản hồi
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PhanHoi (
        PhanHoiID INTEGER PRIMARY KEY AUTOINCREMENT,
        NhanVienID INTEGER,
        LoaiPhanHoi TEXT CHECK(LoaiPhanHoi IN ('Đào tạo', 'Hiệu suất', 'Môi trường làm việc', 'Khác')),
        NoiDung TEXT,
        NgayGui DATE,
        TrangThai TEXT CHECK(TrangThai IN ('Chờ xử lý', 'Đã xử lý', 'Đang xử lý')),
        NguoiXuLyID INTEGER,
        FOREIGN KEY (NhanVienID) REFERENCES NhanVien(MaNhanVien),
        FOREIGN KEY (NguoiXuLyID) REFERENCES NhanVien(MaNhanVien)
    )
    """)
    
    # Bảng Lộ trình Phát triển
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS LoTrinhPhatTrien (
        LoTrinhID INTEGER PRIMARY KEY AUTOINCREMENT,
        NhanVienID INTEGER,
        ViTriMucTieu TEXT,
        ThoiGianDuKien DATE,
        TrangThai TEXT CHECK(TrangThai IN ('Đang thực hiện', 'Hoàn thành', 'Tạm dừng')),
        MoTa TEXT,
        FOREIGN KEY (NhanVienID) REFERENCES NhanVien(MaNhanVien)
    )
    """)
    
    conn.commit()

if __name__ == "__main__":
    conn = database.connect_db()
    if conn:
        create_training_tables(conn)
        print("Đã tạo các bảng cho module Đào tạo & Đánh giá Hiệu suất.")
        database.close_db(conn)
    else:
        print("Không thể kết nối đến cơ sở dữ liệu.") 