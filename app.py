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

# 1. 스타일 설정 (그라데이션 & 호버 애니메이션)
st.set_page_config(page_title="무설치 워드클라우드 생성기", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif !important; }
    .main-title {
        font-size: 42px; font-weight: 900;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 5px;
    }
    div.stButton > button {
        width: 100%; height: 3.5em; border-radius: 15px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%) !important;
        color: white !important; font-weight: 700 !important; border: none !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-7px) !important;
        box-shadow: 0 15px 30px rgba(255, 75, 75, 0.6) !important;
        filter: brightness(1.2);
    }
    </style>
""", unsafe_allow_html=True)

# 2. 마스크 및 컬러 함수 (이전과 동일)
def create_mask(shape_type):
    mask = Image.new("RGB", (1000, 1000), (255, 255, 255))
    draw = ImageDraw.Draw(mask)
    if shape_type == "하트모양":
        draw.pieslice([(150, 200), (650, 700)], 180, 0, fill=(0, 0, 0))
        draw.pieslice([(350, 200), (850, 700)], 180, 0, fill=(0, 0, 0))
        draw.polygon([(150, 450), (500, 950), (850, 450)], fill=(0, 0, 0))
    elif shape_type == "구름모양":
        draw.ellipse([100, 400, 400, 700], fill=(0, 0, 0))
        draw.ellipse([300, 300, 700, 700], fill=(0, 0, 0))
        draw.ellipse([600, 400, 900, 700], fill=(0, 0, 0))
        draw.rectangle([250, 500, 750, 700], fill=(0, 0, 0))
    elif shape_type == "동그라미":
        draw.ellipse([100, 100, 900, 900], fill=(0, 0, 0))
    else: return None
    return np.array(mask)

def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    if font_size > 80: return "rgb(255, 0, 0)"
    elif font_size > 60: return "rgb(255, 165, 0)"
    elif font_size > 45: return "rgb(255, 220, 0)"
    elif font_size > 30: return "rgb(0, 128, 0)"
    elif font_size > 20: return "rgb(0, 0, 255)"
    else: return "rgb(148, 0, 211)"

# 3. 메인 화면 및 사이드바
st.markdown('<div class="main-title">MULTI-SOURCE INTELLIGENCE</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("불러올 매체 선택")
    # --- 변경 포인트 1: 입력 방식 선택 라디오 버튼 ---
    source_type = st.radio("분석할 대상을 선택하세요", ["웹페이지 주소", "텍스트 파일 업로드"])
    
    if source_type == "웹페이지 주소":
        url = st.text_input("주소 입력", "https://news.google.com/home?hl=ko&gl=KR&ceid=KR%3Ako")
        uploaded_file = None
    else:
        # --- 변경 포인트 2: 파일 업로더 추가 ---
        uploaded_file = st.file_uploader("텍스트 파일을 선택해주세요", type=["txt"])
        url = None

    st.divider()
    selected_shape = st.selectbox("워드클라우드 모양 선택", ["사각형", "하트모양", "구름모양", "동그라미"])
    max_words = st.slider("단어 수 선택", 50, 500, 200)

# 4. 분석 실행 로직
if st.button("생성하기!"):
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        st.error("파일이없대요삐뽀삐뽀당장찬후한테전화를걸든지말을하던지하세요")
    else:
        try:
            content = ""
            with st.spinner("생성 중이예요."):
                # --- 변경 포인트 3: 소스에 따라 텍스트를 읽어오는 조건문 ---
                if source_type == "사이트 주소로 생성" and url:
                    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                    res.encoding = 'utf-8'
                    soup = BeautifulSoup(res.text, 'html.parser')
                    content = soup.get_text()
                
                elif source_type == "텍스트 파일 업로드" and uploaded_file:
                    # 업로드된 파일을 문자열로 변환
                    content = uploaded_file.read().decode("utf-8")
                
                if not content:
                    st.warning("텍스트 파일 선택을 안했나봐요. 다시 시도해보세요.")
                    st.stop()

                # 분석 및 렌더링 (이전과 동일)
                okt = Okt()
                nouns = [n for n in okt.nouns(content) if len(n) > 1]
                counts = Counter(nouns)
                mask_arr = create_mask(selected_shape)

                wc = WordCloud(
                    font_path=font_path, background_color="white",
                    width=1000, height=1000, max_words=max_words,
                    mask=mask_arr, color_func=rainbow_color_func,
                    contour_width=0.5, contour_color='lightgrey'
                ).generate_from_frequencies(counts)

                col1, col2 = st.columns([3, 1])
                with col1:
                    fig, ax = plt.subplots(figsize=(10, 10))
                    ax.imshow(wc, interpolation='bilinear'); ax.axis('off')
                    st.pyplot(fig)
                with col2:
                    st.subheader("Top 15")
                    for i, (word, freq) in enumerate(counts.most_common(15)):
                        st.write(f"**{i+1}. {word}** ({freq}회)")

        except Exception as e:
            st.error(f"오류오류오류오류아이고찬후한테빨리전화를걸든지말을하던지하세욥ㅂ: {e}")
