import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# ---- 공통 CSV 로더 (app.py와 동일) ----
def find_latest_csv() -> Path | None:
    candidates = []
    search_dirs = [Path.cwd(), Path(__file__).resolve().parent, Path.cwd() / "data", Path.cwd() / "pages"]
    for d in search_dirs:
        if d.exists():
            candidates += list(d.glob("*.csv"))
            candidates += list(d.glob("**/*.csv"))
    if not candidates:
        return None
    return max(candidates, key=lambda f: f.stat().st_mtime)

def load_csv_or_upload() -> pd.DataFrame:
    latest = find_latest_csv()
    with st.expander("🔎 CSV 탐색/업로드"):
        st.write("**작업 디렉토리**:", str(Path.cwd()))
        if latest:
            st.success(f"자동으로 찾은 CSV: `{latest.name}`")
        else:
            st.warning("자동으로 찾은 CSV가 없습니다. 직접 업로드하세요.")
        uploaded = st.file_uploader("여기에 CSV 업로드", type=["csv"])
    if uploaded is not None:
        return pd.read_csv(uploaded)
    if latest is None:
        st.error("❌ CSV 파일을 찾지 못했고 업로드도 되지 않았습니다.")
        st.stop()
    return pd.read_csv(latest)

# ---- 메인 ----
st.set_page_config(page_title="MBTI 상위 10 유형", layout="centered", page_icon="🌟")
st.title("🌟 전 세계 MBTI 상위 10")
st.markdown("### 📊 가장 최근 CSV 기준, 평균 비율이 높은 10개 유형")

df = load_csv_or_upload()
df.columns = [c.strip() for c in df.columns]

lower_map = {c.lower(): c for c in df.columns}
country_col = lower_map.get("country")
if not country_col:
    st.error("CSV에 'Country' 열이 없습니다.")
    st.stop()

for c in df.columns:
    if c != country_col:
        df[c] = pd.to_numeric(df[c], errors="coerce")

mbti_cols = [c for c in df.columns if c != country_col]
mbti_means = df[mbti_cols].mean(numeric_only=True).sort_values(ascending=False)
top10 = mbti_means.head(10).reset_index()
top10.columns = ["MBTI", "Average"]
top10["percentage"] = top10["Average"] * 100

chart = (
    alt.Chart(top10)
    .mark_bar(color="#7CC5D0")
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
text = chart.mark_text(align="left", baseline="middle", dx=3).encode(
    text=alt.Text("percentage:Q", format=".1f")
)

st.altair_chart(chart + text, use_container_width=True)

st.markdown("#### 🗒️ 데이터 (내림차순)")
st.dataframe(
    top10[["MBTI", "percentage"]]
        .sort_values("percentage", ascending=False)
        .rename(columns={"percentage": "평균 비율(%)"})
        .style.format({"평균 비율(%)": "{:.2f}"}),
    use_container_width=True
)
