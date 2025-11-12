import socket
import datetime
from time import sleep
import threading
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
import numpy as np
import time
from PySide6.QtCore import QObject, Signal
from collections import deque
import queue

connection_lock = threading.Lock()
matplotlib.use('Agg')

# 原有數據列表
skt_data = []
gsr_data = []
hr_data = []
ppi_data = []
act_data = []
imux_data = []
imuy_data = []
imuz_data = []
ppgraw_data = []

# 修改：使用實際時間戳排序
server_timestamp_start = None
server_sequence_counter = 0
timestamp_lock = threading.Lock()

# 數據緩衝隊列用於排序
data_buffer_queue = queue.PriorityQueue()
buffer_processing_thread = None
buffer_lock = threading.Lock()

# 原有全局變量
plot_window_open = False
fig, axs = None, None
ani = None
line_skt, line_gsr, line_hr = None, None, None

user_name = "dylan"
dataType = "test9"
now_status = "None"
now_label = "None"
current_status = "None"

fgsr = None
fhr = None
fskt = None
fppi = None
fact = None
fimux = None
fimuy = None
fimuz = None
fppgraw = None 

startFlag = True
startWriteFlag = False

gsr_status = False
hr_status = False
SKT_status = False

latest_gsr = None
latest_hr = None
latest_skt = None
latest_ppi = None
latest_act = None
latest_imux = None
latest_imuy = None
latest_imuz = None
latest_ppgraw = None  
last_output_time = 0

client_connection = None
last_data_time = 0
SIGNAL_TIMEOUT = 5
is_client_connected = False
data_lock = threading.Lock()
plot_flag = False

class BioSignals(QObject):
    disconnect_signal = Signal(str)
    signal_lost_signal = Signal(str)

bio_signals = BioSignals()

def generate_server_timestamp():
    """伺服器端生成實際接收時間戳"""
    current_time = time.time()
    dt = datetime.datetime.fromtimestamp(current_time)
    return dt.strftime("%Y-%m-%d %H:%M:%S.") + f"{dt.microsecond // 1000:03d}"

class DataPoint:
    """使用客戶端時間戳排序"""
    def __init__(self, signal_type, value, original_timestamp, server_timestamp, sequence):
        self.signal_type = signal_type
        self.value = value
        self.original_timestamp = original_timestamp
        self.server_timestamp = server_timestamp
        self.sequence = sequence
        
        # 將客戶端時間戳轉換為可排序的浮點數
        self.client_time_float = self._parse_timestamp(original_timestamp)
    
    def _parse_timestamp(self, timestamp_str):
        """將時間戳字串轉換為浮點數用於排序"""
        try:
            if timestamp_str:
                # 解析格式：'2025-01-28 14:30:25.123'
                dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                return dt.timestamp()
            else:
                # 如果沒有客戶端時間戳，使用當前時間
                return time.time()
        except (ValueError, TypeError):
            # 解析失敗則使用當前時間
            print(f"時間戳解析失敗: {timestamp_str}，使用當前時間")
            return time.time()
    
    def __lt__(self, other):
        # 使用客戶端時間戳排序
        return self.client_time_float < other.client_time_float

def start_buffer_processing():
    """啟動緩衝區處理線程"""
    global buffer_processing_thread
    
    def process_buffer():
        last_process_time = time.time()
        
        while startFlag:
            try:
                # 使用較短間隔處理緩衝區，確保延遲封包能正確排序
                current_time = time.time()
                if current_time - last_process_time >= 0.3:  # 300ms間隔給予足夠時間讓延遲封包到達
                    
                    # 從優先隊列中取出數據點
                    temp_buffer = []
                    while not data_buffer_queue.empty():
                        try:
                            data_point = data_buffer_queue.get_nowait()
                            temp_buffer.append(data_point)
                        except queue.Empty:
                            break
                    
                    # 按客戶端時間戳排序並處理
                    temp_buffer.sort(key=lambda x: x.client_time_float)
                    
                    for data_point in temp_buffer:
                        process_sorted_data(data_point)
                    
                    
                    last_process_time = current_time
                
                sleep(0.05)  # 減少CPU使用率
                
            except Exception as e:
                print(f"緩衝區處理錯誤: {e}")
                sleep(1)
    
    buffer_processing_thread = threading.Thread(target=process_buffer, daemon=True)
    buffer_processing_thread.start()
    print("緩衝區處理線程已啟動")

