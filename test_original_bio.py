#!/usr/bin/env python3
"""
測試原始 bio_signal 模組
驗證原始程式是否正常運作
"""
import sys
import time
from bio_signal.bioDataUtils import startSerial, startWrite, stopWrite, stopSerial, setFileName, setStatus, setCurrent

def test_original_bio_signal():
    """測試原始的 bio_signal 啟動方式"""

    print("="*60)
    print("測試原始 bio_signal 模組")
    print("="*60)

    try:
        # 設定檔案名稱
        print("\n1. 設定輸出檔案...")
        setFileName("./test_result/test_bio")

        # 啟動 Serial (Socket Server)
        print("2. 啟動 Socket Server (0.0.0.0:8000)...")
        startSerial("0.0.0.0", 8000)

        # 等待連接
        print("3. Server listening on 0.0.0.0:8000")
        print("   請使用另一個終端執行：")
        print("   python3 test_socket_client.py 127.0.0.1")
        print("\n   按 Ctrl+C 停止...")

        # 等待 5 秒讓 Server 啟動
        time.sleep(5)

        # 開始寫入
        print("\n4. 開始寫入數據...")
        setStatus("test_phase")
        setCurrent("test_label")
        startWrite()

        # 保持運行
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n停止測試...")
        stopWrite()
        stopSerial()
        print("✅ 測試結束")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_original_bio_signal()
