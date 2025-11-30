import json
import sys
from PyQt6.QtCore import Qt
from config import Setting
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QFileDialog, QMessageBox, QTextEdit, QProgressBar, QDialog, QCheckBox
from worker import CrawlerThread

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X 爬虫")
        self.setGeometry(500, 200, 650, 750)

        self.headless_mode = True
        self.setup_headless_control()

        # 下载路径
        self.path = QLabel('下载路径：')
        self.path_input = QLineEdit()
        self.browse_button = QPushButton('浏览')
        self.browse_button.clicked.connect(self.choose_folder)

        # 用户ID
        self.user = QLabel('用户ID（@后文字）：')
        self.user_input = QLineEdit()
        self.user.setMaximumWidth(300)

        # 滚动次数
        self.scroll = QLabel('最大滚动次数')
        self.scroll_input = QLineEdit('40')

        # 进度条
        self.stage_label = QLabel('准备就绪')
        self.stage_label.setStyleSheet("font-weight: bold; color: #2c3e50; padding: 5px;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)

        # 开始按钮
        self.start = QPushButton('开始!')
        self.start.clicked.connect(self.start_download)

        # 日志显示
        self.log_label = QLabel('运行日志：')
        self.log_display = QTextEdit()
        self.log_display.setMaximumHeight(200)  # 限制高度
        self.log_display.setReadOnly(True)

        # 退出按钮
        self.quit_button = QPushButton('退出程序')
        self.quit_button.clicked.connect(self.close_application)

        # 设置按钮
        self.settings_btn = QPushButton("设置")
        self.settings_btn.clicked.connect(self.open_settings)

        # 保存配置
        self.current_config = self.load_config()

        # 布局
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        path_layout.addWidget(self.headless_checkbox)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(self.path)
        layout.addLayout(path_layout)
        layout.addWidget(self.user)
        layout.addWidget(self.user_input)
        layout.addWidget(self.scroll)
        layout.addWidget(self.scroll_input)
        layout.addWidget(self.start)
        layout.addWidget(self.settings_btn)


        # 🆕 添加进度显示
        layout.addWidget(self.stage_label)
        layout.addWidget(self.progress_bar)

        layout.addWidget(self.log_label)
        layout.addWidget(self.log_display)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)

    def setup_headless_control(self):
        # 创建控制无头模式的复选框
        self.headless_checkbox = QCheckBox("静 默 行 动")
        self.headless_checkbox.setChecked(self.headless_mode)
        self.headless_checkbox.setToolTip("开启后浏览器在后台运行，不显示界面")
        self.headless_checkbox.stateChanged.connect(self.toggle_headless_mode)

    def toggle_headless_mode(self, state):
        """切换无头模式状态"""
        self.headless_mode = (state == Qt.CheckState.Checked.value)

        # 可选：添加状态提示
        status = "开启" if self.headless_mode else "关闭"
        print(f"无头模式已{status}")

    def open_settings(self):
        dialog = Setting(self)
        dialog.exec()

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

    def load_config(self):
        """加载配置文件"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 确保配置结构正确
                if 'auth_token' not in config:
                    config['auth_token'] = {'twitter': ''}
                if 'father_class' not in config:
                    config['father_class'] = {'twitter': []}
                return config
        except Exception as e:
            print(f"加载配置失败: {e}")
            # 返回默认配置
            return {'auth_token': {'twitter': ''},'father_class': {'twitter': ['r-18u37iz','r-9aw3ui']}}

    def get_auth_token(self):
        return self.current_config.get('auth_token', {}).get('twitter', '')

    def get_father_class(self):
        classes = self.current_config.get('father_class', {}).get('twitter', [])
        if isinstance(classes, list):
            return classes
        return [str(classes)]

    def settings(self):
        dialog = Setting(self)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            # 🆕 设置保存后，重新加载配置
            self.current_config = self.load_config()
            print("配置已重新加载")

    def start_download(self):
        self.progress_bar.setValue(0)
        self.stage_label.setText("启动中...")
        self.log_display.clear()

        scroll = self.scroll_input.text()
        auth_token = self.get_auth_token()
        father_class = self.get_father_class()

        if not auth_token:
            QMessageBox.warning(self, "错误", "请先在设置中配置 auth_token！")
            return

        self.start.setEnabled(False)
        self.thread = CrawlerThread(
            path=self.path_input.text(),
            user=self.user_input.text(),
            move_step=int(self.scroll_input.text()),
            auth_token=auth_token,  # 🆕 使用动态配置
            father_class=father_class,  # 🆕 使用动态配置
            headless = self.headless_mode
        )
        self.thread.log_signal.connect(self.log_output)
        self.thread.progress_signal.connect(self.progress_bar.setValue)  # 更新进度条
        self.thread.stage_signal.connect(self.stage_label.setText)  # 更新阶段文字
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def log_output(self, message):
        self.log_display.append(message)

    def on_finished(self):
        self.start.setEnabled(True)
        QMessageBox.information(self, "完成", "爬虫任务已完成！")

    def close_application(self):
        self.close()

    def closeEvent(self, event: QCloseEvent):
        if hasattr(self, 'thread') and self.thread.isRunning():
            reply = QMessageBox.question(
                self, '确认退出',
                "爬虫任务仍在运行，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.thread.terminate()
                self.thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())