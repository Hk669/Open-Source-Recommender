from sqlite3 import DatabaseError
import chromadb
import random
import os
import logging
from typing import List
from datetime import datetime, timezone
from src.models import RepositoryRecommendation
from src.oai import generate_embeddings
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


async def recommend(user_details=None, 
              languages_topics=None, 
              topics=None, 
              max_recommendations=15) -> List[RepositoryRecommendation]:
    """Generate recommendations for users based on projects or topics."""
    
    recommendations = []
    recommended_repos = set()
    collection = get_chromadb_collection()

    if user_details:
        lang_topics = languages_topics["languages"] + languages_topics["topics"]
        for user_proj in user_details:
            new_doc = f"{user_proj['project_name']} : {user_proj['description']} : {lang_topics}"
            embeddings = generate_embeddings(new_doc)

            results = collection.query(
                query_embeddings=[embeddings],
                n_results=5,
                include=["metadatas", "distances"]
            )

            print(f"UserProject: {user_proj} : language topics : {languages_topics}, Repositories: {results}")
            if results['metadatas'][0]:
                metadatas = results["metadatas"][0]

                for metadata in metadatas:
                    repo_name = metadata.get("full_name")
                    print('----------------\n Repo Name:', repo_name)
                    print('\n------------------')
                    if '/' in repo_name:
                        repo_url = f"https://github.com/{repo_name}"
                        if repo_url not in recommended_repos:
                            recommendations.append({
                                "repo_url": repo_url,
                                "full_name": metadata.get("full_name"),
                                "description": metadata.get("description"),
                                "stargazers_count": metadata.get("stargazers_count"),
                                "forks_count": metadata.get("forks_count"),
                                "open_issues_count": metadata.get("open_issues_count"),
                                "avatar_url": metadata.get("avatar_url"),
                                "language": metadata.get("language"),
                                "updated_at": metadata.get("updated_at"),
                                "topics": metadata.get("topics", [])
                            })
                            recommended_repos.add(repo_url)
                            print('\n--------------\nRecommendations:', recommendations)
                    if len(recommendations) >= max_recommendations:
                        break
            else:
                logger.info(f"No recommendations found for project {user_proj['project_name']}")

    if topics:
        logger.info(f"Querying ChromaDB for topics: {topics}")
        embeddings = [generate_embeddings(topic) for topic in topics]

        results = collection.query(
            query_embeddings=embeddings,
            n_results=8,  # Get more results to allow for filtering
            include=["ids", "metadatas"]
        )

        logger.info(f"Recommendation results: {results}")
        if results['documents'][0]:
                metadatas = results["metadatas"][0]

                for metadata in metadatas:
                    repo_name = metadata.get("full_name")
                    if '/' in repo_name:
                        repo_url = f"https://github.com/{repo_name}"
                        if repo_url not in recommended_repos:
                            recommendations.append({
                                "repo_url": repo_url,
                                "full_name": metadata.get("full_name"),
                                "description": metadata.get("description"),
                                "stargazers_count": metadata.get("stargazers_count"),
                                "forks_count": metadata.get("forks_count"),
                                "open_issues_count": metadata.get("open_issues_count"),
                                "avatar_url": metadata.get("avatar_url"),
                                "language": metadata.get("language"),
                                "updated_at": metadata.get("updated_at"),
                                "topics": metadata.get("topics", [])
                            })
                            recommended_repos.add(repo_url)
                            if len(recommendations) >= max_recommendations:
                                break
        else:
            logger.info(f"No recommendations found for project {user_proj['project_name']}")

        
    return recommendations


async def get_topic_based_recommendations(user):
    all_topics = user.languages + user.extra_topics
    if not all_topics:
        raise ValueError("Please provide at least one language or topic")
    
    # Get recommendations based on topics
    try:
        urls = await recommend(topics=all_topics)
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
    embeddings = []
    
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
        document = f"{full_name}\n{description}\n{topics}"
        documents.append(document)
        
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
        embed_doc = generate_embeddings(document)
        embeddings.append(embed_doc)
    
    try:
        # Upsert data to the collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
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


def convert_to_readable_format(time_str):
    # Parse the input string to a datetime object
    dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")

    dt = dt.replace(tzinfo=timezone.utc)
    readable_time_str = dt.strftime("%B %d, %Y at %H:%M %Z")
    
    return readable_time_str


if __name__ == "__main__":
    collection = get_chromadb_collection()
    print(collection)

    user_details = [
    {'project_name': 'blog', 'description': 'my understanding/ works', 'related_language_or_topic': ['Dockerfile']},
    {'project_name': 'bpetokenizer', 'description': '(py package) train your own tokenizer based on BPE algorithm for the LLMs (supports the regex pattern and special tokens)', 'related_language_or_topic': ['Jupyter Notebook', 'Python']},
    {'project_name': 'HacksArena', 'description': "The django based application classifies user intents using a bag-of-words approach. It predicts intents based on the user's input, retrieves a random response from a predefined set of responses associated with each intent, and generates the appropriate reply.", 'related_language_or_topic': ['Python', 'CSS', 'JavaScript', 'HTML']}
]

    languages_topics = {
        'languages': ['Python', 'typescript'],
        'topics': ['agentic-ai', 'openai', "GPT", "llm"]
    }
    try:
        recommendations = recommend(user_details, languages_topics)
        # logger.info(recommendations)
        print('--------')
        print(recommendations)
    except Exception as e:
        print(f"Error Recommending data: {e}")