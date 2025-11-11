# ui/MusicPageWithTimer.py
"""
音樂播放頁面 - 帶倒數計時功能
固定播放5分鐘，自動停止並跳轉
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QHBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QFont

class MusicPageWithTimer(QWidget):
    """音樂播放頁面 - 含5分鐘倒數計時"""

    def __init__(self, music_path: str, music_title: str, duration_seconds: int,
                 next_page_callback, debug_mode: bool = False):
        """
        初始化音樂播放頁面

        Args:
            music_path: 音樂檔案路徑
            music_title: 音樂標題（顯示用）
            duration_seconds: 播放時長（秒），預設300秒（5分鐘）
            next_page_callback: 播放完成後的回調函數
            debug_mode: 除錯模式
        """
        super().__init__()
        self.music_path = music_path
        self.music_title = music_title
        self.duration_seconds = duration_seconds
        self.next_page_callback = next_page_callback
        self.debug_mode = debug_mode

        self.remaining_seconds = duration_seconds

        # 倒數計時器
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)

        self.init_ui()
        self.init_music()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setAlignment(Qt.AlignCenter)

        # 標題
        title_label = QLabel("音樂播放中")
        title_label.setFont(QFont("Arial", 36, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 音樂標題
        self.music_title_label = QLabel(self.music_title)
        self.music_title_label.setFont(QFont("Arial", 24))
        self.music_title_label.setAlignment(Qt.AlignCenter)
        self.music_title_label.setStyleSheet("color: #34495e;")
        layout.addWidget(self.music_title_label)

        # 說明文字
        instruction_text = "請好好聆聽並放鬆"
        if self.debug_mode:
            instruction_text += "\n\n[除錯模式] 可立即跳過"

        self.description_label = QLabel(instruction_text)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setFont(QFont("Arial", 20))
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        # 倒數計時顯示
        self.countdown_label = QLabel(self.format_time(self.remaining_seconds))
        self.countdown_label.setFont(QFont("Arial", 64, QFont.Bold))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("color: #27ae60;")
        layout.addWidget(self.countdown_label)

        # 剩餘時間提示
        self.time_hint_label = QLabel("剩餘時間")
        self.time_hint_label.setFont(QFont("Arial", 16))
        self.time_hint_label.setAlignment(Qt.AlignCenter)
        self.time_hint_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.time_hint_label)

        # 除錯模式：跳過按鈕
        if self.debug_mode:
            self.skip_button = QPushButton("跳過音樂")
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
            self.skip_button.clicked.connect(self.skip_music)
            layout.addWidget(self.skip_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def init_music(self):
        """初始化音樂播放器"""
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(self.music_path))

    def showEvent(self, event):
        """頁面顯示時開始播放"""
        super().showEvent(event)
        self.start_music()

    def start_music(self):
        """開始播放音樂和倒數計時"""
        self.player.play()
        self.countdown_timer.start(1000)  # 每秒更新一次
        print(f"[MusicPage] 開始播放：{self.music_path}，時長：{self.duration_seconds}秒")

    def update_countdown(self):
        """更新倒數計時"""
        self.remaining_seconds -= 1
        self.countdown_label.setText(self.format_time(self.remaining_seconds))

        # 時間到自動停止
        if self.remaining_seconds <= 0:
            self.finish_music()

    def format_time(self, seconds: int) -> str:
        """格式化時間顯示 (mm:ss)"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def skip_music(self):
        """跳過音樂（除錯模式）"""
        self.finish_music()

    def finish_music(self):
        """完成音樂播放"""
        self.countdown_timer.stop()
        if self.player:
            self.player.stop()
        print(f"[MusicPage] 播放結束：{self.music_title}")
        self.next_page_callback()

    def hideEvent(self, event):
        """頁面隱藏時停止播放和計時"""
        super().hideEvent(event)
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
        if self.player and self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.stop()
