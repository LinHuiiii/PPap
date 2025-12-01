import time
from PyQt6.QtCore import QThread, pyqtSignal
import use
import selenium_a


class CrawlerThread(QThread):
    log_signal = pyqtSignal(str)
    phase_signal = pyqtSignal(str, int)  # (阶段名, 进度)
    stats_signal = pyqtSignal(str)  # 统计信息

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
            self.phase_signal.emit("初始化浏览器", 50)
            time.sleep(0.5)
            self.phase_signal.emit("初始化浏览器", 100)

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
                phase_callback=self.phase_signal.emit,  # 新增
                stats_callback=self.stats_signal.emit,  # 新增
                headless=self.headless
            )
            self.phase_signal.emit("任务完成", 100)

        except Exception as e:
            self.log_signal.emit(f"❌ 爬虫出错：{e}")
            self.phase_signal.emit("出错", 0)