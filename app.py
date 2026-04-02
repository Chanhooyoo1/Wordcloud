import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFont  # 여기에 ImageFont가 있어야 '직접 글자 입력'이 작동해요!
import os

# 1. 스타일 설정
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
    div.stButton > button {
        width: 100%; height: 3.8em; border-radius: 15px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%) !important;
        color: white !important; font-weight: 700 !important; border: none !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 15px 35px rgba(255, 75, 75, 0.5) !important;
        filter: brightness(1.1);
    }
    </style>
""", unsafe_allow_html=True)

# 2. 마스크 생성 함수
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

# 3. 빈도 기반 컬러 함수 (큰 단어 = 파란색 계열)
def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # 1. 가장 큰 핵심 단어 (이미지의 '가상현실' 스타일 - 파랑/청록)
    if font_size > 90: 
        return "rgb(20, 200, 255)"      # 밝은 하늘색 (Cyan)
    
    # 2. 두 번째로 큰 단어 (진한 파랑/남색)
    elif font_size > 70: 
        return "rgb(30, 80, 255)"       # 선명한 파란색 (Blue)
    
    # 3. 중간 크기 단어 (보라/자주)
    elif font_size > 50: 
        return "rgb(160, 50, 255)"      # 보라색 (Purple)
    
    # 4. 중간 이하 단어 (연두/초록)
    elif font_size > 35: 
        return "rgb(150, 230, 50)"      # 밝은 연두색 (Lime)
    
    # 5. 작은 단어 (주황/노랑)
    elif font_size > 20: 
        return "rgb(255, 150, 0)"       # 주황색 (Orange)
    
    # 6. 가장 작은 보조 단어 (빨강/핑크)
    else: 
        return "rgb(255, 75, 88)"       # 부드러운 빨강 (Soft Red)

# 4. 사이드바 구성
st.markdown('<div class="main-title">워드클라우드 생성기</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("📂 1. 데이터 소스")
    source_type = st.radio("입력 방식", ["웹사이트로 생성하기", "텍스트 파일 업로드"])
    
    if source_type == "웹사이트로 생성하기":
        url = st.text_input("주소를 입력해주세요.", "https://news.google.com/home?hl=ko&gl=KR&ceid=KR%3Ako")
        uploaded_file = None
    else:
        uploaded_file = st.file_uploader("텍스트 파일 선택", type=["txt"])
        url = None

    st.divider()  # <--- 이 줄의 들여쓰기가 앞뒤 코드와 일직선이어야 합니다!
    
    st.header("🎨 2. 모양 설정")
    shape_option = st.selectbox("모양 결정 방식", ["직접 글자 입력", "이미지 파일 업로드", "기본 도형"])
    
    if shape_option == "직접 글자 입력":
        user_shape = st.text_input("원하는 글자를 입력하세요", "ESTJ")
    elif shape_option == "이미지 파일 업로드":
        mask_file = st.file_uploader("모양으로 쓸 이미지 업로드", type=["jpg", "jpeg", "png"])
    else:
        # 이 부분이 정의되어야 'selected_shape' 에러가 안 납니다!
        selected_shape = st.selectbox("도형 선택", ["하트모양", "구름모양", "동그라미", "사각형"])

    st.divider()
    max_words = st.slider("생성할 단어 수", 50, 500, 250)
# 5. 분석 엔진 가동
if st.button("워드클라우드 생성하기!"):
    # 1. 폰트 경로를 여기에 정확히 입력하세요!
    font_path = "NanumGothicExtraBold.ttf" 
    
    # 폰트 파일이 실제 폴더에 있는지 체크
    if not os.path.exists(font_path):
        st.error("삐뽀삐뽀삐뽀삐뽀삐뽀삐뽀초비상여러분을실망시켜드리어서죄송합니다도게자박을게요다음날말씀해주시면바로박겟습니다어왜오류가발생했지이거찬후한테말을하던지전화를하던지해주세요제발요제가이런물의를끼쳐드려서죄송합니다아마도다음날이면말끔히고쳐져잇을거에요진짜로요")
    else:
        try:
            # 2. content는 처음에 비워두어야 크롤링/파일 결과가 정상적으로 담깁니다.
            content = "" 
            mask_arr = None  # 마스크 변수 초기화

            with st.spinner("생성 중이예요..."):
                # --- 데이터 가져오기 로직 ---
                if source_type == "웹사이트로 생성하기" and url:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    res = requests.get(url, headers=headers, timeout=15)
                    res.encoding = res.apparent_encoding
                    soup = BeautifulSoup(res.text, 'html.parser')
                    
                    for junk in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                        junk.decompose()
                        
                    potential_bodies = soup.find_all(['article', 'div', 'main', 'section'])
                    content = max([pb.get_text(separator=' ', strip=True) for pb in potential_bodies], key=len) if potential_bodies else soup.get_text()
                
                elif source_type == "텍스트 파일 업로드" and uploaded_file:
                    raw_bytes = uploaded_file.read()
                    for enc in ['utf-8', 'cp949', 'euc-kr']:
                        try:
                            content = raw_bytes.decode(enc)
                            break
                        except: continue

                # 데이터가 잘 가져와졌는지 체크
                if not content or len(content.strip()) < 10:
                    st.warning("분석할 단어가 부족해요. 주소나 파일을 다시 확인해주세요.")
                    st.stop()

                # --- 3. 여기서부터 마스크 생성 및 워드클라우드 로직 시작 ---
                # (이전에 드린 shape_option 관련 마스크 생성 코드를 이어서 붙이시면 됩니다!)

                # 3. 단어 분석
                okt = Okt()
                nouns = [n for n in okt.nouns(content) if len(n) > 1]
                counts = Counter(nouns)

                # 4. 워드클라우드 생성 (여백 최소화 설정)
                wc = WordCloud(
                    font_path=font_path,
                    background_color="#1a1c23", # 어두운 배경 (파란 글씨가 잘 보임)
                    width=mask_arr.shape[1] if mask_arr is not None else 1000,
                    height=mask_arr.shape[0] if mask_arr is not None else 1000,
                    max_words=max_words,
                    mask=mask_arr,
                    color_func=rainbow_color_func,
                    margin=0,               # 여백 0
                    prefer_horizontal=0.9,   # 가로 위주
                    relative_scaling=0.5,    # 빈틈 채우기 최적화
                    min_font_size=5,         # 작은 글자로 빈틈 메우기
                    repeat=True,             # 모양을 꽉 채우기 위해 단어 반복
                    contour_width=0
                ).generate_from_frequencies(counts)

                # 5. 결과 출력
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
