import os
import requests
from bs4 import BeautifulSoup
import json

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
    

# url = 'https://www.zhonghuadiancang.com/xuanxuewushu/xingmingguizhi/'
# data = get_data_from_url(url)

# title_directory = "".join(char for char in data['title'] if char.isalnum() or char in (" ", ".", "_")).rstrip() if data['title'] else "book_data"
# if not os.path.exists(title_directory):
#     os.makedirs(title_directory)

# data_file_path = os.path.join(title_directory, 'data.json')
# with open(data_file_path, 'w', encoding='utf-8') as data_file:
#     json.dump(data, data_file, ensure_ascii=False, indent=4)
# print(f"数据已保存到文件：{data_file_path}")

# for book in data["book_list"]:
#     content = get_content_from_url(book["href"])
#     file_name = "".join(char for char in book["title"] if char.isalnum() or char in (" ", ".", "_")).rstrip()
#     file_name = file_name if file_name else 'unknown_title'
#     file_path = os.path.join(title_directory, file_name + ".txt")
#     with open(file_path, 'w', encoding='utf-8') as f:
#         f.write(content)
#     print(f"内容已保存到文件：{file_path}")

def process_books(json_file):
    # 读取JSON文件内容
    with open(json_file, 'r', encoding='utf-8') as file:
        book_list = json.load(file)

    for book in book_list:
        data = get_data_from_url(book['href'])

        # 创建以书名命名的目录
        title_directory = "".join(char for char in data['title'] if char.isalnum() or char in (" ", ".", "_")).rstrip() if data['title'] else "book_data"
        if not os.path.exists(title_directory):
            os.makedirs(title_directory)

        # 将数据保存为JSON文件
        data_file_path = os.path.join(title_directory, 'data.json')
        with open(data_file_path, 'w', encoding='utf-8') as data_file:
            json.dump(data, data_file, ensure_ascii=False, indent=4)
        print(f"数据已保存到文件：{data_file_path}")

        # 遍历书籍列表并保存内容
        for book in data["book_list"]:
            content = get_content_from_url(book["href"])
            file_name = "".join(char for char in book["title"] if char.isalnum() or char in (" ", ".", "_")).rstrip()
            file_name = file_name if file_name else 'unknown_title'
            file_path = os.path.join(title_directory, file_name + ".txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"内容已保存到文件：{file_path}")

# 假设results2.json是您提供的JSON文件名
json_file = 'results2.json'
process_books(json_file)