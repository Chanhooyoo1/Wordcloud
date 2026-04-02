import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import os

# 1. 페이지 설정 및 UI 스타일 (주식 시스템 스타일 부활)
st.set_page_config(page_title="Premium WordCloud AI", layout="wide")

st.markdown("""
    <style>
    .main-title {
        font-size: 42px !important; font-weight: 900;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 10px;
    }
    .sub-title { text-align: center; color: #888; margin-bottom: 30px; letter-spacing: 2px; }
    div.stButton > button {
        width: 100%; border-radius: 15px;
        background: linear-gradient(135deg, #FF4B4B, #764BA2);
        color: white !important; font-weight: 700; border: none; padding: 15px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    div.stButton > button:hover {
        transform: translateY(-3px); box-shadow: 0 10px 25px rgba(255, 75, 75, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# 2. [핵심] 무지개 컬러 함수 (높음: 빨강 -> 낮음: 보라)
def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # font_size는 빈도에 비례함 (최대 100~ 최소 10 가정)
    if font_size > 80: return "rgb(255, 0, 0)"      # 빨강 (최고)
    elif font_size > 65: return "rgb(255, 127, 0)" # 주황
    elif font_size > 50: return "rgb(255, 212, 0)" # 노랑
    elif font_size > 35: return "rgb(0, 255, 0)"   # 초록
    elif font_size > 25: return "rgb(0, 0, 255)"   # 파랑
    elif font_size > 15: return "rgb(0, 0, 128)"   # 남색
    else: return "rgb(139, 0, 255)"                # 보라 (최저)

# 3. 타이틀 렌더링
st.markdown('<div class="main-title">RAINBOW WORD INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">𝖥𝗋𝖾𝗊𝗎𝖾𝗇𝖼𝗒-𝖡𝖺𝗌𝖾𝖽 𝖢𝗈𝗅𝗈𝗋 𝖲𝗉𝖾𝖼𝗍𝗋𝗎𝗆</div>', unsafe_allow_html=True)

# 4. 분석 설정
with st.sidebar:
    st.header("⚙️ 엔진 설정")
    url = st.text_input("URL 입력", "https://n.news.naver.com/article/001/0014567890")
    max_words = st.slider("단어 수", 50, 300, 100)

# 5. 실행 로직
if st.button("🚀 무지개 분석 시작"):
    try:
        with st.spinner("데이터 수집 및 언어 분석 중..."):
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.get_text()

            okt = Okt()
            nouns = [n for n in okt.nouns(text) if len(n) > 1]
            counts = Counter(nouns)

        if counts:
            # --- [폰트 해결 필살기] ---
            # 1. 윈도우 기본 경로 확인
            font_path = "C:/Windows/Fonts/malgun.ttf"
            
            # 2. 만약 서버(리눅스)라면 나눔고딕 확인
            if not os.path.exists(font_path):
                font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
            
            # 3. 여전히 없다면? 현재 폴더에 malgun.ttf가 있는지 확인
            if not os.path.exists(font_path):
                font_path = "malgun.ttf" 

            # 워드클라우드 생성
            wc = WordCloud(
                font_path=font_path if os.path.exists(font_path) else None,
                background_color="white",
                width=1000, height=600,
                max_words=max_words,
                color_func=rainbow_color_func, # 무지개 함수 적용
                random_state=42
            ).generate_from_frequencies(counts)

            # 결과 시각화
            fig, ax = plt.subplots(figsize=(12, 7))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
            
            if not os.path.exists(font_path):
                st.error("⚠️ 서버에 한글 폰트 파일이 없습니다!")
                st.info("파일 깨짐 해결법: 내 컴퓨터의 'malgun.ttf' 파일을 복사해서 이 파이썬 파일(.py)과 똑같은 폴더에 넣어주세요.")
    except Exception as e:
        st.error(f"오류: {e}")
