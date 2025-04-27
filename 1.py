import requests
from bs4 import BeautifulSoup
import csv

repo = "mem0ai/mem0"
page_num = 100
url = 'https://github.com/{}/network/dependents?dependent_type=REPOSITORY&package_id=UGFja2FnZS00Nzc4NjcyODcx'.format(repo)

for i in range(page_num):
    # print("GET " + url)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    data = []
    for box_row in soup.findAll("div", {"class": "Box-row"}):
        owner_link = box_row.find('a', {"data-repository-hovercards-enabled":""})
        
        if owner_link and owner_link.get("data-hovercard-type") == "organization":
            repo_link = box_row.find('a', {"data-hovercard-type":"repository"})
            
            if repo_link:
                owner_name = owner_link.text
                repo_name = repo_link.text
                data.append(f"{owner_name}/{repo_name}")
    
    print(f'Page num - {i}, fetched - {len(data)} names')
    with open('repos.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        for item in data:
            org_name, repo_name = item.split('/')
            writer.writerow([org_name, repo_name])
            
    next_page = soup.find("div", {"class":"paginate-container"}).find('a', text="Next")
    if next_page:
        url = next_page["href"]
    else:
        break