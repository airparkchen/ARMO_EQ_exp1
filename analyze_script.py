"""
音樂實驗資料分析系統
採用模組化清潔架構 (Modular Clean Architecture)
作者: AI Assistant
版本: 1.0
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

# ============================================================================
# 配置層 (Configuration Layer)
# ============================================================================

class AnalysisConfig:
    """統一管理所有分析參數和設定值"""
    
    # 檔案處理設定
    DEFAULT_ENCODING = 'utf-8'
    CSV_SEPARATOR = ','
    
    # 統計分析設定
    SIGNIFICANCE_LEVEL = 0.05
    NEAR_SIGNIFICANCE_LEVEL = 0.10
    CONFIDENCE_INTERVAL = 0.95
    
    # 評分量表設定
    RATING_SCALE_MIN = 1
    RATING_SCALE_MAX = 5
    
    # 欄位名稱對應 (可根據未來需求調整)
    SUBJECT_COLUMN = 'subject'
    GENRE_COLUMN = 'genre'
    ROUND_COLUMN = 'round'
    
    # 分析維度設定
    ANALYSIS_DIMENSIONS = {
        'liking': {'flat': 'liking_Flat', 'eq': 'liking_EQ', 'name': '喜好度'},
        'relax': {'flat': 'relax_Flat', 'eq': 'relax_EQ', 'name': '放鬆度'},
        'concentrate': {'flat': 'concentrate_Flat', 'eq': 'concentrate_EQ', 'name': '專注度'}
    }
    
    # 音樂類型 (可動態擴展)
    DEFAULT_GENRES = ['古典', '流行', '爵士']
    
    # 輸出格式設定
    DECIMAL_PLACES = 2
    P_VALUE_DECIMAL_PLACES = 3

class OutputConfig:
    """輸出格式和樣式設定"""
    
    # 報告格式
    REPORT_HEADER = "=== 音樂實驗資料分析報告 ==="
    SECTION_SEPARATOR = "=" * 50
    SUBSECTION_SEPARATOR = "-" * 30
    
    # 統計顯著性標示
    SIGNIFICANCE_MARKERS = {
        'highly_significant': '**',  # p < 0.01
        'significant': '*',          # p < 0.05
        'near_significant': '†',     # p < 0.10
        'not_significant': ''        # p >= 0.10
    }

# ============================================================================
# 資料層 (Data Layer)
# ============================================================================

@dataclass
class SubjectData:
    """個別受試者資料模型"""
    subject_id: str
    round_number: int
    genre: str
    responses: Dict[str, Any]
    
    def get_response(self, dimension: str, condition: str) -> Optional[float]:
        """取得特定維度和條件的回應值"""
        key = f"{dimension}_{condition}"
        return self.responses.get(key)

@dataclass
class StatisticalResult:
    """統計分析結果模型"""
    dimension: str
    genre: str
    flat_mean: float
    eq_mean: float
    flat_std: float
    eq_std: float
    mean_difference: float
    t_statistic: float
    p_value: float
    degrees_freedom: int
    effect_size: float
    sample_size: int
    
    def is_significant(self) -> bool:
        return self.p_value < AnalysisConfig.SIGNIFICANCE_LEVEL
    
    def is_near_significant(self) -> bool:
        return self.p_value < AnalysisConfig.NEAR_SIGNIFICANCE_LEVEL
    
    def get_significance_level(self) -> str:
        if self.p_value < 0.01:
            return 'highly_significant'
        elif self.p_value < 0.05:
            return 'significant'
        elif self.p_value < 0.10:
            return 'near_significant'
        else:
            return 'not_significant'

class ExperimentDataModel:
    """實驗資料核心模型"""
    
    def __init__(self):
        self.subjects_data: List[SubjectData] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_subject_data(self, subject_data: SubjectData):
        """新增受試者資料"""
        self.subjects_data.append(subject_data)
    
    def get_subjects_by_genre(self, genre: str) -> List[SubjectData]:
        """根據音樂類型篩選資料"""
        return [data for data in self.subjects_data if data.genre == genre]
    
    def get_subjects_by_name(self, subject_name: str) -> List[SubjectData]:
        """根據受試者姓名篩選資料"""
        return [data for data in self.subjects_data if data.subject_id == subject_name]
    
    def get_unique_genres(self) -> List[str]:
        """取得所有音樂類型"""
        return list(set(data.genre for data in self.subjects_data))
    
    def get_unique_subjects(self) -> List[str]:
        """取得所有受試者名單"""
        return list(set(data.subject_id for data in self.subjects_data))

# ============================================================================
# 服務層 (Service Layer)
# ============================================================================

class DataLoaderService:
    """資料載入服務"""
    
    @staticmethod
    def load_csv_data(file_path: str) -> ExperimentDataModel:
        """
        載入 CSV 檔案並轉換為實驗資料模型
        
        Args:
            file_path: CSV 檔案路徑
            
        Returns:
            ExperimentDataModel: 實驗資料模型實例
        """
        try:
            # 讀取 CSV 檔案
            df = pd.read_csv(file_path, encoding=AnalysisConfig.DEFAULT_ENCODING)
            
            # 建立資料模型
            experiment_data = ExperimentDataModel()
            
            # 處理每一行資料
            for _, row in df.iterrows():
                # 將 row 轉換為字典，排除索引欄位
                responses = {col: row[col] for col in df.columns if col not in ['', 'subject', 'round', 'genre']}
                
                subject_data = SubjectData(
                    subject_id=str(row[AnalysisConfig.SUBJECT_COLUMN]),
                    round_number=int(row[AnalysisConfig.ROUND_COLUMN]),
                    genre=str(row[AnalysisConfig.GENRE_COLUMN]),
                    responses=responses
                )
                
                experiment_data.add_subject_data(subject_data)
            
            # 設定元資料
            experiment_data.metadata = {
                'total_records': len(df),
                'unique_subjects': len(df[AnalysisConfig.SUBJECT_COLUMN].unique()),
                'genres': df[AnalysisConfig.GENRE_COLUMN].unique().tolist(),
                'columns': df.columns.tolist()
            }
            
            return experiment_data
            
        except Exception as e:
            raise ValueError(f"載入資料時發生錯誤: {str(e)}")

class StatisticalAnalysisService:
    """統計分析服務"""
    
    @staticmethod
    def paired_t_test(flat_values: List[float], eq_values: List[float]) -> Tuple[float, float, int]:
        """
        執行配對 t 檢定
        
        Args:
            flat_values: Flat 條件的數值
            eq_values: EQ 條件的數值
            
        Returns:
            Tuple[float, float, int]: (t統計量, p值, 自由度)
        """
        if len(flat_values) != len(eq_values) or len(flat_values) < 2:
            return np.nan, np.nan, 0
        
        # 執行配對 t 檢定
        t_stat, p_value = stats.ttest_rel(eq_values, flat_values)
        df = len(flat_values) - 1
        
        return t_stat, p_value, df
    
    @staticmethod
    def calculate_effect_size(flat_values: List[float], eq_values: List[float]) -> float:
        """
        計算 Cohen's d 效果量
        
        Args:
            flat_values: Flat 條件的數值
            eq_values: EQ 條件的數值
            
        Returns:
            float: Cohen's d 效果量
        """
        if len(flat_values) != len(eq_values) or len(flat_values) < 2:
            return np.nan
        
        # 計算平均差異
        differences = np.array(eq_values) - np.array(flat_values)
        mean_diff = np.mean(differences)
        
        # 計算合併標準差
        flat_std = np.std(flat_values, ddof=1)
        eq_std = np.std(eq_values, ddof=1)
        pooled_std = np.sqrt((flat_std**2 + eq_std**2) / 2)
        
        # 計算 Cohen's d
        if pooled_std == 0:
            return 0
        
        return abs(mean_diff) / pooled_std
    
    @staticmethod
    def analyze_dimension_by_genre(experiment_data: ExperimentDataModel, 
                                 dimension: str, genre: str) -> StatisticalResult:
        """
        分析特定維度和音樂類型的統計結果
        
        Args:
            experiment_data: 實驗資料模型
            dimension: 分析維度 (如 'liking', 'relax', 'concentrate')
            genre: 音樂類型
            
        Returns:
            StatisticalResult: 統計分析結果
        """
        # 取得該類型音樂的所有資料
        genre_data = experiment_data.get_subjects_by_genre(genre)
        
        if not genre_data:
            raise ValueError(f"找不到音樂類型 '{genre}' 的資料")
        
        # 取得維度設定
        dim_config = AnalysisConfig.ANALYSIS_DIMENSIONS.get(dimension)
        if not dim_config:
            raise ValueError(f"未知的分析維度: {dimension}")
        
        # 提取數值
        flat_values = []
        eq_values = []
        
        for data in genre_data:
            flat_val = data.get_response(dimension, 'Flat')
            eq_val = data.get_response(dimension, 'EQ')
            
            if flat_val is not None and eq_val is not None:
                flat_values.append(float(flat_val))
                eq_values.append(float(eq_val))
        
        if len(flat_values) < 2:
            raise ValueError(f"資料量不足，無法進行統計分析")
        
        # 計算基本統計量
        flat_mean = np.mean(flat_values)
        eq_mean = np.mean(eq_values)
        flat_std = np.std(flat_values, ddof=1)
        eq_std = np.std(eq_values, ddof=1)
        mean_difference = eq_mean - flat_mean
        
        # 執行統計檢定
        t_stat, p_value, df = StatisticalAnalysisService.paired_t_test(flat_values, eq_values)
        
        # 計算效果量
        effect_size = StatisticalAnalysisService.calculate_effect_size(flat_values, eq_values)
        
        return StatisticalResult(
            dimension=dimension,
            genre=genre,
            flat_mean=flat_mean,
            eq_mean=eq_mean,
            flat_std=flat_std,
            eq_std=eq_std,
            mean_difference=mean_difference,
            t_statistic=t_stat,
            p_value=p_value,
            degrees_freedom=df,
            effect_size=effect_size,
            sample_size=len(flat_values)
        )

class ReportGeneratorService:
    """報告生成服務"""
    
    @staticmethod
    def generate_comprehensive_report(experiment_data: ExperimentDataModel) -> str:
        """
        生成完整的分析報告
        
        Args:
            experiment_data: 實驗資料模型
            
        Returns:
            str: 完整報告文字
        """
        report_lines = []
        
        # 報告標題
        report_lines.append(OutputConfig.REPORT_HEADER)
        report_lines.append("")
        
        # 實驗概況
        report_lines.append("**實驗設計概況**")
        report_lines.append(f"- 總參與人數: {experiment_data.metadata['unique_subjects']} 人")
        report_lines.append(f"- 音樂類型: {', '.join(experiment_data.metadata['genres'])}")
        report_lines.append(f"- 總資料筆數: {experiment_data.metadata['total_records']} 筆")
        
        # 計算每種音樂類型的樣本數
        genre_counts = {}
        for genre in experiment_data.get_unique_genres():
            genre_counts[genre] = len(experiment_data.get_subjects_by_genre(genre))
        
        report_lines.append("- 各音樂類型樣本數:")
        for genre, count in genre_counts.items():
            report_lines.append(f"  * {genre}: {count} 筆")
        
        report_lines.append("")
        
        # 詳細分析結果
        report_lines.append("**詳細分析結果**")
        report_lines.append("")
        
        for genre in experiment_data.get_unique_genres():
            report_lines.append(f"**{genre}音樂**")
            
            for dimension_key, dimension_config in AnalysisConfig.ANALYSIS_DIMENSIONS.items():
                try:
                    result = StatisticalAnalysisService.analyze_dimension_by_genre(
                        experiment_data, dimension_key, genre
                    )
                    
                    # 判斷方向性
                    if abs(result.mean_difference) < 0.01:
                        direction = "無差異"
                    elif result.mean_difference > 0:
                        direction = "EQ 略高"
                    else:
                        direction = "EQ 略低"
                    
                    # 判斷顯著性
                    significance_level = result.get_significance_level()
                    significance_text = {
                        'highly_significant': '差異高度顯著**',
                        'significant': '差異顯著*',
                        'near_significant': '差異接近顯著',
                        'not_significant': '差異不顯著'
                    }[significance_level]
                    
                    # 格式化輸出
                    dimension_name = dimension_config['name']
                    flat_mean = round(result.flat_mean, AnalysisConfig.DECIMAL_PLACES)
                    eq_mean = round(result.eq_mean, AnalysisConfig.DECIMAL_PLACES)
                    p_value = round(result.p_value, AnalysisConfig.P_VALUE_DECIMAL_PLACES)
                    
                    report_lines.append(
                        f"   * {dimension_name}：Flat 平均 {flat_mean}，EQ 平均 {eq_mean}，"
                        f"{direction}，{significance_text} (p = {p_value})"
                    )
                    
                except Exception as e:
                    report_lines.append(f"   * {dimension_config['name']}：分析錯誤 - {str(e)}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    @staticmethod
    def generate_statistical_summary(experiment_data: ExperimentDataModel) -> Dict[str, Any]:
        """
        生成統計摘要資料 (JSON 格式)
        
        Args:
            experiment_data: 實驗資料模型
            
        Returns:
            Dict[str, Any]: 統計摘要字典
        """
        summary = {
            'metadata': experiment_data.metadata,
            'results': {}
        }
        
        for genre in experiment_data.get_unique_genres():
            summary['results'][genre] = {}
            
            for dimension_key, dimension_config in AnalysisConfig.ANALYSIS_DIMENSIONS.items():
                try:
                    result = StatisticalAnalysisService.analyze_dimension_by_genre(
                        experiment_data, dimension_key, genre
                    )
                    
                    summary['results'][genre][dimension_key] = {
                        'dimension_name': dimension_config['name'],
                        'flat_mean': round(result.flat_mean, AnalysisConfig.DECIMAL_PLACES),
                        'eq_mean': round(result.eq_mean, AnalysisConfig.DECIMAL_PLACES),
                        'flat_std': round(result.flat_std, AnalysisConfig.DECIMAL_PLACES),
                        'eq_std': round(result.eq_std, AnalysisConfig.DECIMAL_PLACES),
                        'mean_difference': round(result.mean_difference, AnalysisConfig.DECIMAL_PLACES),
                        't_statistic': round(result.t_statistic, AnalysisConfig.DECIMAL_PLACES),
                        'p_value': round(result.p_value, AnalysisConfig.P_VALUE_DECIMAL_PLACES),
                        'effect_size': round(result.effect_size, AnalysisConfig.DECIMAL_PLACES),
                        'sample_size': result.sample_size,
                        'is_significant': result.is_significant(),
                        'significance_level': result.get_significance_level()
                    }
                    
                except Exception as e:
                    summary['results'][genre][dimension_key] = {
                        'error': str(e)
                    }
        
        return summary

# ============================================================================
# 介面層 (Interface Layer)
# ============================================================================

class MusicExperimentAnalyzer:
    """音樂實驗分析主控制器"""
    
    def __init__(self):
        self.experiment_data: Optional[ExperimentDataModel] = None
    
    def load_data(self, csv_file_path: str) -> None:
        """
        載入實驗資料
        
        Args:
            csv_file_path: CSV 檔案路徑
        """
        self.experiment_data = DataLoaderService.load_csv_data(csv_file_path)
        print(f"成功載入資料：{self.experiment_data.metadata['total_records']} 筆記錄")
    
    def analyze_all(self) -> str:
        """
        執行完整分析並返回報告
        
        Returns:
            str: 完整分析報告
        """
        if self.experiment_data is None:
            raise ValueError("請先載入資料")
        
        return ReportGeneratorService.generate_comprehensive_report(self.experiment_data)
    
    def get_statistical_summary(self) -> Dict[str, Any]:
        """
        取得統計摘要 (字典格式)
        
        Returns:
            Dict[str, Any]: 統計摘要
        """
        if self.experiment_data is None:
            raise ValueError("請先載入資料")
        
        return ReportGeneratorService.generate_statistical_summary(self.experiment_data)
    
    def analyze_by_genre(self, genre: str) -> str:
        """
        分析特定音樂類型
        
        Args:
            genre: 音樂類型
            
        Returns:
            str: 該音樂類型的分析結果
        """
        if self.experiment_data is None:
            raise ValueError("請先載入資料")
        
        if genre not in self.experiment_data.get_unique_genres():
            raise ValueError(f"找不到音樂類型 '{genre}'")
        
        report_lines = [f"**{genre}音樂分析結果**", ""]
        
        for dimension_key, dimension_config in AnalysisConfig.ANALYSIS_DIMENSIONS.items():
            try:
                result = StatisticalAnalysisService.analyze_dimension_by_genre(
                    self.experiment_data, dimension_key, genre
                )
                
                report_lines.append(
                    f"{dimension_config['name']}："
                    f"Flat M={result.flat_mean:.2f} (SD={result.flat_std:.2f}), "
                    f"EQ M={result.eq_mean:.2f} (SD={result.eq_std:.2f}), "
                    f"t({result.degrees_freedom})={result.t_statistic:.2f}, "
                    f"p={result.p_value:.3f}, "
                    f"d={result.effect_size:.2f}"
                )
                
            except Exception as e:
                report_lines.append(f"{dimension_config['name']}：分析錯誤 - {str(e)}")
        
        return "\n".join(report_lines)
    
    def analyze_by_subject(self, subject_name: str) -> str:
        """
        分析特定受試者的資料
        
        Args:
            subject_name: 受試者姓名
            
        Returns:
            str: 該受試者的分析結果
        """
        if self.experiment_data is None:
            raise ValueError("請先載入資料")
        
        subject_data = self.experiment_data.get_subjects_by_name(subject_name)
        if not subject_data:
            raise ValueError(f"找不到受試者 '{subject_name}'")
        
        report_lines = [f"**受試者 {subject_name} 分析結果**", ""]
        
        for data in subject_data:
            report_lines.append(f"Round {data.round_number} - {data.genre}音樂:")
            
            for dimension_key, dimension_config in AnalysisConfig.ANALYSIS_DIMENSIONS.items():
                flat_val = data.get_response(dimension, 'Flat')
                eq_val = data.get_response(dimension, 'EQ')
                
                if flat_val is not None and eq_val is not None:
                    diff = eq_val - flat_val
                    report_lines.append(
                        f"  {dimension_config['name']}: Flat={flat_val}, EQ={eq_val}, 差異={diff:+.1f}"
                    )
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def export_results(self, output_path: str, format_type: str = 'json') -> None:
        """
        匯出分析結果
        
        Args:
            output_path: 輸出檔案路徑
            format_type: 檔案格式 ('json' 或 'txt')
        """
        if self.experiment_data is None:
            raise ValueError("請先載入資料")
        
        if format_type.lower() == 'json':
            summary = self.get_statistical_summary()
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
        
        elif format_type.lower() == 'txt':
            report = self.analyze_all()
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        else:
            raise ValueError("支援的格式: 'json' 或 'txt'")
        
        print(f"結果已匯出至: {output_path}")

# ============================================================================
# 使用範例和測試程式碼
# ============================================================================

def main():
    """主程式 - 使用範例"""
    
    # 建立分析器實例
    analyzer = MusicExperimentAnalyzer()
    
    try:
        # 載入資料
        analyzer.load_data('total.csv')
        
        # 執行完整分析
        print("=== 完整分析報告 ===")
        full_report = analyzer.analyze_all()
        print(full_report)
        
        print("\n" + "="*50 + "\n")
        
        # 分析特定音樂類型
        print("=== 古典音樂詳細分析 ===")
        classical_analysis = analyzer.analyze_by_genre('古典')
        print(classical_analysis)
        
        print("\n" + "="*50 + "\n")
        
        # 取得統計摘要
        print("=== 統計摘要 (字典格式) ===")
        summary = analyzer.get_statistical_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        
        # 匯出結果
        # analyzer.export_results('analysis_results.json', 'json')
        # analyzer.export_results('analysis_report.txt', 'txt')
        
    except Exception as e:
        print(f"分析過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()
