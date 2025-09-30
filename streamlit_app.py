import streamlit as st
import pandas as pd
import plotly.express as px
from st_supabase_connection import SupabaseConnection

# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

# Perform query.
rows = conn.query("*", table="iris", ttl="10m").execute()


# Streamlit 앱 이름과 레이아웃 설정
st.set_page_config(
    page_title="Supabase IRIS 데이터 대시보드",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚢 타이타닉호 생존자 분석 대시보드 (Supabase 연동)")
st.caption("Streamlit의 st.connection과 secrets를 사용하여 Supabase PostgreSQL 데이터를 시각화합니다.")

# ----------------------------------------------------
# 1. 데이터베이스 연결 및 로드
# ----------------------------------------------------

# st.connection을 사용하여 secrets.toml의 [supabase] 연결 정보를 사용합니다.
try:
    # SQL 기반 데이터베이스 연결 설정
    conn = st.connection("supabase", type="sql")
except Exception as e:
    st.error(f"⚠️ 데이터베이스 연결 실패! `.streamlit/secrets.toml` 파일과 Supabase 접속 정보를 확인해주세요. (에러: {e})")
    st.stop()


@st.cache_data(ttl=600)  # 데이터는 10분마다 새로 로드하도록 캐시 설정
def load_data():
    """Supabase에서 'titanic' 테이블의 모든 데이터를 로드하고 전처리합니다."""
    try:
        # conn.query()를 사용하여 SQL 쿼리를 실행합니다.
        # 데이터베이스의 테이블명은 'titanic'으로 가정합니다.
        df = conn.query("SELECT * FROM titanic", ttl=600)
        # PostgreSQL은 기본적으로 컬럼명을 소문자로 반환합니다. 데이터 처리를 위해 통일
        df.columns = df.columns.str.lower()
        return df
    except Exception as e:
        st.error(f"테이블 'titanic' 로드 중 오류 발생. 테이블 이름 또는 권한을 확인해주세요. (에러: {e})")
        return pd.DataFrame() # 빈 DataFrame 반환

data = load_data()

if data.empty:
    st.warning("데이터 로드에 실패하여 시각화를 진행할 수 없습니다.")
    st.stop()

st.sidebar.header("필터 설정")

# ----------------------------------------------------
# 2. 사이드바 필터 설정
# ----------------------------------------------------

# Pclass (객실 등급) 필터
pclass_options = sorted(data['pclass'].unique())
selected_pclass = st.sidebar.multiselect(
    "객실 등급 (Pclass)",
    options=pclass_options,
    default=pclass_options
)

# Sex (성별) 필터
gender_options = data['sex'].unique().tolist()
selected_gender = st.sidebar.multiselect(
    "성별 (Sex)",
    options=gender_options,
    default=gender_options
)

# Survived (생존 여부) 필터
survival_options = {0: "사망 (Died)", 1: "생존 (Survived)"}
selected_survival = st.sidebar.multiselect(
    "생존 여부 (Survived)",
    options=list(survival_options.keys()),
    format_func=lambda x: survival_options[x],
    default=list(survival_options.keys())
)

# 필터 적용
filtered_data = data[
    data['pclass'].isin(selected_pclass) &
    data['sex'].isin(selected_gender) &
    data['survived'].isin(selected_survival)
]

st.sidebar.metric(
    "총 승객 수 (필터 적용)",
    f"{len(filtered_data):,}"
)

# ----------------------------------------------------
# 3. 대시보드 시각화 구성
# ----------------------------------------------------

# 3.1. 요약 통계 (KPI)
col1, col2, col3 = st.columns(3)

total_passengers = len(data)
# 필터링된 데이터에서 생존자 수 계산
survivors = filtered_data['survived'].sum()
# 생존율 계산 (분모가 0이 아닐 경우만 계산)
survival_rate = (survivors / len(filtered_data)) * 100 if len(filtered_data) > 0 else 0
data_diff = survival_rate - (data['survived'].sum() / total_passengers * 100) # 전체 대비 생존율 변화

col1.metric("전체 승객 수", f"{total_passengers:,}명")
col2.metric("필터 적용 생존자", f"{survivors:,}명")
col3.metric(
    "필터 적용 생존율", 
    f"{survival_rate:.2f}%", 
    delta=f"{data_diff:.2f}% (전체 생존율 대비)", 
    delta_color="normal"
)


st.markdown("---")
st.subheader("주요 승객 특성 및 생존 분석")

# 3.2. 객실 등급별 생존자 수 (Bar Chart)
# 데이터프레임을 그룹화하여 카운트합니다.
pclass_survival_counts = filtered_data.groupby(['pclass', 'survived']).size().reset_index(name='Count')
fig_pclass_survival = px.bar(
    pclass_survival_counts,
    x='pclass',
    y='Count',
    color='survived',
    barmode='group',
    labels={'pclass': '객실 등급', 'Count': '승객 수', 'survived': '생존 여부 (0: 사망, 1: 생존)'},
    category_orders={"survived": [0, 1]},
    color_discrete_map={0: '#FF6347', 1: '#3CB371'}, # Coral, MediumSeaGreen
    title='객실 등급별 생존자 및 사망자 수'
)
fig_pclass_survival.update_layout(xaxis={'type': 'category'})

# 3.3. 연령 분포 (Histogram)
fig_age_distribution = px.histogram(
    filtered_data.dropna(subset=['age']), # NaN 값은 시각화에서 제외
    x='age',
    color='survived',
    nbins=30,
    marginal="box",
    histnorm='density', # 밀도 분포로 표시
    color_discrete_map={0: '#FF6347', 1: '#3CB371'},
    labels={'age': '연령 (Age)', 'count': '밀도'},
    title='연령 및 생존 여부별 분포'
)

# 차트 레이아웃 배치
col_chart_1, col_chart_2 = st.columns(2)
with col_chart_1:
    st.plotly_chart(fig_pclass_survival, use_container_width=True)

with col_chart_2:
    st.plotly_chart(fig_age_distribution, use_container_width=True)


# 3.4. 운임(Fare)과 연령(Age)별 산점도 - 생존 여부 시각화
fig_fare_age = px.scatter(
    filtered_data,
    x='fare',
    y='age',
    color='survived',
    size='fare',
    hover_name='name',
    color_discrete_map={0: '#FF6347', 1: '#3CB371'},
    labels={'fare': '운임 (Fare)', 'age': '연령 (Age)', 'survived': '생존 여부'},
    title='운임과 연령에 따른 생존 분포'
)
st.plotly_chart(fig_fare_age, use_container_width=True)


st.markdown("---")

# 3.5. 원본 데이터 미리보기 (선택 사항)
if st.checkbox("원본 데이터 테이블 보기", False):
    st.subheader("원본 데이터 (필터 적용됨)")
    # 'name' 컬럼이 있는 경우에만 표시
    if 'name' in filtered_data.columns:
        st.dataframe(filtered_data[['pclass', 'sex', 'age', 'fare', 'survived', 'name']].head(100))
    else:
         st.dataframe(filtered_data.head(100))
