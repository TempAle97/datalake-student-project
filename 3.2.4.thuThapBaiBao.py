import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
from urllib.parse import urlparse
from serpapi import GoogleSearch


class TuyenSinhCrawler:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.data = []
        self.processed_urls = set()
        self.api_key = "##############################"

    def search_google(self, keywords, num_results=30):
        print(f"Đang tim kiem: {keywords}")
        try:
            params = {
                "engine": "google",
                "q": keywords,
                "num": num_results,
                "gl": "vn",
                "hl": "vi",
                "api_key": self.api_key
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            urls = []
            if "organic_results" in results:
                for result in results["organic_results"]:
                    if "link" in result:
                        urls.append(result["link"])
            return urls
        except Exception as e:
            print(f"Loi khi tim kiem Google: {e}")
            return []

    def get_article_content(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.title.string.strip() if soup.title else "Không rõ tiêu đề"

            content_div = soup.find("div", class_=["article-content", "post-content", "entry-content",
                                                   "detail-content", "content", "article-body", "post-body",
                                                   "entry", "article", "post"])
            if not content_div:
                content_div = soup.find("div", {"id": ["content", "main-content", "detail-content", "article-content", "post-content"]})
            if not content_div:
                content_div = soup.find("article")

            if content_div:
                for tag in content_div.find_all(["script", "style", "nav", "header", "footer", "aside"]):
                    tag.decompose()

                content = " ".join(content_div.get_text().split())

                if any(keyword in content.lower() for keyword in ['tuyển sinh', 'tuyển dụng', 'thông báo', 'chỉ tiêu', 'điểm chuẩn']):
                    return title, content[:1000] + "..." if len(content) > 1000 else content

        except Exception as e:
            print(f"Loi lhi lay noi dung {url}: {e}")
        return "Khong ro tieu de", "Khong the lay noi dung"

    def crawl_articles(self, urls):
        for url in urls:
            if url in self.processed_urls:
                continue

            domain = urlparse(url).netloc
            if any(x in domain for x in ['facebook.com', 'youtube.com', 'twitter.com', 'instagram.com']):
                continue

            title, content = self.get_article_content(url)
            if content == "Khong the lay noi dung":
                continue

            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                date_tag = soup.find(["time", "span", "div", "meta"],
                                     class_=["date", "time", "post-date", "article-date", "published-date"])
                if not date_tag:
                    date_tag = soup.find("meta", property="article:published_time")
                date = date_tag.get_text(strip=True) if date_tag else "Không rõ ngày"
            except:
                date = "Khong ro ngay"

            self.data.append({
                "nguon": domain,
                "tieu_de": title,
                "link": url,
                "ngay_dang": date,
                "noi_dung": content
            })
            self.processed_urls.add(url)
            print(f"Da lay: {title[:60]}...")
            time.sleep(2)

    def save_to_csv(self):
        if not self.data:
            print("Khong co du lieu de luu")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"tuyen_sinh2_actvn_{today}.csv"

        try:
            with open(filename, "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["nguon", "tieu_de", "link", "ngay_dang", "noi_dung"])
                writer.writeheader()
                writer.writerows(self.data)
            print(f"\nDa luu{len(self.data)} bai viet vao file: {filename}")
        except Exception as e:
            print(f"Loi khi luu file CSV: {e}")

def main():
    crawler = TuyenSinhCrawler()
    
    print("Nhap tu khoa tim kiem cua ban: ")
    keyword = input()

    print("Bat dau thu thap thong tin...\n")

    urls = crawler.search_google(keyword)
    if urls:
        crawler.crawl_articles(urls)
    
    crawler.save_to_csv()

if __name__ == "__main__":
    main()