def process_sorted_data(data_point):
    """處理已排序的數據點 - 使用客戶端原始時間戳"""
    global skt_data, gsr_data, hr_data, ppi_data, act_data
    global imux_data, imuy_data, imuz_data, ppgraw_data
    global fgsr, fhr, fskt, fppi, fact, fimux, fimuy, fimuz, fppgraw
    global now_status, now_label, current_status
    
    signal_type = data_point.signal_type
    value = data_point.value
    # 使用客戶端原始時間戳寫入檔案，保持生理訊號的真實時序
    timestamp = data_point.original_timestamp if data_point.original_timestamp else data_point.server_timestamp
    
    with data_lock:
        # 根據信號類型存儲數據
        if signal_type == "GSR":
            gsr_data.append(value)
            if fgsr:
                fgsr.write(f"{timestamp},{value},{now_status},{current_status},{now_label}\n")
                fgsr.flush()
                
        elif signal_type == "HR":
            hr_data.append(value)
            if fhr:
                fhr.write(f"{timestamp},{value},{now_status},{current_status},{now_label}\n")
                fhr.flush()
                
        elif signal_type == "SKT":
            skt_data.append(value)
            if fskt:
                formatted_value = round(value, 1)
                fskt.write(f"{timestamp},{formatted_value},{now_status},{current_status},{now_label}\n")
                fskt.flush()
                
        elif signal_type == "PPGRAW":
            ppgraw_data.append(value)
            if fppgraw:
                fppgraw.write(f"{timestamp},{value},{now_status},{current_status},{now_label}\n")
                fppgraw.flush()
                
        elif signal_type == "PPI":
            ppi_data.append(value)
            if fppi:
                fppi.write(f"{timestamp},{value},{now_status},{current_status},{now_label}\n")
                fppi.flush()
                
        elif signal_type == "ACT":
            act_data.append(value)
            if fact:
                fact.write(f"{timestamp},{value},{now_status},{current_status},{now_label}\n")
                fact.flush()
                
        elif signal_type == "IMUX":
            imux_data.append(value)
            if fimux:
                fimux.write(f"{timestamp},{value},{now_status},{current_status},{now_label}\n")
                fimux.flush()
                
        elif signal_type == "IMUY":
            imuy_data.append(value)
            if fimuy:
                fimuy.write(f"{timestamp},{value},{now_status},{current_status},{now_label}\n")
                fimuy.flush()
                
        elif signal_type == "IMUZ":
            imuz_data.append(value)
            if fimuz:
                fimuz.write(f"{timestamp},{value},{now_status},{current_status},{now_label}\n")
                fimuz.flush()

# 其餘函數保持不變...
def getBioStatus():
    global SKT_status, gsr_status, hr_status
    if not gsr_status:
        return {"statusCode": 100, "message": "gsrError"}
    if not SKT_status:
        return {"statusCode": 101, "message": "sktError"}
    if not hr_status:
        return {"statusCode": 102, "message": "hrError"}
    return {"statusCode": 200, "message": "success"}

def setStatus(status):
    global now_status
    now_status = status

def setLabel(label):
    global now_label
    now_label = label

def setCurrent(current):
    global current_status
    current_status = current

