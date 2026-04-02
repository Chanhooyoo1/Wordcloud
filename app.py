import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="WordCloud Maker", layout="wide")

# 2. 폰트 경로 설정 (가장 흔한 경로 3가지를 다 시도해봅니다)
def get_font():
    # 시도해볼 폰트 경로들
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",              # 윈도우
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf", # 리눅스(서버)
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf", # 맥
        "malgun.ttf" # 현재 폴더에 복사해둔 경우
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            return path
    return None # 아무것도 없으면 None 반환 (기본 폰트 사용)

st.title("🌐 웹 & 파일 통합 워드클라우드")
st.info("URL을 입력하거나 .txt 파일을 업로드하세요. (폰트가 없어도 실행됩니다!)")

# --- 사이드바 설정 ---
with st.sidebar:
    st.header("📂 데이터 소스")
    choice = st.radio("분석 대상을 고르세요", ["URL 주소", "텍스트 파일(.txt)"])
    
    source_data = ""
    if choice == "URL 주소":
        url = st.text_input("분석할 주소", "https://n.news.naver.com/article/001/0014567890")
    else:
        uploaded_file = st.file_uploader("파일 업로드", type=['txt'])

    st.divider()
    max_words = st.number_input("최대 단어 수", value=100)
    stop_words_raw = st.text_area("제외할 단어 (쉼표로 구분)", "기자, 뉴스, 무단, 배포, 금지")
    stop_words = [x.strip() for x in stop_words_raw.split(",")]

# --- 분석 버튼 클릭 시 ---
if st.button("분석 시작!"):
    try:
        with st.spinner("데이터를 가져오는 중..."):
            # 데이터 가져오기
            if choice == "URL 주소":
                resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.text, 'html.parser')
                for tag in soup(['script', 'style', 'header', 'footer']): tag.extract()
                source_data = soup.get_text()
            else:
                if uploaded_file:
                    source_data = uploaded_file.read().decode('utf-8')
                else:
                    st.warning("파일을 먼저 업로드해주세요!")
                    st.stop()

        if source_data:
            # 형태소 분석 (명사 추출)
            okt = Okt()
            nouns = [n for n in okt.nouns(source_data) if len(n) > 1 and n not in stop_words]
            counts = Counter(nouns)

            if not counts:
                st.error("분석할 단어가 없습니다.")
            else:
                # 워드클라우드 생성
                target_font = get_font()
                
                # 폰트가 없어도 에러 안 나게 처리
                wc_params = {
                    "background_color": "white",
                    "width": 1000,
                    "height": 600,
                    "max_words": max_words,
                    "colormap": "coolwarm",
                    "random_state": 42
                }
                
                if target_font:
                    wc_params["font_path"] = target_font
                
                wc = WordCloud(**wc_params).generate_from_frequencies(counts)

                # 시각화
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader("📊 시각화 결과")
                    fig, ax = plt.subplots()
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("🔝 인기 단어")
                    for word, freq in counts.most_common(10):
                        st.write(f"- **{word}**: {freq}회")
                
                if not target_font:
                    st.warning("⚠️ 시스템에 한글 폰트가 없어 글자가 깨져 보일 수 있습니다. (코드가 멈추지는 않습니다)")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
