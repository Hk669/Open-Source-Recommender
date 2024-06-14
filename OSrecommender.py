import streamlit as st
from src.user_data import get_repos
from chroma.db import recommend
import asyncio
from src.search import get_projects
from linkpreview import link_preview


def get_link_preview(url):
    preview = link_preview(url)
    return preview.title, preview.description, preview.image

# Application Design

st.title("Open-Source Recommender")
prompt = st.text_input("Enter your Github username..")

if prompt:
    status_placeholder = st.empty()
    status_placeholder.text('Crawling your repositories...')
    user_details, language_topics = asyncio.run(get_repos(prompt))

    status_placeholder.text('Crawling open source projects...')
    unique_repos = asyncio.run(get_projects(language_topics))

    status_placeholder.text('Generating recommendations...')

    urls = recommend(user_details, unique_repos)

    status_placeholder.empty()

    with st.expander("Recommended Repositories"):
        for url in urls:
            if url:
                title, description, image = get_link_preview(url)

                if image:
                    st.markdown(f'[<img src="{image}" width="300" align="center"/>]({url})', unsafe_allow_html=True)
                else:
                    st.markdown(f'[{title}]({url})', unsafe_allow_html=True)