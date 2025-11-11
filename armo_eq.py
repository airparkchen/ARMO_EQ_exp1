#!/usr/bin/env python3
# armo_eq.py
import sys
from PySide6.QtWidgets import QApplication
from ui.ARMO_EQ_ui import EQMusicExperimentWindow
import signal

# 除錯模式開關 - 改成 True 開啟除錯模式
DEBUG_MODE = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 讓 Ctrl+C 能中斷 Qt 事件圈
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # 傳遞除錯模式參數
    window = EQMusicExperimentWindow(debug_mode=DEBUG_MODE)
    window.show()
    
    print(f"啟動模式: {'除錯模式' if DEBUG_MODE else '正式模式'}")
    if DEBUG_MODE:
        print("除錯模式功能：音樂頁面會顯示跳過按鈕")
    
    sys.exit(app.exec())
