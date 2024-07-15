
https://github.com/user-attachments/assets/4b59117d-c3e0-479e-8be4-52795dc68873
# Open-Source Recommender


https://github.com/user-attachments/assets/c4e093ea-2256-4f25-8eeb-2de0e6fc67d8


This will be a free public-facing web application designed to find open-source projects for beginners and developers.

Search your next contribution to open source easily! A free web app is here to help every developer find cool open-source projects of interest that fit their skillset. Just enter your GitHub username; our intelligent recommender system will do the rest. 

Give it a star⭐, if you support my intiative to help beginners start with open source!

## Why Use Open-Source Recommender

- **Perfect for Beginners**: Jump into open source with projects perfect for your current skill level.
- **Tailored Recommendations**: Recommendations on projects based on your GitHub profile, preferred languages and interests.
- **Expand Your Horizons**: New technologies, new projects you never would have crossed.
- **Absolutely Free**: Just free – gift to the developer community.

## How It Works

![architecture](/public/architecture.png)

1. Retrives user repositories details which include, _languages_, _topics_, and _description_
2. Collects the best open source projects from the GitHub based on user's topics and languages
3. Processes the open source repositories through the _embedding model_ deployed in the _Azure OpenAI Studio_
4. Stores the resulting embeddings in _ChromaDB_ (VectorStore)
5. Converts the user's repository languages, topics, and descriptions into embeddings using the embedding model
6. Perform a _similarity search_ with the embeddings to find the most relevant open source projects
7. Delivers _personalized recommendations_ to the client


## Features

- **User-Friendly Interface:** Clean, intuitive design for seamless performance.
- **GitHub Integration**: Bases Users and Projects on the GitHub API for proper user data and details of projects
- **Smart Recommendations**: It fits appropriate projects to each user using robust algorithms.
- **Diverse Project Pool**: Multiple projects from different domains and projects which are of any difficulty level
- **Quick Access**: There are multiple direct links to recommended projects to access them fast.

feel free to drop your suggestions and issues at [Discussions](https://github.com/Hk669/Open-Source-Recommender/discussions/12)

## Get Started

**still under construction*

## Feedback

If you have any suggestions, find any bugs, or have success stories you'd like to share with me, please do so. Your input will make the experience better for all.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
