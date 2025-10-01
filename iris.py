import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="Iris 데이터 대시보드",
    page_icon="🌸",
    layout="wide"
)

# 제목
st.title("🌸 Iris 데이터 분석 대시보드")
st.markdown("---")

# Supabase 연결
@st.cache_resource
def init_connection():
    return st.connection("supabase", type=SupabaseConnection)

# 데이터 로드
@st.cache_data(ttl=600)
def load_data():
    conn = init_connection()
    response = conn.table("iris").select("*").execute()
    return pd.DataFrame(response.data)

try:
    # 데이터 로드
    df = load_data()
    
    # 사이드바 - 필터
    st.sidebar.header("📊 필터 옵션")
    
    # 종(species) 선택
    species_list = df['Species'].unique().tolist()
    selected_species = st.sidebar.multiselect(
        "품종 선택",
        species_list,
        default=species_list
    )
    
    # 데이터 필터링
    filtered_df = df[df['Species'].isin(selected_species)]
    
    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 데이터 수", len(filtered_df))
    with col2:
        st.metric("품종 수", filtered_df['Species'].nunique())
    with col3:
        st.metric("평균 꽃잎 길이", f"{filtered_df['PetalLengthCm'].mean():.2f} cm")
    with col4:
        st.metric("평균 꽃받침 길이", f"{filtered_df['SepalLengthCm'].mean():.2f} cm")
    
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 산점도", "📊 히스토그램", "📉 박스플롯", "🔥 히트맵", "📋 데이터"])
    
    # 탭 1: 산점도
    with tab1:
        st.subheader("산점도 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_axis = st.selectbox(
                "X축 선택",
                ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"],
                key="scatter_x"
            )
        
        with col2:
            y_axis = st.selectbox(
                "Y축 선택",
                ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"],
                index=2,
                key="scatter_y"
            )
        
        # 산점도 그리기
        fig_scatter = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color="Species",
            size="PetalWidthCm",
            hover_data=["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"],
            title=f"{x_axis} vs {y_axis}",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 탭 2: 히스토그램
    with tab2:
        st.subheader("분포 분석")
        
        feature = st.selectbox(
            "특성 선택",
            ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"],
            key="hist_feature"
        )
        
        fig_hist = px.histogram(
            filtered_df,
            x=feature,
            color="Species",
            marginal="box",
            nbins=30,
            title=f"{feature} 분포",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_hist.update_layout(height=500)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # 탭 3: 박스플롯
    with tab3:
        st.subheader("박스플롯 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_box1 = px.box(
                filtered_df,
                x="Species",
                y="SepalLengthCm",
                color="Species",
                title="꽃받침 길이 비교",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_box1, use_container_width=True)
            
            fig_box2 = px.box(
                filtered_df,
                x="Species",
                y="SepalWidthCm",
                color="Species",
                title="꽃받침 너비 비교",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_box2, use_container_width=True)
        
        with col2:
            fig_box3 = px.box(
                filtered_df,
                x="Species",
                y="PetalLengthCm",
                color="Species",
                title="꽃잎 길이 비교",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_box3, use_container_width=True)
            
            fig_box4 = px.box(
                filtered_df,
                x="Species",
                y="PetalWidthCm",
                color="Species",
                title="꽃잎 너비 비교",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_box4, use_container_width=True)
    
    # 탭 4: 히트맵
    with tab4:
        st.subheader("상관관계 분석")
        
        # 숫자형 컬럼만 선택
        numeric_cols = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"]
        corr_matrix = filtered_df[numeric_cols].corr()
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="상관계수")
        ))
        
        fig_heatmap.update_layout(
            title="특성 간 상관관계",
            height=500
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # 품종별 평균 비교
        st.subheader("품종별 평균 비교")
        
        avg_by_species = filtered_df.groupby('Species')[numeric_cols].mean().reset_index()
        
        fig_bar = go.Figure()
        
        for col in numeric_cols:
            fig_bar.add_trace(go.Bar(
                name=col,
                x=avg_by_species['Species'],
                y=avg_by_species[col],
                text=avg_by_species[col].round(2),
                textposition='auto',
            ))
        
        fig_bar.update_layout(
            title="품종별 특성 평균값",
            barmode='group',
            height=400,
            xaxis_title="품종",
            yaxis_title="평균값 (cm)"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 탭 5: 데이터 테이블
    with tab5:
        st.subheader("원본 데이터")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**총 {len(filtered_df)}개의 데이터**")
        with col2:
            if st.button("CSV 다운로드"):
                csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSV 파일 다운로드",
                    data=csv,
                    file_name="iris_data.csv",
                    mime="text/csv"
                )
        
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # 통계 요약
        st.subheader("통계 요약")
        st.dataframe(filtered_df.describe(), use_container_width=True)

except Exception as e:
    st.error("⚠️ 데이터를 불러오는 중 오류가 발생했습니다.")
    st.error(f"오류 내용: {str(e)}")
    st.info("""
    **해결 방법:**
    1. `.streamlit/secrets.toml` 파일에 Supabase 인증 정보가 올바르게 설정되어 있는지 확인하세요.
    2. Supabase에 'iris' 테이블이 존재하는지 확인하세요.
    3. 테이블에 다음 컬럼이 있는지 확인하세요: SepalLengthCm, SepalWidthCm, PetalLengthCm, PetalWidthCm, Species
    """)

# 사이드바 정보
st.sidebar.markdown("---")
st.sidebar.info("""
**대시보드 정보**
- 데이터: Iris 데이터셋
- 연결: Supabase
- 시각화: Plotly
- 프레임워크: Streamlit
""")
