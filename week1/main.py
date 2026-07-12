import os
import sys
import pandas as pd

file_path = "data/spending.csv"

if not os.path.exists(file_path):
    print(f"에러: '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
    sys.exit(1)

df = pd.read_csv(file_path, encoding="utf-8-sig")

rows, cols = df.shape
print(f"데이터 로드 완료: {rows}행 x {cols}열")
print("=" * 40)

print("[컬럼 정보 (상세 자료형)]")
for col_name, dtype in df.dtypes.items():
    print(f"- {col_name}: {dtype}")
print("=" * 40)

print("[데이터 미리보기]")
print(df.head(5))
print("=" * 40)

print("[전체 카테고리별 지출 건수 및 비율]")
category_counts = df["category"].value_counts()

for cat, count in category_counts.items():
    percentage = (count / rows) * 100
    print(f"- {cat}: {count}건 ({percentage:.1f}%)")
print("=" * 40)

print("[결제 수단(카드/현금)별 건수 및 비율]")
unique_payments = df["payment"].unique()

for pay in unique_payments:
    pay_df = df[df["payment"] == pay] 
    count = len(pay_df)
    pct = (count / rows) * 100
    print(f"- {pay}: {count}건 ({pct:.1f}%)")
print("=" * 40)

print("[카테고리별 평균 금액]")
category_avg_dict = {}

for cat in df["category"].unique():
    cat_df = df[df["category"] == cat]
    avg_amount = cat_df["amount"].mean()
    category_avg_dict[cat] = avg_amount

for cat, avg in category_avg_dict.items():
    print(f"- {cat}: {avg:,.0f}원")
print("=" * 40)

print("[컬럼별 결측치가 존재하는 컬럼 정보]")
null_counts = df.isnull().sum()
has_missing_value = False

for col_name, count in null_counts.items():
    if count >= 1:
        pct = (count / rows) * 100
        print(f"- {col_name}: {count}개 ({pct:.1f}%)")
        has_missing_value = True
print("=" * 40)

print("[컬럼별 결측치 정보 및 비율에 따른 심각도 진단]")
has_missing_value = False
null_analysis_result = {
    "clean_columns": [],
    "missing_columns": {}
}

total_rows = len(df)

for col in df.columns:
    count = df[col].isnull().sum()

    if count >= 1:
        pct = (count / rows) * 100

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
print("=" * 40)

if not has_missing_value:
    print("- 결측치가 존재하지 않습니다.")
    print("=" * 40)

print("[결측치가 없는 컬럼 목록]")
if null_analysis_result["clean_columns"]:
    for col in null_analysis_result["clean_columns"]:
        print(f"- {col}")
else:
    print("- 모든 컬럼에 결측치가 존재합니다.")
print("=" * 40)