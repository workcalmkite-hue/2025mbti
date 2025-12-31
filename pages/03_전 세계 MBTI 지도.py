import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. 데이터 불러오기 (여기를 고쳤습니다!)
# -----------------------------------------------------------------------------
try:
    # 선생님이 알려주신 파일 이름 'countriesMBTI_16types.csv'를 읽어옵니다.
    df = pd.read_csv('countriesMBTI_16types.csv')
except:
    # 만약 또 에러가 나면, 이제는 올바른 파일 이름을 알려줍니다.
    st.error("앗! 파일을 못 찾겠어요. 깃허브에 올린 파일명이 'countriesMBTI_16types.csv'가 맞는지 대소문자까지 똑같이 확인해주세요!")
    st.stop()

# -----------------------------------------------------------------------------
# 2. 사이드바 메뉴 (페이지 이동)
# -----------------------------------------------------------------------------
st.sidebar.title("🌍 MBTI 대탐험")
st.sidebar.info("원하는 기능을 선택하세요!")

menu = st.sidebar.radio(
    "메뉴 선택",
    ["🏠 홈 (Home)", "💖 내 영혼의 고향 찾기", "🗺️ 전 세계 MBTI 지도", "📊 나라별 성격 분석"]
)

# -----------------------------------------------------------------------------
# 3. 페이지별 기능 구현
# -----------------------------------------------------------------------------

# [페이지 1] 홈 화면
if menu == "🏠 홈 (Home)":
    st.title("🌏 전 세계 MBTI 데이터 분석실")
    st.markdown("### 👋 환영합니다!")
    st.write("이곳은 전 세계 사람들의 MBTI 분포를 분석하는 비밀 연구소입니다.")
    st.write("왼쪽 메뉴를 눌러서 시작해보세요!")
    st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-1.2.1&auto=format&fit=crop&w=1352&q=80", caption="Global Data Visualization")

# [페이지 2] 내 영혼의 고향 찾기
elif menu == "💖 내 영혼의 고향 찾기":
    st.title("💖 내 영혼의 단짝 국가는?")
    st.write("당신의 MBTI 유형이 가장 많이 살고 있는 나라를 찾아줍니다.")
    
    # 데이터의 첫 번째 컬럼(Country)을 제외한 나머지(MBTI 유형들)를 가져옴
    mbti_list = df.columns[1:] 
    my_mbti = st.selectbox("당신의 MBTI를 선택하세요:", mbti_list)
    
    if st.button("내 운명의 나라 찾기! 🚀"):
        # 선택한 MBTI 수치가 높은 순서대로 정렬해서 상위 3개 뽑기
        top_3 = df.nlargest(3, my_mbti)
        
        st.success(f"🎉 **{my_mbti}** 유형이 가장 많은 나라 TOP 3 🎉")
        
        # 표로 보여주기 (깔끔하게)
        display_df = top_3[['Country', my_mbti]].copy()
        display_df[my_mbti] = display_df[my_mbti].apply(lambda x: f"{x*100:.2f}%")
        
        st.table(display_df)
        st.balloons() 

# [페이지 3] 전 세계 MBTI 지도
elif menu == "🗺️ 전 세계 MBTI 지도":
    st.title("🗺️ 대동여지도: MBTI 버전")
    st.write("전 세계 성격 분포를 지도로 확인해보세요.")
    
    mbti_list = df.columns[1:]
    selected_mbti = st.selectbox("지도에 표시할 MBTI 유형:", mbti_list)
    
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

# [페이지 4] 나라별 성격 분석
elif menu == "📊 나라별 성격 분석":
    st.title("📊 이 나라 사람들은 어떤 성격?")
    
    country_list = df['Country'].unique()
    selected_country = st.selectbox("나라를 선택하세요:", country_list)
    
    country_data = df[df['Country'] == selected_country]
    chart_data = country_data.melt(id_vars=["Country"], var_name="MBTI Type", value_name="Ratio")
    
    fig = px.bar(
        chart_data,
        x="MBTI Type",
        y="Ratio",
        color="MBTI Type",
        title=f"{selected_country}의 MBTI 분포 비율",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)
