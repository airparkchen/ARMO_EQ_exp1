# ui/IntervalPage.py
"""
間隔休息頁面
至少3分鐘休息時間，前3分鐘按鈕禁用
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

class IntervalPage(QWidget):
    """間隔休息頁面 - 至少3分鐘"""

    def __init__(self, min_duration_seconds: int, next_callback, debug_mode: bool = False):
        """
        初始化間隔休息頁面

        Args:
            min_duration_seconds: 最小休息時間（秒），預設180秒（3分鐘）
            next_callback: 繼續按鈕的回調函數
            debug_mode: 除錯模式
        """
        super().__init__()
        self.min_duration_seconds = min_duration_seconds
        self.next_callback = next_callback
        self.debug_mode = debug_mode
        self.elapsed_seconds = 0

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
        title_label = QLabel("休息時間")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 提示文字
        self.instruction_label = QLabel("請休息，稍後繼續")
        self.instruction_label.setFont(QFont("Arial", 24))
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)
        layout.addWidget(self.instruction_label)

        # 計時顯示
        self.timer_label = QLabel(self.format_time(self.elapsed_seconds))
        self.timer_label.setFont(QFont("Arial", 64, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: #3498db;")
        layout.addWidget(self.timer_label)

        # 狀態提示
        self.status_label = QLabel(f"至少需要休息 {self.format_time(self.min_duration_seconds)}")
        self.status_label.setFont(QFont("Arial", 18))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.status_label)

        # 繼續按鈕
        self.continue_button = QPushButton("繼續實驗")
        self.continue_button.setFont(QFont("Arial", 20))
        self.continue_button.setFixedSize(200, 70)
        self.continue_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.continue_button.clicked.connect(self.on_continue)

        # 除錯模式立即啟用，否則禁用
        self.continue_button.setEnabled(self.debug_mode)

        layout.addWidget(self.continue_button, alignment=Qt.AlignCenter)

        # 除錯模式提示
        if self.debug_mode:
            debug_label = QLabel("[除錯模式] 按鈕立即可用")
            debug_label.setFont(QFont("Arial", 14))
            debug_label.setAlignment(Qt.AlignCenter)
            debug_label.setStyleSheet("color: #e74c3c;")
            layout.addWidget(debug_label)

        self.setLayout(layout)

    def showEvent(self, event):
        """頁面顯示時開始計時"""
        super().showEvent(event)
        self.start_timer()

    def start_timer(self):
        """開始計時"""
        self.timer.start(1000)  # 每秒更新一次

    def update_timer(self):
        """更新計時器"""
        self.elapsed_seconds += 1
        self.timer_label.setText(self.format_time(self.elapsed_seconds))

        # 更新狀態提示
        if self.elapsed_seconds < self.min_duration_seconds:
            remaining = self.min_duration_seconds - self.elapsed_seconds
            self.status_label.setText(f"還需休息 {self.format_time(remaining)}")
            self.status_label.setStyleSheet("color: #e74c3c;")
        else:
            # 時間到，啟用按鈕
            if not self.debug_mode:  # 除錯模式已經啟用了
                self.continue_button.setEnabled(True)
            self.status_label.setText("✓ 已休息足夠，可以繼續")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")

    def format_time(self, seconds: int) -> str:
        """格式化時間顯示 (mm:ss)"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def on_continue(self):
        """繼續按鈕點擊"""
        self.timer.stop()
        self.next_callback()

    def hideEvent(self, event):
        """頁面隱藏時停止計時器"""
        super().hideEvent(event)
        if self.timer.isActive():
            self.timer.stop()
