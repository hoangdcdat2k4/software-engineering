import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import numpy as np
import time

# Thiết lập trang
st.set_page_config(page_title="Hệ thống Quản lý Chấm công", layout="wide")

# Tiêu đề ứng dụng
st.title("HỆ THỐNG QUẢN LÝ THỜI GIAN & CHẤM CÔNG")
st.markdown("---")

# Dữ liệu mẫu (trong thực tế nên kết nối database)
if 'employees' not in st.session_state:
    st.session_state.employees = pd.DataFrame({
        'Mã NV': ['NV001', 'NV002', 'NV003'],
        'Họ tên': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C'],
        'Phòng ban': ['Kế toán', 'Nhân sự', 'IT'],
        'Vị trí': ['Nhân viên', 'Trưởng phòng', 'Nhân viên'],
        'Ngày vào làm': ['2022-01-15', '2021-05-20', '2023-02-10'],
        'Số ngày phép còn lại': [12, 8, 15]
    })

if 'timekeeping' not in st.session_state:
    st.session_state.timekeeping = pd.DataFrame({
        'Mã NV': ['NV001', 'NV002', 'NV001', 'NV003'],
        'Ngày': ['2023-11-01', '2023-11-01', '2023-11-02', '2023-11-02'],
        'Giờ vào': ['08:00', '08:15', '08:05', '07:55'],
        'Giờ ra': ['17:00', '17:30', '17:45', '17:10'],
        'Trạng thái': ['Đúng giờ', 'Muộn 15 phút', 'Tăng ca 45 phút', 'Đúng giờ'],
        'Địa điểm': ['VP Hà Nội', 'VP Hà Nội', 'VP Hà Nội', 'VP HCM']
    })

if 'leave_requests' not in st.session_state:
    st.session_state.leave_requests = pd.DataFrame({
        'Mã NV': ['NV002'],
        'Họ tên': ['Trần Thị B'],
        'Loại phép': ['Nghỉ phép năm'],
        'Ngày bắt đầu': ['2023-11-15'],
        'Ngày kết thúc': ['2023-11-17'],
        'Số ngày': [3],
        'Lý do': ['Nghỉ du lịch'],
        'Trạng thái': ['Chờ duyệt']
    })

# Sidebar menu
menu = st.sidebar.selectbox("Menu chính", ["Trang chủ", "Chấm công", "Quản lý ca làm việc", "Quản lý nghỉ phép", "Báo cáo"])

if menu == "Trang chủ":
    st.header("Tổng quan hệ thống")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tổng số nhân viên", len(st.session_state.employees))
    with col2:
        late_today = len(st.session_state.timekeeping[st.session_state.timekeeping['Trạng thái'].str.contains('Muộn')])
        st.metric("Đi muộn hôm nay", late_today)
    with col3:
        pending_leave = len(st.session_state.leave_requests[st.session_state.leave_requests['Trạng thái'] == 'Chờ duyệt'])
        st.metric("Đơn nghỉ chờ duyệt", pending_leave)
    
    st.subheader("Nhân viên đi muộn hôm nay")
    late_employees = st.session_state.timekeeping[st.session_state.timekeeping['Trạng thái'].str.contains('Muộn')]
    st.dataframe(late_employees)

