from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                                QLineEdit, QPushButton, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class InstructionPage(QWidget):
    """實驗說明頁面"""

    def __init__(self, on_continue_callback, debug_mode=False):
        super().__init__()
        self.on_continue_callback = on_continue_callback
        self.debug_mode = debug_mode
        self.participant_name = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # 標題
        title = QLabel("實驗說明")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 實驗流程說明
        instruction_text = QTextEdit()
        instruction_text.setReadOnly(True)
        instruction_text.setFont(QFont("Arial", 12))
        instruction_text.setHtml("""
        <h2>實驗流程說明</h2>
        <p>感謝您參與本次音樂實驗！實驗流程如下：</p>
        <ol>
            <li><b>Baseline (3分鐘)</b>：請保持放鬆，靜靜坐著</li>
            <li><b>音樂1 (5分鐘)</b>：聆聽第一首音樂</li>
            <li><b>問卷1</b>：回答3個簡短問題</li>
            <li><b>休息1 (至少3分鐘)</b>：休息片刻</li>
            <li><b>音樂2 (5分鐘)</b>：聆聽第二首音樂</li>
            <li><b>問卷2</b>：回答3個簡短問題</li>
            <li><b>休息2 (至少3分鐘)</b>：休息片刻</li>
            <li><b>音樂3 (5分鐘)</b>：聆聽第三首音樂</li>
            <li><b>問卷3</b>：回答3個簡短問題</li>
            <li><b>休息3 (至少3分鐘)</b>：休息片刻</li>
            <li><b>完成</b></li>
        </ol>
        <p><b>預計時間：</b>約 25-30 分鐘</p>
        <p><b>注意事項：</b></p>
        <ul>
            <li>請在安靜的環境中進行實驗</li>
            <li>實驗過程中請保持自然放鬆</li>
            <li>請認真聆聽音樂並回答問卷</li>
            <li>如有不適請立即告知實驗人員</li>
        </ul>
        """)
        layout.addWidget(instruction_text)

        # 姓名輸入
        name_label = QLabel("請輸入您的姓名（必填）：")
        name_label.setFont(QFont("Arial", 14))
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("請輸入姓名")
        self.name_input.setFont(QFont("Arial", 14))
        self.name_input.setMinimumHeight(40)
        self.name_input.textChanged.connect(self.on_name_changed)
        layout.addWidget(self.name_input)

        # 開始按鈕
        self.start_button = QPushButton("我已了解，開始實驗")
        self.start_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.start_button.setMinimumHeight(60)
        self.start_button.setEnabled(False)  # 初始禁用
        self.start_button.clicked.connect(self.on_start_clicked)

        # 設置按鈕樣式
        self.update_button_style()

        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def update_button_style(self):
        """更新按鈕樣式"""
        if self.start_button.isEnabled():
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
        else:
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #cccccc;
                    color: #666666;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)

    def on_name_changed(self, text):
        """姓名輸入變化時的處理"""
        # 只有輸入姓名後才能點擊開始
        has_name = len(text.strip()) > 0
        self.start_button.setEnabled(has_name)
        self.update_button_style()

    def on_start_clicked(self):
        """點擊開始按鈕"""
        self.participant_name = self.name_input.text().strip()
        if self.participant_name:
            self.on_continue_callback(self.participant_name)

    def get_participant_name(self):
        """獲取參與者姓名"""
        return self.participant_name
