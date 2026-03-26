# -*- codeing = utf-8 -*-
# @Time: 2026/3/26 17:43
# @Author: Hao Xu
# @site: 
# @File: crawler_newsv3.py
# @Software: PyCharm
# 这是判断网页内容后，根据提示词修改后得到爬取代码
import os
import json
import re
import html
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def clean_html_entities(text):
    """解码HTML实体"""
    return html.unescape(text)


def extract_contentdate(html_text):
    """从HTML源码中提取contentdate变量的内容"""
    # 匹配 var contentdate = '...' 的内容（支持跨行和转义字符）
    pattern = r'var contentdate\s*=\s*\'([\s\S]*?)\';'
    match = re.search(pattern, html_text)
    if match:
        content_html = match.group(1)
        # 处理转义字符
        content_html = content_html.replace('\\\'', "'")  # 转义的单引号
        content_html = content_html.replace('\\"', '"')  # 转义的双引号
        content_html = content_html.replace('\\\\', '\\')  # 转义的反斜杠
        # 解码HTML实体
        content_html = clean_html_entities(content_html)
        return content_html
    return None


def extract_paragraphs_from_html(html_fragment):
    """从HTML片段中提取所有段落文本和图片信息"""
    soup = BeautifulSoup(html_fragment, 'html.parser')

    # 提取所有段落
    paragraphs = []
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        # 过滤掉视频占位标记
        if text and not re.match(r'\[!--begin:htmlVideoCode--\].*\[!--end:htmlVideoCode--\]', text):
            # 清理多余的空白和换行
            clean_text = re.sub(r'\s+', ' ', text).strip()
            if clean_text:
                paragraphs.append(clean_text)

    # 提取图片
    images = []
    for img in soup.find_all('img'):
        # 优先使用src，否则使用data-img
        src = img.get('src') or img.get('data-img')
        if src and src.startswith('//'):
            src = 'https:' + src
        if src:
            images.append({
                'src': src,
                'alt': img.get('alt', '')
            })

    return paragraphs, images


def crawl_boao_news(url):
    """爬取博鳌新闻内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None

    html_text = response.text
    soup = BeautifulSoup(html_text, 'html.parser')

    # 1. 提取标题
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "未找到标题"

    # 2. 提取来源和发布时间
    source = "央视网"
    publish_time = ""
    info_div = soup.find('div', class_='info') or soup.find('div', class_='info1')
    if info_div:
        info_text = info_div.get_text(strip=True)
        # 格式类似 "来源：央视网  |  2026年03月24日 14:36:49"
        parts = info_text.split('|')
        for part in parts:
            if '来源' in part:
                source = part.replace('来源：', '').strip()
            elif '年' in part and '月' in part and '日' in part:
                publish_time = part.strip()

    # 3. 提取编辑和责任编辑
    editor = ""
    responsible_editor = ""
    zebian_div = soup.find('div', class_='zebian')
    if zebian_div:
        spans = zebian_div.find_all('span')
        for span in spans:
            text = span.get_text(strip=True)
            if '编辑' in text and not '责任编辑' in text:
                editor = text.replace('编辑：', '').strip()
            elif '责任编辑' in text:
                responsible_editor = text.replace('责任编辑：', '').strip()

    # 4. 提取正文（从contentdate变量）
    content_html = extract_contentdate(html_text)
    if not content_html:
        print("未找到contentdate变量")
        return None

    # 5. 解析正文HTML片段
    paragraphs, images = extract_paragraphs_from_html(content_html)

    # 6. 构建最终内容
    content = '\n\n'.join(paragraphs)

    # 7. 构建结果字典
    result = {
        "title": title,
        "source": source,
        "publish_time": publish_time,
        "editor": editor,
        "responsible_editor": responsible_editor,
        "content": content,
        "images": images,
        "url": url,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return result


def save_results(result, base_filename):
    """保存结果为JSON和TXT文件"""
    # 创建result文件夹
    os.makedirs('result', exist_ok=True)

    # 保存JSON
    json_path = os.path.join('result', f"{base_filename}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print(f"JSON文件已保存至: {json_path}")

    # 保存TXT（格式化文本）
    txt_path = os.path.join('result', f"{base_filename}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"标题：{result['title']}\n")
        f.write(f"来源：{result['source']}\n")
        f.write(f"发布时间：{result['publish_time']}\n")
        f.write(f"编辑：{result['editor']}\n")
        f.write(f"责任编辑：{result['responsible_editor']}\n")
        f.write(f"URL：{result['url']}\n")
        f.write(f"爬取时间：{result['crawl_time']}\n")
        f.write("\n" + "=" * 50 + "\n")
        f.write("正文：\n")
        f.write(result['content'])
        if result['images']:
            f.write("\n\n" + "=" * 50 + "\n")
            f.write("图片列表：\n")
            for idx, img in enumerate(result['images'], 1):
                f.write(f"{idx}. {img['src']}")
                if img['alt']:
                    f.write(f" ({img['alt']})")
                f.write("\n")
    print(f"TXT文件已保存至: {txt_path}")


if __name__ == "__main__":
    # 使用用户提供的新URL
    url = "https://news.cctv.com/2026/03/24/ARTIjsRnrU3x4d6MhufNGzJl260324.shtml"

    print("正在爬取博鳌新闻...")
    result = crawl_boao_news(url)

    if result:
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"boao_news_{timestamp}"
        save_results(result, filename)

        print(f"\n爬取完成！")
        print(f"标题: {result['title']}")
        print(f"来源: {result['source']}")
        print(f"发布时间: {result['publish_time']}")
        print(f"内容长度: {len(result['content'])} 字符")
        print(f"图片数量: {len(result['images'])}")
        if result['content']:
            print(f"\n内容预览:\n{result['content'][:300]}...")
    else:
        print("爬取失败")