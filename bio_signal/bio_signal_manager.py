import csv
import os
import time
from .bioDataUtils import setStatus, startSerial, startWrite, stopWrite, stopSerial, setFileName, setLabel, setCurrent

class BioSignalManager:
    def __init__(self, label_manager):
        self.bio_data_initialized = False
        self.is_collecting_data = False
        self.label_manager = label_manager

    def start_reading(self, case_path, host="0.0.0.0", port=8000):
        """
        開始讀取生理訊號，使用無線通訊。
        :param case_path: 生理數據存檔路徑
        :param host: 無線通訊的 IP 地址
        :param port: 無線通訊的端口
        """
        if not self.bio_data_initialized:
            self.case_path = case_path  # ✅ <--- 加上這一行
            setFileName(f"{case_path}/bio_result")
            startSerial(host, port)  # 無線傳輸，取代原來的串口方式
            self.bio_data_initialized = True

    def start_bio_data_collection(self, case_path, page_label, context_label, host="0.0.0.0", port=8000):
        """
        開始生理數據收集，設置標籤並啟動數據讀取和寫入。
        :param case_path: 生理數據存檔路徑
        :param page_label: 當前頁面標籤
        :param host: 無線通訊的 IP 地址
        :param port: 無線通訊的端口
        """
        print(f"[DEBUG] 收到 context_label: {context_label}")
        self.start_reading(case_path, host, port)
        setStatus(page_label)
        setCurrent(context_label)
        self.start_writing()

    def set_label(self, label):
        """
        設置當前數據收集的標籤。
        :param label: 數據標籤
        """
        setLabel(label)

    def set_current(self, context_label):
        from .bioDataUtils import setCurrent
        setCurrent(context_label)

    def start_writing(self):
        """
        開始將數據寫入文件。
        """
        if not self.is_collecting_data:
            self.is_collecting_data = True
            startWrite()

    def stop_writing(self):
        """
        停止將數據寫入文件。
        """
        if self.is_collecting_data:
            stopWrite()
            self.is_collecting_data = False

    def close(self):
        """
        關閉數據收集流程，包括停止寫入和關閉連接。
        """
        if self.bio_data_initialized:
            self.stop_writing()
            stopSerial()


    # ✅ 新增：標記當下的 label 切換 # Roger
    def mark_label_event(self, label): 
        if not self.case_path:
            print("[⚠️] 尚未設定 case_path，無法寫入事件")
            return

        timestamp = time.time()
        event_log_path = os.path.join(self.case_path, "bio_event_log.csv")
        event = [timestamp, "LABEL_CHANGE", label]

        try:
            write_header = not os.path.exists(event_log_path)
            with open(event_log_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(["Timestamp", "Event Type", "Label"])
                writer.writerow(event)

            print(f"[📌] 已寫入事件標籤切換：{label}")
        except Exception as e:
            print(f"[❌] 寫入事件檔失敗: {e}")