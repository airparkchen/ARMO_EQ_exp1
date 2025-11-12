#!/usr/bin/env python3
# new_experiment_with_bio.py
"""
新音樂實驗系統啟動檔案 - 整合生理訊號記錄

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

生理訊號整合功能：
- 自動在每個階段切換時標記 label
- 記錄 GSR, HR, SKT, PPGRAW, PPI, ACT, IMUX, IMUY, IMUZ
- 生成 bio_event_log.csv 記錄標籤切換時間
- 生成多個生理訊號 CSV 檔案
"""
import sys
from PySide6.QtWidgets import QApplication
from ui.NewExperimentWindowWithBio import NewExperimentWindowWithBio
import signal

# 除錯模式開關
DEBUG_MODE = True  # 改成 False 關閉除錯模式

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 讓 Ctrl+C 能中斷 Qt 事件圈
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # 啟動新實驗視窗（生理訊號版）
    window = NewExperimentWindowWithBio(debug_mode=DEBUG_MODE)
    window.show()

    print("="*70)
    print("音樂實驗系統 - 生理訊號整合版")
    print("="*70)
    print(f"啟動模式: {'除錯模式' if DEBUG_MODE else '正式模式'}")
    if DEBUG_MODE:
        print("除錯模式功能：")
        print("  - Baseline: 可立即跳過")
        print("  - 音樂播放: 可立即跳過")
        print("  - 間隔休息: 立即啟用繼續按鈕")
    print("")
    print("生理訊號功能：")
    print("  - 預設關閉，可在開始頁面勾選「啟用生理訊號記錄」")
    print("  - Socket 連線：0.0.0.0:8000")
    print("  - 自動標記實驗階段 label")
    print("  - 輸出檔案：")
    print("    * bio_result_gsr.csv")
    print("    * bio_result_hr.csv")
    print("    * bio_result_skt.csv")
    print("    * bio_result_ppgraw.csv")
    print("    * bio_result_ppi.csv")
    print("    * bio_result_act.csv")
    print("    * bio_result_imux/imuy/imuz.csv")
    print("    * bio_event_log.csv (標籤切換記錄)")
    print("="*70)

    sys.exit(app.exec())
