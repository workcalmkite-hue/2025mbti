import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="MBTI 상위 10 유형", layout="centered")

st.title("🌟 MBTI 유형 분석")
st.markdown("### 📊 전 세계 MBTI 평균 상위 10개 유형")

# CSV 파일명
CSV_FILE = "countriesMBTI_16types.csv"
target_path = Path(__file__).parent / CSV_FILE

if not target_path.exists():
    st.error(f"파일 `{CSV_FILE}`을(를) 찾을 수 없습니다.")
    st.stop()

# 데이터 불러오기
df = pd.read_csv(target_path)

# 'Country' 제외하고 MBTI 타입만 선택
mbti_cols = [col for col in df.columns if col != "Country"]

# MBTI 유형별 평균값 계산
mbti_means = df[mbti_cols].mean().sort_values(ascending=False)

# 상위 10개 선택
top10 = mbti_means.head(10).reset_index()
top10.columns = ["MBTI", "Average"]

# Altair 막대그래프
chart = (
    alt.Chart(top10)
    .mark_bar(color="skyblue")
    .encode(
        x=alt.X("Average:Q", title="평균 비율"),
        y=alt.Y("MBTI:N", sort="-x", title="MBTI 유형"),
        tooltip=["MBTI", "Average"]
    )
    .properties(width=600, height=400)
)

st.altair_chart(chart, use_container_width=True)
st.caption(f"전체 {len(mbti_cols)}개 MBTI 유형 중 상위 10개 평균값 기준 그래프입니다.")
