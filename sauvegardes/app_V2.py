import streamlit as st
import pandas as pd
import altair as alt

# Green: Caching data load
@st.cache_data
def load_data():
    df = pd.read_csv("imdb-movies-dataset.csv")
    # Filter only Nicolas Cage movies
    return df[df['Cast'].str.contains('Nicolas Cage', na=False)]

# Load data and drop entries without valid Year
movies = load_data().dropna(subset=['Year']).copy()
# Create integer Year column for filtering and charts
movies['Year_int'] = movies['Year'].astype(int)

# Green: Define default placeholder for missing posters
DEFAULT_POSTER_URL = "https://via.placeholder.com/300x450?text=No+Image"
# Ensure poster exists or use placeholder
movies['Poster'] = movies['Poster'].apply(
    lambda url: DEFAULT_POSTER_URL if pd.isna(url) or str(url).strip()=="" else url
)

# Green: Define motifs (themes)
MOTIF_MAP = {
    'Action': 'Action', 'Adventure': 'Adventure', 'Comedy': 'Comedy',
    'Drama': 'Drama', 'Thriller': 'Thriller', 'Crime': 'Crime',
    'Fantasy': 'Fantasy', 'Family': 'Family'
}

def assign_motif(genres):
    for key, label in MOTIF_MAP.items():
        if key in genres:
            return label
    return 'Other'

movies['Motif'] = movies['Genre'].apply(assign_motif)

# Green: App title and summary
st.title("🦁 Nicolas Cage Filmography Explorer")
st.write("Total Cage movies found:", len(movies))

# —————————————————————
# B. Sidebar filters: Year range slider (integers) + Motif selection
st.sidebar.header("Filters")
# Integer Year slider
years = sorted(movies['Year_int'].unique())
yr = st.sidebar.slider(
    "Year range",
    min(years), max(years),
    (min(years), max(years)),
    step=1
)
# Motif selector
top_motifs = ['All'] + sorted(movies['Motif'].unique().tolist())
selected_motif = st.sidebar.selectbox("Motif", top_motifs)

# Apply filters
filtered = movies[
    (movies['Year_int'] >= yr[0]) & (movies['Year_int'] <= yr[1])
]
if selected_motif != 'All':
    filtered = filtered[filtered['Motif'] == selected_motif]

# —————————————————————
# 1. Movies per Year (horizontal bar chart)
st.subheader("Movies per Year")
counts = filtered.groupby('Year_int').size().reset_index(name='Count')
counts['Year'] = counts['Year_int']
year_chart = (
    alt.Chart(counts)
    .mark_bar()
    .encode(
        x=alt.X('Count:Q', title='Number of Movies', axis=alt.Axis(format='d', tickMinStep=1)),
        y=alt.Y('Year:O', title='Year', sort='descending'),
        color=alt.Color('Year:O', legend=None, scale=alt.Scale(scheme='category20'))
    )
    .properties(height=400)
)
st.altair_chart(year_chart, use_container_width=True)

