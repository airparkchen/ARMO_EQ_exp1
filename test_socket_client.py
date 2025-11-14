#!/usr/bin/env python3

"""

測試 Socket 連接 - 模擬手機 APP

用於測試電腦端 Socket Server 是否正常運作

"""

import socket

import json

import time

import sys

 

def test_connection(host, port=8000):

    """測試連接到電腦的 Socket Server"""

 

    print(f"嘗試連接到 {host}:{port}...")

 

    try:

        # 建立 TCP Socket 連接

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client.settimeout(5)  # 5秒超時

 

        # 連接到 Server

        client.connect((host, port))

        print(f"✅ 成功連接到 {host}:{port}")

        print(f"本地端口: {client.getsockname()}")

 

        # 發送測試數據

        print("\n開始發送測試數據...")

        for i in range(5):

            # 模擬生理訊號數據

            data = {

                "GSR": 45.2 + i * 0.1,

                "GSR_Timestamp": time.strftime("%Y-%m-%d %H:%M:%S.") + f"{int(time.time() * 1000) % 1000:03d}",

                "HR": 75 + i,

                "HR_Timestamp": time.strftime("%Y-%m-%d %H:%M:%S.") + f"{int(time.time() * 1000) % 1000:03d}",

                "SKT": 32.5,

                "PPGRAW": 1024,

                "PPI": 800,

                "ACT": 0.5,

                "IMUX": 0.1,

                "IMUY": 0.2,

                "IMUZ": 9.8

            }

 

            # 轉換為 JSON 並添加換行符

            message = json.dumps(data) + "\n"

 

            # 發送數據

            client.send(message.encode('utf-8'))

            print(f"  發送 #{i+1}: GSR={data['GSR']:.1f}, HR={data['HR']}")

 

            time.sleep(1)

 

        print("\n✅ 測試完成！檢查電腦終端是否顯示生理訊號數據。")

 

    except ConnectionRefusedError:

        print(f"❌ 連接被拒絕。請確認：")

        print(f"   1. 實驗程式已啟動")

        print(f"   2. 已勾選「啟用生理訊號記錄」")

        print(f"   3. 看到 'Server listening on 0.0.0.0:8000...'")

 

    except socket.timeout:

        print(f"❌ 連接超時。請確認：")

        print(f"   1. IP 地址正確")

        print(f"   2. 防火牆允許 port 8000")

        print(f"   3. 兩台設備在同一網路")

 

    except Exception as e:

        print(f"❌ 錯誤: {e}")

 

    finally:

        try:

            client.close()

            print("\n連接已關閉")

        except:

            pass

 

if __name__ == "__main__":

    if len(sys.argv) > 1:

        host = sys.argv[1]

    else:

        print("請輸入電腦的 IP 地址：")

        host = input().strip()

        if not host:

            print("使用 localhost 測試...")

            host = "127.0.0.1"

 

    test_connection(host)