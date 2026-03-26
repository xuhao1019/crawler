import os
import json
import glob


def print_json_content(filepath, show_filename=False):
    """读取 JSON 文件并打印内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if show_filename:
            print(f"\n文件: {os.path.basename(filepath)}")
        print("=" * 50)
        print("【标题】", data.get("标题", "无"))
        print("-" * 50)
        print("【作者】", data.get("作者", "无"))
        print("-" * 50)
        print("【事件】", data.get("事件", "无"))
        print("-" * 50)
        print("【内容】")
        print(data.get("内容", "无"))
        print("=" * 50)
    except Exception as e:
        print(f"读取文件失败: {e}")


def print_all_json():
    """打印 result 文件夹下所有 JSON 文件"""
    json_files = glob.glob("result/*.json")
    if not json_files:
        print("result 文件夹中没有找到 JSON 文件。")
        return
    for file in json_files:
        print_json_content(file, show_filename=True)


def print_latest_json():
    """打印最新生成的 JSON 文件"""
    json_files = glob.glob("result/*.json")
    if not json_files:
        print("result 文件夹中没有找到 JSON 文件。")
        return
    latest_file = max(json_files, key=os.path.getmtime)
    print(f"正在读取最新文件: {latest_file}\n")
    print_json_content(latest_file)


def print_specific_json(filename):
    """打印指定的 JSON 文件"""
    filepath = os.path.join("result", filename)
    if os.path.exists(filepath):
        print_json_content(filepath)
    else:
        print(f"文件不存在: {filepath}")


if __name__ == "__main__":
    print("请选择操作：")
    print("1 - 打印所有 JSON 文件")
    print("2 - 打印最新 JSON 文件")
    print("3 - 打印特定 JSON 文件")

    choice = input("请输入数字 (1/2/3): ").strip()

    if choice == '1':
        print_all_json()
    elif choice == '2':
        print_latest_json()
    elif choice == '3':
        filename = input("请输入文件名（如 cctv_news_20250326_123456.json）: ").strip()
        print_specific_json(filename)
    else:
        print("无效选择，程序退出。")