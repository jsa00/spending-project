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

    # 3. 기본 조회(SELECT)
    query_db()

    # 4. 조건 조회(WHERE + ORDER BY)
    query_db_condition()

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
        amount_level TEXT,                      -- 금액 구간 (소액/중액/고액)
        payment TEXT                            -- 결제 수단
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
    db_columns = ["date", "category", "amount", "memo", "year", "month", "day", "amount_level", "payment"]
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

def query_db():
    """pd.read_sql을 사용하여 데이터베이스 데이터를 조회하고 출력"""
    print("=== 카테고리별 집계 ===")

    conn = sqlite3.connect(DB_PATH)
    pd.set_option('display.float_format', '{:.0f}'.format)
    df_top5 = pd.read_sql("SELECT * FROM spendings LIMIT 5", conn)
    
    summary_query = """
    SELECT 
        category,
        COUNT(*) AS '건수',
        SUM(amount) AS '총지출액',
        AVG(amount) AS '평균지출액',
        MAX(amount) AS '최대지출액'
    FROM spendings
    GROUP BY category
    ORDER BY amount DESC;
    """
    df_summary = pd.read_sql(summary_query, conn)
    print(df_summary.to_string(index=False))

    conn.close()
    print()

def query_db_condition():
    """WHERE로 조건(식비, 3만원 이상 카드 결제)을 걸고 ORDER BY로 정렬(금액 높은 순)해 원하는 데이터만 조회 출력"""
    conn = sqlite3.connect(DB_PATH)
    pd.set_option('display.float_format', '{:.0f}'.format)

    # 특정 카테고리(예: 식비)를 금액 높은 순으로 조회
    print("=== 식비 조회 (금액 높은 순) ===")
    condition_category = """
    SELECT * FROM spendings
    WHERE category = '식비'
    ORDER BY amount DESC;
    """
    df_category = pd.read_sql(condition_category, conn)
    print(df_category.to_string(index=False))
    print()

    print("=== 3만원 이상 & 카드 결제 (금액 높은 순) ===")
    condition_query = """
    SELECT * FROM spendings 
    WHERE amount >= 30000 
        AND payment = '카드'
    ORDER BY amount DESC;
    """
    df_condition = pd.read_sql(condition_query, conn)
    print(df_condition.to_string(index=False))
    print(f"- 3만원 이상 카드 결제 {len(df_condition)}건")
    print()

if __name__ == "__main__":
    main()