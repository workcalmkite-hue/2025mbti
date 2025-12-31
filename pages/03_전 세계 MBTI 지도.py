elif menu == "🗺️ 전 세계 MBTI 지도":
    st.title("🗺️ 대동여지도: MBTI 버전")
    st.write("전 세계에서 특정 MBTI가 어디에 많이 분포하는지 지도로 확인해보세요.")
    
    # 1. 보고 싶은 유형 선택
    mbti_list = df.columns[1:]
    selected_mbti = st.selectbox("지도에 표시할 MBTI 유형:", mbti_list)
    
    # 2. 지도 그리기 (Plotly 사용)
    st.write(f"⏳ **{selected_mbti}** 데이터를 지도에 그리는 중...")
    
    fig = px.choropleth(
        df,
        locations="Country",         # 나라 이름이 들어있는 컬럼
        locationmode='country names',# 나라 이름으로 인식하겠다
        color=selected_mbti,         # 색깔을 결정할 수치 (선택한 MBTI 비율)
        hover_name="Country",        # 마우스 올렸을 때 나라 이름 표시
        color_continuous_scale=px.colors.sequential.Plasma, # 색상 테마 (예쁜 걸로)
        title=f"전 세계 {selected_mbti} 분포도"
    )
    
    # 지도를 화면에 꽉 차게 보여주기
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
