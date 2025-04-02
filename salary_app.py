import streamlit as st
import pandas as pd
from fpdf import FPDF
import pymongo

# Định nghĩa Employee
class Employee:
    MIN_SALARY = [4680000, 4160000, 3640000, 3250000]  # Lương tối thiểu theo vùng

    def __init__(self, id, name, region, base_salary, bonus, dependents, allowance, membership_card):
        self.id = id
        self.name = name
        self.region = region
        self.base_salary = max(base_salary, self.MIN_SALARY[region - 1])
        self.bonus = bonus
        self.dependents = dependents
        self.allowance = allowance
        self.membership_card = membership_card
        self.insurance = self.calculate_insurance()
        self.tax = self.calculate_tax()
        self.net_salary = self.calculate_net_salary()

    def calculate_insurance(self):
        return self.base_salary * 0.105

    def calculate_tax(self):
        taxable_income = self.base_salary + self.bonus - 11000000 - (self.dependents * 4400000)
        if taxable_income <= 0:
            return 0
        
        tax_brackets = [
            (5000000, 0.05, 0), (10000000, 0.1, 250000), (18000000, 0.15, 750000),
            (32000000, 0.2, 1650000), (52000000, 0.25, 3250000), (80000000, 0.3, 5850000)
        ]
        
        for limit, rate, deduction in tax_brackets:
            if taxable_income <= limit:
                return taxable_income * rate - deduction
        return taxable_income * 0.35 - 9850000

    def calculate_net_salary(self):
        return self.base_salary + self.bonus - self.tax - self.insurance + self.allowance

# Thông tin kết nối MongoDB Atlas
MONGO_URI = "mongodb+srv://Manhdoxxx:Manhdoxxxx1234@cluster0.8xcl2.mongodb.net/salary_management?retryWrites=true&w=majority&appName=Cluster0"

# Kết nối đến MongoDB Atlas
client = pymongo.MongoClient(MONGO_URI)
db = client["salary_management"]
collection = db["employees"]

def save_data(employees):
    data = []
    for emp in employees:
        emp_data = {
            "id": emp.id,
            "name": emp.name,
            "region": emp.region,
            "base_salary": emp.base_salary,
            "bonus": emp.bonus,
            "dependents": emp.dependents,
            "allowance": emp.allowance,
            "membership_card": emp.membership_card
        }
        data.append(emp_data)
    collection.delete_many({})  # Xóa dữ liệu cũ
    collection.insert_many(data)  # Lưu dữ liệu mới

def load_data():
    data = list(collection.find())
    employees = []
    
    for emp in data:
        emp.pop('_id', None)  # Xóa khóa '_id' do MongoDB tự động thêm
        emp.pop('insurance', None)  # Loại bỏ trường dư thừa
        emp.pop('tax', None)  # Loại bỏ trường dư thừa
        emp.pop('net_salary', None)  # Loại bỏ trường dư thừa

        employees.append(Employee(
            id=emp["id"],
            name=emp["name"],
            region=emp["region"],
            base_salary=emp["base_salary"],
            bonus=emp["bonus"],
            dependents=emp["dependents"],
            allowance=emp["allowance"],
            membership_card=emp["membership_card"]
        ))

    return employees

def generate_salary_report(employee):
    pdf = FPDF()
    pdf.add_page()
    
    # Thêm font Unicode (ví dụ: DejaVuSans)
    pdf.add_font('DejaVuSans', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVuSans', size=12)

    # Thêm nội dung tiếng Việt
    pdf.cell(200, 10, txt="Báo cáo lương nhân viên", ln=True, align="C")
    pdf.cell(200, 10, txt=f"ID: {employee.id}", ln=True)
    pdf.cell(200, 10, txt=f"Tên nhân viên: {employee.name}", ln=True)
    pdf.cell(200, 10, txt=f"Vùng: {employee.region}", ln=True)
    pdf.cell(200, 10, txt=f"Lương cơ bản: {employee.base_salary}", ln=True)
    pdf.cell(200, 10, txt=f"Thưởng: {employee.bonus}", ln=True)
    pdf.cell(200, 10, txt=f"Số người phụ thuộc: {employee.dependents}", ln=True)
    pdf.cell(200, 10, txt=f"Trợ cấp: {employee.allowance}", ln=True)
    pdf.cell(200, 10, txt=f"Thẻ thành viên: {employee.membership_card}", ln=True)
    pdf.cell(200, 10, txt=f"Bảo hiểm: {employee.insurance}", ln=True)
    pdf.cell(200, 10, txt=f"Thuế: {employee.tax}", ln=True)
    pdf.cell(200, 10, txt=f"Lương thực nhận: {employee.net_salary}", ln=True)

    # Xuất PDF dưới dạng bytes
    pdf_bytes = pdf.output(dest="S").encode('latin1', errors='replace')
    return pdf_bytes

# Giao diện Streamlit
st.title("Hệ thống tính lương và phúc lợi")

employees = load_data()

# Form thêm nhân viên
st.sidebar.header("Thêm nhân viên")
with st.sidebar.form("add_employee_form"):
    id = st.number_input("ID", min_value=1, step=1)
    name = st.text_input("Tên nhân viên")
    region = st.selectbox("Vùng", [1, 2, 3, 4])
    base_salary = st.number_input("Lương cơ bản", min_value=0.0)
    bonus = st.number_input("Thưởng", min_value=0.0)
    dependents = st.number_input("Số người phụ thuộc", min_value=0, step=1)
    allowance = st.number_input("Trợ cấp", min_value=0.0)
    membership_card = st.text_input("Loại thẻ thành viên")

    if st.form_submit_button("Thêm nhân viên"):
        if any(emp.id == id for emp in employees):
            st.error("ID đã tồn tại! Vui lòng nhập ID khác.")
        else:
            emp = Employee(id, name, region, base_salary, bonus, dependents, allowance, membership_card)
            employees.append(emp)
            save_data(employees)
            st.success("Đã thêm nhân viên!")
            st.rerun()

# Hiển thị danh sách nhân viên
st.header("Danh sách nhân viên")
if employees:
    df = pd.DataFrame([vars(emp) for emp in employees])
    st.dataframe(df)

# Xóa nhân viên theo tên
delete_name = st.text_input("Nhập tên nhân viên cần xóa")
if st.button("Xóa nhân viên"):
    employees = [emp for emp in employees if emp.name != delete_name]
    save_data(employees)
    st.success(f"Đã xóa nhân viên có tên {delete_name}!")
    st.rerun()

# Xuất báo cáo theo ID nhân viên
specific_id = st.number_input("Nhập ID nhân viên để tạo báo cáo", min_value=1, step=1)
if st.button("Tạo báo cáo lương"):
    employee = next((emp for emp in employees if emp.id == specific_id), None)
    if employee:
        pdf_bytes = generate_salary_report(employee)
        st.download_button(
            label="Tải báo cáo lương",
            data=pdf_bytes,
            file_name=f"bao_cao_luong_{employee.id}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Không tìm thấy nhân viên với ID đã nhập.")