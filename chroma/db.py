import chromadb
import random

# Recommendations
def recommend(user_details, repos):
    recommendations =[]

    # starting a database
    client = chromadb.Client()

    collection = client.get_or_create_collection("projects")

    # iterate through every project of the user
    projects = list(repos.values())
    for project in projects:
        document = f"{project['full_name']} : {project['description']}"
        
        # add the data to the DB
        collection.add(
            documents = [document],
            ids = [project['full_name']],
        )

    for user_proj in user_details:
        new_doc = f"{user_proj['project_name']} : {user_proj['description']}"
        results = collection.query(
            query_texts = [new_doc],
            n_results = 4,
        )
        try:
            # recommending the repos in random
            recommended_proj_id = random.choice(results['ids'][0])
            recommendations.append(f"https://www.github.com/{recommended_proj_id}")

            # if not found any repo "no repos found"
        except IndexError:
            print(f"No recommendations found for projects{user_proj['project_name']}")
            continue
    return recommendations

       
