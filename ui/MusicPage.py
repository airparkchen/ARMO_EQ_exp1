# ui/MusicPage.py - 添加延遲跳過按鈕功能
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QHBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QFont

class MusicPage(QWidget):
    def __init__(self, music_path, next_page_callback, debug_mode=False):
        super().__init__()
        self.music_path = music_path
        self.next_page_callback = next_page_callback
        self.debug_mode = debug_mode
        
        # 新增：跳過按鈕延遲顯示
        self.skip_button_timer = QTimer()
        self.skip_button_timer.timeout.connect(self.show_skip_button)
        self.skip_button_timer.setSingleShot(True)
        
        self.init_ui()
        self.init_music()

    def init_ui(self):
        # 主佈局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        # 說明文字標籤
        instruction_text = "稍後會有音樂供您聆聽，待音樂播放完畢後頁面會自動跳轉，請好好放鬆～"
        if self.debug_mode:
            instruction_text += "\n\n[除錯模式] 您可以點擊下方按鈕跳過音樂"
            
        self.description_label = QLabel(instruction_text)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.description_label.setWordWrap(True)

        # 設定字體大小
        font = QFont()
        font.setPointSize(48)
        self.description_label.setFont(font)
        layout.addWidget(self.description_label, alignment=Qt.AlignCenter)

        # 按鈕區域（用來放置跳過按鈕）
        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(self.button_layout)
        
        # 除錯模式跳過按鈕（立即顯示）
        if self.debug_mode:
            self.create_skip_button()

        self.setLayout(layout)
    
    def create_skip_button(self):
        """創建跳過按鈕"""
        if not hasattr(self, 'skip_button'):
            self.skip_button = QPushButton("跳過音樂")
            self.skip_button.setFont(QFont("Arial", 24))
            self.skip_button.setFixedSize(200, 80)
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
                QPushButton:pressed {
                    background-color: #ff2222;
                }
            """)
            self.skip_button.clicked.connect(self.skip_music)
            self.button_layout.addWidget(self.skip_button)
    
    def show_skip_button(self):
        """2分30秒後顯示跳過按鈕"""
        if not self.debug_mode:  # 只有非除錯模式才需要延遲顯示
            self.create_skip_button()

    def skip_music(self):
        """跳過音樂播放"""
        if hasattr(self, 'player'):
            self.player.stop()
        self.skip_button_timer.stop()  # 停止計時器
        self.next_page_callback()

    def init_music(self):
        # 初始化播放器
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(self.music_path))

        # 音樂播放結束時自動跳頁
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

    def showEvent(self, event):
        """當頁面顯示時開始播放音樂"""
        super().showEvent(event)
        self.start_music()

    def on_media_status_changed(self, status):
        # 音樂播放結束時自動執行換頁
        if status == QMediaPlayer.EndOfMedia:
            self.skip_button_timer.stop()  # 停止計時器
            self.next_page_callback()

    def start_music(self):
        # 開始播放音樂
        self.player.play()
        
        # 非除錯模式：2分30秒後顯示跳過按鈕
        if not self.debug_mode:
            self.skip_button_timer.start(150000)  # 2分30秒 = 150000毫秒