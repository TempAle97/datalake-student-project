import os
import pandas as pd
import pdfplumber
import fitz
import re

STANDARD_COLUMNS = [
    'SBD', 'Mã SV', 'Tên', 'Lớp',
    'THI', 'HP', 'Chữ', 'Ghi chú', 'Môn học'
]

def clean_dataframe(df):
    df = df[~df.astype(str).apply(lambda x: x.str.contains("ngay|Hà N|tháng|năm", case=False)).any(axis=1)]
    df = df.dropna(how='all')
    df = df[~(df.apply(lambda x: ','.join(x.astype(str)).strip(','), axis=1) == '')]
    return df

def chuan_hoa_bang_diem(df, subject_name):
    df.columns = [str(col).strip() for col in df.columns]
    df['Môn học'] = subject_name
    if "Họ đệm" in df.columns and "Tên" in df.columns:
        df["Tên"] = df["Họ đệm"].astype(str).str.strip() + " " + df["Tên"].astype(str).str.strip()
        df.drop(columns=["Họ đệm"], inplace=True)
    column_mapping = {
        "Mã HVSV": "Mã SV",
        "Mã sinh\nviên": "Mã SV",
        "Mã sinh viên": "Mã SV",
        "KQ chấm \n(Phúc khảo)": "THI",
        "KQ chấm (Phúc khảo)": "THI",
        "TKHP": "HP"
    }
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    cols_to_drop = ["TP1", "TP2", "THI\n(lần 1)", "STT", "TT", "Thứ tự"]
    for col in cols_to_drop:
        if col in df.columns:
            df.drop(columns=col, inplace=True)
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[STANDARD_COLUMNS]

def get_base_subject_name(subject):
    subject = re.sub(r'phúc khảo.*', '', subject, flags=re.IGNORECASE)
    subject = subject.strip(' -–—:').strip()
    return subject

def get_unique_path(base_path):
    if not os.path.exists(base_path):
        return base_path
    base, ext = os.path.splitext(base_path)
    counter = 1
    while os.path.exists(f"{base}_{counter}{ext}"):
        counter += 1
    return f"{base}_{counter}{ext}"

