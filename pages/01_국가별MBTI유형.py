# ---- 공통: 최신 CSV 자동탐색 + 업로드 대안 ----
import streamlit as st
import pandas as pd
from pathlib import Path

def find_latest_csv() -> Path | None:
    """
    다음 경로들을 순서대로 뒤져서 *.csv 중 '가장 최근 수정 파일'을 찾습니다.
    1) 현재 스크립트 기준 폴더(__file__.parent)
    2) 작업 디렉토리(Path.cwd())
    3) 프로젝트 루트에서 pages/, data/ 폴더
    4) 위 경로들에 대한 재귀 탐색(glob('**/*.csv'))까지 수행
    """
    candidates: list[Path] = []

    # 기준 경로들
    script_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()
    root = script_dir
    # 레포 루트 추정: pages/ 안에서 실행될 때 상위 폴더가 루트일 가능성 큼
    # (너무 과하게 올라가지 않도록 3단계까지만)
    for _ in range(3):
        if (root / "pages").exists() or (root / ".git").exists():
            break
        root = root.parent

    search_dirs = [
        script_dir,
        cwd,
        root,
        root / "pages",
        root / "data",
    ]

    # 1차: 각 폴더 바로 아래 *.csv
    for d in search_dirs:
        if d.exists():
            candidates += list(d.glob("*.csv"))

    # 2차: 재귀 탐색(프로젝트 구조 다양성 대비)
    for d in search_dirs:
        if d.exists():
            candidates += list(d.glob("**/*.csv"))

    # 중복 제거 및 존재 확인
    uniq = []
    seen = set()
    for p in candidates:
        if p.exists():
            key = str(p.resolve())
            if key not in seen:
                seen.add(key)
                uniq.append(p)

    if not uniq:
        return None

    # 가장 최근 수정 시간 기준 선택
    return max(uniq, key=lambda f: f.stat().st_mtime)

def load_csv_or_upload() -> pd.DataFrame:
    latest = find_latest_csv()

    with st.expander("🔎 CSV 탐색/업로드"):
        st.write("**작업 디렉토리**:", str(Path.cwd()))
        st.write("**스크립트 폴더**:", str(Path(__file__).resolve().parent))
        if latest:
            st.success(f"자동으로 찾은 CSV: `{latest.name}`")
        else:
            st.warning("자동으로 찾은 CSV가 없습니다. 아래에서 업로드해주세요.")

        uploaded = st.file_uploader("여기에 CSV 업로드(대안)", type=["csv"])

    if uploaded is not None:
        df = pd.read_csv(uploaded)
        return df

    if latest is None:
        st.error("❌ CSV 파일을 찾지 못했고 업로드도 되지 않았습니다.")
        st.stop()

    return pd.read_csv(latest)

# -----------------------------------------------
# 사용 예시(상위 10개 페이지 / 국가별 페이지 공통):
# df = load_csv_or_upload()
# df.columns = [c.strip() for c in df.columns]
# lower_map = {c.lower(): c for c in df.columns}
# country_col = lower_map.get("country")
# if not country_col:
#     st.error("CSV에 'Country' 열이 없습니다.")
#     st.stop()
