import pandas as pd

def process_excel_file(file_path, sheet_info, output_csv, header_row=0, col_mapping=None):
    all_records = []
    for sheet in (sheet_info.keys() if isinstance(sheet_info, dict) else sheet_info):
        try:
            df = pd.read_excel(file_path, sheet_name=sheet, header=header_row)
            df.columns = df.columns.str.strip()
            # Đổi tên cột trước khi lọc
            if col_mapping:
                df.rename(columns=col_mapping, inplace=True)
            # Danh sách cột bắt buộc
            expected_cols = ["STT", "HỌ TÊN", "MÃ SV", "LỚP"]
            if not isinstance(sheet_info, dict):
                expected_cols.append("Chuyên Ngành")
            # Kiểm tra và chọn cột hợp lệ
            if set(expected_cols).issubset(df.columns):
                df = df[expected_cols]
                df.drop(columns=["STT"], inplace=True)
                # Gán hoặc chuẩn hóa chuyên ngành
                if isinstance(sheet_info, dict):
                    df["Chuyên Ngành"] = sheet_info[sheet]
                else:
                    df["Chuyên Ngành"] = df["Chuyên Ngành"].astype(str).str.strip().str.title()
                all_records.append(df)
            else:
                print(f"Sheet '{sheet}' thieu cot can thiet: {df.columns.tolist()}")
        except Exception as e:
            print(f"Loi o sheet '{sheet}': {e}")
    # Gộp kết quả và xuất ra file CSV
    if all_records:
        df_final = pd.concat(all_records, ignore_index=True)
        df_final.insert(0, "STT", range(1, len(df_final) + 1))
        df_final.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"Xuat file thanh cong: {output_csv}")
    else:
        print(f"Khong co du lieu hop le trong {file_path}")
#GỌI HÀM CHO AT18.XLSX
process_excel_file(
    file_path=r"/home/nifi/HOCTAP/dulieuexcel/AT18.xlsx",
    sheet_info={
        "AT-HỆ THỐNG": "AT - Hệ Thống",
        "AT- KỸ NGHỆ": "AT - Kỹ Nghệ",
        "AT -PHẦN MỀM": "AT - Phần Mềm"
    },
    output_csv=r"/home/nifi/HOCTAP/data/dang_ky_chuyen_nganh/AT18_chuyen_nganh.csv",
    header_row=2
)
#GỌI HÀM CHO AT19.XLSX
process_excel_file(
    file_path=r"/home/nifi/HOCTAP/dulieuexcel/AT19.xlsx",
    sheet_info=["An toàn HTTT", "Công nghệ PM", "Kỹ nghệ ATM"],
    output_csv=r"/home/nifi/HOCTAP/data/dang_ky_chuyen_nganh/AT19_chuyen_nganh.csv",
    header_row=0,
    col_mapping={
        "Họ tên": "HỌ TÊN",
        "MSSV": "MÃ SV",
        "Lớp": "LỚP",
        "Chuyên ngành đăng ký": "Chuyên Ngành"
    }
)