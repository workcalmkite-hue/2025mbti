import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="MBTI 비율 대시보드", layout="centered", page_icon="🌍")

# 제목 & 안내
st.title("🌍 MBTI by Country")
st.markdown("### 🧭 나라를 선택하면 👉 **MBTI 비율**을 보여줄게요!")

# CSV 파일 경로
CSV_FILE = "countriesMBTI_16types.csv"
path = Path(__file__).parent / CSV_FILE

if not path.exists():
    st.error(f"같은 폴더에서 `{CSV_FILE}` 파일을 찾을 수 없어요. 파일명을 확인해 주세요.")
    st.stop()

# 데이터 로드 (캐시)
@st.cache_data
def load_data(p: Path) -> pd.DataFrame:
    df = pd.read_csv(p)
    return df

df = load_data(path)

# MBTI 열만 추출
mbti_cols = [c for c in df.columns if c != "Country"]

# 나라 선택 UI (South Korea가 있으면 기본값으로)
countries = sorted(df["Country"].unique().tolist())
default_country = "South Korea" if "South Korea" in countries else countries[0]
country = st.selectbox("🌐 나라 선택", countries, index=countries.index(default_country))

# 선택한 나라의 MBTI 비율 데이터프레임 준비
row = df.loc[df["Country"] == country, mbti_cols].iloc[0]
plot_df = (
    row.reset_index()
       .rename(columns={"index": "MBTI", country if country in row.index else 0: "value"})
)
# 위에서 rename이 애매할 수 있으니 확실히 지정
plot_df.columns = ["MBTI", "value"]
plot_df["percentage"] = plot_df["value"] * 100
plot_df = plot_df.sort_values("percentage", ascending=True)  # 수평막대 위에서 크게 보이도록 오름차순

# Plotly 막대 그래프
fig = px.bar(
    plot_df,
    x="percentage",
    y="MBTI",
    orientation="h",
    color="percentage",
    color_continuous_scale="Tealrose",  # 보기 좋은 파스텔 계열
    labels={"percentage": "비율(%)", "MBTI": "유형"},
    title=f"📊 {country} — MBTI 비율 Top 16",
    text=plot_df["percentage"].map(lambda x: f"{x:.1f}%"),
)

# 그래프 스타일 다듬기
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(
    height=600,
    margin=dict(l=80, r=30, t=70, b=40),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,  # 색상바 숨김(깔끔 버전)
)
fig.update_xaxes(ticksuffix="%", showgrid=True)

st.plotly_chart(fig, use_container_width=True)

# 표도 함께 제공(정렬된 순서로 보기)
st.markdown("#### 🗒️ 데이터 (내림차순)")
st.dataframe(
    plot_df.sort_values("percentage", ascending=False)[["MBTI", "percentage"]]
           .rename(columns={"percentage": "비율(%)"})
           .style.format({"비율(%)": "{:.2f}"}),
    use_container_width=True
)

st.caption("Tip: 값은 0~1 사이 비율을 %로 변환해서 표시했어요. (예: 0.15 → 15%)")
