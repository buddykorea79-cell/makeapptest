import streamlit as st
from st_supabase_connection import SupabaseConnection

st.title("Supabase 연결 테스트")

try:
    # 연결 생성
    st.write("1️⃣ Supabase 연결 시도중...")
    conn = st.connection("supabase", type=SupabaseConnection)
    st.success("✅ 연결 성공!")
    
    # 테이블 목록 확인
    st.write("2️⃣ 테이블 조회 시도중...")
    response = conn.table("iris").select("*").limit(5).execute()
    st.success("✅ 테이블 조회 성공!")
    
    # 데이터 표시
    st.write("3️⃣ 데이터:")
    st.json(response.data)
    
    # 데이터 개수
    st.write(f"📊 총 {len(response.data)}개의 행을 가져왔습니다.")
    
except Exception as e:
    st.error("❌ 오류 발생!")
    st.error(f"오류 메시지: {str(e)}")
    st.write("**오류 타입:**", type(e).__name__)