def extract_and_split_by_subject(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    subject_dict = {}
    for file in os.listdir(input_folder):
        if file.lower().endswith(".pdf"):
            path = os.path.join(input_folder, file)
            with pdfplumber.open(path) as pdf:
                current_subject = None
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    for line in text.splitlines():
                        match = re.search(r"Môn thi:\s*([^\n]+)", line)
                        if match:
                            current_subject = match.group(1).strip()
                    tables = page.extract_tables()
                    for table in tables:
                        if current_subject:
                            df = pd.DataFrame(table)
                            if df.shape[0] < 2 or df.shape[1] < 4:
                                continue
                            df.columns = df.iloc[0]
                            df = df[1:].reset_index(drop=True)
                            if "Tên" in df.columns:
                                idx = list(df.columns).index("Tên")
                                if idx == len(df.columns) - 1 and df.shape[1] == len(df.columns) + 1:
                                    new_cols = list(df.columns)
                                    new_cols[idx] = "Họ đệm"
                                    new_cols.append("Tên")
                                    df.columns = new_cols
                                    df["Tên"] = df["Họ đệm"].astype(str).str.strip() + " " + df["Tên"].astype(str).str.strip()
                                    df.drop(columns=["Họ đệm"], inplace=True)
                            df_clean = chuan_hoa_bang_diem(df, current_subject)
                            base_subject = get_base_subject_name(current_subject)
                            safe_subject = re.sub(r"[^\w\-]", "_", base_subject)
                            if safe_subject not in subject_dict:
                                subject_dict[safe_subject] = []
                            subject_dict[safe_subject].append(df_clean)
    for subject, df_list in subject_dict.items():
        full_df = pd.concat(df_list, ignore_index=True)
        full_df = full_df.drop_duplicates(subset=["SBD", "Mã SV", "Tên"], keep="last")
        out_path = get_unique_path(os.path.join(output_folder, f"{subject}.csv"))
        full_df.to_csv(out_path, index=False, encoding='utf-8-sig')
        print(f"Da xuat: {out_path} ({len(full_df)} dong)")

def process_2022_2024(path_folder, output_folder, error_files):
    if not os.path.exists(path_folder):
        print("Folder khong ton tai:", path_folder)
        return
    list_file = os.listdir(path_folder)
    print("Cac file tim thay:", list_file)
    found = False
    for name_file in list_file:
        if name_file.lower().endswith('.pdf'):
            found = True
            print("Dang xu ly file:", name_file)
            try:
                dfs = []
                doc = fitz.open(os.path.join(path_folder, name_file))
                tabs = [p.find_tables() for p in doc]
                for i in range(len(doc)):
                    print(f" → Trang {i+1}")
                    if len(tabs[i].tables) > 0:
                        df = pd.DataFrame(tabs[i].tables[0].extract())
                        if df.iloc[0, 0] in ['STT', 'TT']:
                            df.columns = df.iloc[0]
                            df = df[1:].reset_index(drop=True)
                            if len(df.columns) > 4:
                                df = clean_dataframe(df)
                                dfs.append(df)
                course_names = []
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    for line in text.split('\n'):
                        if 'Mã học phần' in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                course_names.append(parts[1].strip())
                listset = list(set(course_names))
                list_df_va_name = []
                for name in listset:
                    name_indices = [i for i, x in enumerate(course_names) if x == name]
                    tmp = [dfs[idx] for idx in name_indices if idx < len(dfs)]
                    if tmp:
                        list_df_va_name.append([name, pd.concat(tmp, ignore_index=True)])
                for name, df in list_df_va_name:
                    out_df = df.copy()
                    safe_name = re.sub(r'[^\w\-]', '_', name)
                    os.makedirs(output_folder, exist_ok=True)
                    raw_path = os.path.join(output_folder, f"{safe_name}.csv")
                    out_path = get_unique_path(raw_path)
                    out_df.to_csv(out_path, index=False)
                    print(f"Da xuat: {out_path} ({len(out_df)} dong)")
            except Exception as e:
                print("LOI:", name_file, "-", e)
                error_files.append(name_file)
    if not found:
        print("Khong tim thay file PDF nao trong folder:", path_folder)

def run_for_year(year):
    error_files = []
    if year == "2022-2023":
        process_2022_2024(
            "/home/nifi/HOCTAP/data/Diem_KTHP/nam-22-23",
            "/home/nifi/HOCTAP/data/Diem_KTHP/File csv 22-23",
            error_files
        )
    elif year == "2023-2024":
        process_2022_2024(
            "/home/nifi/HOCTAP/data/Diem_KTHP/nam-23-24",
            "/home/nifi/HOCTAP/data/Diem_KTHP/File csv 23-24",
            error_files
        )
    elif year == "2024-2025":
        extract_and_split_by_subject(
            "/home/nifi/HOCTAP/data/Diem_KTHP/nam-24-25",
            "/home/nifi/HOCTAP/data/Diem_KTHP/File csv 24-25",
        )
    else:
        print("Nam nay chua ho tro")
    if error_files:
        print("\nCac file loi khong doc duoc:")
        for f in error_files:
            print("   -", f)
    else:
        print("\nTat ca cac file deu duoc xu ly thanh cong!")

if __name__ == "__main__":
    print("Chon nam can xu ly:")
    print("1. 2022-2023")
    print("2. 2023-2024")
    print("3. 2024-2025")
    chon = input("Nhap so(1/2/3): ").strip()
    nam_dict = {"1": "2022-2023", "2": "2023-2024", "3": "2024-2025"}
    nam = nam_dict.get(chon)
    if nam:
        run_for_year(nam)
    else:
        print("Lua chon khong hop le!")