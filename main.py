import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="MBTI by Country – Top 5", layout="centered")
st.title("MBTI by Country — 상위 5행 미리보기")

# 같은 폴더에 있는 CSV 파일명 (필요하면 바꿔주세요)
DEFAULT_CSV = "mbti_by_country.csv"

# 파일 탐색: 기본 파일명 우선, 없으면 폴더 내 첫 번째 CSV로 대체
cwd = Path(__file__).parent
target_path = cwd / DEFAULT_CSV

if not target_path.exists():
    csv_candidates = sorted(cwd.glob("*.csv"))
    if csv_candidates:
        target_path = csv_candidates[0]
        st.info(f"기본 파일 `{DEFAULT_CSV}`을(를) 찾지 못해, 폴더 내 첫 번째 CSV(`{target_path.name}`)를 사용합니다.")
    else:
        st.error("같은 폴더에서 CSV 파일을 찾지 못했습니다. CSV를 추가하거나 파일명을 확인하세요.")
        st.stop()

# CSV 로드 및 상위 5행 표시
try:
    df = pd.read_csv(target_path)
except Exception as e:
    st.error(f"CSV를 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

st.dataframe(df.head(5), use_container_width=True)
st.caption(f"파일: `{target_path.name}` · 전체 행: {len(df):,} · 열: {len(df.columns)}")

# 실행 방법 (터미널):
# streamlit run app.py
