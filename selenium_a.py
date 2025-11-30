import os
import sys
import time
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

PICTURE_CONTAINER_CLASS = 'css-175oi2r'


def get_driver_path(driver_filename='msedgedriver.exe'):
    """
    【自动路径定位函数】
    根据程序运行环境（普通Python脚本或PyInstaller打包的EXE）
    智能确定 WebDriver 的绝对路径。

    定位策略：
    1. 正常运行：与当前脚本文件 (selenium_a.py) **同目录**。
    2. 打包后（--onefile模式）：
       - 优先检查临时解压目录 (sys._MEIPASS) - WebDriver被打包进去的情况
       - 备选检查EXE文件所在目录 - WebDriver放在EXE旁边的情况

    返回：
        str: WebDriver 的完整路径（优先返回存在的路径）
    """
    # 检查是否在 PyInstaller 创建的临时环境中运行
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 EXE
        # 策略1：检查临时解压目录（--onefile模式下，打包的文件在这里）
        temp_path = os.path.join(sys._MEIPASS, driver_filename)
        if os.path.exists(temp_path):
            print(f"WebDriver 尝试路径（临时目录）: {temp_path}")
            return temp_path

        # 策略2：检查EXE文件所在目录（用户可能将WebDriver放在EXE旁边）
        exe_dir = os.path.dirname(sys.executable)
        exe_path = os.path.join(exe_dir, driver_filename)
        if os.path.exists(exe_path):
            print(f"WebDriver 尝试路径（EXE目录）: {exe_path}")
            return exe_path

        # 如果都不存在，返回临时目录的路径（让调用方处理错误）
        print(f"WebDriver 尝试路径（临时目录，可能不存在）: {temp_path}")
        return temp_path
    else:
        # 如果是普通脚本运行，使用当前脚本文件所在的目录
        # (os.path.abspath(__file__) 获取当前脚本的绝对路径)
        base_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_path, driver_filename)
        print(f"WebDriver 尝试路径: {full_path}")
        return full_path


# --- 动态路径构建逻辑结束 ---
def visit_edge(download_dir, driver_path):
    """
    【原有索引方式说明】
    本函数仍然接受 driver_path 参数，保持向后兼容性。

    使用方式：
    1. 自动定位方式（推荐）：
       driver_path = get_driver_path('msedgedriver.exe')
       driver = visit_edge(download_dir, driver_path)

    2. 手动指定路径方式（仍支持）：
       driver = visit_edge(download_dir, 'C:\\path\\to\\msedgedriver.exe')

    这样设计的好处：
    - 将路径生成的责任与使用路径的责任分离
    - 保持函数的灵活性，可以接受任意路径
    - 兼容旧代码，无需修改所有调用处
    """
    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"WebDriver文件未找到。请检查路径是否正确: {driver_path}")
    edge_options = webdriver.EdgeOptions()
    # 添加参数，禁用所有扩展程序
    edge_options.add_argument("--disable-extensions")
    # 禁用 GPU 加速
    edge_options.add_argument("--disable-gpu")
    # 解决打包后的兼容性问题
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    # 解决 SSL 错误：忽略证书错误（仅用于打包环境）
    edge_options.add_argument("--ignore-certificate-errors")
    edge_options.add_argument("--ignore-ssl-errors")
    edge_options.add_argument("--allow-insecure-localhost")

    # 无头浏览器模式 ———— 调试的时候记得关掉。

    edge_options.add_argument("--headless")

    prefs = {
        'download.default_directory': download_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    }
    edge_options.add_experimental_option('prefs', prefs)
    # 禁用证书验证（用于解决 SSL 握手问题）
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    edge_service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=edge_service, options=edge_options)
    return driver


def visit_x(driver, cookies, url, user_id):
    try:
        driver.get(url)
        cookies_dict = {
            'name': 'auth_token',
            'value': cookies,
            'domain': '.x.com',
            'path': '/',
            'secure': True,
            'httpOnly': True
        }
        driver.add_cookie(cookies_dict)
        print("Cookie 注入成功，尝试以登录状态访问")

        driver.get(f'{url}{user_id}/media')
        driver.maximize_window()

    except Exception as e:
        print(e)


