import os
import sys
import pandas as pd

DATA_PATH = "data/spending.csv"

# 메인 제어 흐름
def main():
    """전체 데이터 분석 파이프라인 순서대로 호출"""
    # 1. 데이터 로드
    df = load_data(DATA_PATH)

    # 2. 날짜 데이터 정제 및 파생 컬럼
    df = parse_dates(df)

    # 3. 카테고리 표준화
    df = standardize_category(df)

    # 4. 금액 구간 컬럼
    df = add_amount_level(df)

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

def parse_dates(df):
    print("[날짜 데이터(date) 형식 변환]")

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    fail_count = df["date"].isna().sum()
    print(f"- 날짜 형식 변환 실패(NaT) 행 수: {fail_count}개")

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    print("- 파생 컬럼 생성 완료: year, month, day")
    draw_line()
    return df

def standardize_category(df):
    """category 컬럼의 앞뒤 공백을 제거하고 허용 목록 외의 값은 '기타'로 변경"""
    print("[카테고리 표준화]")

    allowed_categories = ["식비", "교통", "쇼핑", "의료", "문화", "기타"]

    def clean_category(val):
        if isinstance(val, str):
            cleaned = val.strip()

            if cleaned in allowed_categories:
                return cleaned
        return "기타"
    
    df["category"] = df["category"].apply(clean_category)
    new_categories = df["category"].value_counts()
    print(f"- 표준화된 카테고리별 건수 집계:\n{new_categories}")
    draw_line()
    return df

def add_amount_level(df):
    """amount 컬럼을 기준에 따라 소액, 중액, 고액 구간으로 분류"""
    print("[금액 구간 파생 컬럼 생성]")

    def get_amount_level(val):
        if pd.isna(val):
            return "미분류"
            
        if val < 10000:
            return "소액"
        elif val < 50000:
            return "중액"
        else:
            return "고액"
        
    df["amount_level"] = df["amount"].apply(get_amount_level)
    level_counts = df["amount_level"].value_counts()
    print(f"- 금액 구간별 건수 집계:\n{level_counts}")
    draw_line()
    return df

if __name__ == "__main__":
    main()