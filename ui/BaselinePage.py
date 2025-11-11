# ui/BaselinePage.py
"""
Baseline 階段頁面
顯示3分鐘倒數計時，提示受測者保持放鬆
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

class BaselinePage(QWidget):
    """Baseline階段頁面 - 3分鐘倒數計時"""

    def __init__(self, duration_seconds: int, next_callback, debug_mode: bool = False):
        """
        初始化Baseline頁面

        Args:
            duration_seconds: 持續時間（秒），預設180秒（3分鐘）
            next_callback: 完成後的回調函數
            debug_mode: 除錯模式
        """
        super().__init__()
        self.duration_seconds = duration_seconds
        self.next_callback = next_callback
        self.debug_mode = debug_mode
        self.remaining_seconds = duration_seconds

        # 計時器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(40)
        layout.setAlignment(Qt.AlignCenter)

        # 標題
        title_label = QLabel("Baseline 階段")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 提示文字
        instruction_text = "請保持放鬆，配戴好設備"
        if self.debug_mode:
            instruction_text += "\n\n[除錯模式] 可立即跳過"

        self.instruction_label = QLabel(instruction_text)
        self.instruction_label.setFont(QFont("Arial", 24))
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)
        layout.addWidget(self.instruction_label)

        # 倒數計時顯示
        self.timer_label = QLabel(self.format_time(self.remaining_seconds))
        self.timer_label.setFont(QFont("Arial", 72, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self.timer_label)

        # 除錯模式：跳過按鈕
        if self.debug_mode:
            self.skip_button = QPushButton("跳過 Baseline")
            self.skip_button.setFont(QFont("Arial", 18))
            self.skip_button.setFixedSize(200, 60)
            self.skip_button.setStyleSheet("""
                QPushButton {
                    background-color: #ff6666;
                    color: white;
                    border: none;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #ff4444;
                }
            """)
            self.skip_button.clicked.connect(self.skip_baseline)
            layout.addWidget(self.skip_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def showEvent(self, event):
        """頁面顯示時開始計時"""
        super().showEvent(event)
        self.start_timer()

    def start_timer(self):
        """開始倒數計時"""
        self.timer.start(1000)  # 每秒更新一次

    def update_timer(self):
        """更新計時器"""
        self.remaining_seconds -= 1
        self.timer_label.setText(self.format_time(self.remaining_seconds))

        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.finish_baseline()

    def format_time(self, seconds: int) -> str:
        """格式化時間顯示 (mm:ss)"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def skip_baseline(self):
        """跳過Baseline（除錯模式）"""
        self.timer.stop()
        self.finish_baseline()

    def finish_baseline(self):
        """完成Baseline階段"""
        self.next_callback()

    def hideEvent(self, event):
        """頁面隱藏時停止計時器"""
        super().hideEvent(event)
        if self.timer.isActive():
            self.timer.stop()
