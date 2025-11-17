import selenium_a
import download

def main_use(download_dir, cookies, url, user_id, father_class, move_step, driver_path):

    """
        运行图片爬取器的主逻辑。

        Args:
            download_dir (str): 图片下载路径。
            cookies (str): 登录所需的 auth_token。
            url (str): 基础网址。
            user_id (str): 用户的 ID。
            father_class: 图片最后所属父类，其Class值的提取
            move_step: 最大滚动次数
    """
    # 调用 selenium.py 中的函数来创建并返回 driver
    driver = selenium_a.visit_edge(download_dir, driver_path)
    print("Driver初始化成功。")

    # 2. 访问并注入 Cookie (传递 driver)
    print("--- 登录和访问用户页 ---")
    selenium_a.visit_x(driver, cookies, url, user_id)
    print("已访问用户媒体页。")

    # --- 核心滚动和提取循环 ---
    all_final_urls = []
    seen_thumbnail_urls = set()  # 存储已处理的略缩图 URL，用于去重
    seen_container_ids = set()
    max_scrolls = move_step  # 最大滚动次数，防止无限循环
    consecutive_no_new_images_limit = 5  # 连续多少次未找到新图片则停止
    consecutive_no_new_images = 0
    total_containers_scanned = 0
    total_containers_skipped = 0
    total_thumbnails_scanned = 0
    total_thumbnails_skipped_by_dedupe = 0
    total_thumbnails_failed_to_extract = 0
    scroll_count = 0

    print("--- 启动模块化滚动和提取循环 ---")

    for scroll_count in range(max_scrolls):
        print(f"\n--- 滚动循环 {scroll_count + 1} / {max_scrolls} ---")

        # 1. 调用 【寻找图片模块】 获取所有可见的元素
        all_container = selenium_a.get_new_content_containers(driver, father_class)
        print(f"当前可见 {len(all_container)} 个内容容器。")

        new_images_found_in_scroll = 0
        new_containers_processed = 0
        total_containers_scanned += len(all_container)
        # 2. 遍历并提取未处理的图片 URL
        for container in all_container:
            container_id = container.id

            if container_id not in seen_container_ids:
                seen_container_ids.add(container_id)
                new_containers_processed += 1
                print(f'发现并处理新容器 ID:{container_id}')

                find_one = selenium_a.get_visible_thumbnails(container)
                print(f"      容器内找到 {len(find_one)} 个略缩图。")
                total_thumbnails_scanned += len(find_one)

                for element in find_one:
                    try:
                        final_url = element.get_attribute('src')
                    except Exception as e:
                        total_thumbnails_failed_to_extract += 1
                        print(f"      获取略缩图 URL 失败: {e}")
                        continue


                    if final_url not in seen_thumbnail_urls:

                        large_urls = selenium_a.extract_large_url(driver, element)

                        seen_thumbnail_urls.add(final_url)

                        if large_urls and 'VIDEO_OR_FAIL' not in large_urls:
                            # 【修改】extract_large_url 现在返回一个集合，包含所有图片URL
                            # 将集合中的所有URL添加到列表中
                            for url in large_urls:
                                all_final_urls.append(url)
                            new_images_found_in_scroll += len(large_urls)
                        else:
                            # 【更新】大图 URL 提取失败（在 extract_large_url 内发生的错误）
                            total_thumbnails_failed_to_extract += 1

                    else:
                        #【更新】因去重而跳过（已处理过的旧图片）
                        total_thumbnails_skipped_by_dedupe += 1
            else:
                # 【更新】容器因已处理而跳过（旧容器）
                total_containers_skipped += 1
        # 5. 检查停止条件
        if new_images_found_in_scroll == 0:
            consecutive_no_new_images += 1
            print(f"   本次循环未找到新的 URL。连续 {consecutive_no_new_images} 次。")
            if consecutive_no_new_images >= consecutive_no_new_images_limit:
                print("🛑 连续多次未找到新内容，停止滚动。")
                break
        else:
            consecutive_no_new_images = 0

        print(f"   新处理容器数量: {new_containers_processed}")
        print(f"   本次循环新增 URL 数量: {new_images_found_in_scroll}")
        print(f"   当前已提取总 URL 数量: {len(all_final_urls)}")

        # 6. 调用 【滚动模块】
        selenium_a.move(driver, scroll_distance=500, scroll_delay=2)

    print(f"--- 循环结束。总共找到 {len(all_final_urls)} 个图片 URL。---")

    print("\n=======================================================")
    print("                  抓取统计总结                    ")
    print("=======================================================")
    print(f"总滚动次数: {scroll_count + 1} / {max_scrolls}")
    print("--- 容器统计 ---")
    print(f"总共扫描到的容器元素数量: {total_containers_scanned}")
    print(f"因已处理（旧内容）而跳过的容器数量: {total_containers_skipped}")
    print("--- 略缩图统计 ---")
    print(f"总共扫描到的略缩图元素数量: {total_thumbnails_scanned}")
    print(f"因去重而跳过的略缩图数量 (旧图片): {total_thumbnails_skipped_by_dedupe}")
    print(f"因提取大图 URL 失败而跳过的图片数量: {total_thumbnails_failed_to_extract}")
    print("--- 结果统计 ---")
    print(f"✅ 成功提取的图片 URL 总数: {len(all_final_urls)}")
    print("=======================================================")

    # 3. 爬取图片 (传递 driver)
    print("--- 抓取图片大图 URL ---")
    fin_pic = all_final_urls

    print("--- 下载图片到本地 ---")
    download.download_main(fin_pic, download_dir)

    print(input('——————   一切顺利，请按回车键退出程序   ——————'))
    # 4. 关闭浏览器
    driver.quit()
    print("浏览器已关闭。程序结束。")