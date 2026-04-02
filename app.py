import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import os

# 1. 페이지 설정 및 프리미움 UI 스타일
st.set_page_config(page_title="Premium WordCloud Engine", layout="wide")

st.markdown("""
    <style>
    /* 웹 화면 폰트 설정 (사용자 브라우저용) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    /* 주식 시스템 스타일의 그라데이션 타이틀 */
    .main-title {
        font-size: 42px !important;
        font-weight: 900;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        color: #888;
        font-size: 16px;
        letter-spacing: 3px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }

    /* 입체적인 호버 버튼 */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%);
        color: white !important;
        font-weight: 700;
        border: none;
        padding: 15px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2);
    }

    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(255, 75, 75, 0.4);
        background: linear-gradient(135deg, #FF6B6B 0%, #8E5ACD 100%) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 무지개 컬러 함수 (높음: 빨강 -> 낮음: 보라)
def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # font_size(빈도)에 따른 빨주노초파남보 로직
    if font_size > 75: return "rgb(255, 0, 0)"      # 빨강
    elif font_size > 60: return "rgb(255, 165, 0)" # 주황
    elif font_size > 45: return "rgb(255, 255, 0)" # 노랑
    elif font_size > 30: return "rgb(0, 128, 0)"   # 초록
    elif font_size > 20: return "rgb(0, 0, 255)"   # 파랑
    elif font_size > 10: return "rgb(75, 0, 130)"  # 남색
    else: return "rgb(148, 0, 211)"                # 보라

# 3. 메인 화면 구성
st.markdown('<div class="main-title">NOTO-RAINBOW INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Advanced Linguistic Visualization System</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 분석 컨트롤러")
    url = st.text_input("URL 입력", "https://n.news.naver.com/article/001/0014567890")
    max_words = st.slider("최대 단어 수", 50, 300, 100)

# 4. 실행 로직
if st.button("🚀 분석 엔진 가동"):
    try:
        with st.spinner("노토산스 엔진으로 분석 중..."):
            # 크롤링 및 형태소 분석
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.get_text()

            okt = Okt()
            nouns = [n for n in okt.nouns(text) if len(n) > 1]
            counts = Counter(nouns)

        if counts:
            # --- [노토산스 폰트 경로 설정] ---
            # 파이썬 파일과 같은 폴더에 NotoSansKR-Bold.ttf 가 있어야 합니다.
            font_path = "NotoSansKR-Bold.ttf" 
            
            if not os.path.exists(font_path):
                # 파일이 없을 경우 시스템 폰트 경로를 백업으로 뒤집니다.
                font_path = "C:/Windows/Fonts/malgun.ttf" 

            # 워드클라우드 생성
            wc = WordCloud(
                font_path=font_path if os.path.exists(font_path) else None,
                background_color="white",
                width=1200, height=700,
                max_words=max_words,
                color_func=rainbow_color_func,
                random_state=42
            ).generate_from_frequencies(counts)

            # 시각화 결과 출력
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("📊 무지개 워드클라우드")
                fig, ax = plt.subplots(figsize=(12, 7))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            
            with col2:
                st.subheader("🔝 빈도수 순위")
                for i, (word, freq) in enumerate(counts.most_common(10)):
                    st.write(f"**{i+1}. {word}** ({freq}회)")
            
            if not os.path.exists("NotoSansKR-Bold.ttf") and not os.path.exists("C:/Windows/Fonts/malgun.ttf"):
                st.warning("⚠️ 한글 폰트 파일을 찾지 못해 글자가 깨질 수 있습니다. 폴더에 NotoSansKR-Bold.ttf를 넣어주세요!")

    except Exception as e:
        st.error(f"엔진 오류: {e}")
