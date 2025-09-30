import streamlit as st

# 앱 제목
st.title("Hello Streamlit 👋")

# 텍스트 출력
st.write("이것은 간단한 Streamlit 예제 앱입니다.")

# 사용자 입력
name = st.text_input("이름을 입력하세요:")

# 버튼 클릭 시 동작
if st.button("인사하기"):
    st.success(f"안녕하세요, {name}님! 반갑습니다 😊")

# 슬라이더
age = st.slider("나이를 선택하세요", 0, 100, 25)
st.write(f"당신의 나이는 {age}살 입니다.")
