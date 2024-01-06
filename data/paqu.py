import os
import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor

def get_content_from_url(book_url):
    response = requests.get(book_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find('div', {'id': 'content'})
    content_text = content_div.get_text(separator="\n", strip=True) if content_div else ""
    return content_text

def get_data_from_url(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取标题
    panel_heading = soup.select_one('div.panel-heading > h1')
    if panel_heading and panel_heading.find('small'):
        panel_heading.find('small').extract()  # 删除不需要的小标签部分(如果存在)
    title_text = panel_heading.get_text(strip=True) if panel_heading else None
    
    # 获取封面图片
    img_src = soup.select_one('div.panel-body > div.fmpic > img')['src'] if soup.select_one('div.panel-body > div.fmpic > img') else None
    
    # 获取简介
    summary_text = soup.select_one('div.panel-body > p.m-summary').get_text(strip=True) if soup.select_one('div.panel-body > p.m-summary') else None
    
    # 获取所有 <ul class="list-group"> 下的 <li>
    booklist = soup.select('ul.list-group > li')
    books = []
    for li in booklist:
        a_tag = li.find('a')
        if a_tag and 'href' in a_tag.attrs:
            books.append({
                'href': a_tag['href'],
                'title': a_tag.get_text(strip=True)
            })
    
    # 组织数据
    data = {
        'title': title_text,
        'cover_image': img_src,
        'summary': summary_text,
        'book_list': books
    }
    
    return data


# 新函数：下载书籍并保存到文件
def download_and_save_book(book, title_directory, num):
    content = get_content_from_url(book["href"])
    file_name = "".join(char for char in book["title"] if char.isalnum() or char in (" ", ".", "_")).rstrip()
    file_name = f"{num}_{file_name}.txt" if file_name else f"{num}_unknown_title.txt"
    file_path = os.path.join(title_directory, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"内容已保存到文件：{file_path}")

def process_books(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        book_list = json.load(file)

    for index, book in enumerate(book_list, start=1):
        data = get_data_from_url(book['href'])

        # 创建以书名命名的目录
        title_directory = "".join(char for char in data['title'] if char.isalnum() or char in (" ", ".", "_")).rstrip() if data['title'] else f"book_data_{index}"
        if not os.path.exists(title_directory):
            os.makedirs(title_directory)

        # 将数据保存为JSON文件
        data_file_path = os.path.join(title_directory, 'data.json')
        with open(data_file_path, 'w', encoding='utf-8') as data_file:
            json.dump(data, data_file, ensure_ascii=False, indent=4)
        print(f"数据已保存到文件：{data_file_path}")

        # 使用多线程下载书籍内容
        with ThreadPoolExecutor(max_workers=10) as executor:
            for num, book_item in enumerate(data["book_list"], start=1):
                executor.submit(download_and_save_book, book_item, title_directory, num)

# 运行程序处理书籍
json_file = 'results2.json'
process_books(json_file)