def move(driver, scroll_distance, scroll_delay):
    """
    【滚动模块】
    执行一次相对滚动，向下滚动指定的像素距离。
    """
    current_scroll_position = driver.execute_script("return window.pageYOffset;")
    new_scroll_position = current_scroll_position + scroll_distance

    driver.execute_script(f"window.scrollTo(0, {new_scroll_position});")
    print(f"   执行滚动: 向下滚动 {scroll_distance} 像素。")
    time.sleep(scroll_delay)


def get_new_content_containers(driver, father_class):
    """
    【寻找内容容器模块】
    查找并返回所有当前可见的、包含图片行的特定 DIV 容器元素。
    使用多个 class 片段进行更鲁棒的定位。
    """
    wait = WebDriverWait(driver, 10)

    # 动态构建 XPath 表达式，要求同时包含所有片段
    # 示例结果：//div[contains(@class, 'r-18u37iz') and contains(@class, 'r-9aw3ui')]
    xpath_conditions = [f"contains(@class, '{fragment}')" for fragment in father_class]
    container_selector = f'//div[{" and ".join(xpath_conditions)}]'

    try:
        # 查找所有可见的容器元素
        content_containers = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, container_selector)),
            f"等待内容容器加载超时，使用选择器: {container_selector}"
        )
        return content_containers
    except TimeoutException:
        print("未找到新的内容容器。")
        return []


def get_visible_thumbnails(parent_element):
    """
    【寻找图片模块】
    查找并返回当前屏幕上所有可见的略缩图元素。
    """
    catch_pic_selector = 'img[src*="media/"]'

    try:
        # 使用父元素的 find_elements 方法在局部范围内查找
        get_small_ones = parent_element.find_elements(By.CSS_SELECTOR, catch_pic_selector)
        return get_small_ones
    except Exception as e:
        print(f"在父元素中查找略缩图失败: {e}")
        return []


def _get_next_button(driver):
    """
    尝试定位模态框中的"下一页"按钮。
    """
    # 已确认按钮名称，直接查找
    next_btn_xpath = '//button[@aria-label="下一张幻灯片"]'
    try:
        button = driver.find_element(By.XPATH, next_btn_xpath)
        # 直接返回，不检查is_displayed()以节省时间
        return button
    except NoSuchElementException:
        return None


def _find_large_image_by_src(driver):
    """
    查找所有img元素，找到包含正确src的图片（不限制displayed状态）。
    优化：使用CSS选择器直接过滤，减少遍历时间。
    """
    try:
        # 使用CSS选择器先过滤，只查找src包含pbs.twimg.com/media的图片
        candidate_imgs = driver.find_elements(By.CSS_SELECTOR, 'img[src*="pbs.twimg.com/media"]')
        for img in candidate_imgs:
            try:
                alt = img.get_attribute("alt") or ""
                # 只检查alt属性，src已经在选择器中过滤了
                if "图像" in alt:
                    return img
            except:
                continue
        return None
    except:
        return None


def _find_all_large_images(driver):
    """
    查找所有符合条件的img元素（不限制displayed状态），返回列表。
    优化：使用CSS选择器直接过滤，减少遍历时间。
    """
    result = []
    try:
        # 先使用CSS选择器过滤，减少需要检查的元素数量
        # 查找src包含pbs.twimg.com/media的img元素
        candidate_imgs = driver.find_elements(By.CSS_SELECTOR, 'img[src*="pbs.twimg.com/media"]')
        for img in candidate_imgs:
            try:
                alt = img.get_attribute("alt") or ""
                # 只检查alt属性，src已经在选择器中过滤了
                if "图像" in alt:
                    result.append(img)
            except:
                continue
        return result
    except:
        return []


def _wait_for_src_change(driver, old_url):
    """
    等待大图元素的 src 属性发生变化，表示图片已成功切换。
    优化：减少等待时间，使用更短的轮询间隔。
    """

    # 定义一个自定义的等待条件函数
    def src_has_changed(driver):
        try:
            # 查找所有符合条件的img元素
            all_matching_imgs = _find_all_large_images(driver)
            if not all_matching_imgs:
                return False

            # 遍历所有图片，找到src不等于old_url的那个（新切换的图片）
            for img in all_matching_imgs:
                try:
                    new_url = img.get_attribute("src")
                    # 如果新URL存在且不等于旧URL，则切换成功
                    if new_url and new_url != old_url:
                        return img
                except:
                    continue
            return False
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    # 使用较短的等待时间，因为图片切换通常很快
    wait = WebDriverWait(driver, 8, poll_frequency=0.2)  # 每0.2秒检查一次，最多8秒
    try:
        # 等待自定义条件满足
        new_img = wait.until(src_has_changed, "等待图片切换超时")
        return new_img
    except TimeoutException:
        # 如果超时，快速再检查一次
        try:
            all_matching_imgs = _find_all_large_images(driver)
            for img in all_matching_imgs:
                try:
                    new_url = img.get_attribute("src")
                    if new_url and new_url != old_url:
                        return img
                except:
                    continue
        except:
            pass
        return None


