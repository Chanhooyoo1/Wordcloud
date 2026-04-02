import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import numpy as np
from PIL import Image
import os

# 1. 페이지 설정 및 프리미엄 UI 스타일 (그라데이션 & 호버 복구)
st.set_page_config(page_title="Custom Heart Cloud Engine", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* 그라데이션 타이틀 */
    .main-title {
        font-size: 42px !important; font-weight: 900;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 5px;
    }

    .sub-title {
        text-align: center; color: #888; font-size: 16px;
        letter-spacing: 2px; margin-bottom: 30px;
    }

    /* 입체적인 그라데이션 버튼 및 호버 효과 */
    div.stButton > button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%);
        color: white !important; font-weight: 700; border: none; padding: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2);
    }

    div.stButton > button:hover {
        transform: translateY(-3px); /* 위로 들림 */
        box-shadow: 0 10px 25px rgba(255, 75, 75, 0.4);
        background: linear-gradient(135deg, #FF6B6B 0%, #8E5ACD 100%) !important;
        filter: brightness(1.1);
    }
    </style>
""", unsafe_allow_html=True)

# 2. 무지개 컬러 함수 (빈도 기반)
def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    if font_size > 75: return "rgb(255, 0, 0)"      # 빨강
    elif font_size > 60: return "rgb(255, 165, 0)" # 주황
    elif font_size > 45: return "rgb(255, 220, 0)" # 노랑
    elif font_size > 30: return "rgb(0, 128, 0)"   # 초록
    elif font_size > 20: return "rgb(0, 0, 255)"   # 파랑
    else: return "rgb(148, 0, 211)"                # 보라

# 3. 메인 화면 구성
st.markdown('<div class="main-title">HEART-MASK INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Premium Custom Shape Visualization System</div>', unsafe_allow_html=True)

# 4. 사이드바 설정 (사용자 지정 마스크 업로드 추가)
with st.sidebar:
    st.header("⚙️ 분석 컨트롤러")
    url = st.text_input("URL 입력", "https://n.news.naver.com/article/001/0014567890")
    max_words = st.slider("최대 단어 수", 50, 500, 200)
    
    st.divider()
    st.header("🎨 마스크 설정")
    mask_file = st.file_uploader("하트 모양 등 마스크 이미지 업로드 (흰 배경 권장)", type=["png", "jpg", "jpeg"])

# 5. 실행 로직
if st.button("🚀 하트 분석 엔진 가동"):
    try:
        with st.spinner("언어 데이터 분석 및 마스킹 작업 중..."):
            # 크롤링
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.select_one('article').get_text() if soup.select_one('article') else soup.get_text()

            # 형태소 분석
            okt = Okt()
            nouns = [n for n in okt.nouns(text) if len(n) > 1]
            counts = Counter(nouns)

            # 마스크 처리
            mask_array = None
            if mask_file:
                mask_image = Image.open(mask_file)
                mask_array = np.array(mask_image)

            # 폰트 경로 설정
            font_path = "C:/Windows/Fonts/malgun.ttf" # 윈도우 기준
            if not os.path.exists(font_path):
                font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf" # 리눅스/서버 기준

            # 워드클라우드 생성
            wc = WordCloud(
                font_path=font_path if os.path.exists(font_path) else None,
                background_color="white",
                width=1200, height=800,
                max_words=max_words,
                mask=mask_array,  # 사용자가 올린 하트 이미지 적용
                contour_width=1,
                contour_color='firebrick',
                color_func=rainbow_color_func,
                random_state=42
            ).generate_from_frequencies(counts)

            # 결과 시각화
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("📊 커스텀 마스크 결과")
                fig, ax = plt.subplots(figsize=(10, 7))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)

            with col2:
                st.subheader("🔝 TOP 10 키워드")
                for i, (word, freq) in enumerate(counts.most_common(10)):
                    st.write(f"**{i+1}. {word}** ({freq}회)")

    except Exception as e:
        st.error(f"엔진 오류: {e}")
