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
st.set_page_config(page_title="Premium WordCloud Engine", layout="wide")
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
    /* 버튼 스타일: 그라데이션 + 호버 시 솟아오름 */
    div.stButton > button {
        width: 100%; height: 3.8em; border-radius: 15px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%) !important;
        color: white !important; font-weight: 700 !important; border: none !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-8px) !important; /* 더 다이내믹하게 솟아오름 */
        box-shadow: 0 15px 35px rgba(255, 75, 75, 0.5) !important;
        filter: brightness(1.1);
    }
    </style>
""", unsafe_allow_html=True)

# 2. 마스크 생성 함수 (외곽선 없이 단어만 배치하기 위한 용도)
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

# 3. 빈도 기반 컬러 함수
def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    if font_size > 80: return "rgb(255, 0, 0)"
    elif font_size > 60: return "rgb(255, 165, 0)"
    elif font_size > 45: return "rgb(255, 220, 0)"
    elif font_size > 30: return "rgb(0, 128, 0)"
    elif font_size > 20: return "rgb(0, 0, 255)"
    else: return "rgb(148, 0, 211)"

# 4. 사이드바 구성
st.markdown('<div class="main-title">NO-BORDER CLOUD ENGINE</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("📂 데이터 소스")
    source_type = st.radio("입력 방식", ["URL 크롤링", "TXT 파일 업로드"])
    
    if source_type == "URL 크롤링":
        url = st.text_input("URL 입력", "https://n.news.naver.com/article/001/0014567890")
        uploaded_file = None
    else:
        uploaded_file = st.file_uploader("TXT 파일 선택", type=["txt"])
        url = None

    st.divider()
    st.header("🎨 디자인 설정")
    selected_shape = st.selectbox("모양 선택", ["하트(Heart)", "구름(Cloud)", "원형(Circle)", "사각형(Full)"])
    max_words = st.slider("최대 단어 수", 50, 500, 250)

# 5. 분석 엔진 가동
if st.button("🚀 무지개 분석 엔진 가동"):
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        st.error("⚠️ 폴더에 'NanumGothic.ttf' 파일이 필요합니다!")
    else:
        try:
            content = ""
            with st.spinner("데이터를 가져오는 중..."):
                # URL 크롤링 로직 강화
                if source_type == "URL 크롤링" and url:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    res = requests.get(url, headers=headers, timeout=10)
                    res.encoding = 'utf-8'
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # 본문 영역 탐색
                    target = soup.select_one('article, #articleBodyContents, .article_body, body')
                    content = target.get_text() if target else ""
                
                # 파일 업로드 로직 강화 (인코딩 대응)
                elif source_type == "TXT 파일 업로드" and uploaded_file:
                    raw_bytes = uploaded_file.read()
                    for enc in ['utf-8', 'cp949', 'euc-kr']:
                        try:
                            content = raw_bytes.decode(enc)
                            break
                        except UnicodeDecodeError:
                            continue

                if not content or len(content.strip()) < 10:
                    st.warning("⚠️ 데이터를 불러오지 못했습니다. URL이나 파일 내용을 확인해주세요.")
                    st.stop()

                # 형태소 분석
                okt = Okt()
                nouns = [n for n in okt.nouns(content) if len(n) > 1]
                if not nouns:
                    st.warning("⚠️ 분석할 수 있는 명사가 없습니다.")
                    st.stop()

                counts = Counter(nouns)
                mask_arr = create_mask(selected_shape)

                # 워드클라우드 생성 (contour 관련 설정 제거)
                wc = WordCloud(
                    font_path=font_path,
                    background_color="white",
                    width=1000, height=1000,
                    max_words=max_words,
                    mask=mask_arr,
                    color_func=rainbow_color_func,
                    contour_width=0, # 외곽선 두께 0 (제거)
                    contour_color='white' # 외곽선 색상 무시
                ).generate_from_frequencies(counts)

                # 결과 출력
                col1, col2 = st.columns([3, 1])
                with col1:
                    fig, ax = plt.subplots(figsize=(10, 10))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                with col2:
                    st.subheader("🔝 주요 키워드")
                    for i, (word, freq) in enumerate(counts.most_common(15)):
                        st.write(f"**{i+1}. {word}** ({freq})")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
