# pages/02_상위10유형.py
import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="MBTI 상위 10 유형", layout="centered", page_icon="🌟")

st.title("🌟 전 세계 MBTI 상위 10")
st.markdown("### 📊 가장 최근 CSV 기준, 평균 비율이 높은 10개 유형")

# --- 가장 최근 CSV 찾기 ---
def get_latest_csv():
    csv_files = list(Path(".").glob("*.csv"))
    if not csv_files:
        return None
    return max(csv_files, key=lambda f: f.stat().st_mtime)

latest_csv = get_latest_csv()
if latest_csv is None:
    st.error("❌ 현재 폴더에 CSV 파일이 없습니다.")
    st.stop()
else:
    st.info(f"📂 불러온 파일: `{latest_csv.name}`")

# --- 데이터 로드 & 정리 ---
@st.cache_data
def load_data(p: Path):
    df = pd.read_csv(p, encoding="utf-8", engine="python")
    # 열 이름 공백 제거
    df.columns = [c.strip() for c in df.columns]

    # Country 열 찾기 (대소문자/공백 방어)
    lower_map = {c.lower(): c for c in df.columns}
    if "country" not in lower_map:
        raise ValueError("CSV에 'Country' 열이 없습니다. 열 이름을 확인해 주세요.")
    country_col = lower_map["country"]

    # 수치형 변환 (실패값 NaN)
    for c in df.columns:
        if c != country_col:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df, country_col

try:
    df, country_col = load_data(latest_csv)
except Exception as e:
    st.error(f"CSV 읽기/정리 중 오류 발생: {e}")
    st.stop()

# --- MBTI 열 목록 ---
mbti_cols = [c for c in df.columns if c != country_col]
if not mbti_cols:
    st.error("MBTI 열을 찾을 수 없습니다. CSV 포맷을 확인해 주세요.")
    st.stop()

# --- MBTI 유형별 전 세계 평균 계산 ---
mbti_means = df[mbti_cols].mean(numeric_only=True).sort_values(ascending=False)
top10 = mbti_means.head(10).reset_index()
top10.columns = ["MBTI", "Average"]
top10["percentage"] = top10["Average"] * 100

# --- Altair 막대 그래프 ---
chart = (
    alt.Chart(top10)
    .mark_bar(color="#7CC5D0")  # 파스텔 블루
    .encode(
        x=alt.X("percentage:Q", title="평균 비율(%)"),
        y=alt.Y("MBTI:N", sort="-x", title="MBTI 유형"),
        tooltip=[
            alt.Tooltip("MBTI:N", title="유형"),
            alt.Tooltip("percentage:Q", title="평균 비율(%)", format=".2f"),
        ],
    )
    .properties(width=650, height=420, title="🌍 전 세계 MBTI 평균 비율 Top 10")
)

# 값 라벨 표시
text = chart.mark_text(align="left", baseline="middle", dx=3).encode(
    text=alt.Text("percentage:Q", format=".1f")
)

st.altair_chart(chart + text, use_container_width=True)

# --- 표 표시 ---
st.markdown("#### 🗒️ 데이터 (내림차순)")
st.dataframe(
    top10[["MBTI", "percentage"]]
        .sort_values("percentage", ascending=False)
        .rename(columns={"percentage": "평균 비율(%)"})
        .style.format({"평균 비율(%)": "{:.2f}"}),
    use_container_width=True
)

# --- 디버그용 ---
with st.expander("🔧 디버그 정보"):
    st.write("열 목록:", df.columns.tolist())
    st.write("Country 열:", country_col)
    st.write("MBTI 열 개수:", len(mbti_cols))
    st.write("행 개수:", len(df))