elif menu == "Chấm công":
    st.header("Quản lý Chấm công")
    
    tab1, tab2, tab3 = st.tabs(["Chấm công tự động", "Lịch sử chấm công", "Nhập liệu thủ công"])
    
    with tab1:
        st.subheader("Chấm công tự động")
        
        # Giả lập chấm công qua GPS
        st.write("**Chấm công qua định vị GPS**")
        current_location = st.selectbox("Địa điểm hiện tại", ["VP Hà Nội", "VP HCM", "Chi nhánh Đà Nẵng"])
        
        if st.button("Chấm công vào"):
            new_record = pd.DataFrame({
                'Mã NV': ['NV001'],
                'Ngày': [date.today().strftime("%Y-%m-%d")],
                'Giờ vào': [datetime.datetime.now().strftime("%H:%M")],
                'Giờ ra': [""],
                'Trạng thái': ["Đang làm việc"],
                'Địa điểm': [current_location]
            })
            st.session_state.timekeeping = pd.concat([st.session_state.timekeeping, new_record], ignore_index=True)
            st.success("Chấm công vào thành công!")
        
        if st.button("Chấm công ra"):
            # Tìm bản ghi chấm công vào chưa có giờ ra
            mask = (st.session_state.timekeeping['Mã NV'] == 'NV001') & (st.session_state.timekeeping['Giờ ra'] == "")
            if len(st.session_state.timekeeping[mask]) > 0:
                st.session_state.timekeeping.loc[mask, 'Giờ ra'] = datetime.datetime.now().strftime("%H:%M")
                
                # Tính toán trạng thái
                time_in = datetime.datetime.strptime(st.session_state.timekeeping.loc[mask, 'Giờ vào'].values[0], "%H:%M")
                time_out = datetime.datetime.now()
                work_hours = (time_out - time_in).seconds / 3600
                
                if work_hours >= 8:
                    st.session_state.timekeeping.loc[mask, 'Trạng thái'] = "Hoàn thành ca"
                else:
                    st.session_state.timekeeping.loc[mask, 'Trạng thái'] = "Về sớm"
                
                st.success("Chấm công ra thành công!")
            else:
                st.warning("Không tìm thấy bản ghi chấm công vào")
    
    with tab2:
        st.subheader("Lịch sử chấm công")
        selected_employee = st.selectbox("Chọn nhân viên", st.session_state.employees['Họ tên'])
        
        emp_id = st.session_state.employees[st.session_state.employees['Họ tên'] == selected_employee]['Mã NV'].values[0]
        emp_records = st.session_state.timekeeping[st.session_state.timekeeping['Mã NV'] == emp_id]
        
        st.dataframe(emp_records)
        
        # Thống kê
        late_days = len(emp_records[emp_records['Trạng thái'].str.contains('Muộn')])
        early_days = len(emp_records[emp_records['Trạng thái'].str.contains('Về sớm')])
        
        st.write(f"**Thống kê:** Số ngày đi muộn: {late_days} | Số ngày về sớm: {early_days}")
    
    with tab3:
        st.subheader("Nhập liệu thủ công")
        with st.form("manual_timekeeping"):
            emp = st.selectbox("Nhân viên", st.session_state.employees['Họ tên'])
            work_date = st.date_input("Ngày làm việc", date.today())
            time_in = st.time_input("Giờ vào", datetime.time(8, 0))
            time_out = st.time_input("Giờ ra", datetime.time(17, 0))
            location = st.selectbox("Địa điểm", ["VP Hà Nội", "VP HCM", "Chi nhánh Đà Nẵng"])
            notes = st.text_input("Ghi chú")
            
            submitted = st.form_submit_button("Lưu thông tin")
            if submitted:
                emp_id = st.session_state.employees[st.session_state.employees['Họ tên'] == emp]['Mã NV'].values[0]
                
                new_record = pd.DataFrame({
                    'Mã NV': [emp_id],
                    'Ngày': [work_date.strftime("%Y-%m-%d")],
                    'Giờ vào': [time_in.strftime("%H:%M")],
                    'Giờ ra': [time_out.strftime("%H:%M")],
                    'Trạng thái': ["Nhập tay"],
                    'Địa điểm': [location]
                })
                
                st.session_state.timekeeping = pd.concat([st.session_state.timekeeping, new_record], ignore_index=True)
                st.success("Đã lưu thông tin chấm công!")

elif menu == "Quản lý ca làm việc":
    st.header("Quản lý Ca làm việc")
    
    # Dữ liệu mẫu về ca làm việc
    shifts = pd.DataFrame({
        'Ca': ['Sáng', 'Chiều', 'Tối'],
        'Giờ bắt đầu': ['08:00', '13:00', '18:00'],
        'Giờ kết thúc': ['12:00', '17:00', '22:00'],
        'Phụ cấp': ['0%', '10%', '20%']
    })
    
    st.dataframe(shifts)
    
    st.subheader("Đăng ký đổi ca")
    with st.form("shift_change"):
        emp = st.selectbox("Nhân viên", st.session_state.employees['Họ tên'])
        current_shift = st.selectbox("Ca hiện tại", shifts['Ca'])
        new_shift = st.selectbox("Ca muốn đổi", shifts['Ca'])
        change_date = st.date_input("Ngày đổi ca", date.today())
        reason = st.text_area("Lý do")
        
        submitted = st.form_submit_button("Gửi yêu cầu")
        if submitted:
            st.success(f"Đã gửi yêu cầu đổi ca từ {current_shift} sang {new_shift} cho {emp}")

