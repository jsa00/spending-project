import os
import sys
import numpy as np
import pandas as pd

DATA_PATH = "data/spending.csv"

def draw_line(char="=", length=40):
    print(char * length)

def load_data(file_path):
    """지정된 경로에서 CSV 데이터 로드"""
    if not os.path.exists(file_path):
        print(f"에러: '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
        sys.exit(1)
        
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    rows, cols = df.shape
    print(f"데이터 로드 완료: {rows}행 x {cols}열")
    draw_line()
    return df

def check_data_structure(df):
    """데이터프레임의 컬럼 자료형 정보 확인"""
    print("[컬럼 정보 (상세 자료형)]")
    for col_name, dtype in df.dtypes.items():
        print(f"- {col_name}: {dtype}")
    draw_line()

def analyze_categories(df):
    """카테고리별 지출 건수와 비율 출력"""
    print("[카테고리별 지출 건수 및 비율(%)]")
    total_rows = len(df)
    category_counts = df["category"].value_counts()

    for cat, count in category_counts.items():
        percentage = (count / total_rows) * 100
        print(f"- {cat}: {count}건 ({percentage:.1f}%)")
    draw_line()

def calculate_category_averages(df):
    """딕셔너리 반복문을 활용한 카테고리별 평균 지출 금액 출력"""
    print("[카테고리별 평균 금액]")
    category_avg_dict = {}

    for cat in df["category"].unique():
        cat_df = df[df["category"] == cat]
        avg_amount = cat_df["amount"].mean()
        category_avg_dict[cat] = avg_amount

    for cat, avg in category_avg_dict.items():
        print(f"- {cat}: {avg:,.0f}원")
    draw_line()
    return category_avg_dict

def analyze_payments(df):
    """결제 수단별(카드/현금) 건수와 전체 대비 비율 출력"""
    print("[결제 수단별 건수 및 비율(%)]")
    total_rows = len(df)
    unique_payments = df["payment"].unique()

    for pay in unique_payments:
        pay_df = df[df["payment"] == pay] 
        count = len(pay_df)
        pct = (count / total_rows) * 100
        print(f"- {pay}: {count}건 ({pct:.1f}%)")
    draw_line()

def diagnose_missing_values(df):
    """결측치 현황(수·비율·심각도) 출력"""
    total_rows = len(df)

    print("[결측치 현황]")
    has_missing_value = False
    null_analysis_result = {
        "clean_columns": [],
        "missing_columns": {}
    }

    for col in df.columns:
        count = df[col].isnull().sum()

        if count >= 1:
            pct = (count / total_rows) * 100

            if pct < 5:
                severity = "낮음"
            elif pct < 20:
                severity = "주의"
            else:
                severity = "높음"
                
            print(f"- {col}: {count}개 ({pct:.1f}%) [심각도: {severity}]")
            has_missing_value = True
            
            null_analysis_result["missing_columns"][col] = {
                "count": count,
                "percentage": f"{pct:.1f}%",
                "severity": severity
            }
        else:
            null_analysis_result["clean_columns"].append(col)
    draw_line()
    return null_analysis_result

def analyze_amount_statistics(df):
    """NumPy로 계산한 5가지 통계량 출력"""
    print("[지출 금액 통계량 - NumPy]")
    clean_amount = df["amount"].dropna()
    amount_arr = np.array(clean_amount)

    np_stats = {
        "mean": np.mean(amount_arr),
        "std": np.std(amount_arr, ddof=1),
        "median": np.median(amount_arr),
        "min": np.min(amount_arr),
        "max": np.max(amount_arr)
    }

    print(f"- 평균 지출액: {np_stats['mean']:,.0f}원")
    print(f"- 표본표준편차: {np_stats['std']:,.0f}원")
    print(f"- 중앙값: {np_stats['median']:,.0f}원")
    print(f"- 최솟값: {np_stats['min']:,.0f}원")
    print(f"- 최댓값: {np_stats['max']:,.0f}원")
    draw_line()
    return np_stats

def verify_with_pandas_describe(df, np_stats):
    """Pandas의 describe() 결과와 NumPy 통계치 상호 교차 검증"""
    print("[Pandas와 NumPy 수치 비교 검증]")
    desc = df["amount"].describe()

    mean_match = "일치" if np.isclose(np_stats["mean"], desc["mean"]) else "불일치"
    std_match = "일치" if np.isclose(np_stats["std"], desc["std"]) else "불일치"
    median_match = "일치" if np.isclose(np_stats["median"], desc["50%"]) else "불일치"
    min_match = "일치" if np.isclose(np_stats["min"], desc["min"]) else "불일치"
    max_match = "일치" if np.isclose(np_stats["max"], desc["max"]) else "불일치"

    print(f"- 평균값 검증: {mean_match}")
    print(f"- 표본표준편차 검증: {std_match}")
    print(f"- 중앙값 검증: {median_match}")
    print(f"- 최솟값 검증: {min_match}")
    print(f"- 최댓값 검증: {max_match}")
    draw_line()

# 메인 제어 흐름
def main():
    """전체 데이터 분석 파이프라인 순서대로 호출"""
    # 1. 데이터 로드 및 초기 구조 확인
    df = load_data(DATA_PATH)
    check_data_structure(df)
    
    # 2. 카테고리별 통계 및 결제수단 건수
    analyze_categories(df)
    calculate_category_averages(df)
    analyze_payments(df)
    
    # 3. 결측치 현황 분석
    diagnose_missing_values(df)
    
    # 4. 데이터 수치 연산 분석 및 교차 검증
    np_stats = analyze_amount_statistics(df)
    verify_with_pandas_describe(df, np_stats)

if __name__ == "__main__":
    main()