def setFileName(fileName):
    global fgsr, fhr, fskt, fppi, fact, fimux, fimuy, fimuz, fppgraw
    
    fgsr = open(fileName + "_gsr.csv", "a")
    fgsr.write("Time,Data,Condition,Current,Label\n")
    fhr = open(fileName + "_hr.csv", "a")
    fhr.write("Time,Data,Condition,Current,Label\n")
    fskt = open(fileName + "_skt.csv", "a")
    fskt.write("Time,Data,Condition,Current,Label\n")
    fppi = open(fileName + "_ppi.csv", "a")
    fppi.write("Time,Data,Condition,Current,Label\n")
    fact = open(fileName + "_act.csv", "a")
    fact.write("Time,Data,Condition,Current,Label\n")
    fimux = open(fileName + "_imux.csv", "a")
    fimux.write("Time,Data,Condition,Current,Label\n")
    fimuy = open(fileName + "_imuy.csv", "a")
    fimuy.write("Time,Data,Condition,Current,Label\n")
    fimuz = open(fileName + "_imuz.csv", "a")
    fimuz.write("Time,Data,Condition,Current,Label\n")
    fppgraw = open(fileName + "_ppgraw.csv", "a")
    fppgraw.write("Time,Data,Condition,Current,Label\n")

def read_wireless(host="0.0.0.0", port=8000):
    global client_connection, latest_gsr, latest_hr, latest_skt, latest_ppi, latest_act
    global latest_imux, latest_imuy, latest_imuz, latest_ppgraw
    global last_output_time, last_data_time, is_client_connected

    buffer = ""
    while startFlag:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen(1)
            print(f"Server listening on {host}:{port}...")

            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")

            with connection_lock:
                client_connection = conn
                is_client_connected = True
                last_data_time = time.time()

            while startFlag:
                try:
                    conn.settimeout(1.0)
                    data = conn.recv(1024)
                    if not data:
                        print("Client disconnected. Waiting for reconnection...")
                        bio_signals.disconnect_signal.emit("Client disconnected gracefully")
                        break

                    buffer += data.decode('utf-8')
                    while "\n" in buffer:
                        message, buffer = buffer.split("\n", 1)
                        message = message.strip()
                        if not message:
                            continue
                        try:
                            parsed_data = json.loads(message)

                            # 更新最新值用於顯示
                            latest_gsr = parsed_data.get("GSR", latest_gsr)
                            latest_hr = parsed_data.get("HR", latest_hr)
                            latest_skt = parsed_data.get("SKT", latest_skt)
                            latest_ppi = parsed_data.get("PPI", latest_ppi)
                            latest_act = parsed_data.get("ACT", latest_act)
                            latest_imux = parsed_data.get("IMUX", latest_imux)
                            latest_imuy = parsed_data.get("IMUY", latest_imuy)
                            latest_imuz = parsed_data.get("IMUZ", latest_imuz)
                            latest_ppgraw = parsed_data.get("PPGRAW", latest_ppgraw)

                            last_data_time = time.time()
                            current_time = time.time()
                            if current_time - last_output_time >= 1:
                                output = []
                                if latest_gsr is not None:
                                    output.append(f"GSR: {latest_gsr}")
                                if latest_hr is not None:
                                    output.append(f"HR: {latest_hr}")
                                if latest_skt is not None:
                                    output.append(f"SKT: {latest_skt:.1f}")
                                if latest_ppi is not None:
                                    output.append(f"PPI: {latest_ppi}")
                                if latest_act is not None:
                                    output.append(f"ACT: {latest_act}")
                                if latest_imux is not None:
                                    output.append(f"IMUX: {latest_imux}")
                                if latest_imuy is not None:
                                    output.append(f"IMUY: {latest_imuy}")
                                if latest_imuz is not None:
                                    output.append(f"IMUZ: {latest_imuz}")
                                if latest_ppgraw is not None:
                                    output.append(f"PPGRAW: {latest_ppgraw}")

                                print(", ".join(output))
                                last_output_time = current_time

                            if startWriteFlag:
                                process_data_with_server_timestamp(parsed_data)

                        except json.JSONDecodeError:
                            print(f"Invalid JSON format: {message}. Skipping this message.")
                    if is_client_connected and time.time() - last_data_time > SIGNAL_TIMEOUT:
                        bio_signals.signal_lost_signal.emit("No physiological signals received for too long")
                except socket.timeout:
                    if is_client_connected and time.time() - last_data_time > SIGNAL_TIMEOUT:
                        bio_signals.signal_lost_signal.emit("No physiological signals received for too long")
                except Exception as e:
                    print(f"Error in communication: {e}")
                    bio_signals.disconnect_signal.emit(f"Connection error: {e}")
                    break

            with connection_lock:
                client_connection = None
                is_client_connected = False
            conn.close()
            print("Connection closed. Restarting server...")
        except Exception as e:
            print(f"Error in server setup: {e}")
            bio_signals.disconnect_signal.emit(f"Server setup error: {e}")
            sleep(1)
        finally:
            server_socket.close()

