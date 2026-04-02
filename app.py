import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw
import os

# 1. 페이지 설정 및 프리미엄 스타일 (그라데이션 & 호버 애니메이션)
st.set_page_config(page_title="Premium Mask Cloud Engine", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* 프리미엄 그라데이션 타이틀 */
    .main-title {
        font-size: 42px; font-weight: 900;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 5px;
    }

    /* 버튼 스타일링: 그라데이션 + 입체감 */
    div.stButton > button {
        width: 100%;
        height: 3.5em;
        border-radius: 15px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }

    /* 버튼 호버 효과: 솟아오름 + 그림자 강화 */
    div.stButton > button:hover {
        transform: translateY(-7px) !important;
        box-shadow: 0 15px 30px rgba(255, 75, 75, 0.6) !important;
        filter: brightness(1.2);
    }
    </style>
""", unsafe_allow_html=True)

# 2. 도형 마스크 생성 함수 (이미지 파일 없이 코드로 생성)
def create_mask(shape_type):
    mask = Image.new("RGB", (1000, 1000), (255, 255, 255))
    draw = ImageDraw.Draw(mask)
    
    if shape_type == "하트(Heart)":
        # 하트 그리기 로직 (간단한 다각형 조합)
        draw.pieslice([(150, 200), (650, 700)], 180, 0, fill=(0, 0, 0))
        draw.pieslice([(350, 200), (850, 700)], 180, 0, fill=(0, 0, 0))
        draw.polygon([(150, 450), (500, 950), (850, 450)], fill=(0, 0, 0))
    elif shape_type == "구름(Cloud)":
        # 구름 모양 (여러 개의 원 조합)
        draw.ellipse([100, 400, 400, 700], fill=(0, 0, 0))
        draw.ellipse([300, 300, 700, 700], fill=(0, 0, 0))
        draw.ellipse([600, 400, 900, 700], fill=(0, 0, 0))
        draw.rectangle([250, 500, 750, 700], fill=(0, 0, 0))
    elif shape_type == "원형(Circle)":
        draw.ellipse([100, 100, 900, 900], fill=(0, 0, 0))
    else: # 사각형
        return None
        
    return np.array(mask)

# 3. 빈도 기반 무지개 색상 함수
def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    if font_size > 80: return "rgb(255, 0, 0)"
    elif font_size > 60: return "rgb(255, 165, 0)"
    elif font_size > 45: return "rgb(255, 220, 0)"
    elif font_size > 30: return "rgb(0, 128, 0)"
    elif font_size > 20: return "rgb(0, 0, 255)"
    else: return "rgb(148, 0, 211)"

# 4. 메인 UI 및 사이드바 선택지
st.markdown('<div class="main-title">SHAPE-SELECT INTELLIGENCE</div>', unsafe_allow_html=True)
st.write("<p style='text-align: center; color: #888;'>Select your shape and analyze</p>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 분석 및 도형 설정")
    url = st.text_input("URL 입력", "https://n.news.naver.com/article/001/0014567890")
    
    # 도형 선택지 추가
    selected_shape = st.selectbox("워드클라우드 모양 선택", ["사각형(Full)", "하트(Heart)", "구름(Cloud)", "원형(Circle)"])
    
    max_words = st.slider("단어수 제한", 50, 500, 200)
    st.divider()
    st.info("💡 '나눔고딕' 폰트를 사용하여 분석합니다.")

# 5. 실행 로직
if st.button("🚀 선택한 모양으로 분석 시작"):
    font_path = "NanumGothic.ttf"
    
    if not os.path.exists(font_path):
        st.error(f"⚠️ '{font_path}' 파일이 없습니다! 폴더에 폰트를 넣어주세요.")
    else:
        try:
            with st.spinner(f"{selected_shape} 모양으로 렌더링 중..."):
                # 1. 크롤링
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                content = soup.get_text()

                # 2. 형태소 분석
                okt = Okt()
                nouns = [n for n in okt.nouns(content) if len(n) > 1]
                counts = Counter(nouns)

                # 3. 마스크 생성
                mask_arr = create_mask(selected_shape)

                # 4. 워드클라우드 생성
                wc = WordCloud(
                    font_path=font_path,
                    background_color="white",
                    width=1000, height=1000,
                    max_words=max_words,
                    mask=mask_arr,
                    color_func=rainbow_color_func,
                    contour_width=1 if mask_arr is not None else 0,
                    contour_color='lightgrey'
                ).generate_from_frequencies(counts)

                # 5. 결과 시각화
                col1, col2 = st.columns([3, 1])
                with col1:
                    fig, ax = plt.subplots(figsize=(10, 10))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)

                with col2:
                    st.subheader("🔝 빈도 TOP 15")
                    for i, (word, freq) in enumerate(counts.most_common(15)):
                        st.write(f"**{i+1}. {word}** ({freq}회)")

        except Exception as e:
            st.error(f"엔진 오류: {e}")
