import json
import os

from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QMessageBox


def load_existing_config():
    """加载现有配置，如果文件不存在则返回默认配置"""
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败，使用默认配置: {e}")

    # 默认配置
    return {
        'auth_token': {'twitter': ''},
        'father_class': {'twitter': ['r-18u37iz', 'r-9aw3ui']}
    }


def save_to_json(config):
    """保存配置到文件"""
    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False


class Setting(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置')
        self.setModal(True)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QFormLayout()
        self.auth_token_input = QLineEdit()
        self.father_class_input = QLineEdit()

        layout.addRow('Auth Token:', self.auth_token_input)
        layout.addRow('Father Class (用逗号分隔):', self.father_class_input)

        button_layout = QHBoxLayout()
        self.save_btn = QPushButton('保存')
        self.cancel_btn = QPushButton('取消')

        # 连接按钮事件
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def load_settings(self):
        """加载设置到界面"""
        try:
            config = load_existing_config()
            auth_token = config.get('auth_token', {}).get('twitter', '')
            father_class = config.get('father_class', {}).get('twitter', [])

            self.auth_token_input.setText(auth_token)
            # 将列表转换为逗号分隔的字符串
            if isinstance(father_class, list):
                self.father_class_input.setText(','.join(father_class))
            else:
                self.father_class_input.setText(str(father_class))
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载配置失败: {e}')

    def save_settings(self):
        """保存设置到文件"""
        try:
            config = load_existing_config()

            # 更新配置
            config['auth_token'] = {'twitter': self.auth_token_input.text().strip()}

            # 处理 father_class，分割字符串为列表
            class_text = self.father_class_input.text().strip()
            if class_text:
                father_class_list = [cls.strip() for cls in class_text.split(',')]
            else:
                father_class_list = []
            config['father_class'] = {'twitter': father_class_list}

            # 保存到文件
            if save_to_json(config):
                QMessageBox.information(self, '成功', '配置已保存！')
                self.accept()  # 关闭对话框并返回 Accepted
            else:
                QMessageBox.warning(self, '错误', '保存配置失败')

        except Exception as e:
            QMessageBox.warning(self, '错误', f'保存配置失败: {e}')