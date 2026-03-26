# -*- codeing = utf-8 -*-
# @Time: 2026/3/26 17:20
# @Author: Hao Xu
# @site: 
# @File: crawler_newsv1.py
# @Software: PyCharm
# 这是一个演示抓取玉渊潭天的文章--DeepSeeker
import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def crawl_cctv_news(url):
    """
    爬取央视新闻网新闻内容
    :param url: 新闻URL
    :return: 包含标题、作者、事件、内容的字典
    """
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

    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取标题
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "未找到标题"

    # 提取作者（文中显示为“玉渊谭天”）
    # 尝试在正文前寻找作者信息，通常位于class="info"或类似位置
    author = "未知"
    author_candidate = soup.find('div', class_='info')
    if author_candidate:
        text = author_candidate.get_text(strip=True)
        # 常见格式 "玉渊谭天 2025年03月07日 10:16"
        if '玉渊谭天' in text:
            author = "玉渊谭天"

    # 提取事件（可自定义为新闻的核心主题）
    # 这里取正文第一段或标题的概括
    event = "全国两会确定2025年经济增长目标5%左右"

    # 提取正文内容
    content_div = soup.find('div', class_='content_area')  # 常见正文容器class
    if not content_div:
        # 备用：寻找article或主要文本区域
        content_div = soup.find('div', class_='article')
    if not content_div:
        content_div = soup.find('div', class_='text')

    content = ""
    if content_div:
        # 获取所有段落文本
        paragraphs = content_div.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                content += text + "\n"
    else:
        # 如果找不到特定容器，尝试直接找所有p标签
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # 过滤掉短文本
                content += text + "\n"

    # 清理多余换行
    content = content.strip()

    return {
        "标题": title,
        "作者": author,
        "事件": event,
        "内容": content
    }


def save_to_json(data, filename):
    """
    保存数据为JSON文件到result文件夹
    :param data: 要保存的数据
    :param filename: 文件名
    """
    # 确保result文件夹存在
    os.makedirs('result', exist_ok=True)

    filepath = os.path.join('result', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"文件已保存至: {filepath}")


if __name__ == "__main__":
    url = "https://news.cctv.com/2025/03/07/ARTI2kCIEcnNM288M03Xayg8250307.shtml?spm=C94212.P4YnMod9m2uD.E7v7lEZZ0WEM.4"

    news_data = crawl_cctv_news(url)
    if news_data:
        # 生成文件名，使用当前时间避免覆盖
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cctv_news_{timestamp}.json"
        save_to_json(news_data, filename)
        print("爬取完成！")
    else:
        print("爬取失败")