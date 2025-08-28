# create_questionnaires.py
import os
import json

def create_questionnaire_jsons():
    # 創建目錄
    output_dir = "./ui/json/eq_experiment/"
    os.makedirs(output_dir, exist_ok=True)
    
    # 前測問卷 - 修正為 tvghQuestionnairePage 預期格式
    pre_questionnaire = [
        {
            "question": "您的年齡區間？",
            "options": [
                "18-25 歲",
                "26-35 歲", 
                "36-45 歲",
                "46-55 歲",
                "56 歲以上"
            ],
            "first_round_only": True
        },
        {
            "question": "您平均多久聽一次音樂？",
            "options": [
                "每天都聽",
                "幾乎每天（一週5-6次）",
                "經常聽（一週3-4次）",
                "偶爾聽（一週1-2次）",
                "很少聽（一個月幾次）"
            ],
            "first_round_only": True
        },
        {
            "question": "您平時最喜歡的音樂類型是？（可複選）",
            "options": [
                "流行音樂（Pop）",
                "搖滾音樂（Rock）",
                "電子音樂（Electronic）",
                "古典音樂（Classical）",
                "爵士音樂（Jazz）",
                "嘻哈音樂（Hip-hop）",
                "民謠音樂（Folk）",
                "其他"
            ],
            "first_round_only": True
        },
        {
            "question": "請描述您目前的心情狀態",
            "options": [
                "非常正面愉快",
                "有點正面愉快", 
                "普通中性",
                "有點負面低落",
                "非常負面低落"
            ],
            "first_round_only": False
        },
        {
            "question": "您目前的聆聽環境噪音程度",
            "options": [
                "非常安靜",
                "有點安靜",
                "普通", 
                "有點吵雜",
                "非常吵雜"
            ],
            "first_round_only": True
        }
    ]
    
    # 音樂評估問卷
    music_evaluation = [
        {
            "question": "您覺得這段音樂的喜好程度如何？",
            "options": [
                "1 - 非常不喜歡",
                "2 - 不喜歡", 
                "3 - 普通",
                "4 - 喜歡",
                "5 - 非常喜歡"
            ]
        },
        {
            "question": "聆聽這段音樂時，您感到多放鬆？",
            "options": [
                "1 - 完全不放鬆",
                "2 - 有點不放鬆",
                "3 - 普通",
                "4 - 有點放鬆", 
                "5 - 非常放鬆"
            ]
        },
        {
            "question": "您覺得這段音樂的音量（響度）如何？",
            "options": [
                "1 - 非常小聲",
                "2 - 有點小聲",
                "3 - 剛剛好",
                "4 - 有點大聲",
                "5 - 非常大聲"
            ]
        },
        {
            "question": "您之前是否聽過這首音樂？",
            "options": [
                "是，聽過",
                "否，沒聽過"
            ]
        },
        {
            "question": "聆聽這段音樂時，您的專注程度如何？",
            "options": [
                "1 - 完全無法專注聆聽",
                "2 - 大部分時間不專注",
                "3 - 普通",
                "4 - 大部分時間都專注",
                "5 - 完全專注聆聽"
            ]
        }
    ]
    
    # 後測問卷
    post_questionnaire = [
        {
            "question": "整體而言，您比較喜歡哪一段？",
            "options": [
                "偏好 A 段音樂",
                "沒有差別",
                "偏好 B 段音樂"
            ]
        },
        {
            "question": "在放鬆效果上，您覺得哪一段音樂更能讓您感到放鬆？",
            "options": [
                "A 段音樂比較放鬆",
                "沒有差別",
                "B 段音樂比較放鬆"
            ]
        },
        {
            "question": "您覺得這兩段音樂聽起來有明顯差異嗎？", 
            "options": [
                "有非常明顯的差異",
                "有一些差異",
                "有細微差異",
                "幾乎沒有差異",
                "完全沒有差異"
            ]
        }
    ]
    
    # 保存檔案
    questionnaires = {
        "pre_questionnaire.json": pre_questionnaire,
        "music_evaluation.json": music_evaluation,
        "post_questionnaire.json": post_questionnaire
    }
    
    for filename, data in questionnaires.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"創建問卷: {filepath}")

if __name__ == "__main__":
    create_questionnaire_jsons()
    print("問卷檔案創建完成！")