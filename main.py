import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="MBTI by Country – Top 5", layout="centered")

# 제목 꾸미기
st.title("🌍 MBTI by Country")
st.markdown("### 📊 데이터 상위 5줄 미리보기")

# CSV 파일명 지정
CSV_FILE = "countriesMBTI_16types.csv"

# 현재 폴더 내 경로 확인
target_path = Path(__file__).parent / CSV_FILE

if not target_path.exists():
    st.error(f"파일 `{CSV_FILE}`을(를) 찾을 수 없습니다. 같은 폴더에 파일이 있는지 확인해주세요.")
    st.stop()

# CSV 불러오기
try:
    df = pd.read_csv(target_path)
except Exception as e:
    st.error(f"CSV를 읽는 중 오류 발생: {e}")
    st.stop()

# 상위 5행 출력
st.dataframe(df.head(5), use_container_width=True)
st.caption(f"파일: `{target_path.name}` · 전체 행: {len(df):,} · 열: {len(df.columns)}")

# 실행 방법 (터미널):
# streamlit run app.py
