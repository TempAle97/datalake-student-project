import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import re

BASE_URL = 'https://ktdbcl.actvn.edu.vn/khao-thi/to-chuc-thi/ket-qua-thi.html'
SAVE_FOLDER = r'/home/nifi/HOCTAP/data/Diem_khac'
os.makedirs(SAVE_FOLDER, exist_ok=True)

def clean_name(text):
    # Loại ký tự không hợp lệ trong tên folder/file
    text = unquote(str(text)).strip()
    text = re.sub(r'[\\/:*?"<>|]', '', text)
    return text[:100] if len(text) > 100 else text

def get_pdf_links(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    tables = soup.find_all('table')
    if len(tables) < 2:
        raise Exception("Khong tim thay bang diem phu hop!")
    table = tables[1]
    rows = table.find_all('tr')[1:]  # bo dong tieu de

    pdfs = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue
        title = clean_name(cells[1].get_text())
        for a in row.find_all('a', href=True):
            href = a['href']
            if href.endswith('.pdf'):
                pdfs.append((title, urljoin(url, href)))
    return pdfs

def save_pdf_to_folder(folder, pdf_url):
    file_name = os.path.basename(unquote(pdf_url))
    file_path = os.path.join(folder, file_name)
    if os.path.exists(file_path):
        print(f"Da ton tai: {file_name}")
        return
    try:
        r = requests.get(pdf_url, timeout=30)
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            f.write(r.content)
        print(f"Da tai: {file_name}")
    except Exception as e:
        print(f"Loi tai {file_name}: {e}")

def main():
    pdfs = get_pdf_links(BASE_URL)
    for title, pdf_url in pdfs:
        folder = os.path.join(SAVE_FOLDER, title)
        os.makedirs(folder, exist_ok=True)
        save_pdf_to_folder(folder, pdf_url)
    print(f"\nHoan tat! File da duoc tai ve folder: {SAVE_FOLDER}")

if __name__ == "__main__":
    main()