def extract_large_url(driver, small_one):
    """
    【获取大图模块 - 用户的 get_pic 逻辑】
    点击略缩图，获取大图 URL，并关闭模态框。
    【主要修改】：新增循环逻辑，点击"下一页"获取推文中所有图片的 URL。
    """
    wait = WebDriverWait(driver, 20)

    # 用于存储所有图片 URL 的集合
    image_urls = set()

    try:
        # a. 点击略缩图，打开模态框
        small_one.click()

        # b. 使用显式等待查找第一张大图，比固定等待更快
        get_large_one = None
        try:
            # 使用显式等待，最多等待3秒，每0.2秒检查一次
            wait_short = WebDriverWait(driver, 3, poll_frequency=0.2)
            # 等待至少有一个符合条件的图片出现
            wait_short.until(lambda d: _find_large_image_by_src(d) is not None, "等待大图出现")
            get_large_one = _find_large_image_by_src(driver)
        except TimeoutException:
            # 如果3秒内没找到，再快速尝试几次
            for attempt in range(3):
                time.sleep(0.3)
                get_large_one = _find_large_image_by_src(driver)
                if get_large_one:
                    break

        if not get_large_one:
            raise Exception("无法找到大图元素")

        # c. **核心循环逻辑开始**

        # 记录当前 URL，用于后续判断是否已切换
        current_url = get_large_one.get_attribute("src")
        image_urls.add(current_url)
        print(f"   已获取第一张图 URL: {current_url}")

        # 短暂等待，确保按钮已渲染（减少等待时间）
        time.sleep(0.3)

        # 循环，直到无法找到下一张按钮或图片不再切换
        while True:
            # 1. 尝试定位"下一页"按钮
            next_button = _get_next_button(driver)

            # 如果没有下一页按钮，则退出循环（单图或已是最后一张）
            if not next_button:
                print("   未找到下一页按钮，或已到最后一张。")
                break

            # 2. 点击下一页按钮
            try:
                next_button.click()
                time.sleep(0.2)  # 减少等待时间，图片切换通常很快
            except Exception as e:
                # 按钮不可点击等异常，也退出循环
                print(f"   点击下一页按钮失败，退出循环: {e}")
                break

            # 3. 等待图片切换（核心：等待 src 属性变化）
            next_img_element = _wait_for_src_change(driver, current_url)

            if next_img_element:
                new_url = next_img_element.get_attribute("src")
                if new_url in image_urls:
                    # 如果新 URL 已经在集合中（如回到第一张），则停止
                    print("   检测到 URL 重复，已完成遍历。")
                    break

                image_urls.add(new_url)
                current_url = new_url  # 更新当前 URL
                print(f"   已获取下一张图 URL: {new_url}")
            else:
                # 等待超时，可能加载失败或没有更多图片
                print("   等待新图片加载超时，退出循环。")
                break

        # d. 关闭模态框
        close(driver)
        time.sleep(0.2)  # 减少等待时间
        # e. 返回所有 URL 的集合
        return image_urls
    except Exception as e:
        # 如果等待超时 (TimeoutException) 或其他失败
        print(f"提取大图 URL 过程失败: {e}")
        # 尝试关闭模态框以防万一
        try:
            close(driver)
        except:
            pass  # 可能是超时失败，模态框根本没开
        # 返回一个特殊的标识符，让调用方知道这是一个被忽略的项目
        # 注意：现在返回的是一个包含错误标识符的集合
        return {'VIDEO_OR_FAIL'}


def close(driver):
    wait = WebDriverWait(driver, 20)
    close_btn = '//button[@aria-label="关闭"]'
    wait.until(
        EC.element_to_be_clickable((By.XPATH, close_btn)),
        "等待关闭"
    ).click()
