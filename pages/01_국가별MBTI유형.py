import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="MBTI 비율 대시보드", layout="centered", page_icon="🌍")

st.title("🌍 MBTI by Country")
st.markdown("### 🧭 가장 최근 CSV에서 나라별 MBTI 비율을 보여줄게요!")

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
def load_data(p: Path) -> pd.DataFrame:
    # 인코딩/이상치 방어
    df = pd.read_csv(p, encoding="utf-8", engine="python")
    # 컬럼 정리: 앞뒤 공백 제거
    df.columns = [c.strip() for c in df.columns]
    # 'Country' 열 찾기 (대소문자/공백 방어)
    lower_map = {c.lower(): c for c in df.columns}
    if "country" not in lower_map:
        raise ValueError("CSV에 'Country' 열이 없습니다. 열 이름을 확인해 주세요.")
    country_col = lower_map["country"]

    # 수치형으로 강제(실수 변환 실패값은 NaN 처리)
    for c in df.columns:
        if c != country_col:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df, country_col

try:
    df, country_col = load_data(latest_csv)
except Exception as e:
    st.error(f"CSV 읽기/정리 중 오류가 발생했습니다: {e}")
    st.stop()

# MBTI 컬럼 목록
mbti_cols = [c for c in df.columns if c != country_col]

# --- 나라 선택 UI ---
countries = sorted(df[country_col].dropna().astype(str).unique().tolist())
default_country = "South Korea" if "South Korea" in countries else countries[0]
country = st.selectbox("🌐 나라 선택", countries, index=countries.index(default_country))

# --- 선택 나라 데이터 → 긴 형식(melt)으로 변환 ---
row_df = df[df[country_col] == country]
if row_df.empty:
    st.error(f"선택한 나라 '{country}' 데이터를 찾을 수 없습니다.")
    st.stop()

# melt로 안정적인 컬럼 구성(MBTI, value)
long_df = row_df.melt(
    id_vars=[country_col],
    value_vars=mbti_cols,
    var_name="MBTI",
    value_name="value"
)[["MBTI", "value"]]

# 숫자 변환/결측 제거
long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
plot_df = long_df.dropna(subset=["value"]).copy()
plot_df["percentage"] = plot_df["value"] * 100
plot_df = plot_df.sort_values("percentage", ascending=True)

# --- Plotly 막대 그래프 (수평) ---
fig = px.bar(
    plot_df,
    x="percentage",
    y="MBTI",
    orientation="h",
    color="percentage",
    color_continuous_scale="Tealrose",   # 파스텔톤
    labels={"percentage": "비율(%)", "MBTI": "유형"},
    title=f"📊 {country} — MBTI 비율",
    text=plot_df["percentage"].map(lambda x: f"{x:.1f}%"),
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(
    height=600,
    margin=dict(l=80, r=30, t=70, b=40),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,
)
fig.update_xaxes(ticksuffix="%", showgrid=True)

st.plotly_chart(fig, use_container_width=True)

# --- 표도 함께 제공(내림차순) ---
st.markdown("#### 🗒️ 데이터 (내림차순) 🗒️")
st.dataframe(
    plot_df.sort_values("percentage", ascending=False)[["MBTI", "percentage"]]
           .rename(columns={"percentage": "비율(%)"})
           .style.format({"비율(%)": "{:.2f}"}),
    use_container_width=True
)

# 디버그 도움말(필요할 때 접어서 확인)
with st.expander("🔧 디버그 정보 보기"):
    st.write("열 목록:", df.columns.tolist())
    st.write("Country 열 식별:", country_col)
    st.write("행 개수:", len(df))
    st.write("MBTI 컬럼 수:", len(mbti_cols))
