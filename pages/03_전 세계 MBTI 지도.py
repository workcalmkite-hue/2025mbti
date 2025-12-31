import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. 데이터 불러오기 (여기가 중요해요!)
# -----------------------------------------------------------------------------
try:
    # 파일 이름이 깃허브에 올린 것과 똑같아야 합니다!
    # 만약 파일명이 길다면 아래 'mbti.csv' 부분을 실제 파일명으로 고쳐주세요.
    df = pd.read_csv('mbti.csv') 
except:
    st.error("앗! 엑셀 파일을 찾을 수 없어요. 파일 이름이 'mbti.csv'가 맞는지 확인해주세요!")
    st.stop()

# -----------------------------------------------------------------------------
# 2. 사이드바 메뉴
# -----------------------------------------------------------------------------
st.sidebar.title("🌍 MBTI 대탐험")
menu = st.sidebar.radio(
    "메뉴 선택",
    ["🏠 홈", "💖 내 영혼의 고향", "🗺️ 전 세계 지도", "📊 나라별 분석"]
)

# -----------------------------------------------------------------------------
# 3. 페이지별 기능
# -----------------------------------------------------------------------------

if menu == "🏠 홈":
    st.title("🌏 전 세계 MBTI 데이터 분석실")
    st.write("왼쪽 메뉴를 선택해서 데이터를 구경해보세요!")

elif menu == "💖 내 영혼의 고향":
    st.header("💖 내 영혼의 고향 찾기")
    mbti_list = df.columns[1:] 
    my_mbti = st.selectbox("당신의 MBTI는?", mbti_list)
    if st.button("결과 보기"):
        top_3 = df.nlargest(3, my_mbti)
        st.table(top_3[['Country', my_mbti]])

# 👇 선생님이 만드신 지도 코드 부분
elif menu == "🗺️ 전 세계 지도":
    st.header("🗺️ 대동여지도: MBTI 버전")
    st.write("전 세계 성격 분포를 지도로 확인해보세요.")
    
    # 데이터 컬럼 가져오기
    mbti_list = df.columns[1:]
    selected_mbti = st.selectbox("보고 싶은 MBTI 유형:", mbti_list)
    
    st.write(f"⏳ **{selected_mbti}** 데이터를 지도에 그리는 중...")
    
    # 지도 그리기
    fig = px.choropleth(
        df,
        locations="Country",
        locationmode='country names',
        color=selected_mbti,
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"전 세계 {selected_mbti} 분포도"
    )
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

elif menu == "📊 나라별 분석":
    st.header("📊 나라별 성격 분석")
    country_list = df['Country'].unique()
    selected_country = st.selectbox("나라 선택:", country_list)
    
    country_data = df[df['Country'] == selected_country]
    chart_data = country_data.melt(id_vars=["Country"], var_name="MBTI", value_name="Ratio")
    
    fig = px.bar(chart_data, x="MBTI", y="Ratio", title=f"{selected_country}의 MBTI")
    st.plotly_chart(fig)