# —————————————————————
# 2. Genre Breakdown
st.subheader("Top 5 Genres")
genres = filtered['Genre'].str.split(', ').explode()
top_genres = genres.value_counts().nlargest(5).reset_index()
top_genres.columns = ['Genre','Count']
genre_chart = (
    alt.Chart(top_genres)
    .mark_bar()
    .encode(
        x=alt.X('Genre:O', title='Genre', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Count:Q', title='Count'),
        color=alt.Color('Genre:N', legend=None, scale=alt.Scale(scheme='category10'))
    )
    .properties(title="Top 5 Genres")
)
st.altair_chart(genres if False else genre_chart, use_container_width=True)

# —————————————————————
# 3. Rating & Duration Distributions
st.subheader("Rating & Duration Distributions")
# Metrics cards
avg_rating = filtered['Rating'].mean()
min_rating = filtered['Rating'].min()
max_rating = filtered['Rating'].max()
avg_duration = filtered['Duration (min)'].mean()
min_duration = filtered['Duration (min)'].min()
max_duration = filtered['Duration (min)'].max()
col1, col2, col3 = st.columns(3)
col1.metric("Avg Rating", f"{avg_rating:.1f}")
col2.metric("Min Rating", f"{min_rating:.1f}")
col3.metric("Max Rating", f"{max_rating:.1f}")
col4, col5, col6 = st.columns(3)
col4.metric("Avg Duration", f"{avg_duration:.0f} min")
col5.metric("Min Duration", f"{min_duration:.0f} min")
col6.metric("Max Duration", f"{max_duration:.0f} min")
# Detailed charts
dist_col1, dist_col2 = st.columns(2)
with dist_col1:
    st.markdown("**Rating Distribution**")
    rating_counts = filtered['Rating'].value_counts().sort_index().reset_index()
    rating_counts.columns = ['Rating','Count']
    rating_chart = (
        alt.Chart(rating_counts)
        .mark_bar()
        .encode(
            x=alt.X('Rating:O', title='Rating', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Count:Q', title='Count'),
            color=alt.Color('Rating:O', legend=None, scale=alt.Scale(scheme='viridis'))
        )
        .properties(height=300)
    )
    st.altair_chart(rating_chart, use_container_width=True)
with dist_col2:
    st.markdown("**Duration Distribution**")
    duration_chart = (
        alt.Chart(filtered)
        .mark_bar()
        .encode(
            alt.X('Duration (min):Q', bin=alt.Bin(maxbins=30), title='Duration (min)'),
            alt.Y('count():Q', title='Count'),
            color=alt.Color('Duration (min):Q', legend=None, scale=alt.Scale(scheme='turbo'))
        )
        .properties(height=300)
    )
    st.altair_chart(duration_chart, use_container_width=True)

# —————————————————————
# 4. Career Highlights
top5 = filtered.nlargest(5,'Rating')[['Title','Year_int','Rating','Poster','Genre']].copy()
top5['Year'] = top5['Year_int'].astype(str)
top5['Rating'] = top5['Rating'].apply(lambda x: f"{x:.1f}")
st.subheader("Career Highlights")
cols = st.columns(5)
for idx,(_,row) in enumerate(top5.iterrows()):
    with cols[idx]:
        st.image(row['Poster'],caption=f"{row['Title']} ({row['Year']})",use_container_width=True)
        st.markdown(f"**{row['Rating']} / 10**")
        st.caption(row['Genre'])

# —————————————————————
# 5. Frequent Collaborators
st.subheader("Frequent Collaborators")
director_df = filtered['Director'].value_counts().nlargest(5).reset_index()
director_df.columns=['Director','Count']
co_stars_df = (
    filtered['Cast'].str.split(', ').explode().loc[lambda s:s!='Nicolas Cage']
    .value_counts().nlargest(5).reset_index()
)
co_stars_df.columns=['Actor','Count']
col1,col2 = st.columns(2)
with col1:
    st.markdown("**Top 5 Directors**")
    dir_chart = alt.Chart(director_df).mark_bar().encode(
        x=alt.X('Count:Q',title='Number of Films',axis=alt.Axis(format='d',tickMinStep=1)),
        y=alt.Y('Director:O',sort='-x'),
        color=alt.Color('Director:N',legend=None,scale=alt.Scale(scheme='category10'))
    ).properties(height=300)
    st.altair_chart(dir_chart,use_container_width=True)
with col2:
    st.markdown("**Top 5 Co-Stars**")
    co_chart=alt.Chart(co_stars_df).mark_bar().encode(
        x=alt.X('Count:Q',title='Number of Films',axis=alt.Axis(format='d',tickMinStep=1)),
        y=alt.Y('Actor:O',sort='-x'),
        color=alt.Color('Actor:N',legend=None,scale=alt.Scale(scheme='category10'))
    ).properties(height=300)
    st.altair_chart(co_chart,use_container_width=True)

# —————————————————————
# 6. Filmography
exclusions = ["Arcadian","Dream Scenario","Longlegs","The Retirement Plan","Wild at Heart","Ghost Rider: Spirit of Vengeance","The Surfer","Lords of War","Running with the Devil","Jiu Jitsu","The Gunslingers","The Carpenter's Son"]
filtered_filmography=filtered[~filtered['Title'].isin(exclusions)]
st.subheader("Filmography")
rows=[filtered_filmography.iloc[i:i+5] for i in range(0,len(filtered_filmography),5)]
for row in rows:
    cols=st.columns(5)
    for idx,(_,movie) in enumerate(row.iterrows()):
        with cols[idx]:
            st.image(movie['Poster'],caption=f"{movie['Title']} ({movie['Year_int']})",use_container_width=True)
            st.markdown(f"**{movie['Rating']:.1f} / 10**")
            st.caption(movie['Genre'])
