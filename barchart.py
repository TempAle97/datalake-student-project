import matplotlib
matplotlib.use('Agg')  
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import gc  

# Cấu hình font cơ bản
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False

def read_csv_standardized(filepath):
    try:
        df = pd.read_csv(filepath)
        thi_column = None
        for col in df.columns:
            if 'THI' in str(col):
                thi_column = col
                break
        if thi_column is None:
            print(f"Khong tim thay cot diem thi trong file {filepath}")
            return None
        scores = df[thi_column]
        scores = pd.to_numeric(scores, errors='coerce')
        scores = scores.dropna()
        return scores
    except Exception as e:
        print(f"Error reading {filepath}: {str(e)}")
        return None

def create_grade_distribution(scores, subject_code, year):
    plt.figure(figsize=(15, 8))
    bins = np.arange(0, 10.2, 0.2)
    hist, bin_edges = np.histogram(scores, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    plt.bar(bin_centers, hist, width=0.16, alpha=0.8, color='dodgerblue')
    total_students = len(scores)
    passed_students = len(scores[scores >= 4.0])
    failed_students = total_students - passed_students
    pass_rate = (passed_students / total_students * 100) if total_students > 0 else 0
    fail_rate = 100 - pass_rate
    min_score = scores.min()
    max_score = scores.max()
    stats_text = f'Phan tich diem thi:\n'
    stats_text += f'• Tong so SV: {total_students}\n'
    stats_text += f'• So SV dat (>=4.0): {passed_students}\n'
    stats_text += f'• Ty le dat: {pass_rate:.1f}%\n'
    stats_text += f'• Ty le truot: {fail_rate:.1f}%\n'
    stats_text += f'• Diem cao nhat: {max_score:.1f}\n'
    stats_text += f'• Diem thap nhat: {min_score:.1f}'
    plt.text(
        0.02, 0.98, stats_text,
        transform=plt.gca().transAxes,
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'),
        verticalalignment='top',
        fontsize=10
    )
    plt.title(f'Pho diem thi mon {subject_code} - Nam {year}\nTong so sinh vien: {total_students}', pad=20)
    plt.xlabel('Diem thi')
    plt.ylabel('So luong sinh vien')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(np.arange(0, 10.2, 0.2), rotation=45, fontsize=8)
    max_students = hist.max()
    plt.ylim(0, max_students * 1.2)
    plt.yticks(np.arange(0, max_students + 1, max(1, max_students // 10)))
    for i, v in enumerate(hist):
        if v > 1:
            plt.text(bin_centers[i], v, str(int(v)), ha='center', va='bottom', fontsize=6)
    plt.tight_layout()
    return plt

if __name__ == "__main__":
    folders_and_years = [
        (r"E:\3rdYear\HocKi2\Dot2\CDCS1\Diem_KTHP\File csv 22-23", "22-23"),
        (r"E:\3rdYear\HocKi2\Dot2\CDCS1\Diem_KTHP\File csv 23-24", "23-24"),
        (r"E:\3rdYear\HocKi2\Dot2\CDCS1\Diem_KTHP\File csv 24-25", "24-25"),
    ]
    for csv_directory, year in folders_and_years:
        print(f"Xu ly thu muc: {csv_directory}")
        for filename in os.listdir(csv_directory):
            if filename.endswith('.csv'):
                filepath = os.path.join(csv_directory, filename)
                subject_code = filename.split('.')[0]
                print(f"  Dang xu ly: {subject_code}")
                scores = read_csv_standardized(filepath)
                if scores is not None and not scores.empty:
                    try:
                        plt_fig = create_grade_distribution(scores, subject_code, year)
                        # Lưu biểu đồ
                        output_dir = os.path.join(r'E:\3rdYear\HocKi2\Dot2\CDCS1\Do_thi_KQ_KTHP', year)
                        os.makedirs(output_dir, exist_ok=True)
                        output_path = os.path.join(output_dir, f'{subject_code}_{year}.png')
                        plt_fig.savefig(output_path, dpi=300, bbox_inches='tight')
                        print(f"    Da luu: {output_path}")
                    except Exception as e:
                        print(f"    Loi khi xu ly {subject_code}: {str(e)}")
                    finally:
                        plt.close('all')   
                        gc.collect()       
                else:
                    print(f"    Khong co du lieu hop le cho {subject_code}")