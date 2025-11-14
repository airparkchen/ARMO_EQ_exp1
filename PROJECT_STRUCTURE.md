# ARMO_EQ_exp1 專案結構說明

本文檔詳細說明專案中各個部分的功能分類，幫助快速理解哪些是舊實驗內容、哪些是新實驗內容、哪些是通用模組。

## 📋 目錄

- [舊 EQ 實驗內容 (已完成)](#舊-eq-實驗內容-已完成)
- [新音樂實驗系統 (當前使用)](#新音樂實驗系統-當前使用)
- [通用模組](#通用模組)
- [生理訊號整合模組](#生理訊號整合模組)
- [測試與工具](#測試與工具)

---

## 🔵 舊 EQ 實驗內容 (已完成)

這些文件屬於原始的 EQ vs Original 音樂對比實驗，目前已完成實驗並產生結果。

### **主程式**
```
armo_eq.py                          # 舊實驗啟動器 (25 行)
```

### **UI 介面**
```
ui/ARMO_EQ_ui.py                    # 舊實驗主控制器 (807 行)
                                    # - EQ vs Original 音樂對比
                                    # - 3 種音樂類型：Classical, Pop, Jazz
                                    # - A/B 測試與評分問卷

ui/MusicPage.py                     # 音樂播放頁面 (119 行)
                                    # - 自動播放下一首
                                    # - 2.5 分鐘後允許跳過

ui/PostQuestionnairePage.py         # 後測問卷頁面 (457 行)
                                    # - A/B 音樂回放功能
                                    # - 偏好選擇與評分
```

### **問卷與分析**
```
ui/json/pre_questionnaire.json      # 前測問卷 (基本資料、音樂偏好)
ui/json/music_evaluation.json       # 音樂評估問卷 (7 維度)
ui/json/post_questionnaire.json     # 後測問卷 (整體回饋)

create_questionnaires.py            # 問卷生成腳本 (167 行)
analyze_script.py                   # 統計分析腳本 (639 行)
                                    # - Paired t-tests
                                    # - Cohen's d effect size
                                    # - 結果可視化
```

### **音樂文件**
```
music/Classical/                    # 古典音樂 (EQ/Original)
music/Pop/                          # 流行音樂 (EQ/Original)
music/Jazz/                         # 爵士音樂 (EQ/Original)
```

### **實驗結果**
```
experiment_results/                 # 舊實驗的受測者數據
analysis_results/                   # 舊實驗的統計分析結果
```

---

## 🟢 新音樂實驗系統 (當前使用)

這是新開發的音樂實驗系統，用於測試 6 種音樂類別對情緒與放鬆的影響，整合生理訊號記錄。

### **主程式**
```
new_experiment.py                   # 新實驗啟動器 (無生理訊號)
new_experiment_with_bio.py          # 新實驗啟動器 (含生理訊號)
```

### **核心控制器**
```
ui/NewExperimentWindow.py           # 新實驗主控制器 (687 行)
                                    # - 6 種音樂類別測試
                                    # - A/B 組別設計
                                    # - 完整實驗流程控制

ui/NewExperimentWindowWithBio.py    # 生理訊號整合版 (687 行)
                                    # - 所有 NewExperimentWindow 功能
                                    # - 整合 BioSignalManager
                                    # - 自動標記實驗階段
```

### **UI 組件**
```
ui/BaselinePage.py                  # 基線期頁面 (119 行)
                                    # - 3 分鐘倒數計時
                                    # - Debug 模式可跳過

ui/MusicPageWithTimer.py            # 音樂播放頁面 (168 行)
                                    # - 5 分鐘倒數計時
                                    # - 自動停止播放

ui/IntervalPage.py                  # 間隔休息頁面 (163 行)
                                    # - 最少 3 分鐘休息
                                    # - 時間到後啟用繼續按鈕

ui/QuestionPage.py                  # 通用問卷頁面 (125 行)
                                    # - 單選/多選題支援
                                    # - 5 點量表評分

ui/ThankYouPage.py                  # 實驗結束頁面 (100 行)
                                    # - 感謝訊息
                                    # - 關閉視窗
```

### **配置與問卷**
```
music_catalog.json                  # 音樂目錄配置
                                    # - 6 種音樂類別定義
                                    # - Nature, Ambient, New-Age,
                                    #   Instrumental, Lo-fi, Therapeutic
                                    # - 每類 2 首歌 (001, 002)

ui/json/new_experiment/
  └─ music_evaluation_new.json      # 新實驗問卷 (3 題)
                                    # - Valence (心情)
                                    # - Arousal (精神)
                                    # - Relaxation (放鬆)
```

### **音樂文件**
```
music/Nature/                       # 自然音樂 (NA001.wav, NA002.wav)
music/Ambient/                      # 環境音樂 (AB001.wav, AB002.wav)
music/New-Age/                      # 新世紀音樂 (NA001.wav, NA002.wav)
music/Instrumental/                 # 器樂音樂 (IN001.wav, IN002.wav)
music/Lo-fi/                        # Lo-fi 音樂 (LO001.wav, LO002.wav)
music/Therapeutic/                  # 療癒音樂 (TH001.wav, TH002.wav)
```

### **實驗數據**
```
new_experiment_results/             # 新實驗受測者數據目錄
  └─ P{ID}_S{N}_G{A/B}_{timestamp}/ # 單次實驗數據資料夾
      ├─ experiment_info.json       # 實驗配置資訊
      ├─ event_log.csv              # 事件日誌 (毫秒級時間戳)
      ├─ music1_evaluation_*.csv    # 第一首歌問卷結果
      ├─ music2_evaluation_*.csv    # 第二首歌問卷結果
      ├─ bio_event_log.csv          # 生理訊號事件標記
      └─ bio_result_*.csv           # 9 種生理訊號數據
                                    # (gsr, hr, skt, ppgraw, ppi,
                                    #  act, imux, imuy, imuz)

sample_data/                        # 測試數據範例
```

---

## 🟡 通用模組

這些模組在舊實驗和新實驗中都可能使用。

### **事件記錄**
```
ui/EventLogger.py                   # 事件日誌系統 (95 行)
                                    # - 毫秒級時間戳記錄
                                    # - 階段切換追蹤
                                    # - CSV 格式輸出
                                    # 🔹 Phase 類別定義 8 個階段：
                                    #    BASELINE, MUSIC1, QUESTIONNAIRE1,
                                    #    INTERVAL1, MUSIC2, QUESTIONNAIRE2,
                                    #    INTERVAL2, COMPLETE
```

### **配置管理**
```
ui/ExperimentConfig.py              # 實驗配置類別 (86 行)
                                    # - 時間參數設定
                                    # - Debug 模式開關
                                    # - 生理訊號配置
                                    # 🔹 可調整參數：
                                    #    - baseline_duration (預設 180 秒)
                                    #    - music_duration (預設 300 秒)
                                    #    - interval_min_duration (預設 180 秒)
```

### **音樂管理**
```
ui/MusicCatalogManager.py           # 音樂目錄管理 (145 行)
                                    # - 載入 music_catalog.json
                                    # - 音樂文件檢查
                                    # - 類別與歌曲查詢
```

---

## 🟣 生理訊號整合模組

這些模組專門處理生理訊號的記錄與整合。

### **核心模組**
```
bio_signal/
  ├─ __init__.py                    # 模組初始化
  ├─ bio_signal_manager.py          # 生理訊號管理器 (95 行)
  │                                 # - Socket Server 啟動
  │                                 # - 數據寫入控制
  │                                 # - 標籤事件標記
  │
  └─ bioDataUtils.py                # 生理訊號工具函式 (600 行)
                                    # - TCP Socket 伺服器 (端口 8000)
                                    # - UDP 廣播服務 (端口 9999)
                                    # - 9 種生理訊號處理
                                    # - 數據緩衝與排序
                                    # - CSV 文件寫入
                                    # 🔹 支援的訊號：
                                    #    GSR, HR, SKT, PPGRAW, PPI,
                                    #    ACT, IMUX, IMUY, IMUZ
```

### **標籤管理**
```
labels/
  ├─ __init__.py                    # 模組初始化
  ├─ LabelManager.py                # 標籤管理器 (150 行)
  │                                 # - 實驗階段標籤定義
  │                                 # - 頁面索引映射
  │                                 # - 標籤配置載入
  │
  └─ experiment_labels.json         # 標籤配置文件
                                    # - 定義 9 個實驗階段標籤
                                    # - 頁面索引對應關係
```

### **連接架構**
```
┌─────────────┐  Bluetooth SPP/BLE   ┌──────────┐  WiFi Socket    ┌──────────┐
│ 生理訊號耳機 │ ──────────────────→ │ 手機 APP │ ───────────────→ │ 實驗電腦 │
└─────────────┘                      └──────────┘  (TCP 8000)     └──────────┘
                                           ↑                              ↓
                                           │      UDP 廣播 (9999)        │
                                           └──────────────────────────────┘
                                              (自動發現伺服器 IP)
```

### **數據格式**

#### **生理訊號 JSON (手機 → 電腦)**
```json
{
  "GSR": 262763.0,
  "HR": 75,
  "SKT": 32.5,
  "PPGRAW": 12345,
  "PPI": 800,
  "ACT": 0.5,
  "IMUX": 0.1,
  "IMUY": 0.2,
  "IMUZ": 9.8,
  "GSR_Timestamp": "2025-11-12 16:20:32.350",
  ...
}
```

#### **UDP 廣播 (電腦 → 手機)**
```json
{
  "service": "bio_signal_server",
  "ip": "192.168.43.1",
  "tcp_port": 8000,
  "timestamp": 1762935630.123,
  "status": "online"
}
```

---

## 🔧 測試與工具

### **測試腳本**
```
test_socket_client.py               # Socket 客戶端測試 (87 行)
                                    # - 模擬手機 APP 發送數據
                                    # - 測試 Socket 連接
                                    # - 驗證數據接收
                                    # 使用方式：
                                    #   python3 test_socket_client.py <IP>
```

### **文檔**
```
README.md                           # 專案說明
NEW_EXPERIMENT_README.md            # 新實驗系統使用手冊
BIO_SIGNAL_INTEGRATION.md           # 生理訊號整合說明 (已過時)
PROJECT_STRUCTURE.md                # 本文件 (專案結構說明)
```

### **桌面捷徑**
```
EQ_experiment.desktop               # 舊實驗啟動器
EQ音樂實驗.desktop                   # 舊實驗啟動器 (中文)
```

---

## 📊 實驗數據結構對比

### **舊 EQ 實驗數據**
```
experiment_results/P{ID}_{timestamp}/
  ├─ experiment_info.txt            # 實驗資訊 (純文字)
  ├─ pre_questionnaire.json         # 前測問卷
  ├─ post_questionnaire.json        # 後測問卷
  └─ music_evaluations/             # 音樂評估 (7 維度 × N 首)
      ├─ Classical_EQ.json
      ├─ Classical_Original.json
      └─ ...
```

### **新實驗數據**
```
new_experiment_results/P{ID}_S{N}_G{A/B}_{timestamp}/
  ├─ experiment_info.json           # 實驗配置 (JSON)
  ├─ event_log.csv                  # 事件日誌 (毫秒級)
  ├─ music1_evaluation_*.csv        # 音樂 1 問卷 (3 題)
  ├─ music2_evaluation_*.csv        # 音樂 2 問卷 (3 題)
  ├─ bio_event_log.csv              # 生理訊號事件標記
  └─ bio_result_*.csv               # 9 種生理訊號 (時序數據)
```

---

## 🎯 快速索引

### **我想啟動實驗**
- 舊 EQ 實驗：`python3 armo_eq.py`
- 新實驗（無生理訊號）：`python3 new_experiment.py`
- 新實驗（含生理訊號）：`python3 new_experiment_with_bio.py`

### **我想修改實驗參數**
- 音樂類別與文件：編輯 `music_catalog.json`
- 時間參數：編輯 `ui/ExperimentConfig.py`
- 問卷題目：編輯 `ui/json/new_experiment/music_evaluation_new.json`

### **我想分析數據**
- 舊實驗統計分析：`python3 analyze_script.py`
- 新實驗數據：在 `new_experiment_results/` 或 `sample_data/` 中查看 CSV 文件

### **我想測試生理訊號**
1. 啟動實驗程式並勾選「啟用生理訊號記錄」
2. 在另一個終端執行：`python3 test_socket_client.py 127.0.0.1`
3. 查看 `test_result/` 資料夾中的 CSV 文件

### **我想了解如何使用新實驗系統**
- 詳細說明：閱讀 `NEW_EXPERIMENT_README.md`
- 測試數據範例：查看 `sample_data/` 資料夾

---

## 📝 注意事項

### **文件相容性**
- 舊實驗使用 JSON 格式問卷
- 新實驗使用 CSV 格式記錄
- 兩者數據結構不相容，需分別分析

### **音樂文件命名**
- 舊實驗：`{類別}_EQ.wav` / `{類別}_Original.wav`
- 新實驗：`{代碼}{編號}.wav` (例如：NA001.wav, AB002.wav)

### **生理訊號**
- 僅新實驗系統支援生理訊號記錄
- 需要手機 APP 配合使用
- UDP 廣播功能可讓手機自動發現電腦 IP

### **Debug 模式**
- 新實驗支援 Debug 模式，可快速測試流程
- Debug 模式下所有計時器可立即跳過
- 在 `new_experiment.py` 或 `new_experiment_with_bio.py` 中設定 `DEBUG_MODE = True`

---

## 🔄 版本歷史

- **v1.0** - 舊 EQ 實驗系統完成
- **v2.0** - 新音樂實驗系統開發
- **v2.1** - 生理訊號整合
- **v2.2** - 修復數據寫入問題 (添加 `start_writing()`)
- **v2.3** - 添加 UDP 廣播自動發現功能
- **v2.4** - 完成測試並產生 sample_data

---

## 📧 聯絡資訊

如有問題或建議，請聯絡：airparkchen@gmail.com
