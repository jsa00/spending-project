import os
import sys
import sqlite3
import pandas as pd

DATA_PATH = "data/spending_cleaned.csv"
DB_PATH = "data/spending.db"

# 메인 제어 흐름
def main():
    """전체 데이터 분석 파이프라인 순서대로 호출"""
    # 0. 데이터 로드
    df = load_clean_data(DATA_PATH)

    # 1. DB 연결 및 테이블 생성
    init_db()

    # 2. 정제 데이터 저장
    save_to_db(df)

def load_clean_data(file_path):
    """지정된 경로에서 정제된 CSV 데이터 로드"""
    if not os.path.exists(file_path):
        print(f"에러: '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
        sys.exit(1)
        
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    rows, cols = df.shape
    print(f"데이터 로드 완료: {rows}행 x {cols}열")
    return df

def init_db():
    """데이터베이스 초기화 및 연결, 테이블 생성"""
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS spendings")
    
    create_table_query = """
    CREATE TABLE spendings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 고유 식별자(자동 증가)
        date TEXT NOT NULL,                     -- 지출 날짜 (YYYY-MM-DD)
        category TEXT NOT NULL,                 -- 지출 분류
        amount REAL NOT NULL,                   -- 지출 금액
        memo TEXT,                              -- 지출 메모
        year INTEGER,                           -- 년도 (분석용)
        month INTEGER,                          -- 월 (분석용)
        day INTEGER,                            -- 일 (분석용)
        amount_level TEXT                       -- 금액 구간 (소액/중액/고액)
    );
    """
    cursor.execute(create_table_query)
    
    conn.commit()
    conn.close()
    print("테이블 생성 완료")

def save_to_db(df):
    """정제 완료된 데이터를 SQLite 테이블에 저장, 저장된 행 수 검증"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    df_db = df.copy()
    db_columns = ["date", "category", "amount", "memo", "year", "month", "day", "amount_level"]
    df_db = df_db[db_columns]

    df_db["year"] = df_db["year"].astype(float).astype(int)
    df_db["month"] = df_db["month"].astype(float).astype(int)
    df_db["day"] = df_db["day"].astype(float).astype(int)

    df_db.to_sql("spendings", conn, if_exists="append", index=False)
    
    inserted_rows = len(df_db)
    cursor.execute("SELECT COUNT(*) FROM spendings")
    total_rows = cursor.fetchone()[0]
    print(f"{inserted_rows}행 저장 완료 (DB 내 행 수: {total_rows})")

    conn.commit()
    conn.close()
    print()

if __name__ == "__main__":
    main()