import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ------------------------------
# 공통: 최신 CSV 자동탐색 + 업로드
# ------------------------------
def find_latest_csv() -> Path | None:
    candidates = []
    search_dirs = [
        Path.cwd(),
        Path(__file__).resolve().parent,
        Path.cwd() / "data",
        Path.cwd() / "pages",
    ]
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

# ------------------------------
# 메인
# ------------------------------
st.set_page_config(page_title="MBTI 궁합 Best 3(데이터 기반)", layout="centered", page_icon="💞")
st.title("💞 MBTI 궁합 Best 3")
st.markdown("### 📊 같은 나라에서 **함께 자주 나타나는** 유형을 기준으로, 국가 Top 3를 찾아줘요!")

# 데이터 로드 & 정리
df = load_csv_or_upload()
df.columns = [c.strip() for c in df.columns]

lower_map = {c.lower(): c for c in df.columns}
country_col = lower_map.get("country")
if not country_col:
    st.error("CSV에 'Country' 열이 없습니다.")
    st.stop()

# 수치형 변환
for c in df.columns:
    if c != country_col:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# MBTI 열 목록
mbti_cols = [c for c in df.columns if c != country_col]
if not mbti_cols:
    st.error("MBTI 열을 찾을 수 없습니다.")
    st.stop()

# 내 MBTI 선택
user_mbti = st.selectbox("🧑 내 MBTI 선택", sorted(mbti_cols))

# --- 데이터 기반 추천 파트너 유형: '동반출현(상관계수) Top k' ---
# 같은 국가 집합에서 내 MBTI와 **함께 높은/낮은 비율로 움직이는** 유형을 찾음
corr_series = df[mbti_cols].corr(method="pearson")[user_mbti].drop(labels=[user_mbti])
# 상관 높은 순으로 상위 4개(기본값)
data_based_defaults = corr_series.sort_values(ascending=False).head(4).index.tolist()

with st.expander("ℹ️ 추천 방식 설명", expanded=False):
    st.write(
        "- ‘궁합’은 절대적인 과학적 사실이 아니므로, 여기서는 **국가별 분포 데이터 상관**을 사용해 "
        "내 MBTI와 **함께 자주 분포하는 유형**을 기본 추천으로 제시합니다.\n"
        "- 원하면 아래에서 직접 선호 유형을 바꿔서 결과를 확인하세요."
    )

# 사용자가 최종 선호 파트너 유형(가중치 동일) 선택
partner_types = st.multiselect(
    "💡 선호(상대) MBTI 유형 선택 (기본: 데이터 기반 추천)",
    options=sorted(mbti_cols),
    default=data_based_defaults,
    help="여기서 고른 유형들의 '합계 비율'이 높은 국가를 순위로 보여줍니다.",
)

if not partner_types:
    st.warning("적어도 한 개 이상의 상대 유형을 선택하세요.")
    st.stop()

# 국가별 점수 계산: 선택한 유형들 비율 합계 (0~1 범위를 %로 변환)
score_series = df[partner_types].sum(axis=1) * 100.0
rank_df = pd.DataFrame({
    country_col: df[country_col],
    "Score(%)": score_series
}).sort_values("Score(%)", ascending=False)

# Top 3 하이라이트 카드
st.subheader("🏆 Best 3 국가")
top3 = rank_df.head(3).reset_index(drop=True)
cols = st.columns(3)
trophy = ["🥇", "🥈", "🥉"]
for i in range(len(top3)):
    with cols[i]:
        st.metric(
            f"{trophy[i]} {top3.loc[i, country_col]}",
            f"{top3.loc[i, 'Score(%)']:.2f}%",
            help="선택한 상대 유형들의 총합 비율"
        )

# Top 10 막대 그래프
st.subheader("📈 상위 10개 국가 (선택 유형 합계 비율)")
top10 = rank_df.head(10)
fig = px.bar(
    top10,
    x="Score(%)",
    y=country_col,
    orientation="h",
    color="Score(%)",
    color_continuous_scale="Sunset",  # 보기 좋은 그라데이션
    text=top10["Score(%)"].map(lambda x: f"{x:.1f}%"),
    labels={"Score(%)": "선택 유형 합계 비율(%)", country_col: "국가"}
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(
    height=550,
    margin=dict(l=90, r=30, t=30, b=40),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,
)
st.plotly_chart(fig, use_container_width=True)

# 상세 표 + 다운로드
st.markdown("#### 🗒️ 국가별 점수 전체 표")
st.dataframe(rank_df.reset_index(drop=True), use_container_width=True)

@st.cache_data
def to_csv_bytes(df_: pd.DataFrame) -> bytes:
    return df_.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "⬇️ 결과를 CSV로 다운로드",
    data=to_csv_bytes(rank_df),
    file_name=f"mbti_match_rank_{user_mbti}.csv",
    mime="text/csv",
)

# 디버그(필요 시 펼치기)
with st.expander("🔧 디버그 정보"):
    st.write("선택한 내 MBTI:", user_mbti)
    st.write("데이터 기반 기본 추천:", data_based_defaults)
    st.write("최종 선택 유형:", partner_types)
    st.write("MBTI 열 수:", len(mbti_cols))
    st.write("행 개수:", len(df))
