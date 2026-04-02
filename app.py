import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import os
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="AI 시각화 시스템", layout="wide")

# 2. [디자인 부활] 주식 시스템 스타일 가이드
st.markdown("""
    <style>
    /* 브라우저 폰트 시스템 */
    html, body, [class*="css"] {
        font-family: 'Pretendard', 'Malgun Gothic', sans-serif !important;
    }

    /* 메인 타이틀: 빨강-보라 그라데이션 */
    .main-title {
        font-size: 42px !important;
        font-weight: 900;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: -20px;
    }

    .sub-title {
        text-align: center;
        color: #888;
        font-size: 18px;
        letter-spacing: 2px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }

    /* 주식 시스템 스타일의 호버 버튼 */
    div.stButton > button {
        width: 100%;
        border-radius: 15px;
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

    /* 사이드바 다크 카드 스타일 */
    section[data-testid="stSidebar"] {
        background-color: #111;
    }
    </style>
""", unsafe_allow_html=True)

# 3. [색상 로직] 빈도수별 무지개 컬러 함수
def rainbow_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # 폰트 크기가 클수록(빈도가 높을수록) 빨강/주황/노랑 계열
    # 폰트 크기가 작을수록(빈도가 낮을수록) 파랑/남색/보라 계열
    if font_size > 70: # 매우 높음: 빨강
        return "hsl(0, 100%, 50%)"
    elif font_size > 50: # 높음: 주황~노랑
        return f"hsl({np.random.randint(30, 60)}, 100%, 50%)"
    elif font_size > 30: # 중간: 초록~연두
        return f"hsl({np.random.randint(80, 140)}, 100%, 50%)"
    else: # 낮음: 파랑~보라
        return f"hsl({np.random.randint(200, 280)}, 100%, 50%)"

# 4. 타이틀 렌더링
st.markdown('<div class="main-title">REAL-TIME WORD INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">𝖵𝗂𝗌𝗎𝖺𝗅𝗂𝗓𝖺𝗍𝗂𝗈𝗇 & 𝖪𝖾𝗒𝗐𝗈𝗋𝖽 𝖤𝗇𝗀𝗂𝗇𝖾</div>', unsafe_allow_html=True)

# 5. 사이드바 설정
with st.sidebar:
    st.header("⚙️ 분석 제어")
    mode = st.radio("데이터 소스", ["URL 분석", "파일 업로드"])
    
    source = ""
    if mode == "URL 분석":
        source = st.text_input("URL 주소", "https://n.news.naver.com/article/001/0014567890")
    else:
        uploaded_file = st.file_uploader("텍스트 파일", type=['txt'])

    st.divider()
    max_words = st.slider("최대 단어 수", 50, 300, 100)
    stop_words_raw = st.text_area("제외 단어", "기자, 뉴스, 배포, 금지")
    stop_words = [x.strip() for x in stop_words_raw.split(",")]

# 6. 실행 및 시괄화
if st.button("🚀 데이터 엔진 가동"):
    try:
        with st.spinner("언어 모델 분석 중..."):
            # 데이터 로딩
            if mode == "URL 분석":
                res = requests.get(source, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                for s in soup(["script", "style"]): s.extract()
                raw_text = soup.get_text()
            else:
                if uploaded_file:
                    raw_text = uploaded_file.read().decode('utf-8')
                else:
                    st.warning("파일을 올려주세요."); st.stop()

            # 명사 추출 및 빈도 계산
            okt = Okt()
            nouns = [n for n in okt.nouns(raw_text) if len(n) > 1 and n not in stop_words]
            counts = Counter(nouns)

        if counts:
            # 폰트 경로 자동 탐색 (네모 방지)
            font_path = "C:/Windows/Fonts/malgun.ttf"
            if not os.path.exists(font_path):
                font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf" # 리눅스 서버용
            
            # 워드클라우드 생성 (무지개 컬러 함수 적용)
            wc = WordCloud(
                font_path=font_path if os.path.exists(font_path) else None,
                background_color="white",
                width=1200, height=700,
                max_words=max_words,
                color_func=rainbow_color_func, # 커스텀 무지개 색상 로직 적용!
                random_state=42
            ).generate_from_frequencies(counts)

            # 결과 출력
            c1, c2 = st.columns([3, 1])
            with c1:
                st.subheader("📊 키워드 분포 (무지개 필터)")
                fig, ax = plt.subplots(figsize=(12, 7))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            
            with c2:
                st.subheader("🔝 TOP 10")
                for i, (word, freq) in enumerate(counts.most_common(10)):
                    st.markdown(f"**{i+1}. {word}** : {freq}회")
        else:
            st.error("데이터가 부족합니다.")

    except Exception as e:
        st.error(f"엔진 오류: {e}")
        st.info("Tip: 한글 폰트가 없는 환경이면 글자가 깨질 수 있습니다.")
