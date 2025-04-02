# init_db.py
import sqlite3
from utils import database

DATABASE_PATH = "data/quanlynhansu.db"

def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

conn = connect_db()

if conn:
    database.create_tables(conn)  # Gọi hàm tạo bảng từ database.py
    conn.close()
    print("Đã tạo database và các bảng (nếu chưa tồn tại).")
else:
    print("Không thể kết nối đến database.")