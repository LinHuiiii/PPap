import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTextEdit
from worker import CrawlerThread

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X 爬虫")
        self.setGeometry(300, 300, 500, 400)

        # 下载路径
        self.path = QLabel('下载路径：')
        self.path_input = QLineEdit()
        self.browse_button = QPushButton('浏览')
        self.browse_button.clicked.connect(self.choose_folder)

        # 用户ID
        self.user = QLabel('用户ID（@后文字）：')
        self.user_input = QLineEdit()

        # 滚动次数
        self.scroll = QLabel('最大滚动次数')
        self.scroll_input = QLineEdit('40')

        # 开始按钮
        self.start = QPushButton('下载')
        self.start.clicked.connect(self.start_download)

        # 日志显示
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)

        # 退出按钮
        self.quit_button = QPushButton('退出程序')
        self.quit_button.clicked.connect(self.close_application)

        # 布局
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)

        layout = QVBoxLayout()
        layout.addWidget(self.quit_button)
        layout.addWidget(self.path)
        layout.addLayout(path_layout)
        layout.addWidget(self.user)
        layout.addWidget(self.user_input)
        layout.addWidget(self.scroll)
        layout.addWidget(self.scroll_input)
        layout.addWidget(self.start)
        layout.addWidget(self.log_display)  # 添加日志显示框

        self.setLayout(layout)

    def close_application(self):
        # 如果有线程在运行，先终止线程
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        QApplication.quit()

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择下载文件夹')
        if folder:
            self.path_input.setText(folder)

    def start_download(self):
        path = self.path_input.text()
        user = self.user_input.text()
        scroll = self.scroll_input.text()

        if not path or not user or not scroll.isdigit():
            QMessageBox.warning(self, "输入错误", "请填写完整信息！")
            return

        self.start.setEnabled(False)
        self.thread = CrawlerThread(path, user, int(scroll))
        self.thread.log_signal.connect(self.log_output)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def log_output(self, message):
        self.log_display.append(message)  # 现在这个控件存在了

    def on_finished(self):
        self.start.setEnabled(True)
        QMessageBox.information(self, "完成", "爬虫任务已完成！")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())