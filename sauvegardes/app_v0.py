import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def load_data():
    df = pd.read_csv("imdb-movies-dataset.csv")
    # Filter only Nicolas Cage movies
    return df[df['Cast'].str.contains('Nicolas Cage', na=False)]

movies = load_data()

# App title and summary
st.title("🦁 Nicolas Cage Filmography Explorer")
st.write("Total Cage movies found:", len(movies))

# —————————————————————
# 1. Movies per year (integers + horizontal labels)
# Count movies by year
counts = movies.groupby('Year').size().reset_index(name='Count')

# Ensure Year is integer (no .0)
counts['Year'] = counts['Year'].astype(int)

# Build an Altair line chart with horizontal x-axis labels
chart = alt.Chart(counts).mark_line(point=True).encode(
    x=alt.X(
        'Year:O',
        title='Year',
        axis=alt.Axis(labelAngle=0)      # 0° = horizontal labels
    ),
    y=alt.Y('Count:Q', title='Number of Movies')
).properties(
    title="Movies per Year"
)

st.altair_chart(chart, use_container_width=True)
# —————————————————————
# 2. Genre breakdown (colored bars)
genres = movies['Genre'].str.split(', ').explode()
top_genres = genres.value_counts().nlargest(5).reset_index()
top_genres.columns = ['Genre', 'Count']

st.subheader("Top 5 Genres")

genre_chart = (
    alt.Chart(top_genres)
    .mark_bar()
    .encode(
        x=alt.X(
            'Genre:O',
            title='Genre',
            axis=alt.Axis(labelAngle=0)    # keep labels horizontal
        ),
        y=alt.Y('Count:Q', title='Count'),
        color=alt.Color(
            'Genre:N',
            title='Genre',
            scale=alt.Scale(scheme='category10')  # distinct color per genre
        )
    )
    .properties(
        title="Top 5 Genres"
    )
)

st.altair_chart(genre_chart, use_container_width=True)

# —————————————————————
# 3. Rating & Duration Distributions
st.subheader("Rating & Duration Distributions")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("**IMDb Rating**")
    # Display summary statistics
    st.write(movies['Rating'].describe())
    # Bar chart of rating counts
    rating_counts = movies['Rating'].value_counts().sort_index().reset_index()
    rating_counts.columns = ['Rating', 'Count']
    rating_chart = (
        alt.Chart(rating_counts)
        .mark_bar()
        .encode(
            x=alt.X('Rating:O', title='Rating', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Count:Q', title='Count'),
            color=alt.Color('Rating:O', legend=None)
        )
        .properties(title="Rating Distribution")
    )
    st.altair_chart(rating_chart, use_container_width=True)

with col2:
    st.markdown("**Duration (min)**")
    # Display summary statistics
    st.write(movies['Duration (min)'].describe())
    # Histogram of durations
    duration_chart = (
        alt.Chart(movies)
        .mark_bar()
        .encode(
            alt.X('Duration (min):Q', bin=alt.Bin(maxbins=30), title='Duration (min)'),
            alt.Y('count():Q', title='Count')
        )
        .properties(title="Duration Distribution")
    )
    st.altair_chart(duration_chart, use_container_width=True)


# —————————————————————
# 4. Career Highlights (Top Rated Films)
st.subheader("Career Highlights")

# Select top 5 movies by IMDb rating
top5 = movies.nlargest(5, 'Rating')[['Title', 'Year', 'Rating']].copy()

# Format Year as string "YYYY"
top5['Year'] = top5['Year'].astype(int).astype(str)

# Format Rating as string with one decimal "X.X"
top5['Rating'] = top5['Rating'].apply(lambda x: f"{x:.1f}")

# Display as a simple table, with Title as index
st.table(top5.set_index('Title'))


import altair as alt

# —————————————————————
# 5. Frequent Collaborators (visualized with integer axes)
st.subheader("Frequent Collaborators")

# Prepare directors data
director_df = (
    movies['Director']
    .value_counts()
    .nlargest(5)
    .reset_index()
)
director_df.columns = ['Director', 'Count']

# Prepare co-stars data
co_stars_df = (
    movies['Cast']
    .str.split(', ')
    .explode()
    .loc[lambda s: s != 'Nicolas Cage']
    .value_counts()
    .nlargest(5)
    .reset_index()
)
co_stars_df.columns = ['Actor', 'Count']

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Top 5 Directors**")
    dir_chart = (
        alt.Chart(director_df)
        .mark_bar()
        .encode(
            x=alt.X(
                'Count:Q',
                title='Number of Films',
                axis=alt.Axis(format='d', tickMinStep=1)
            ),
            y=alt.Y('Director:O', title=None, sort='-x'),
            color=alt.Color('Director:N', legend=None, scale=alt.Scale(scheme='category10'))
        )
        .properties(height=300, width=300)
    )
    st.altair_chart(dir_chart, use_container_width=True)

with col2:
    st.markdown("**Top 5 Co-Stars**")
    co_chart = (
        alt.Chart(co_stars_df)
        .mark_bar()
        .encode(
            x=alt.X(
                'Count:Q',
                title='Number of Films',
                axis=alt.Axis(format='d', tickMinStep=1)
            ),
            y=alt.Y('Actor:O', title=None, sort='-x'),
            color=alt.Color('Actor:N', legend=None, scale=alt.Scale(scheme='category10'))
        )
        .properties(height=300, width=300)
    )
    st.altair_chart(co_chart, use_container_width=True)