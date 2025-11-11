#!/usr/bin/env python3
# new_experiment.py
"""
新音樂實驗系統啟動檔案

實驗流程：
1. 配戴設備
2. Baseline (3分鐘)
3. 音樂1 (5分鐘)
4. 問卷1
5. 間隔休息1 (至少3分鐘)
6. 音樂2 (5分鐘)
7. 問卷2
8. 間隔休息2 (至少3分鐘)
9. 完成
"""
import sys
from PySide6.QtWidgets import QApplication
from ui.NewExperimentWindow import NewExperimentWindow
import signal

# 除錯模式開關
DEBUG_MODE = True  # 改成 False 關閉除錯模式

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 讓 Ctrl+C 能中斷 Qt 事件圈
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # 啟動新實驗視窗
    window = NewExperimentWindow(debug_mode=DEBUG_MODE)
    window.show()

    print("="*60)
    print("音樂實驗系統 - 新版")
    print("="*60)
    print(f"啟動模式: {'除錯模式' if DEBUG_MODE else '正式模式'}")
    if DEBUG_MODE:
        print("除錯模式功能：")
        print("  - Baseline: 可立即跳過")
        print("  - 音樂播放: 可立即跳過")
        print("  - 間隔休息: 立即啟用繼續按鈕")
    print("="*60)

    sys.exit(app.exec())
