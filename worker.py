import time
from PyQt6.QtCore import QThread, pyqtSignal
import use
import selenium_a


class CrawlerThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)  # 进度百分比
    stage_signal = pyqtSignal(str)  # 当前阶段描述

    def __init__(self, path, user, move_step, auth_token, father_class, headless = True):
        super().__init__()
        self.download_dir = path
        self.user_id = user
        self.move_step = move_step
        self.auth_token = auth_token
        self.father_class = father_class
        self.headless = headless

    def run(self):
        try:
            self.stage_signal.emit('初始化环境中...')
            self.progress_signal.emit(10)

            self.stage_signal.emit('准备浏览器驱动中...')
            self.progress_signal.emit(20)
            time.sleep(1)

            self.stage_signal.emit('访问目标界面中...')
            self.progress_signal.emit(30)
            time.sleep(1)

            self.stage_signal.emit('查找并且获取图片中...')
            self.progress_signal.emit(40)

            # 使用传入的参数而不是从文件读取
            use.main_use(
                download_dir=self.download_dir,
                cookies=self.auth_token,
                url='https://x.com/',
                user_id=self.user_id,
                father_class=self.father_class,
                move_step=self.move_step,
                driver_path=selenium_a.get_driver_path('msedgedriver.exe'),
                log_func=self.log_signal.emit,
                headless=self.headless
            )

            self.stage_signal.emit('一切顺利！')
            self.progress_signal.emit(100)

        except Exception as e:
            self.log_signal.emit(f"❌ 爬虫出错：{e}")
            self.progress_signal.emit(0)