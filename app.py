# import streamlit as st
# from main import recommend, has_cast, has_keywords, has_embeddings

# st.set_page_config(
#     page_title="Movie Recommender",
#     page_icon="🎬",
#     layout="wide"
# )

# # =========================================================
# # HEADER
# # =========================================================

# st.title("🎬 AI Movie Recommender")

# mode = "TF-IDF + Embeddings" if has_embeddings else "TF-IDF Only"
# st.caption(f"Hybrid Recommendation System • {mode}")

# if not has_cast or not has_keywords:
#     missing = []
#     if not has_cast:
#         missing.append("credits.csv")
#     if not has_keywords:
#         missing.append("keywords.csv")

#     st.info(f"Missing: {', '.join(missing)} → recommendations may be weaker")


# st.divider()

# # =========================================================
# # INPUT
# # =========================================================

# col1, col2 = st.columns([4, 1])

# with col1:
#     movie_name = st.text_input("Enter movie name")

# with col2:
#     n = st.slider("Results", 5, 20, 10)

# if st.button("Recommend 🚀"):

#     if not movie_name.strip():
#         st.warning("Enter a valid movie name")
#         st.stop()

#     recs = recommend(movie_name, n)

#     if not recs:
#         st.error("No match found")
#         st.stop()

#     # =====================================================
#     # METRICS
#     # =====================================================

#     avg = sum(r["similarity"] for r in recs) / len(recs)

#     st.metric("Average Similarity", f"{avg:.3f}")

#     st.divider()

#     # =====================================================
#     # TOP RESULTS
#     # =====================================================

#     st.subheader(f"Top Recommendations for: {movie_name}")

#     cols = st.columns(5)

#     for i, r in enumerate(recs[:5]):

#         with cols[i]:

#             st.image(
#                 r["poster"] or "https://via.placeholder.com/300x450",
#                 use_container_width=True
#             )

#             st.write(f"**{r['title']}**")

#             sim = r["similarity"]

#             if sim >= 0.30:
#                 st.success(f"sim {sim}")
#             elif sim >= 0.15:
#                 st.warning(f"sim {sim}")
#             else:
#                 st.error(f"sim {sim}")

#             st.caption(f"⭐ {r['rating']} | 📅 {r['year']}")
#             st.caption(r["genres"])

#             with st.expander("Overview"):
#                 st.write(r["overview"])

#     # =====================================================
#     # TABLE
#     # =====================================================

#     st.divider()

#     with st.expander("View all results"):
#         st.dataframe(
#             [
#                 {
#                     "Title": r["title"],
#                     "Year": r["year"],
#                     "Rating": r["rating"],
#                     "Similarity": r["similarity"],
#                     "Score": r["score"],
#                     "Genres": r["genres"],
#                 }
#                 for r in recs
#             ],
#             use_container_width=True
#         )










import streamlit as st
from main import recommend, has_cast, has_keywords, has_embeddings

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM THEME TOGGLE (CSS INJECTION)
# =========================================================
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True  # Default to dark mode

