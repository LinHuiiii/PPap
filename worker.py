from PyQt6.QtCore import QThread, pyqtSignal
import use
import selenium_a
import json

class CrawlerThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, download_dir, user_id, move_step):
        super().__init__()
        self.download_dir = download_dir
        self.user_id = user_id
        self.move_step = move_step

    def run(self):
        self.log_signal.emit("开始爬虫线程...")
        try:
            config = json.load(open('config.json'))
            cookies = config['auth_token']['twitter']
            father_class = config['father_class']['twitter'].split(',')

            use.main_use(
                download_dir=self.download_dir,
                cookies=cookies,
                url='https://x.com/',
                user_id=self.user_id,
                father_class=father_class,
                move_step=self.move_step,
                driver_path=selenium_a.get_driver_path('msedgedriver.exe'),
                log_func=self.log_signal.emit
            )
        except Exception as e:
            self.log_signal.emit(f"❌ 爬虫出错：{e}")