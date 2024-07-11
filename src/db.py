from sqlite3 import DatabaseError
import chromadb
import random
import os
from typing import List
from src.models import RepositoryRecommendation
import logging

logger = logging.getLogger(__name__)

def recommend(user_details, 
              languages_topics) -> List[RepositoryRecommendation]:
    """generate recommendations for the user"""

    recommendations = []
    recommended_repos = set()

    collection = get_chromadb_collection()
    languages_topics = languages_topics["languages"] + languages_topics["topics"]
    for user_proj in user_details:
        new_doc = f"{user_proj['project_name']} : {user_proj['description']}"
        

        results = collection.query(
            query_texts = [new_doc],
            n_results = 10,
            where = {
                "related_language_or_topic": {"$in": languages_topics}
            }
        )
        logging.info(f"UserProject: {user_proj}, Repositories: {results}")
        if results['documents'][0]:
            # Extract repository names and construct GitHub URLs
            ids = results["ids"][0]
            i = 0
            for doc in results['documents'][0]:
                repo_name = doc.split('\n')[0]  # Get the part before the first newline
                if '/' in repo_name:  # Ensure it's a valid repo name
                    repo_url = f"https://github.com/{repo_name}"
                    if repo_url not in recommended_repos:
                        try:
                            repo_details = collection.get(ids=[ids[i]])
                            metadata = repo_details.get("metadatas")[0]
                        except Exception as e:
                            logging.error(f"Error getting repo details: {str(e)}")

                        if metadata:
                            recommendations.append({
                            "repo_url": repo_url,
                            "full_name": metadata.get("full_name"),
                            "description": metadata.get("description"),
                            "stargazers_count": metadata.get("stargazers_count"),
                            "forks_count": metadata.get("forks_count"),
                            "open_issues_count": metadata.get("open_issues_count"),
                            "avatar_url": metadata.get("owner", {}).get("avatar_url"),
                            "language": metadata.get("language"),
                            "updated_at": metadata.get("updated_at"),
                            "topics": metadata.get("topics", [])
                        })
                        recommended_repos.add(repo_url)
                        i+=1
                        if len(recommendations) >= 15:
                            break
                    else:
                        logger.error(f"Repository details not found for {repo_name}")
        else:
            logger.info(f"No recommendations found for project {user_proj['project_name']}")

    return recommendations


def recommend_by_topics(topics: List[str], 
                        max_recommendations: int = 7) -> List[RepositoryRecommendation]:
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
        ids = results["ids"][0]
        i = 0
        for doc in results['documents'][0]:
            repo_name = doc.split('\n')[0]  # Get the part before the first newline
            if '/' in repo_name:  # Ensure it's a valid repo name
                repo_url = f"https://github.com/{repo_name}"
                if repo_url not in recommended_repos:
                    try:
                        repo_details = collection.get(ids=[ids[i]])
                        metadata = repo_details.get("metadatas")[0]
                    except Exception as e:
                        logging.error(f"Error getting repo details: {str(e)}")

                    if metadata:
                        recommendations.append({
                            "repo_url": repo_url,
                            "full_name": metadata.get("full_name"),
                            "description": metadata.get("description"),
                            "stargazers_count": metadata.get("stargazers_count"),
                            "forks_count": metadata.get("forks_count"),
                            "open_issues_count": metadata.get("open_issues_count"),
                            "avatar_url": metadata.get("owner", {}).get("avatar_url"),
                            "language": metadata.get("language"),
                            "updated_at": metadata.get("updated_at"),
                            "topics": metadata.get("topics", [])
                        })
                    recommended_repos.add(repo_url)
                    i+=1
                    if len(recommendations) >= 15:
                        break
                    else:
                        logger.error(f"Repository details not found for {repo_name}")

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
    


def get_chromadb_collection():
    try:
        # client = chromadb.PersistentClient(path=r"C:\Users\hrush\OneDrive - Student Ambassadors\Desktop\Open-Source-Recommender\chroma")
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(project_dir, "chroma")

        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection("projects")
        return collection
    except DatabaseError as e:
        raise Exception(f"Error in getting collection: {e}")



def upsert_to_chroma_db(collection, unique_repos):
    # Prepare lists to hold data for upsert
    ids = []
    documents = []
    metadatas = []
    
    for repo_id, repo_data in unique_repos.items():
        # Extract data from repo_data with default values or handling None
        full_name = repo_data.get('full_name', 'No Name')
        description = repo_data.get('description', 'No Description')
        related_language_or_topic = repo_data.get('related_language_or_topic', 'Unknown')
        stargazers_count = repo_data.get('stargazers_count', 0)
        forks_count = repo_data.get('forks_count', 0)
        open_issues_count = repo_data.get('open_issues_count', 0)
        avatar_url = repo_data.get('avatar_url', '')
        language = repo_data.get('language', 'Unknown')
        updated_at = repo_data.get('updated_at', '')
        topics = repo_data.get('topics', "")

        # Convert related_language_or_topic to string if it's a list
        # because the chromadb metadata field only accepts strings, int, float
        if isinstance(related_language_or_topic, list):
            related_language_or_topic = ", ".join(related_language_or_topic)
        
        
        # Append data to respective lists for upsert
        ids.append(str(repo_id))
        documents.append(f"{full_name}\n{description}")
        
        # Prepare metadata dictionary
        metadata = {
            "full_name": str(full_name),
            "description": str(description),
            "related_language_or_topic": str(related_language_or_topic),
            "stargazers_count": int(stargazers_count),
            "forks_count": int(forks_count),
            "open_issues_count": int(open_issues_count),
            "avatar_url": str(avatar_url),
            "language": str(language),
            "updated_at": str(updated_at),
            "topics": str(topics)
        }
        
        # Add metadata to the list
        metadatas.append(metadata)
    
    try:
        # Upsert data to the collection
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"Upserted {len(ids)} repositories to ChromaDB")
        return collection
    
    except ValueError as ve:
        # Handle specific ChromaDB metadata validation errors
        raise ValueError(f"Error upserting data to ChromaDB: {ve}")
    
    except Exception as e:
        # Catch any unexpected errors during upsert
        raise Exception(f"Unexpected error upserting data to ChromaDB: {e}")

