import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---- 공통: 최신 CSV 자동탐색 + 업로드 대안 ----
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
st.set_page_config(page_title="MBTI 비율 대시보드", layout="centered", page_icon="🌍")
st.title("🌍 MBTI by Country")
st.markdown("### 🧭 나라를 선택하면 👉 MBTI 비율을 보여줄게요!")

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
countries = sorted(df[country_col].dropna().astype(str).unique().tolist())
default_country = "South Korea" if "South Korea" in countries else countries[0]
country = st.selectbox("🌐 나라 선택", countries, index=countries.index(default_country))

row_df = df[df[country_col] == country]
long_df = row_df.melt(id_vars=[country_col], value_vars=mbti_cols, var_name="MBTI", value_name="value")
plot_df = long_df.dropna(subset=["value"]).copy()
plot_df["percentage"] = plot_df["value"] * 100
plot_df = plot_df.sort_values("percentage", ascending=True)

fig = px.bar(
    plot_df,
    x="percentage", y="MBTI", orientation="h",
    color="percentage", color_continuous_scale="Tealrose",
    labels={"percentage": "비율(%)", "MBTI": "유형"},
    title=f"📊 {country} — MBTI 비율",
    text=plot_df["percentage"].map(lambda x: f"{x:.1f}%"),
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(height=600, margin=dict(l=80, r=30, t=70, b=40),
                  plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                  coloraxis_showscale=False)
fig.update_xaxes(ticksuffix="%", showgrid=True)

st.plotly_chart(fig, use_container_width=True)

st.markdown("#### 🗒️ 데이터 (내림차순)")
st.dataframe(
    plot_df.sort_values("percentage", ascending=False)[["MBTI", "percentage"]]
           .rename(columns={"percentage": "비율(%)"})
           .style.format({"비율(%)": "{:.2f}"}),
    use_container_width=True
)
