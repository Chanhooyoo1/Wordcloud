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
st.set_page_config(page_title="Multi-Source Cloud Engine", layout="wide")
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

# 2. 마스크 및 컬러 함수
def create_mask(shape_type):
    mask = Image.new("RGB", (1000, 1000), (255, 255, 255))
    draw = ImageDraw.Draw(mask)
    if shape_type == "하트(Heart)":
        draw.pieslice([(150, 200), (650, 700)], 180, 0, fill=(0, 0, 0))
        draw.pieslice([(350, 200), (850, 700)], 180, 0, fill=(0, 0, 0))
        draw.polygon([(150, 450), (500, 950), (850, 450)], fill=(0, 0, 0))
    elif shape_type == "구름(Cloud)":
        draw.ellipse([100, 400, 400, 700], fill=(0, 0, 0))
        draw.ellipse([300, 300, 700, 700], fill=(0, 0, 0))
        draw.ellipse([600, 400, 900, 700], fill=(0, 0, 0))
        draw.rectangle([250, 500, 750, 700], fill=(0, 0, 0))
    elif shape_type == "원형(Circle)":
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
    st.header("⚙️ 데이터 소스 선택")
    source_type = st.radio("분석 대상을 선택하세요", ["URL 크롤링", "TXT 파일 업로드"])
    
    if source_type == "URL 크롤링":
        url = st.text_input("URL 입력", "https://n.news.naver.com/article/001/0014567890")
        uploaded_file = None
    else:
        uploaded_file = st.file_uploader("텍스트(.txt) 파일을 선택하세요", type=["txt"])
        url = None

    st.divider()
    selected_shape = st.selectbox("모양 선택", ["사각형(Full)", "하트(Heart)", "구름(Cloud)", "원형(Circle)"])
    max_words = st.slider("단어수 제한", 50, 500, 200)

# 4. 분석 실행 로직
if st.button("🚀 분석 엔진 가동"):
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        st.error("⚠️ 'NanumGothic.ttf' 파일이 없습니다! 폰트를 폴더에 넣어주세요.")
    else:
        try:
            content = ""
            with st.spinner("데이터 분석 중..."):
                # --- 수정 포인트: 데이터 읽기 로직 강화 ---
                if source_type == "URL 크롤링" and url:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    res = requests.get(url, headers=headers)
                    res.encoding = 'utf-8'
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # 뉴스 기사 본문 위주로 가져오되 없으면 전체 텍스트
                    article = soup.select_one('article') or soup.select_one('#articleBodyContents') or soup.body
                    content = article.get_text() if article else ""
                
                elif source_type == "TXT 파일 업로드" and uploaded_file:
                    # 인코딩 오류 방지 (utf-8 시도 후 안되면 cp949)
                    raw_data = uploaded_file.read()
                    try:
                        content = raw_data.decode("utf-8")
                    except UnicodeDecodeError:
                        content = raw_data.decode("cp949")
                
                # 내용 검증
                if not content or len(content.strip()) < 5:
                    st.warning("⚠️ 읽어온 텍스트 내용이 너무 적거나 없습니다. 소스를 확인해주세요.")
                    st.stop()

                # 형태소 분석
                okt = Okt()
                nouns = [n for n in okt.nouns(content) if len(n) > 1]
                
                if not nouns:
                    st.warning("⚠️ 분석된 명사가 없습니다. 다른 텍스트를 입력해보세요.")
                    st.stop()

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
                    st.subheader("🔝 빈도 TOP 15")
                    for i, (word, freq) in enumerate(counts.most_common(15)):
                        st.write(f"**{i+1}. {word}** ({freq}회)")

        except Exception as e:
            st.error(f"엔진 오류 발생: {e}")
