import os
import sys
import pandas as pd

DATA_PATH = "data/spending.csv"

# 메인 제어 흐름
def main():
    """전체 데이터 분석 파이프라인 순서대로 호출"""
    # 1. 데이터 로드
    df = load_data(DATA_PATH)

    # 2. 날짜 데이터 정제 및 파생 컬럼 생성
    df = parse_dates(df)

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
    print()

    print("[생성된 파생 컬럼 미리보기]")
    print(df[["date", "year", "month", "day"]].head(5))

    draw_line()
    return df

if __name__ == "__main__":
    main()