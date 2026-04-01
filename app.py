import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import os

# 1. 페이지 설정
st.set_page_config(page_title="Multi-Source WordCloud", layout="wide")

# 2. 폰트 경로 설정 (윈도우 기본 맑은 고딕 경로)
# 만약 Mac 사용자라면 "/System/Library/Fonts/Supplemental/AppleGothic.ttf"로 변경하세요.
FONT_PATH = "C:/Windows/Fonts/맑은 고딕.ttf"

st.title("📊 통합 워드클라우드 분석기")
st.write("웹페이지 주소를 입력하거나, 메모장(.txt) 파일을 업로드하여 단어 빈도를 분석해보세요.")

# --- 사이드바: 설정 및 파일 업로드 ---
with st.sidebar:
    st.header("🛠 설정 및 업로드")
    
    # 분석 모드 선택
    mode = st.radio("분석 대상을 선택하세요", ["웹페이지 URL", "텍스트 파일 업로드"])
    
    if mode == "웹페이지 URL":
        url = st.text_input("URL 입력", "https://n.news.naver.com/article/001/0014567890")
    else:
        uploaded_file = st.file_uploader("텍스트 파일 선택 (.txt)", type=["txt"])
    
    st.divider()
    max_words = st.slider("최대 단어 수", 50, 300, 100)
    stop_words_input = st.text_area("제외할 단어 (쉼표 구분)", "기자, 뉴스, 무단, 배포, 금지")
    stop_words = [w.strip() for w in stop_words_input.split(",")]

# --- 데이터 처리 함수 ---
def get_nouns(text):
    okt = Okt()
    # 2글자 이상인 명사만 추출 및 불용어 제거
    nouns = [n for n in okt.nouns(text) if len(n) > 1 and n not in stop_words]
    return Counter(nouns)

# --- 메인 실행 로직 ---
text_data = ""

if st.button("🚀 분석 시작"):
    try:
        # 데이터 수집 단계
        if mode == "웹페이지 URL":
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            for s in soup(["script", "style"]): s.extract()
            text_data = soup.get_text()
        else:
            if uploaded_file is not None:
                # 업로드된 파일 읽기
                text_data = uploaded_file.read().decode("utf-8")
            else:
                st.warning("분석할 파일을 먼저 업로드해주세요.")
                st.stop()

        # 분석 및 시각화 단계
        if text_data:
            with st.spinner("단어 분석 및 시각화 중..."):
                counts = get_nouns(text_data)
                
                if not counts:
                    st.error("분석할 단어가 충분하지 않습니다.")
                    st.stop()

                # 워드클라우드 생성
                wc = WordCloud(
                    font_path=FONT_PATH,
                    background_color="white",
                    width=1200,
                    height=700,
                    max_words=max_words,
                    colormap="coolwarm"
                ).generate_from_frequencies(counts)

                # 레이아웃 구성
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.subheader("🖼 워드클라우드")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)

                with col2:
                    st.subheader("📈 Top 10 빈도")
                    top_10 = counts.most_common(10)
                    for i, (word, freq) in enumerate(top_10):
                        st.write(f"**{i+1}. {word}** ({freq}회)")

    except OSError:
        st.error(f"폰트 파일을 찾을 수 없습니다: {FONT_PATH}")
        st.info("윈도우 사용자라면 경로가 맞는지 확인하시고, Mac/Linux라면 해당 OS의 폰트 경로로 수정해야 합니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")
