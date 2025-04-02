import sqlite3
from utils import database
import hashlib  # Import hashlib

DATABASE_PATH = "data/quanlynhansu.db"

def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def hash_password(password):
    """Mã hóa mật khẩu sử dụng SHA-256."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

conn = connect_db()

if conn:
    database.create_tables(conn)

    # Kiểm tra xem tài khoản admin đã tồn tại chưa
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TaiKhoan WHERE TenDangNhap = 'admin'")  # Thay 'admin' bằng tên đăng nhập mong muốn
    admin_account = cursor.fetchone()

    if not admin_account:
        # Tạo tài khoản admin nếu chưa tồn tại
        admin_username = "admin"  # Thay đổi nếu cần
        admin_password = "password"  # **KHÔNG** dùng mật khẩu này trong thực tế
        admin_hashed_password = hash_password(admin_password) # Mã hóa mật khẩu
        cursor.execute(
            "INSERT INTO TaiKhoan (TenDangNhap, MatKhau, QuyenHan) VALUES (?, ?, ?)",
            (admin_username, admin_hashed_password, "admin"),
        )
        conn.commit()
        print("Đã tạo tài khoản admin.")
    else:
        print("Tài khoản admin đã tồn tại.")

    conn.close()
else:
    print("Không thể kết nối đến database.")