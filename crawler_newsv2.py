# 这份代码是针对CCTV网页的JavaScript动态渲染问题进行了修复
# 使用模拟人类浏览网页的模式
# 爬取https://news.cctv.com/2026/03/24/ARTIzVjHbV9milFZx0tFUisk260324.shtml内容
"""
CCTV新闻爬虫 - 解决JavaScript动态渲染问题

问题：requests只获取初始HTML，文章正文通过JavaScript动态加载
解决：使用Playwright模拟浏览器，执行JavaScript后再提取内容

安装方法：
pip install playwright
playwright install chromium
"""

import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright


def crawl_cctv_news(url, timeout=30000):
    """
    爬取CCTV新闻页面（支持JavaScript渲染）

    Args:
        url: 新闻页面URL
        timeout: 超时时间（毫秒），默认30秒

    Returns:
        dict: 包含标题、来源、日期、内容等字段的字典
    """
    result = {
        "标题": "",
        "来源": "",
        "日期": "",
        "内容": "",
        "字数统计": 0,
        "爬取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "状态": "失败"
    }

    with sync_playwright() as p:
        # 启动Chromium浏览器（无头模式：headless=True）
        browser = p.chromium.launch(headless=True)
        # 创建新页面
        page = browser.new_page()

        try:
            print(f"正在访问: {url}")

            # 导航到目标URL，等待网络空闲
            page.goto(url, wait_until='networkidle', timeout=timeout)

            # 等待内容区域加载完成
            page.wait_for_selector('div.content_area', timeout=10000)
            print("页面加载完成！")

            # ============ 提取标题 ============
            if page.locator('h1').count() > 0:
                result["标题"] = page.locator('h1').inner_text().strip()
            else:
                # 备用：提取title标签
                result["标题"] = page.title().replace('_新闻频道_央视网(cctv.com)', '').strip()

            # ============ 提取来源 ============
            # 方法1：尝试从 .info span 或 .source 中提取
            source_selectors = [
                '.info .f_other',
                '.source',
                '.post_source',
                '.article-src'
            ]
            for selector in source_selectors:
                if page.locator(selector).count() > 0:
                    result["来源"] = page.locator(selector).first.inner_text().strip()
                    break

            if not result["来源"]:
                result["来源"] = "央视网"

            # ============ 提取日期 ============
            date_selectors = [
                '.info span',
                '.time',
                '.publish_time',
                '.article-time'
            ]
            for selector in date_selectors:
                if page.locator(selector).count() > 0:
                    date_text = page.locator(selector).first.inner_text().strip()
                    # 提取日期部分
                    date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)', date_text)
                    if date_match:
                        result["日期"] = date_match.group(1)
                        break

            # ============ 提取正文内容 ============
            content_div = page.locator('div.content_area')

            # 获取所有段落
            paragraphs = content_div.locator('p').all()

            content_list = []
            for p in paragraphs:
                text = p.inner_text().strip()
                # 过滤掉空白内容和加载提示
                if text and '正在加载' not in text and len(text) > 10:
                    content_list.append(text)

            result["内容"] = '\n\n'.join(content_list)
            result["字数统计"] = len(result["内容"])
            result["状态"] = "成功"

            print(f"标题: {result['标题']}")
            print(f"来源: {result['来源']}")
            print(f"字数: {result['字数统计']}")

        except Exception as e:
            result["状态"] = f"失败: {str(e)}"
            print(f"错误: {e}")

        finally:
            browser.close()

    return result


def save_to_json(data, filename='result/news_data.json'):
    """保存数据到JSON文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✓ 文件已保存: {filename}")


def main():
    """主函数"""
    print("=" * 60)
    print("CCTV新闻爬虫（Playwright版）")
    print("=" * 60)

    # 测试URL
    url = "https://news.cctv.com/2026/03/24/ARTIzVjHbV9milFZx0tFUisk260324.shtml"

    print(f"\n目标: {url}\n")

    # 执行爬取
    news_data = crawl_cctv_news(url)

    # 保存结果
    if news_data["状态"] == "成功":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result/cctv_news_{timestamp}.json"
        save_to_json(news_data, filename)

        # 打印内容预览
        print("\n" + "-" * 60)
        print("内容预览（前1000字）:")
        print("-" * 60)
        print(news_data["内容"][:1000])
        if len(news_data["内容"]) > 1000:
            print("\n...（内容过长已截断）")
        print("-" * 60)
    else:
        print(f"\n✗ 爬取失败: {news_data['状态']}")


if __name__ == "__main__":
    main()