import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # genre 열에 세로막대(|)로 여러 장르가 적힌 경우 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # openDt(여덟 자리 숫자, 예: 20230115)를 날짜 타입으로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")

    return df


df = load_data(DATA_URL)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "최근 1년간 박스오피스 10위권에 든 영화 가운데, 해당 기간에 개봉한 216편의 데이터를 살펴봅니다."
)

with st.expander("📋 원본 데이터 보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ------------------------------------------------------------
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# ------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)
genre_counts.columns = ["genre", "count"]

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig_genre.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_genre.update_layout(
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_genre, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 문장을 작성해 주세요.")

st.divider()

# ------------------------------------------------------------
# 그래프 2. 장르 안의 영화 - 트리맵 (칸 크기: 총 관객)
# ------------------------------------------------------------
st.header("2. 장르별 영화 트리맵 (칸 크기 = 총 관객)")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 문장을 작성해 주세요.")

st.divider()

# ------------------------------------------------------------
# 그래프 3. 총 관객 히스토그램
# ------------------------------------------------------------
st.header("3. 총 관객 수 분포")

NBINS = 30

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=NBINS,
)
fig_hist.update_traces(
    hovertemplate="관객 구간: %{x}<br>영화 수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 수",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_hist, use_container_width=True)

# 대부분의 영화가 몰려 있는 구간 계산
counts, bin_edges = np.histogram(df["total_audi"].dropna(), bins=NBINS)
max_bin_idx = counts.argmax()
bin_start = int(bin_edges[max_bin_idx])
bin_end = int(bin_edges[max_bin_idx + 1])

# 총 관객이 가장 많은 영화 계산
top_movie_row = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie_row["movieNm"]
top_movie_audi = int(top_movie_row["total_audi"])

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info(
    f"대부분의 영화는 총 관객 {bin_start:,}명 ~ {bin_end:,}명 구간에 몰려 있으며, "
    f"총 관객이 가장 많은 영화는 **{top_movie_name}**({top_movie_audi:,}명)입니다."
)

st.divider()

# ------------------------------------------------------------
# 그래프 4. 개봉일 스크린수 vs 총 관객 - 산점도 (색: 장르)
# ------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
)
fig_scatter.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}<br>총 관객: %{y:,}명<extra></extra>",
)
fig_scatter.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 문장을 작성해 주세요.")

st.divider()

# ------------------------------------------------------------
# 그래프 5. 장르별 총 관객 박스플롯 (영화 10편 이상인 장르만)
# ------------------------------------------------------------
st.header("5. 장르별 총 관객 분포 (10편 이상 장르)")

genre_movie_counts = df["genre"].value_counts()
major_genres = genre_movie_counts[genre_movie_counts >= 10].index
df_major_genres = df[df["genre"].isin(major_genres)]

fig_box = px.box(
    df_major_genres,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_name="movieNm",
)
fig_box.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객: %{y:,}명<extra></extra>",
)
fig_box.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    showlegend=False,
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 문장을 작성해 주세요.")

st.divider()

# ------------------------------------------------------------
# 그래프 6. 개봉일 스크린수 vs 총 관객 - 버블 그래프
#          (버블 크기: 첫 주 관객, 색: 장르)
# ------------------------------------------------------------
st.header("6. 개봉일 스크린수와 총 관객의 관계 (버블 크기 = 첫 주 관객)")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,
)
fig_bubble.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,}<br>"
        "총 관객: %{y:,}명<br>"
        "첫 주 관객: %{marker.size:,}명<extra></extra>"
    ),
)
fig_bubble.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 문장을 작성해 주세요.")

st.divider()

# ------------------------------------------------------------
# 그래프 7. 제작 국가 → 장르 선버스트 (칸 크기: 영화 편수)
# ------------------------------------------------------------
st.header("7. 제작 국가별 장르 구성")

fig_sunburst = px.sunburst(
    df,
    path=["nation", "genre"],
)
fig_sunburst.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 수: %{value}편<extra></extra>",
)
fig_sunburst.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 문장을 작성해 주세요.")

st.divider()

# ------------------------------------------------------------
# 그래프 8. 개봉 월별 영화 편수 - 원형(달력) 막대 그래프
# ------------------------------------------------------------
st.header("8. 영화는 어느 달에 개봉이 몰려 있나")

month_names = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]

df_month = df.dropna(subset=["openDt"]).copy()
df_month["open_month"] = df_month["openDt"].dt.month

month_counts = df_month["open_month"].value_counts().reindex(range(1, 13), fill_value=0)

fig_month_polar = go.Figure(
    go.Barpolar(
        r=month_counts.values,
        theta=month_names,
        marker=dict(
            color=month_counts.values,
            colorscale="Blues",
            line=dict(color="white", width=1),
        ),
        hovertemplate="<b>%{theta}</b><br>개봉 편수: %{r}편<extra></extra>",
    )
)
fig_month_polar.update_layout(
    title="영화는 어느 달에 개봉이 몰려 있나",
    polar=dict(
        radialaxis=dict(visible=True, showticklabels=True, ticksuffix="편"),
        angularaxis=dict(direction="clockwise"),
    ),
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig_month_polar, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 문장을 작성해 주세요.")

st.divider()
