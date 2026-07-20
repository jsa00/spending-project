import os
import sys
import pandas as pd
import sqlite3

DATA_PATH = "data/spending.csv"
NEW_DATA_PATH = "data/spending_cleaned.csv"
DB_PATH = "data/spending.db"

# 메인 제어 흐름
def main():
    """전체 데이터 분석 파이프라인 순서대로 호출"""
    # 0. Pandas 출력 포맷 설정
    pd.set_option('display.float_format', '{:.0f}'.format)

    # 1. 로드
    df = load_data(DATA_PATH)
    dfc = load_clean_data(NEW_DATA_PATH)

    # 3. DB 저장
    init_db()
    save_to_db(dfc)

    # 2. 정리
    parse_dates(df)
    standardize_category(df)
    add_amount_level(df)
    clean_values(df)

    # 4. 조회
    query_db()
    query_db_aggregation()

    # (선택) 카드/현금 요일별 심화 분석
    query_payment_by_month()
    query_by_day_of_week()

    # 5. 검증
    verify_with_python(dfc)


def load_data(file_path):
    """지정된 경로에서 CSV 데이터 로드"""
    if not os.path.exists(file_path):
        print(f"에러: '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
        sys.exit(1)
        
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    rows, cols = df.shape
    print(f"[1] 데이터 로드 완료: {rows}행 x {cols}열")
    return df

def parse_dates(df):
    print("=== 날짜 데이터(date) 형식 변환 ===")

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    fail_count = df["date"].isna().sum()
    print(f"- 날짜 형식 변환 실패(NaT) 행 수: {fail_count}개")

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    print("- 파생 컬럼 생성 완료: year, month, day")
    print()
    return df

def standardize_category(df):
    """category 컬럼의 앞뒤 공백을 제거하고 허용 목록 외의 값은 '기타'로 변경"""
    print("=== 카테고리 표준화 ===")

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
    print()
    return df

def add_amount_level(df):
    """amount 컬럼을 기준에 따라 소액, 중액, 고액 구간으로 분류"""
    print("=== 금액 구간 파생 컬럼 생성 ===")

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
    print()
    return df

def clean_values(df):
    """메모 결측치를 채우고, 금액이 0 이하이거나 날짜 변환에 실패한 행을 제거"""
    print("=== 결측·이상값 처리 ===")

    df["memo"] = df["memo"].fillna("")

    before_count = len(df)
    df = df[df["amount"] > 0]
    df = df.dropna(subset=["date"])
    df = df.reset_index(drop=True)

    after_count = len(df)
    removed_count = before_count - after_count
    
    print(f"- 정제 전 데이터 크기: {before_count}행")
    print(f"- 정제 후 데이터 크기: {after_count}행 (총 {removed_count}개 행 제거됨)")
    print()
    
    return df

def load_clean_data(file_path):
    """지정된 경로에서 정제된 CSV 데이터 로드"""
    if not os.path.exists(file_path):
        print(f"에러: '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
        sys.exit(1)
        
    dfc = pd.read_csv(file_path, encoding="utf-8-sig")
    rows, cols = dfc.shape
    print(f"[2] 데이터 로드 완료: {rows}행 x {cols}열")
    return dfc

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

def save_to_db(dfc):
    """정제 완료된 데이터를 SQLite 테이블에 저장, 저장된 행 수 검증"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    dfc_db = dfc.copy()
    db_columns = ["date", "category", "amount", "memo", "year", "month", "day", "amount_level", "payment"]
    dfc_db = dfc_db[db_columns]

    dfc_db["year"] = dfc_db["year"].astype(float).astype(int)
    dfc_db["month"] = dfc_db["month"].astype(float).astype(int)
    dfc_db["day"] = dfc_db["day"].astype(float).astype(int)

    dfc_db.to_sql("spendings", conn, if_exists="append", index=False)
    
    inserted_rows = len(dfc_db)
    cursor.execute("SELECT COUNT(*) FROM spendings")
    total_rows = cursor.fetchone()[0]
    print(f"[3] {inserted_rows}행 저장 완료 (DB 내 행 수: {total_rows})")

    conn.commit()
    conn.close()
    print()

def query_db():
    """pd.read_sql을 사용하여 데이터베이스 데이터를 조회하고 출력"""
    print("=== 카테고리별 집계 ===")

    conn = sqlite3.connect(DB_PATH)
    
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
    dfc_summary = pd.read_sql(summary_query, conn)
    print(dfc_summary.to_string(index=False))

    conn.close()
    print()

def query_db_aggregation():
    """GROUP BY로 월별 지출을 집계"""
    print("=== 월별 총 지출 ===")

    conn = sqlite3.connect(DB_PATH)

    aggregation_query = """
    SELECT 
        month,
        COUNT(*) AS '건수',
        SUM(amount) AS '총지출액'
    FROM spendings
    GROUP BY month
    ORDER BY month ASC;
    """
    dfc_aggregation = pd.read_sql(aggregation_query, conn)
    print(dfc_aggregation.to_string(index=False))
    
    conn.close()
    print()

def verify_with_python(dfc):
    """파이썬 계산 결과와 SQL 집계 결과를 하나로 합쳐서 일치 여부 검증"""
    print("=== Python vs SQL 검증 ===")

    conn = sqlite3.connect(DB_PATH)
    dfc_py = dfc.groupby("category")["amount"].sum().reset_index()
    dfc_py.columns = ["category", "총지출액_파이썬"]

    sql_query = """
    SELECT category, SUM(amount) AS '총지출액_SQL'
    FROM spendings
    GROUP BY category;
    """
    dfc_sql = pd.read_sql(sql_query, conn)
    conn.close()

    dfc_merged = pd.merge(dfc_py, dfc_sql, on="category")
    is_match = (dfc_merged["총지출액_파이썬"].round(0) == dfc_merged["총지출액_SQL"].round(0)).all()
    print(f"전체 카테고리 일치: {is_match}")

def query_payment_by_month():
    """SQL 월별 카드 vs 현금 지출 금액 비교"""
    print("=== 월별 결제 수단(카드 vs 현금) 지출 비교 ===")

    conn = sqlite3.connect(DB_PATH)

    payment_query = """
    SELECT 
        month AS '월',
        SUM(CASE WHEN payment = '카드' THEN amount ELSE 0 END) AS '카드 지출',
        SUM(CASE WHEN payment = '현금' THEN amount ELSE 0 END) AS '현금 지출',
        SUM(amount) AS '합계'
    FROM spendings
    GROUP BY month
    ORDER BY month ASC;
    """
    dfc_payment = pd.read_sql(payment_query, conn)
    print(dfc_payment.to_string(index=False))

    conn.close()
    print()

def query_by_day_of_week():
    """요일별 건수, 평균, 총지출액 집계 출력"""
    print("=== 요일별 지출 집계 (평균 및 총지출) ===")

    conn = sqlite3.connect(DB_PATH)

    day_query = """
    SELECT 
        CASE strftime('%w', date)
            WHEN '0' THEN '일요일'
            WHEN '1' THEN '월요일'
            WHEN '2' THEN '화요일'
            WHEN '3' THEN '수요일'
            WHEN '4' THEN '목요일'
            WHEN '5' THEN '금요일'
            WHEN '6' THEN '토요일'
        END AS '요일',
        COUNT(*) AS '건수',
        AVG(amount) AS '평균지출액',
        SUM(amount) AS '총지출액'
    FROM spendings
    GROUP BY strftime('%w', date)
    ORDER BY strftime('%w', date) ASC;
    """
    dfc_day = pd.read_sql(day_query, conn)
    print(dfc_day.to_string(index=False))

    conn.close()
    print()

if __name__ == "__main__":
    main()