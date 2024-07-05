from sqlite3 import DatabaseError
import chromadb
import random
import os
from typing import List
import logging

logger = logging.getLogger(__name__)


def recommend(user_details):
    """generate recommendations for the user"""

    recommendations = []
    recommended_repos = set()

    collection = get_chromadb_collection()
    print("collection", collection)

    for user_proj in user_details:
        new_doc = f"{user_proj['project_name']} : {user_proj['description']}"
        languages = user_proj['related_language_or_topic']

        results = collection.query(
            query_texts = [new_doc],
            n_results = 10,
            where = {
                "related_language_or_topic": {"$in": languages}
            }
        )
        print("--------\n", results)
        if results['documents'][0]:
            # Extract repository names and construct GitHub URLs
            repo_urls = []
            for doc in results['documents'][0]:
                repo_name = doc.split('\n')[0]  # Get the part before the first newline
                if '/' in repo_name:  # Ensure it's a valid repo name
                    repo_url = f"https://github.com/{repo_name}"
                    if repo_url not in recommended_repos:
                        repo_urls.append(repo_url)
            
            if repo_urls:
                # Select the top result (first in the list)
                recommendations.append(repo_urls[0])
                recommended_repos.add(repo_urls[0])
            else:
                print(f"No valid recommendations found for project {user_proj['project_name']}")
        else:
            print(f"No recommendations found for project {user_proj['project_name']}")

    return recommendations


def recommend_by_topics(topics: List[str], max_recommendations: int = 7):
    """Generate recommendations based on given topics"""
    recommendations = []
    recommended_repos = set()
    collection = get_chromadb_collection()

    logger.info(f"Querying ChromaDB for topics: {topics}")
    results = collection.query(
        query_texts=topics,
        n_results=max_recommendations * 2,  # Get more results to allow for filtering
        where={"related_language_or_topic": {"$in": topics}}
    )
    logger.info(f"Recommendation results: {results}")
    if results['documents'][0]:
        for doc in results['documents'][0]:
            repo_name = doc.split('\n')[0]  # Get the part before the first newline
            if '/' in repo_name:  # Ensure it's a valid repo name
                repo_url = f"https://github.com/{repo_name}"
                if repo_url not in recommended_repos:
                    recommendations.append(repo_url)
                    recommended_repos.add(repo_url)
                    if len(recommendations) >= max_recommendations:
                        break

    return recommendations


def get_topic_based_recommendations(user):
    all_topics = user.languages + user.extra_topics
    if not all_topics:
        raise ValueError("Please provide at least one language or topic")
    
    # Get recommendations based on topics
    try:
        urls = recommend_by_topics(all_topics)
    except Exception as e:
        logger.error(f"Error generating topic-based recommendations: {str(e)}")
        return {'recommendations': [], 'message': 'Error generating recommendations'}
    
    if not urls:
        return {'recommendations': [], 'message': 'No recommendations found for the given topics'}
    return {'recommendations': urls}


def get_or_create_chromadb_collection():
    try:
        path = os.path.dirname(os.path.abspath(__file__))
        client = chromadb.PersistentClient(path=path)
        collection = client.get_or_create_collection("projects")
        return collection
    except DatabaseError as e:
        raise Exception(f"Error in creating collection: {e}")
    

def get_chromadb_collection():
    try:
        client = chromadb.PersistentClient(path=r"C:\Users\hrush\OneDrive - Student Ambassadors\Desktop\Open-Source-Recommender\chroma")
        collection = client.get_collection("projects")
        return collection
    except DatabaseError as e:
        raise Exception(f"Error in getting collection: {e}")



def upsert_to_chroma_db(collection, unique_repos):
    # Prepare data for upsert
    ids = []
    documents = []
    metadatas = []
    
    for repo_id, repo_data in unique_repos.items():
        ids.append(str(repo_id))
        documents.append(f"{repo_data['full_name']}\n{repo_data['description']}")
        metadatas.append({
            "related_language_or_topic": repo_data["related_language_or_topic"]
        })
    
    # Upsert data to the collection
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Upserted {len(ids)} repositories to ChromaDB")
    return collection
