import requests
import re
from bs4 import BeautifulSoup
import os
from datetime import datetime
import json
import time


data = {}
config = {}


def dump_post_info(data_file,post_info):
    global data
    post_id = post_info['post_id']
    if not data.get(post_id):
        data[post_id] = post_info
        with open(data_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

def load_post_info(data_file):
    global data
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)



def get_page_list(home_page):
    pattern = r'Showing \d+ - \d+ of (\d+)'
    rsp = requests.get(home_page)
    match = re.search(pattern, rsp.text)
    if match:
        result = match.group(1)
        print(result)
    else:
        print("未找到匹配的字符串")
        return None
    
    o = 50
    page_list = [f'{home_page}']
    while o < int(result):
        page_list.append(f'{home_page}?o={o}')
        o += 50
    print(page_list)
    return page_list

def get_post_list(page_list):
    global config
    if page_list is None or len(page_list) == 0:
        print('page list error')
    
    post_list = []
    pattern = r'< \d+ - \d+ of (\d+)'
    for page_url in page_list:
        rsp = requests.get(page_url)
        if rsp.status_code != 200:
            print(f'get {page_url} error')
        else:
            text = rsp.text
            soup = BeautifulSoup(text, 'html.parser')
            while True:
                # 查找符合条件的 article 标签
                article_tag = soup.find('article')
                if article_tag:
                # 在 article 标签内查找 a 标签
                    a_tag = article_tag.find('a')
                    if a_tag:
                        href_value = a_tag.get('href')
                        print(href_value)
                        post_list.append(f'https://{config["coomer"]}{href_value}')
                        article_tag.decompose()
                else:
                    break
        print(f'Done for {page_url}')
    return post_list

def parse_page(page_url):
    post_id = page_url.split('/')[-1]
    post_info = {'is_video': False, 'is_img': False, 'video_links':[], 'img_links':[],'parse_is_OK': False}
    post_info['post_id'] = post_id

    rsp = requests.get(page_url)
    if rsp.status_code == 200:
        html = rsp.text
        soup = BeautifulSoup(html, 'html.parser')
        title_span = soup.find('h1').find('span')
        post_info['title'] = title_span.get_text(strip=True)

        content_tag = soup.find('div', class_='post__content')
        if content_tag:
            pre_tag = content_tag.find('pre')
            post_info['content'] = pre_tag.get_text(strip=True)
        else:
            post_info['content'] = ''
        
        h2_all = soup.find_all('h2')
        for h2 in h2_all:
            if h2.get_text(strip=True) == 'Videos':
                post_info['is_video'] = True
            if h2.get_text(strip=True) == 'Files':
                post_info['is_img'] = True

        if post_info['is_video']:
            a_tag_videos = soup.find_all('a', class_="post__attachment-link")
            if a_tag_videos:
                for a in a_tag_videos:
                    post_info['video_links'].append(a.get('href'))
        if post_info['is_img']:
            a_tag_imgs = soup.find_all('a', class_="fileThumb")
            if a_tag_imgs:
                for a in a_tag_imgs:
                    post_info['img_links'].append(a.get('href'))
        post_info['parse_is_OK'] = True
    else:
        print(f'get failed for {page_url}')
        post_info['parse_is_OK'] = False
    
    return post_info

def download_post(post_info, base_path):
    flag = True
    readme_content = f'''
## Content
{post_info['content']}

## imgs
'''
    post_path = os.path.join(base_path, f"{post_info['post_id']}")
    video_path = os.path.join(post_path, 'videos') if post_info['is_video'] else None
    img_path = os.path.join(post_path, 'imgs') if post_info['is_img'] else None
    if not os.path.exists(post_path):
        os.makedirs(post_path)  # 创建主目录

    if video_path:
        if not os.path.exists(video_path):
            os.makedirs(video_path)  # 创建视频目录

        # 下载视频链接
        for index, video_link in enumerate(post_info['video_links']):
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            video_filename = f"video_{index + 1}_{timestamp_str}.mp4"
            video_filepath = os.path.join(video_path, video_filename)
            flag = download_file(video_link, video_filepath)

    if img_path:
        if not os.path.exists(img_path):
            os.makedirs(img_path)  # 创建图片目录

        # 下载图片链接
        for index, img_link in enumerate(post_info['img_links']):
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            img_filename = f"img_{index + 1}_{timestamp_str}.jpg"
            img_filepath = os.path.join(img_path, img_filename)
            flag = download_file(img_link, img_filepath)
            readme_content += f'\n![](./imgs/{img_filename})\n'
    with open(f'{post_path}/README.md', 'w', encoding='utf-8') as readme:
        readme.write(readme_content)
    time.sleep(10)

    return flag

def download_file(url, filepath):
    try:
        # 发起请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 以二进制写入文件
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Downloaded {url} to {filepath}")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False
    

def start_download(cfg):
    global config, data 
    config = cfg
    for username in cfg['user_name']:
        home_page = f"https://{cfg['coomer']}/{cfg['service']}/user/{username}"
        load_post_info(f'{username}.json')
        page_list = get_page_list(home_page)
        post_list = get_post_list(page_list)
        for post in post_list:
            print(f"parse {post}")
            post_info = parse_page(post)
            if not data.get(post_info.get('post_id')):
                if download_post(post_info, f'./Downloads/{username}'):
                    dump_post_info(f'{username}.json',post_info)
            else:
                print(f'{post_info.get("post_id")} has been download')
                


    
