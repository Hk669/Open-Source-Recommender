# Open-Source-Recommender
The application recommends Open Source Repositories based on your interests and languages that interest you.

## Features

- Retrieves repository details of a GitHub user, including project names, descriptions, programming languages, and topics.
- Searches and gathers open source projects based on user language and topic interests using the GitHub API.
- Generates recommendations by comparing user repository details with the collected open-source projects.
- Provides a web interface using Streamlit to input user information and display recommended projects with link previews.

## Installation

1. Clone the repository:

   ``` shell
   git clone https://github.com/Hk669/Open-Source-Recommender.git

   ```

2. Install the required dependencies:

   ```shell
   pip install -r requirements.txt
   ```

3. Obtain a GitHub Personal Access Token (PAT):
   - Visit https://github.com/settings/tokens and generate a new token with the necessary permissions.
   - Copy the token and update the `ACCESS_TOKEN` variable in the `user.py` file with your token.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```
