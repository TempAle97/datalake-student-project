import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Cau hinh
download_dir = r"E:\3rdYear\HocKi2\Dot2\CDCS1\Diem_tuyen_sinh_KoDN"
os.makedirs(download_dir, exist_ok=True)
chromedriver_path = r"E:\3rdYear\HocKi2\Dot2\CĐCS\BaiTapLon\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# Bo file CTDT
def is_training_program(filename):
    fn = filename.lower().replace(" ", "").replace("_", "").replace("-", "")
    return any(p in fn for p in ["chuongtrinhdaotao", "chươngtrìnhđàotạo", "ctdt"])

# Tai file PDF truc tiep
def download_pdf(pdf_url, year):
    name = os.path.basename(unquote(pdf_url)).replace(".pdf", "")
    if is_training_program(name):
        print("Bo qua CTDT:", name)
        return
    path = os.path.join(download_dir, f"{year}_{name}.pdf")
    try:
        r = requests.get(pdf_url)
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"{year} Tai thanh cong:", name)
    except Exception as e:
        print("Loi khi tai:", name, "->", e)

# Lay link pdf 2022
def get_pdf_links_2022(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    return [
        urljoin(url, link['href']) for link in soup.find_all('a', href=True)
        if link['href'].endswith('.pdf') and not is_training_program(link['href'])
    ]

# Lay pdf cuoi 2023
def get_last_pdf_2023(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    last_pdf = None
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.pdf') and not is_training_program(href):
            last_pdf = urljoin(url, href)
    return last_pdf

# Mo click here roi tai file cho 2024
def selenium_2024_onedrive_download(actvn_news_url):
    options = webdriver.ChromeOptions()
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "download.default_directory": download_dir
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    driver.get(actvn_news_url)
    time.sleep(5)
    onedrive_links = []
    try:
        buttons = driver.find_elements(By.XPATH, "//a[img[contains(@src, 'click') or contains(@src, 'button')]]")
        for btn in buttons:
            href = btn.get_attribute("href")
            if href and "sharepoint.com" in href:
                onedrive_links.append(href)
    except Exception as e:
        print("Loi lay link click:", e)
    print("Tim thay", len(onedrive_links), "link OneDrive.")
    for i, link in enumerate(onedrive_links, 1):
        print(f"Mo link {i}:", link)
        driver.get(link)
        time.sleep(8)
        try:
            btn = driver.find_element(By.XPATH, "//button[@aria-label='Download this file to your device']")
            btn.click()
            print("Da bam Download.")
        except Exception as e:
            print("Khong thay nut download:", e)
        time.sleep(10)

    driver.quit()

# Danh sach url
list_url = [
    ('https://thi.tuyensinh247.com/danh-sach-trung-tuyen-nam-2022-hoc-vien-ky-thuat-mat-ma-c24a71677.html', '2022'),
    ('https://actvn.edu.vn/News/Detail?NewsId=28237', '2023'),
    ('https://actvn.edu.vn/News/Detail?NewsId=28354', '2024')
]

# Chay
for url, year in list_url:
    print("== NAM", year, "==")
    if year == '2022':
        for pdf in get_pdf_links_2022(url):
            download_pdf(pdf, year)
    elif year == '2023':
        pdf = get_last_pdf_2023(url)
        if pdf:
            download_pdf(pdf, year)
        else:
            print("Khong tim thay pdf 2023.")
    elif year == '2024':
        selenium_2024_onedrive_download(url)

print("Da hoan tat luu file tai:", download_dir)