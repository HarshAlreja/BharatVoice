import os
from dotenv import load_dotenv
from groq import Groq


load_dotenv()
groq_key = os.getenv("API_KEY")


if not groq_key:
    print("No Api Alloted yet !... Apply Groq Api First")
    exit()

client=Groq(api_key=groq_key)
data_path="data/business_data.txt"
if not os.path.exists(data_path):
    print("{data_path} not found")
    exit()

with open(data_path,"r",encoding="utf-8") as file:
    context_data=file.read() 
user_query=input("Ask BharatVoice (eg. fever ki tablet kaunsi hai?): ")
system_prompt=f"""
you are BharatVOice , an AI assistant for Om SaiMedical Store in Nashik .
Strictly answer the user's question based ONLY on the provided Context below. 
If the answer is not present in the Context, reply with "Sorry, mujhe is baare mein nahi pata."
Do not hallucinate or make up facts. Reply in a natural, friendly tone (Hindi/Hinglish/Marathi as appropriate).

Context:
{context_data}
"""
print("Fetching answerr....")

try:
    completion=client.chat.completions.create(

        model="llama-3.1-8b-instant",
        messages=[

            {"role":"system","content":system_prompt},
            {"role":"user","content":user_query}
        ],
        temperature=0.2,
    )
    print("Response....\n")
    print(completion.choices[0].message.content)
except Exception as e:
    print (f"Api call Failed {e}")    
