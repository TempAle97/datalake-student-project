import pandas as pd
import matplotlib.pyplot as plt

# ==== CHUẨN BỊ DỮ LIỆU AT18 ====
path_at18 = r"E:\3rdYear\HocKi2\Dot2\CDCS1\output_nguyenvong\AT18_chuyen_nganh.csv"
df18 = pd.read_csv(path_at18)
df18.columns = [col.strip() for col in df18.columns]
df18["Chuyên Ngành"] = df18["Chuyên Ngành"].str.strip()
ds_chuyen_nganh = ["AT - Kỹ Nghệ", "AT - Phần Mềm", "AT - Hệ Thống"]
df18_filtered = df18[df18["Chuyên Ngành"].isin(ds_chuyen_nganh)]
count_18 = df18_filtered["Chuyên Ngành"].value_counts().reindex(ds_chuyen_nganh).reset_index()
count_18.columns = ["Chuyên Ngành", "Số lượng"]
count_18["Tỷ lệ (%)"] = round(100 * count_18["Số lượng"] / count_18["Số lượng"].sum(), 2)
# ==== CHUẨN BỊ DỮ LIỆU AT19 ====
path_at19 = r"E:\3rdYear\HocKi2\Dot2\CDCS1\output_nguyenvong\AT19_chuyen_nganh.csv"
df19 = pd.read_csv(path_at19)
df19.columns = [col.strip() for col in df19.columns]
df19["Chuyên Ngành"] = df19["Chuyên Ngành"].str.strip()

def chuan_hoa_chuyen_nganh(text):
    text = text.lower()
    if "hệ thống" in text:
        return "AT - Hệ Thống"
    elif "kỹ nghệ" in text:
        return "AT - Kỹ Nghệ"
    elif "phần mềm" in text:
        return "AT - Phần Mềm"
    else:
        return "Khác"

df19["Chuyên Ngành chuẩn"] = df19["Chuyên Ngành"].apply(chuan_hoa_chuyen_nganh)
df19_filtered = df19[df19["Chuyên Ngành chuẩn"].isin(ds_chuyen_nganh)]
count_19 = df19_filtered["Chuyên Ngành chuẩn"].value_counts().reindex(ds_chuyen_nganh).reset_index()
count_19.columns = ["Chuyên Ngành", "Số lượng"]
count_19["Tỷ lệ (%)"] = round(100 * count_19["Số lượng"] / count_19["Số lượng"].sum(), 2)
colors = ['#66c2a5', '#fc8d62', '#8da0cb']
color_map = dict(zip(ds_chuyen_nganh, colors))
# ==== VẼ BIỂU ĐỒ ====
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
axes[0].pie(count_18["Tỷ lệ (%)"], labels=None, autopct='%1.1f%%',
            startangle=90, colors=colors)
axes[0].set_title("AT18")
axes[1].pie(count_19["Tỷ lệ (%)"], labels=None, autopct='%1.1f%%',
            startangle=90, colors=colors)
axes[1].set_title("AT19")
# Chú thích (legend) chung cho toàn ảnh
labels = [f"{nganh} ({color})" for nganh, color in color_map.items()]
fig.legend(ds_chuyen_nganh, loc='lower center', ncol=3, fontsize=10)
plt.suptitle("So sánh tỷ lệ chọn chuyên ngành giữa AT18 và AT19", fontsize=14)
plt.tight_layout(rect=[0, 0.05, 1, 0.93])  
plt.savefig(r"E:\3rdYear\HocKi2\Dot2\CDCS1\output_nguyenvong\bieu_do_chuyen_nganh_2khoa.png", dpi=300)
plt.show()