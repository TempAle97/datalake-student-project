import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time

# ==== CẤU HÌNH CHUNG ====
download_dir = r"/home/nifi/HOCTAP/data/Diem_tuyen_sinh_DN"
os.makedirs(download_dir, exist_ok=True)
chromedriver_path = r"/home/nifi/HOCTAP/chromedriver-win64/chromedriver.exe"
username = 'at190@actvn.edu.vn'
password = ''

# ==== BỎ FILE CTĐT ====
def is_training_program(filename):
    filename_norm = filename.lower().replace(" ", "").replace("_", "").replace("-", "")
    patterns = ["chuongtrinhdaotao", "chươngtrìnhđàotạo", "ctdt"]
    return any(pat in filename_norm for pat in patterns)

# ==== TẢI FILE PDF TRỰC TIẾP ====
def download_pdf(pdf_url, year):
    filename = os.path.basename(unquote(pdf_url)).replace(".pdf", "")
    if is_training_program(filename):
        print(f"Bo qua CTĐT: {filename}")
        return
    path = os.path.join(download_dir, f"{year}_{filename}.pdf")
    try:
        r = requests.get(pdf_url)
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"✔ [{year}] Tai thanh cong: {filename}")
    except Exception as e:
        print(f"Loi khi tai {filename}: {e}")

# ==== LẤY FILE PDF CHO 2022 ====
def get_pdf_links_2022(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    return [
        urljoin(url, link['href'])
        for link in soup.find_all('a', href=True)
        if link['href'].endswith('.pdf') and not is_training_program(link['href'])
    ]

# ==== LẤY LINK CUỐI PDF CHO 2023 ====
def get_last_pdf_2023(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    last_pdf = None
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.pdf') and not is_training_program(href):
            last_pdf = urljoin(url, href)
    return last_pdf

# ==== TẢI FILE TỪ ONEDRIVE NĂM 2024 ====
def selenium_download_onedrive_links(onedrive_links):
    options = webdriver.ChromeOptions()
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "download.default_directory": download_dir
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=options)

    # ==== ĐĂNG NHẬP LẦN ĐẦU VỚI LINK ĐẦU ====
    print("Dang dang nhap vao OneDrive...")
    driver.get(onedrive_links[0])
    time.sleep(6)
    try:
        # Kiểm tra username và password, nếu thiếu thì báo lỗi và return luôn
        if not username.strip():
            print("Thieu ten dang nhap (username) hoac nhap sai")
            driver.quit()
            return
        if not password.strip():
            print("Thieu mat khau (password) hoac nhap sai")
            driver.quit()
            return
        email_input = driver.find_element(By.NAME, "loginfmt")
        email_input.send_keys(username)
        email_input.send_keys(Keys.ENTER)
        time.sleep(3)
        password_input = driver.find_element(By.NAME, "passwd")
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(3)
        try:
            driver.find_element(By.ID, "idBtn_Back").click()
        except:
            pass
        print("Dang nhap Microsoft thanh cong.")
    except Exception as e:
        print("Co the dang nhap sai hoac bi loi:", e)
        driver.quit()
        return

    # ==== DUYỆT TỪNG LINK ====
    for link in onedrive_links:
        print(f"📥Đang mo: {link}")
        driver.get(link)
        time.sleep(7)
        try:
            download_button = driver.find_element(By.XPATH, "//button[@aria-label='Download this file to your device']")
            download_button.click()
            print("Da bam Download!")
        except Exception as e:
            print("Khong thay nut Download:", e)
        time.sleep(10)
    driver.quit()
    print("Hoan tat tai file 2024.")

# ==== DANH SÁCH URL CHO 2022 & 2023 ====
list_url = [
    ('https://thi.tuyensinh247.com/danh-sach-trung-tuyen-nam-2022-hoc-vien-ky-thuat-mat-ma-c24a71677.html', '2022'),
    ('https://actvn.edu.vn/News/Detail?NewsId=28237', '2023')
]

# ==== DANH SÁCH LINK ONEDRIVE CHO 2024 ====
onedrive_2024_links = [
    'https://actvneduvn-my.sharepoint.com/personal/vinhlk_actvn_edu_vn/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fvinhlk%5Factvn%5Fedu%5Fvn%2FDocuments%2FC%C3%B4ng%20vi%E1%BB%87c%2FTin%20t%E1%BB%A9c%20Website%2FTrung%20tuyen%202024%2FNg%C3%A0nh%5FATTT%5FPh%C3%ADa%20B%E1%BA%AFc%2D2024%2Epdf&parent=%2Fpersonal%2Fvinhlk%5Factvn%5Fedu%5Fvn%2FDocuments%2FC%C3%B4ng%20vi%E1%BB%87c%2FTin%20t%E1%BB%A9c%20Website%2FTrung%20tuyen%202024&ga=1',
    'https://actvneduvn-my.sharepoint.com/personal/vinhlk_actvn_edu_vn/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fvinhlk%5Factvn%5Fedu%5Fvn%2FDocuments%2FC%C3%B4ng%20vi%E1%BB%87c%2FTin%20t%E1%BB%A9c%20Website%2FTrung%20tuyen%202024%2FNg%C3%A0nh%5FATTT%5FPh%C3%ADa%20Nam%2D2024%2Epdf&parent=%2Fpersonal%2Fvinhlk%5Factvn%5Fedu%5Fvn%2FDocuments%2FC%C3%B4ng%20vi%E1%BB%87c%2FTin%20t%E1%BB%A9c%20Website%2FTrung%20tuyen%202024&ga=1',
    'https://actvneduvn-my.sharepoint.com/personal/vinhlk_actvn_edu_vn/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fvinhlk%5Factvn%5Fedu%5Fvn%2FDocuments%2FC%C3%B4ng%20vi%E1%BB%87c%2FTin%20t%E1%BB%A9c%20Website%2FTrung%20tuyen%202024%2FHVKTMM%5FNg%C3%A0nh%5FCNTT%2D2024%2Epdf&parent=%2Fpersonal%2Fvinhlk%5Factvn%5Fedu%5Fvn%2FDocuments%2FC%C3%B4ng%20vi%E1%BB%87c%2FTin%20t%E1%BB%A9c%20Website%2FTrung%20tuyen%202024&ga=1',
    'https://actvneduvn-my.sharepoint.com/personal/vinhlk_actvn_edu_vn/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fvinhlk%5Factvn%5Fedu%5Fvn%2FDocuments%2FC%C3%B4ng%20vi%E1%BB%87c%2FTin%20t%E1%BB%A9c%20Website%2FTrung%20tuyen%202024%2FNg%C3%A0nh%5FKT%20%C4%90TVT%2D2024%2Epdf&parent=%2Fpersonal%2Fvinhlk%5Factvn%5Fedu%5Fvn%2FDocuments%2FC%C3%B4ng%20vi%E1%BB%87c%2FTin%20t%E1%BB%A9c%20Website%2FTrung%20tuyen%202024&ga=1',
    # Thêm các link khác nếu có
]

# ==== CHẠY TOÀN BỘ ====
for url, year in list_url:
    print(f"\n==== NAM {year} ====")
    if year == '2022':
        for pdf in get_pdf_links_2022(url):
            download_pdf(pdf, year)
    elif year == '2023':
        pdf = get_last_pdf_2023(url)
        if pdf:
            download_pdf(pdf, year)
        else:
            print("Khong tim thay PDF 2023.")
print("\n==== NAM 2024 ====")
selenium_download_onedrive_links(onedrive_2024_links)
print("\nDa hoan tat tai vao file:", download_dir)