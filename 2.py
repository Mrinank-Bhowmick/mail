import requests
import os
import csv

TOKEN = ""  


def run_query(query, variables=None):
    """Runs a GraphQL query against the GitHub API."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    
    request = requests.post('https://api.github.com/graphql', json=payload, headers=headers)
    request.raise_for_status()
    return request.json()
 

query = """
query GetMentionableUsers($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    description
    mentionableUsers(first: 100, after: $after) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        login
        email
        name
        organizations(first: 100) {
          nodes {
            login
          }
        }
      }
    }
  }
}
"""

def fetch_collaborators(GITHUB_ORG,GITHUB_REPO,csv_file_writer):
    print(f"Fetching users from {GITHUB_ORG}/{GITHUB_REPO}...")
    
    all_users = []
    has_next_page = True
    end_cursor = None
    
    while has_next_page:
        variables = {
            "owner": GITHUB_ORG,
            "name": GITHUB_REPO,
            "after": end_cursor
        }
        
        result = run_query(query, variables)
        # print(result)
        
        mentionable_users_data = result["data"]["repository"]["mentionableUsers"]
        repo_description = result['data']['repository']['description']
        users = mentionable_users_data["nodes"]
        all_users.extend(users)
        
        page_info = mentionable_users_data["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        
    
    target_org_login = GITHUB_ORG.lower()
    org_users = []
    
    for user in all_users:
        org_nodes = user.get("organizations", {}).get("nodes", [])
        user_orgs = [org.get("login", "").lower() for org in org_nodes if org.get("login")]
        
        if target_org_login in user_orgs:
            org_users.append(user)
    
    print(f"\nFound {len(org_users)} users belonging to {GITHUB_ORG} organization:")
    for user in org_users:
        name = user.get('name') or 'N/A'
        login = user.get('login') or 'N/A'
        email = user.get('email') or 'No public email'
        
        csv_file_writer.writerow([GITHUB_ORG,GITHUB_REPO,repo_description,login,name,email])


with open('repos.csv','r',newline='',encoding='utf-8') as file:
    
    reader = csv.reader(file)
    with open('emails.csv','a',newline='', encoding='utf-8') as emails:
        writer = csv.writer(emails)
        
        next(reader)
        print("Starting")
        for row in reader:
            fetch_collaborators(row[0],row[1],writer)