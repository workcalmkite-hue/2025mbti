import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="MBTI 비율 대시보드", layout="centered", page_icon="🌍")

# 제목
st.title("🌍 MBTI by Country")
st.markdown("### 🧭 가장 최근 CSV 파일에서 나라별 MBTI 비율을 불러옵니다!")

# 가장 최근 CSV 파일 찾기
def get_latest_csv():
    csv_files = list(Path(".").glob("*.csv"))
    if not csv_files:
        return None
    return max(csv_files, key=lambda f: f.stat().st_mtime)

latest_csv = get_latest_csv()

if latest_csv is None:
    st.error("❌ 현재 폴더에 CSV 파일이 없어요!")
    st.stop()
else:
    st.info(f"📂 불러온 파일: `{latest_csv.name}`")

# 데이터 로드 (캐시)
@st.cache_data
def load_data(p: Path) -> pd.DataFrame:
    return pd.read_csv(p)

df = load_data(latest_csv)

# MBTI 열만 추출
mbti_cols = [c for c in df.columns if c != "Country"]

# 나라 선택
countries = sorted(df["Country"].unique().tolist())
default_country = "South Korea" if "South Korea" in countries else countries[0]
country = st.selectbox("🌐 나라 선택", countries, index=countries.index(default_country))

# 선택한 나라 데이터
row = df.loc[df["Country"] == country, mbti_cols].iloc[0]
plot_df = row.reset_index().rename(columns={"index": "MBTI", 0: "value"})
plot_df["percentage"] = plot_df["value"] * 100
plot_df = plot_df.sort_values("percentage", ascending=True)

# 그래프 (Plotly)
fig = px.bar(
    plot_df,
    x="percentage",
    y="MBTI",
    orientation="h",
    color="percentage",
    color_continuous_scale="Tealrose",
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

# 데이터 테이블
st.markdown("#### 🗒️ 데이터 (내림차순)")
st.dataframe(
    plot_df.sort_values("percentage", ascending=False)[["MBTI", "percentage"]]
           .rename(columns={"percentage": "비율(%)"})
           .style.format({"비율(%)": "{:.2f}"}),
    use_container_width=True
)
