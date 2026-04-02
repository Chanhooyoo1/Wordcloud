import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import io

# 1. 페이지 설정
st.set_page_config(page_title="Premium WordCloud Analyzer", layout="wide")

# 2. 주식 시스템의 UI 스타일 이식 (그라데이션 + 호버 + 브라우저 폰트)
st.markdown("""
    <style>
    /* 폰트 시스템: 사용자의 브라우저 폰트(맑은 고딕 등)를 최우선으로 사용 */
    html, body, [class*="css"] {
        font-family: 'Pretendard', 'Malgun Gothic', sans-serif !important;
    }

    /* 메인 타이틀: 그라데이션 디자인 */
    .main-title {
        font-size: 42px !important;
        font-weight: 900;
        background: linear-gradient(135deg, #FF4B4B 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }

    /* 서브 타이틀 */
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 18px;
        margin-bottom: 30px;
    }

    /* 버튼 스타일: 주식 시스템의 호버 애니메이션 적용 */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #FF4B4B, #764BA2);
        color: white !important;
        font-weight: 700;
        border: none;
        padding: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2);
    }

    /* 버튼 호버 시 효과 */
    div.stButton > button:hover {
        transform: translateY(-3px); /* 위로 띄우기 */
        box-shadow: 0 8px 25px rgba(255, 75, 75, 0.4);
        background: linear-gradient(135deg, #FF6B6B, #8E5ACD) !important;
    }

    /* 분석 결과 박스 디자인 */
    .result-card {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 75, 75, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# 3. 상단 타이틀 섹션
st.markdown('<div class="main-title">🌐 AI WORDCLOUD SYSTEM</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">데이터 시각화 및 키워드 추출 엔진</div>', unsafe_allow_html=True)

# 4. 사이드바 및 입력 섹션
with st.sidebar:
    st.header("⚙️ 분석 설정")
    mode = st.radio("데이터 소스", ["웹페이지 URL", "텍스트 파일(.txt)"])
    
    if mode == "웹페이지 URL":
        url = st.text_input("분석할 주소", "https://n.news.naver.com/article/001/0014567890")
    else:
        uploaded_file = st.file_uploader("파일 선택", type=['txt'])
    
    st.divider()
    max_words = st.slider("최대 단어 수", 50, 300, 100)
    stop_words_input = st.text_area("제외할 단어", "기자, 뉴스, 배포, 금지")
    stop_words = [w.strip() for w in stop_words_input.split(",")]

# 5. 분석 로직
if st.button("🚀 데이터 분석 및 워드클라우드 생성"):
    try:
        with st.spinner("데이터를 처리하는 중입니다..."):
            # 데이터 수집
            if mode == "웹페이지 URL":
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                for s in soup(["script", "style"]): s.extract()
                text = soup.get_text()
            else:
                if uploaded_file:
                    text = uploaded_file.read().decode("utf-8")
                else:
                    st.error("파일을 업로드해주세요."); st.stop()

            # 명사 추출
            okt = Okt()
            nouns = [n for n in okt.nouns(text) if len(n) > 1 and n not in stop_words]
            counts = Counter(nouns)

            if counts:
                # 워드클라우드 생성 (폰트 경로 에러 방지 로직)
                # 윈도우 기본 폰트 경로를 시도하되, 없으면 기본값 사용
                font_path = "C:/Windows/Fonts/malgun.ttf"
                import os
                if not os.path.exists(font_path): font_path = None

                wc = WordCloud(
                    font_path=font_path,
                    background_color="white",
                    width=1200, height=700,
                    max_words=max_words,
                    colormap="coolwarm", # 빈도별 색상 (Blue -> Red)
                    random_state=42
                ).generate_from_frequencies(counts)

                # 결과 출력
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📊 시각화 결과")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("🔝 주요 키워드")
                    for i, (word, freq) in enumerate(counts.most_common(10)):
                        color = "#FF4B4B" if i < 3 else "#764BA2"
                        st.markdown(f"**{i+1}.** <span style='color:{color}; font-size:18px;'>{word}</span> ({freq}회)", unsafe_allow_html=True)
            else:
                st.warning("분석할 텍스트가 부족합니다.")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
