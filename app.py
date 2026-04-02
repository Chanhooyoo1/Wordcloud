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
st.set_page_config(page_title="워드클라우드 생성기", layout="wide")
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

# 3. 빈도 기반 컬러 함수
def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    if font_size > 80: return "rgb(255, 0, 0)"
    elif font_size > 60: return "rgb(255, 165, 0)"
    elif font_size > 45: return "rgb(255, 220, 0)"
    elif font_size > 30: return "rgb(0, 128, 0)"
    elif font_size > 20: return "rgb(0, 0, 255)"
    else: return "rgb(148, 0, 211)"

# 4. 사이드바 구성
st.markdown('<div class="main-title">워드클라우드 생성기</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("📂 불러올 방식 선택하기")
    source_type = st.radio("입력 방식", ["웹사이트로 생성하기", "텍스트 파일 업로드"])
    
    if source_type == "웹사이트로 생성하기":
        url = st.text_input("주소를 입력해주세요.", "https://news.google.com/home?hl=ko&gl=KR&ceid=KR%3Ako")
        uploaded_file = None
    else:
        uploaded_file = st.file_uploader("텍스트 파일 선택", type=["txt"])
        url = None

    st.divider()
    st.header("디자인 설정")
    selected_shape = st.selectbox("워드클라우드 모양 선택", ["하트모양", "구름모양", "동그라미", "사각형"])
    max_words = st.slider("생성할 단어 수", 50, 500, 250)

# 5. 분석 엔진 가동
if st.button("워드클라우드 생성하기!"):
    font_path = "SeoulAlrimTTF-Bold.ttf"
    if not os.path.exists(font_path):
        st.error("비상초비상폰트파일이없다삐뽀삐뽀삐뽀삐뽀찬후한테발리전화를하던지말을하던지해주세요제발요")
    else:
        try:
            content = ""
            with st.spinner("가져오는 중입니다..."):
                # URL 크롤링 로직 강화
                if source_type == "주소로 생성하기" and url:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    res = requests.get(url, headers=headers, timeout=10)
                    res.encoding = 'utf-8'
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # 본문 영역 탐색
                    target = soup.select_one('article, #articleBodyContents, .article_body, body')
                    content = target.get_text() if target else ""
                # --- 이 부분을 기존 코드의 if source_type == "URL 크롤링" 블록에 덮어쓰세요 ---
                if source_type == "URL 크롤링" and url:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Referer': 'https://www.google.com/'
                    }
                    res = requests.get(url, headers=headers, timeout=15)
                    res.raise_for_status()
                    res.encoding = res.apparent_encoding # 인코딩 자동 감지 강화
                    
                    soup = BeautifulSoup(res.content, 'html.parser')
                    
                    # 1. 광고, 메뉴, 푸터 등 잡음 제거
                    for junk in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'button', 'input']):
                        junk.decompose()
                    
                    # 2. 본문 추정 로직 (글자수가 가장 많은 태그 찾기)
                    # article, div, section 중 가장 내용이 풍부한 곳을 선택
                    potential_bodies = soup.find_all(['article', 'div', 'main', 'section'])
                    
                    best_text = ""
                    for pb in potential_bodies:
                        # 하위 태그들 사이 공백을 주어 단어가 붙지 않게 추출
                        txt = pb.get_text(separator=' ', strip=True)
                        if len(txt) > len(best_text):
                            best_text = txt
                    
                    # 추출된 텍스트가 너무 짧으면 전체 페이지 텍스트 사용
                    content = best_text if len(best_text) > 100 else soup.get_text(separator=' ', strip=True)
                # ------------------------------------------------------------------
                # 형태소 분석
                okt = Okt()
                nouns = [n for n in okt.nouns(content) if len(n) > 1]
                if not nouns:
                    st.warning("분석할 수 있는 단어가 없어요. 글자 수가 너무 적나봐요.")
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
                    st.subheader("주요 키워드 Top 10")
                    for i, (word, freq) in enumerate(counts.most_common(10)):
                        st.write(f"**{i+1}. {word}** ({freq})")

        except Exception as e:
            st.error(f"삐뽀삐뽀삐뽀삐뽀삐뽀삐뽀초비상여러분을실망시켜드리어서죄송합니다도게자박을게요다음날말씀해주시면바로박겟습니다어왜오류가발생했지이거찬후한테말을하던지전화를하던지해주세요제발요제가이런물의를끼쳐드려서죄송합니다아마도다음날이면말끔히고쳐져잇을거에요진짜로요: {e}")
