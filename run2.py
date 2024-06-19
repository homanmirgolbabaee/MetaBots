import os
import openai
import requests
import yaml

# Load configuration
config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
os.environ["GITHUB_API_TOKEN"] = config["github_api_token"]
os.environ["SLACK_API_TOKEN"] = config["slack_api_token"]

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message['content'].strip()

def create_github_repo(repo_name, token):
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {token}"}
    data = {"name": repo_name, "private": False}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return f"Repository '{repo_name}' created successfully"
    elif response.status_code == 422 and 'name already exists on this account' in response.text:
        return f"Repository '{repo_name}' already exists"
    else:
        return f"Failed to create repository '{repo_name}': {response.text}"

def send_slack_message(channel, text, token):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"channel": channel, "text": text}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 and response.json().get("ok"):
        return "Message sent to Slack successfully"
    else:
        return f"Failed to send message to Slack: {response.text}"

def execute_api_calls(generated_instructions):
    # Extract relevant information from generated instructions
    # For simplicity, we assume the instructions include the repo name and Slack message
    repo_name = "HQ"  # Example repo name; extract from generated_instructions in a real scenario
    slack_channel = "#general"
    github_token = os.getenv("GITHUB_API_TOKEN")
    slack_token = os.getenv("SLACK_API_TOKEN")

    # Call GitHub API
    github_response = create_github_repo(repo_name, github_token)
    print(github_response)

    # Prepare and send Slack message
    slack_message = f"{github_response}. Check the repository at https://github.com/{config['github_user']}/{repo_name}"
    slack_response = send_slack_message(slack_channel, slack_message, slack_token)
    print(slack_response)

def main():
    scenario = input("Please select a scenario (github_slack_scheduler): ")
    if scenario != "github_slack_scheduler":
        raise ValueError("Invalid scenario selected")

    user_id = input("Enter the user id: ")

    # Example prompt
    prompt = input("Please input an instruction: ") or "Create a repository named 'test' on GitHub"
    generated_text = generate_text(prompt)
    print("Generated Text:", generated_text)

    # Execute API calls based on the generated instructions
    execute_api_calls(generated_text)

if __name__ == "__main__":
    main()