def inject_custom_css(is_dark):
    if is_dark:
        # Dark Theme CSS
        css = """
        <style>
            [data-testid="stAppViewContainer"] { background-color: #0E1117; color: #FAFAFA; }
            [data-testid="stSidebar"] { background-color: #262730; }
            
            /* Force all text inside the sidebar to be light */
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
            [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, 
            [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
                color: #FAFAFA !important; 
            }
            
            [data-testid="stHeader"] { background-color: transparent; }
            .movie-card { border-radius: 10px; padding: 15px; background-color: #1E1E1E; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        </style>
        """
    else:
        # Light Theme CSS
        css = """
        <style>
            [data-testid="stAppViewContainer"] { background-color: #FFFFFF; color: #111111; }
            [data-testid="stSidebar"] { background-color: #F0F2F6; }
            
            /* Force all text inside the sidebar to be dark */
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
            [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, 
            [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
                color: #111111 !important; 
            }
            
            [data-testid="stHeader"] { background-color: transparent; }
            .movie-card { border-radius: 10px; padding: 15px; background-color: #FFFFFF; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #E0E0E0; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Theme Toggle
    st.session_state.dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    inject_custom_css(st.session_state.dark_mode)
    
    st.divider()
    
    # Results Slider
    n_results = st.slider("Number of Recommendations", min_value=5, max_value=30, value=10, step=5)
    
    st.divider()
    
    # System Status
    st.subheader("System Status")
    mode = "Hybrid (TF-IDF + Embeddings)" if has_embeddings else "TF-IDF Only"
    st.caption(f"**Engine:** {mode}")
    
    if not has_cast or not has_keywords:
        missing = []
        if not has_cast: missing.append("credits.csv")
        if not has_keywords: missing.append("keywords.csv")
        st.warning(f"Missing data: {', '.join(missing)}\n\nRecommendations may lack cast/director context.")
    else:
        st.success("All datasets loaded optimally. ✅")

# =========================================================
# MAIN HEADER & SEARCH
# =========================================================
st.title("🎬 AI Movie Recommender")
st.markdown("Find your next favorite film based on plot semantics, genres, and crew.")
st.write("") # Spacer

# Using a form allows the user to press 'Enter' to submit
with st.form(key='search_form'):
    col1, col2 = st.columns([5, 1])
    with col1:
        movie_name = st.text_input("Search for a movie you like...", placeholder="e.g., The Dark Knight, Avatar, Jumanji", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button(label='Search 🚀', use_container_width=True)

# =========================================================
# RESULTS DISPLAY
# =========================================================
if submit_button:
    if not movie_name.strip():
        st.warning("Please enter a valid movie name to get started.")
        st.stop()

    with st.spinner('Scanning the cinematic universe...'):
        recs = recommend(movie_name, n_results)

    if not recs:
        st.error(f"Couldn't find a match for '{movie_name}'. Try checking the spelling!")
        st.stop()

    # Metrics Row
    avg_sim = sum(r["similarity"] for r in recs) / len(recs)
    st.divider()
    st.subheader(f"Top Matches for: **{movie_name.title()}**")
    st.caption(f"Found {len(recs)} results | Average Similarity: {avg_sim:.3f}")
    st.write("")

    # --- TOP 5 CARDS ---
    cols = st.columns(5)
    
    for i, r in enumerate(recs[:5]):
        with cols[i]:
            # Streamlit's built in container with borders makes great "Cards"
            with st.container(border=True):
                # Poster
                st.image(r["poster"] or "https://via.placeholder.com/300x450", use_container_width=True)
                
                # Title & Year
                st.markdown(f"**{r['title']}** ({r['year']})")
                
                # Similarity Progress Bar
                sim = float(r["similarity"])
                if sim >= 0.30:
                    bar_color = "green"
                elif sim >= 0.15:
                    bar_color = "orange"
                else:
                    bar_color = "red"
                
                # Visual Similarity Indicator
                st.caption(f"Match Score: {sim:.3f}")
                st.progress(min(sim, 1.0)) # Caps at 1.0 just in case
                
                # Badges / Meta
                st.markdown(f"⭐ **{r['rating']}/10**")
                st.caption(f"🎭 {r['genres']}")
                
                # Overview Expander
                with st.expander("Read Plot"):
                    st.write(r["overview"])

    st.write("") # Spacer

    # --- ALL RESULTS TABLE ---
    with st.expander("📊 View All Raw Results & Data"):
        st.dataframe(
            [
                {
                    "Rank": idx + 1,
                    "Title": r["title"],
                    "Year": r["year"],
                    "Rating": r["rating"],
                    "Sim Score": r["similarity"],
                    "Overall Rank Score": r["score"],
                    "Genres": r["genres"],
                }
                for idx, r in enumerate(recs)
            ],
            use_container_width=True,
            hide_index=True
        )