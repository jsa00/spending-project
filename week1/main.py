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
print("-" * 30)

print(df.head())