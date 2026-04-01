import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import platform

# 페이지 설정
st.set_page_config(page_title="Dynamic Color WordCloud", layout="wide")

# OS별 폰트 설정 (폰트가 없으면 에러가 날 수 있으므로 주의)
def get_font_path():
    sys_name = platform.system()
    if sys_name == "Windows":
        return "malgun.ttf"
    elif sys_name == "Darwin": # macOS
        return "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    else: # Linux/Docker 환경 (나눔폰트 설치 가정)
        return "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

st.title("🌐 웹페이지 빈도 분석 워드클라우드")
st.info("주소를 입력하면 내용을 분석하여, 빈도가 높으면 **빨간색**, 낮으면 **파란색**으로 표시합니다.")

# 1. URL 입력 및 설정
with st.sidebar:
    st.header("⚙️ 분석 설정")
    url = st.text_input("분석할 URL", "https://n.news.naver.com/article/001/0014567890")
    max_words = st.slider("최대 단어 수", 50, 300, 100)
    # 불용어(제외할 단어) 설정
    stop_words_input = st.text_area("제외할 단어 (쉼표로 구분)", "기자, 뉴스, 무단, 배포, 금지, 사진, 연합뉴스")
    stop_words = [word.strip() for word in stop_words_input.split(",")]

# 2. 분석 실행 버튼
if st.button("웹페이지 데이터 추출 및 시각화"):
    try:
        with st.spinner('웹페이지를 분석 중입니다...'):
            # 웹 크롤링 (Timeout 추가)
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.encoding = 'utf-8' 
            soup = BeautifulSoup(response.text, 'html.parser')

            # 불필요한 태그 제거
            for tag in soup(["script", "style", "header", "footer", "nav"]): 
                tag.extract() 

            text = soup.get_text()

            # 데이터 처리 (명사 추출 및 불용어 제거)
            okt = Okt()
            nouns = [n for n in okt.nouns(text) if len(n) > 1 and n not in stop_words]
            count = Counter(nouns)

        if count:
            # 3. 워드클라우드 생성
            wc = WordCloud(
                font_path=get_font_path(),
                background_color="white",
                width=1000,
                height=600,
                max_words=max_words,
                colormap="coolwarm", # 빈도 기반 색상 매핑 (Low: Blue, High: Red)
                random_state=42
            ).generate_from_frequencies(count)

            # 4. 시각화 출력
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 워드클라우드 결과")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            
            with col2:
                st.subheader("🔝 빈도수 Top 10")
                top_10 = count.most_common(10)
                for i, (word, freq) in enumerate(top_10):
                    # 순위에 따른 시각적 차별화
                    color = "red" if i < 3 else "black"
                    st.markdown(f"{i+1}. <span style='color:{color}; font-weight:bold'>{word}</span> : {freq}회", unsafe_allow_html=True)

            # 데이터 테이블 추가
            with st.expander("전체 단어 빈도 보기"):
                st.write(count)

        else:
            st.warning("분석할 명사가 충분하지 않습니다.")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        st.info("Tip: URL이 유효한지, 혹은 해당 사이트가 크롤링을 차단하고 있지 않은지 확인해 보세요.")
