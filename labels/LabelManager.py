import json

class LabelManager:
    def __init__(self, label_file_path):
        self.page_configs = self.load_label_configs(label_file_path)
        self.current_label = None

    def load_label_configs(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                configs = json.load(file)
                return configs
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"載入標籤配置失敗: {e}")
            return []

    def get_label_for_page(self, page_index):
        # 根據頁面的索引獲取對應的標籤配置
        for config in self.page_configs:
            if config["page"] == page_index:
                self.current_label = config
                return config
        return None

    def get_current_label(self):
        # 獲取當前頁面的標籤
        if self.current_label:
            return self.current_label.get("label", None)
        return None
