import csv
from mem0 import MemoryClient
#from mem0.proxy.main import Mem0
from google import genai
from google.genai import types

client = MemoryClient(api_key="m0-")
genai_client = genai.Client(api_key="")

with open("sample.csv",'r',encoding='utf-8') as emails_file:
    reader = csv.reader(emails_file)
    next(reader)

    with open("final.csv","a",encoding="utf-8", newline='') as final_file: # Added newline=''
        writer = csv.writer(final_file)

        for row in reader:
            #print(row)
            member_name = row[4]
            org_name = row[0]
            repo_name= row[1]
            repo_description=row[2]
            if(row[-1]=="No public email"):
                continue

            messages = [
                {"role":"user","content":f"""My name is "{member_name}".
My organization name is "{org_name}".
My repository name is "{repo_name}".
Repository description is "{repo_description}"."""},
            ]

            result = client.add(messages, user_id=row[3],version="v2",infer=True,output_format='v1.1')
            print("result - ",result)

            mem = client.get_all(user_id=row[3])

            memory=""
            for i in mem:
                memory= i["memory"] + ", " +memory

            print(memory)

            email_body = genai_client.models.generate_content(
                model="gemini-2.5-flash-preview-04-17",
                contents=f"""You are an email expert. Your task is to write a highly short personalized outreach email explaining how the recipient can adopt Mem0 in their project.

You will use the following Mem0 details verbatim in my pitch (adjusting phrasing naturally into your email):

- Mem0 is a self-improving memory layer for LLM applications, enabling personalized AI experiences that save costs and delight users.
- Mem0 remembers user preferences, adapts to individual needs, and continuously improves over time.
- Enhance Future Conversations: Build smarter AI that learns from every interaction, providing context-rich responses without repetitive questions.
- Save Money: Reduce LLM costs by up to 80% through intelligent data filtering, sending only the most relevant information to AI models.
- Improve AI Responses: Deliver more accurate and personalized AI outputs by leveraging historical context and user preferences.
- Easy Integration: Seamlessly enhance your existing AI solutions with Mem0's memory layer, compatible with OpenAI, Claude, and more.

Email Structure:

1. Greeting: Address {member_name} by name.
2. Value Hook: Reference {repo_description} in {org_name}/{repo_name} to show you understand their work.
3. Mem0 Benefits: Weave in 2-3 of the Mem0 benefit bullets above, tailoring each to how it could improve their specific repo.
4. Call to Action: Invite them to try Mem0 in their codebase or schedule a quick demo.
5. Sign-off: Friendly close with name mem0 and a link to Mem0's website https://mem0.ai/. Write a short email, here are some information. {memory}""",

            )

            print(email_body)
            cleaned_email_body = email_body.text.replace('\n', ' ').replace('\r', '')
            writer.writerow([org_name,repo_name,repo_description,row[3],member_name,row[5],cleaned_email_body])

            