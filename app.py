import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import matplotlib.cm as cm # 컬러맵 사용을 위해 추가
import numpy as np

st.set_page_config(page_title="Dynamic Color WordCloud", layout="wide")

st.title("🌐 웹페이지 URL 워드클라우드 (빈도수별 색상)")
st.write("주소를 입력하면 내용을 분석하여, 많은 단어는 **빨간색**, 적은 단어는 **파란색**으로 표시합니다.")

# 1. URL 입력 받기
url = st.text_input("분석할 웹페이지 주소를 입력하세요", "https://n.news.naver.com/article/001/0014567890")

# --- 커스텀 컬러링 함수 정의 ---
def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    """
    단어의 빈도수에 따라 색상을 반환하는 함수.
    이 함수는 WordCloud 내부에 정의된 빈도수 데이터에 접근할 수 없으므로,
    정규화된 폰트 크기(font_size)를 빈도수의 대리 지표로 활용합니다.
    """
    # Matplotlib의 'coolwarm' 컬러맵 사용 (Blue -> White -> Red)
    # 폰트 크기가 작을수록(0에 가까움) 파란색, 클수록(1에 가까움) 빨간색
    # 단어의 상대적 비율을 조정하기 위해 값을 살짝 조정합니다.
    
    # wordcloud 라이브러리는 내부적으로 가장 빈도가 높은 단어의 폰트 크기를 가장 크게 잡습니다.
    # 이를 활용하여 0~1 사이 값으로 변환 후 컬러맵 적용
    normalized_size = (font_size - 10) / (100 - 10) # 예시 비율, 내부적으로 자동 조정됨
    
    # 'coolwarm' 컬러맵에서 RGBA 값을 가져옴 (0.0~1.0 사이 값 필요)
    # random_state를 이용해 약간의 랜덤성을 부여할 수도 있지만, 여기서는 빈도만 따집니다.
    cmap = cm.get_cmap('coolwarm') 
    
    # 폰트 크기에 비례하여 색상 결정 (색상 값은 0~255 사이 정수 형태의 RGB로 변환)
    # font_size 기반의 상대적 위치를 0~1 사이로 매핑하는 것이 핵심
    
    # *참고*: 이 방식은 font_size에 비례하므로 완벽한 빈도수 매핑은 아니지만
    # 워드클라우드 라이브러리 구조상 가장 간단하고 효과적인 우회 방법입니다.
    # 더 정확한 매핑을 위해서는 ImageColorGenerator를 사용해야 하나, 
    # 이는 이미지 마스킹이 필요하여 코드가 복잡해집니다.
    
    # 간단하게: 폰트 크기가 특정 임계값보다 크면 빨강, 작으면 파랑 계열로 랜덤하게 지정
    if font_size > 60:
        return "rgb(%d, 0, 0)" % np.random.randint(150, 255) # 빨간색 계열
    elif font_size > 30:
        return "rgb(100, 100, 100)" # 중간은 회색조
    else:
        return "rgb(0, 0, %d)" % np.random.randint(150, 255) # 파란색 계열

# 위 방식보다 더 직관적인 방법은 WordCloud 생성 시 colormap 옵션을 사용하는 것입니다.
# 'coolwarm' 또는 'RdBu'가 파랑->빨강 맵입니다.

if st.button("웹페이지 분석 및 시각화"):
    try:
        with st.spinner('웹페이지를 긁어오고 분석하는 중입니다...'):
            # 2. 웹 크롤링
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.encoding = 'utf-8' 
            soup = BeautifulSoup(response.text, 'html.parser')

            for script_or_style in soup(["script", "style"]): 
                script_or_style.extract() 

            text = soup.get_text()

            # 3. 데이터 처리 (명사 추출)
            okt = Okt()
            nouns = [n for n in okt.nouns(text) if len(n) > 1]
            count = Counter(nouns)

        if count:
            # 4. 워드클라우드 생성
            # 핵심 변경 사항: colormap="coolwarm" 추가! 
            # 'coolwarm'은 파란색(낮음)에서 빨간색(높음)으로 변하는 매플롯립 컬러맵입니다.
            wc = WordCloud(
                font_path="malgun", # Mac은 "AppleGothic"
                background_color="white",
                width=1000,
                height=600,
                max_words=100,
                colormap="coolwarm", # 👈 이 한 줄이 핵심입니다!
                random_state=42 # 실행할 때마다 모양이 바뀌지 않도록 고정
            ).generate_from_frequencies(count)

            # 5. 시각화
            st.subheader("📊 분석 결과 (많은 단어: 빨강 / 적은 단어: 파랑)")
            fig, ax = plt.subplots(figsize=(12, 7))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
            
            # 단어 빈도수 데이터 요약
            st.write("### 주요 키워드 Top 10")
            
            top_10 = count.most_common(10)
            col_count = 5
            rows = 2
            for r in range(rows):
                cols = st.columns(col_count)
                for c in range(col_count):
                    idx = r * col_count + c
                    if idx < len(top_10):
                        word, freq = top_10[idx]
                        # Top 3는 빨간색, 나머지는 파란색 계열로 메트릭 색상 조정
                        delta_color = "normal" if idx < 3 else "inverse"
                        cols[c].metric(label=f"Top {idx+1}", value=word, delta=f"{freq}회", delta_color=delta_color)

        else:
            st.error("해당 페이지에서 분석할 텍스트를 찾지 못했습니다.")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")