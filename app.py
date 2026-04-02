import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import os

# --- [UI 디자인 섹션: 주식 시스템 스타일 이식] ---
st.markdown("""
    <style>
    .main-title {
        font-size: 40px !important; font-weight: 900;
        background: linear-gradient(135deg, #FF4B4B, #764BA2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 20px;
    }
    div.stButton > button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(135deg, #FF4B4B, #764BA2);
        color: white !important; font-weight: 700; border: none;
        padding: 12px; transition: all 0.3s;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(255, 75, 75, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Premium WordCloud AI</div>', unsafe_allow_html=True)

# --- [폰트 자동 탐색 시스템] ---
def get_font_path():
    # 1. 윈도우, 맥, 리눅스 서버의 대표적인 한글 폰트 경로들
    paths = [
        "C:/Windows/Fonts/malgun.ttf", # 윈도우
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf", # 리눅스/서버
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf", # 맥
        "/usr/share/fonts/nanum/NanumGothic.ttf", # 리눅스 대안 경로
        "malgun.ttf" # 현재 폴더에 직접 넣어둔 경우
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

# --- [메인 로직] ---
with st.sidebar:
    url = st.text_input("URL 입력", "https://n.news.naver.com/article/001/0014567890")
    max_words = st.slider("최대 단어", 50, 200, 100)

if st.button("분석 시작"):
    try:
        # 데이터 가져오기
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text()

        # 명사 추출
        okt = Okt()
        nouns = [n for n in okt.nouns(text) if len(n) > 1]
        count = Counter(nouns)

        # 워드클라우드 생성
        font = get_font_path()
        
        if font:
            wc = WordCloud(
                font_path=font, # 찾은 폰트 적용
                background_color="white",
                colormap="coolwarm",
                width=1000, height=600
            ).generate_from_frequencies(count)

            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.error("서버에 한글 폰트가 설치되어 있지 않습니다.")
            st.info("해결책: 컴퓨터의 'malgun.ttf' 파일을 복사해서 이 파이썬 파일과 같은 폴더에 넣어주세요!")

    except Exception as e:
        st.error(f"오류 발생: {e}")