def process_data_with_server_timestamp(parsed_data):
    """使用伺服器端時間戳處理數據"""
    global server_sequence_counter
    
    # 支援的信號類型
    signal_types = ["GSR", "HR", "SKT", "PPGRAW", "PPI", "ACT", "IMUX", "IMUY", "IMUZ"]
    
    for signal_type in signal_types:
        if signal_type in parsed_data:
            try:
                value = float(parsed_data[signal_type])
                original_timestamp = parsed_data.get(f"{signal_type}_Timestamp", "")
                server_timestamp = generate_server_timestamp()
                
                # 創建數據點並加入緩衝隊列
                data_point = DataPoint(
                    signal_type=signal_type,
                    value=value,
                    original_timestamp=original_timestamp,
                    server_timestamp=server_timestamp,
                    sequence=server_sequence_counter
                )
                
                data_buffer_queue.put(data_point)
                server_sequence_counter += 1
                
            except (ValueError, TypeError) as e:
                print(f"數據轉換錯誤 {signal_type}: {e}")

def process_data(parsed_data):
    """保持向後兼容的原始函數"""
    process_data_with_server_timestamp(parsed_data)

def startSerial(host="0.0.0.0", port=8000):
    global startFlag, server_timestamp_start, server_sequence_counter
    
    # 重置時間戳生成器
    with timestamp_lock:
        server_timestamp_start = None
        server_sequence_counter = 0
    
    # 啟動緩衝區處理
    start_buffer_processing()
    
    startFlag = True
    thread = threading.Thread(target=read_wireless, args=(host, port))
    thread.daemon = True
    thread.start()

def startWrite():
    global startWriteFlag
    print("[startWrite]")
    startWriteFlag = True

def stopWrite():
    global startWriteFlag, fhr, fgsr, fskt, fppi, fact, fimux, fimuy, fimuz, fppgraw
    print("[stopWrite]")
    startWriteFlag = False
    if fhr:
        fhr.flush()
    if fgsr:
        fgsr.flush()
    if fskt:
        fskt.flush()
    if fppi:
        fppi.flush()
    if fact:
        fact.flush()
    if fimux: 
        fimux.flush()
    if fimuy: 
        fimuy.flush()
    if fimuz: 
        fimuz.flush()
    if fppgraw:
        fppgraw.flush()

def closeFile():
    global fhr, fgsr, fskt, fppi, fact, fimux, fimuy, fimuz, fppgraw
    print("[closeFile]")
    startWriteFlag = False
    if fhr: fhr.close()
    if fgsr: fgsr.close()
    if fskt: fskt.close()
    if fppi: fppi.close()
    if fact: fact.close()
    if fimux: fimux.close()
    if fimuy: fimuy.close()
    if fimuz: fimuz.close()
    if fppgraw: fppgraw.close()

def stopSerial():
    global startFlag
    print("[stopSerial]")
    startFlag = False
    closeFile()

def get_timestamp_stats():
    """獲取時間戳生成統計信息"""
    with timestamp_lock:
        return {
            "sequence_counter": server_sequence_counter,
            "start_time": server_timestamp_start,
            "current_time": time.time()
        }