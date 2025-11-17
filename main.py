import use
import selenium_a
import os

# --- 个性化信息和用户输入 ---

# 1. 获取用户输入

print("‘\’是没问题的。")
download_dir = input("选择下载路径：")
# download_dir = 'E:/爬虫！/test'
user_id = input('输入你要寻找的用户ID（@后文字）：')
# user_id = 'AjiuDemon'
print('取决于你要下的图片有多少，推荐全部媒体500内就设置40，多了就100。\n')
move_step = int(input('输入最大滚动次数：'))
father_class = ['r-18u37iz', 'r-9aw3ui']  #建议时常确认是否修改
# 其位于图片从下往上的第一个父类里的class值，从中随意选择两个作为定位。（别选css-）


# 2. WebDriver 路径配置（自动定位优先，手动指定作为备选）

print('\n--- WebDriver 路径配置 ---')
# 优先尝试自动定位

auto_driver_path = selenium_a.get_driver_path('msedgedriver.exe')

# 检查自动定位的路径是否存在

if os.path.exists(auto_driver_path):
    print(f"自动定位成功，使用路径: {auto_driver_path}")
    driver_path = auto_driver_path
else:
    print(f"自动定位的路径不存在: {auto_driver_path}")
    print('将使用手动指定的路径作为备选。')

    # 手动指定的路径（作为备选）

    manual_driver_path = ''

    if os.path.exists(manual_driver_path):
        print(f"✅ 使用手动指定路径: {manual_driver_path}")
        driver_path = manual_driver_path
    else:
        print(f"手动指定路径也不存在: {manual_driver_path}")
        print("路径需要带有最后的exe文件位置，同时 ‘\’是没问题的。")
        driver_path = input("请手动输入 Edge WebDriver (msedgedriver.exe) 的完整路径：")


# 3. 其他固定配置信息
print("请按照以下步骤配置认证信息：")
print("1. 登录 X (Twitter)")
print("2. 从浏览器 Cookie 获取 auth_token 的值。")
print("3. 在此输入（信息不会保存）")
cookies = input("请输入 auth_token: ").strip()   # 您的 Auth Token

url = 'https://x.com/' # 基础网址


# --- 启动程序 ---
if __name__ == '__main__':
    # 调用 use.py 中的函数，并将所有配置信息作为参数传递进去
    use.main_use(
        download_dir=download_dir,
        cookies=cookies,
        url=url,
        user_id=user_id,
        father_class=father_class,
        move_step=move_step,
        driver_path=driver_path,
    )
