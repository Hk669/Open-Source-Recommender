import requests 

#extracting the user repos data by sending requests with the Github Personal Access token 
def get_repos(username):
    #headers required to make requests to Github API
    headers = {
        'Authorization': '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', #Enter your Github PAT
        'User-Agent': 'Open-Source-Repo-Recommender',
        'Accept': 'application/vnd.github.json', # Github mediatype, the format data is returned
    }

    # To store the unique data of the user 
    languages_set = set()
    topics_set = set()
    user_details = []
    language_topics = {}

    
    try:
        # the request is sent to the below URL and returned data is stored in .json
        url = f'https://api.github.com/users/{username}/repos'
        repos = requests.get(url,headers=headers)
        repos_data = repos.json()

        # iterates through every repository of the user data
        for repo in repos_data:

            # It checks 1.Not Fork, 2.Description or Atleast one Language associated with the repository
            if not repo['fork'] and (repo['description'] or repo['language'] or len(repo['topics'])>0):

                # If the conditioned is satisfied, makes a request for languages 
                languages = requests.get(repo['languages_url'],headers=headers)
                languages_data = languages.json()

                # To store the user repositories name and the descripton
                user_repo = {
                    'project_name' : repo['name'],
                    'description' : repo['description'],
                }
                user_details.append(user_repo)

                languages_set.update(languages_data.keys())
                topics_set.update(repo['topics'])

        language_topics = {"languages" : list(languages_set), "topics" : list(topics_set)}

    except Exception as e:
        print(e)

    return user_details, language_topics