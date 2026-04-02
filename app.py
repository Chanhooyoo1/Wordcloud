import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import os
import numpy as np
from PIL import Image, ImageDraw

# 1. 페이지 설정 및 프리미움 UI 스타일
st.set_page_config(page_title="Streamlit WordCloud Engine", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif !important; }
    .main-title {
        font-size: 42px !important; font-weight: 900;
        background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 5px;
    }
    .sub-title {
        text-align: center; color: #888; font-size: 14px; letter-spacing: 2px;
        margin-bottom: 30px; text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 도형 마스크 생성 함수 (별도 파일 없이 그리기)
def create_shape_mask(shape):
    size = (800, 800)
    mask = Image.new("L", size, 0) # 검정 배경
    draw = ImageDraw.Draw(mask)
    
    if shape == "구름":
        # 구름 형태를 위한 원들의 집합
        draw.ellipse([150, 200, 450, 500], fill=255)
        draw.ellipse([300, 150, 650, 550], fill=255)
        draw.ellipse([500, 250, 750, 500], fill=255)
        draw.ellipse([350, 400, 600, 650], fill=255)
    elif shape == "하트":
        # 하트 모양 그리기
        draw.polygon([(400, 750), (100, 350), (200, 150), (400, 300), (600, 150), (700, 350)], fill=255)
        draw.ellipse([100, 120, 410, 450], fill=255)
        draw.ellipse([390, 120, 700, 450], fill=255)
    else: # 기본 사각형
        return None
    return np.array(mask)

# 3. 무지개 컬러 함수
def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    if font_size > 70: return "rgb(255, 50, 50)"    # Red
    elif font_size > 50: return "rgb(255, 150, 0)"  # Orange
    elif font_size > 30: return "rgb(34, 197, 94)"  # Green
    elif font_size > 15: return "rgb(59, 130, 246)" # Blue
    else: return "rgb(168, 85, 247)"                # Purple

# 4. 사이드바 컨트롤러
st.markdown('<div class="main-title">STREAMLIT INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">WordCloud Masking System</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 분석 설정")
    
    # [기능 1] 데이터 소스 선택
    data_mode = st.radio("데이터 불러오기", ["URL 크롤링", "TXT 파일 업로드"])
    
    source_text = ""
    if data_mode == "URL 크롤링":
        url_input = st.text_input("URL 입력", "https://n.news.naver.com/article/001/0014567890")
    else:
        uploaded_file = st.file_uploader("TXT 파일 선택", type=['txt'])

    # [기능 2] 모양 선택
    shape_choice = st.selectbox("워드클라우드 모양", ["기본(사각형)", "구름", "하트"])
    max_words = st.slider("최대 단어 수", 50, 500, 150)

# 5. 메인 로직 실행
if st.button("🚀 엔진 가동"):
    try:
        # 데이터 텍스트 추출
        with st.spinner("텍스트를 분석하는 중입니다..."):
            if data_mode == "URL 크롤링":
                res = requests.get(url_input, headers={'User-Agent': 'Mozilla/5.0'})
                res.encoding = 'utf-8'
                source_text = BeautifulSoup(res.text, 'html.parser').get_text()
            else:
                if uploaded_file:
                    source_text = uploaded_file.read().decode('utf-8')
                else:
                    st.warning("파일을 먼저 업로드해 주세요.")
                    st.stop()

            # 명사 추출 및 빈도 계산
            okt = Okt()
            nouns = [n for n in okt.nouns(source_text) if len(n) > 1]
            counts = Counter(nouns)

            if not counts:
                st.error("분석할 단어가 없습니다.")
                st.stop()

            # 폰트 경로 (Windows/Mac 대응)
            font_path = "NotoSansKR-Bold.ttf"
            if not os.path.exists(font_path):
                font_path = "C:/Windows/Fonts/malgun.ttf" # Windows 백업

            # 마스크 적용 및 생성
            mask_arr = create_shape_mask(shape_choice)
            
            wc = WordCloud(
                font_path=font_path if os.path.exists(font_path) else None,
                background_color="white",
                width=1000, height=1000,
                max_words=max_words,
                mask=mask_arr,
                color_func=rainbow_color_func,
                contour_width=2 if mask_arr is not None else 0,
                contour_color='skyblue'
            ).generate_from_frequencies(counts)

            # 결과 레이아웃
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader(f"✨ {shape_choice} 결과")
                fig, ax = plt.subplots(figsize=(10, 10))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            
            with col2:
                st.subheader("📊 빈도 순위")
                for i, (word, freq) in enumerate(counts.most_common(10)):
                    st.write(f"**{i+1}. {word}** : {freq}회")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