elif menu == "Quản lý nghỉ phép":
    st.header("Quản lý Nghỉ phép")
    
    tab1, tab2 = st.tabs(["Yêu cầu nghỉ phép", "Duyệt yêu cầu"])
    
    with tab1:
        st.subheader("Tạo yêu cầu nghỉ phép")
        with st.form("leave_request"):
            emp = st.selectbox("Nhân viên", st.session_state.employees['Họ tên'])
            leave_type = st.selectbox("Loại phép", ["Nghỉ phép năm", "Nghỉ ốm", "Nghỉ việc riêng"])
            start_date = st.date_input("Ngày bắt đầu", date.today())
            end_date = st.date_input("Ngày kết thúc", date.today() + timedelta(days=1))
            reason = st.text_area("Lý do")
            
            submitted = st.form_submit_button("Gửi yêu cầu")
            if submitted:
                emp_id = st.session_state.employees[st.session_state.employees['Họ tên'] == emp]['Mã NV'].values[0]
                emp_name = st.session_state.employees[st.session_state.employees['Họ tên'] == emp]['Họ tên'].values[0]
                days_off = (end_date - start_date).days + 1
                
                new_request = pd.DataFrame({
                    'Mã NV': [emp_id],
                    'Họ tên': [emp_name],
                    'Loại phép': [leave_type],
                    'Ngày bắt đầu': [start_date.strftime("%Y-%m-%d")],
                    'Ngày kết thúc': [end_date.strftime("%Y-%m-%d")],
                    'Số ngày': [days_off],
                    'Lý do': [reason],
                    'Trạng thái': ["Chờ duyệt"]
                })
                
                st.session_state.leave_requests = pd.concat([st.session_state.leave_requests, new_request], ignore_index=True)
                st.success("Đã gửi yêu cầu nghỉ phép!")
    
    with tab2:
        st.subheader("Duyệt yêu cầu nghỉ phép")
        pending_requests = st.session_state.leave_requests[st.session_state.leave_requests['Trạng thái'] == 'Chờ duyệt']
        
        for idx, row in pending_requests.iterrows():
            with st.expander(f"Yêu cầu của {row['Họ tên']} - {row['Loại phép']}"):
                st.write(f"**Mã NV:** {row['Mã NV']}")
                st.write(f"**Thời gian:** Từ {row['Ngày bắt đầu']} đến {row['Ngày kết thúc']} ({row['Số ngày']} ngày)")
                st.write(f"**Lý do:** {row['Lý do']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Duyệt ✅", key=f"approve_{idx}"):
                        st.session_state.leave_requests.at[idx, 'Trạng thái'] = "Đã duyệt"
                        
                        # Trừ ngày phép
                        emp_idx = st.session_state.employees[st.session_state.employees['Mã NV'] == row['Mã NV']].index[0]
                        current_leave = st.session_state.employees.at[emp_idx, 'Số ngày phép còn lại']
                        st.session_state.employees.at[emp_idx, 'Số ngày phép còn lại'] = current_leave - row['Số ngày']
                        
                        st.rerun()
                
                with col2:
                    if st.button(f"Từ chối ❌", key=f"reject_{idx}"):
                        st.session_state.leave_requests.at[idx, 'Trạng thái'] = "Từ chối"
                        st.rerun()

elif menu == "Báo cáo":
    st.header("Báo cáo Chấm công")
    
    report_type = st.selectbox("Loại báo cáo", ["Theo nhân viên", "Theo phòng ban", "Thống kê tổng hợp"])
    
    if report_type == "Theo nhân viên":
        selected_employee = st.selectbox("Chọn nhân viên", st.session_state.employees['Họ tên'])
        emp_id = st.session_state.employees[st.session_state.employees['Họ tên'] == selected_employee]['Mã NV'].values[0]
        
        # Lấy dữ liệu chấm công
        emp_data = st.session_state.timekeeping[st.session_state.timekeeping['Mã NV'] == emp_id]
        
        # Tính toán các chỉ số
        total_days = len(emp_data)
        on_time = len(emp_data[emp_data['Trạng thái'].str.contains('Đúng giờ|Hoàn thành ca')])
        late_days = len(emp_data[emp_data['Trạng thái'].str.contains('Muộn')])
        early_days = len(emp_data[emp_data['Trạng thái'].str.contains('Về sớm')])
        overtime_hours = 0  # Giả định cần tính toán thực tế
        
        # Hiển thị thống kê
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tổng ngày làm", total_days)
        col2.metric("Đúng giờ", on_time)
        col3.metric("Đi muộn", late_days)
        col4.metric("Về sớm", early_days)
        
        # Hiển thị dữ liệu chi tiết
        st.dataframe(emp_data)
    
    elif report_type == "Thống kê tổng hợp":
        st.subheader("Thống kê toàn công ty")
        
        # Tính toán các chỉ số
        total_employees = len(st.session_state.employees)
        avg_late = round(len(st.session_state.timekeepingst.session_state.timekeeping['Trạng thái'].str.contains('Muộn')) / total_employees, 1)
        avg_early = round(len(st.session_state.timekeepingst.session_state.timekeeping['Trạng thái'].str.contains('Về sớm')) / total_employees, 1)
        
        # Hiển thị thống kê
        col1, col2, col3 = st.columns(3)
        col1.metric("Tổng số nhân viên", total_employees)
        col2.metric("Số lần đi muộn TB", avg_late)
        col3.metric("Số lần về sớm TB", avg_early)
        
        # Biểu đồ
        st.bar_chart(st.session_state.timekeeping['Trạng thái'].value_counts())