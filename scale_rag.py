import os
from dotenv import load_dotenv
from groq import Groq

from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()
groq_key=os.getenv("API_KEY")
if not groq_key:
    print("no api")
    exit()

client= Groq(api_key=groq_key)
data_path="data/business_data.txt"
with open(data_path,"r",encoding="utf-8") as file:
    raw_text=file.read()

print("Document loaded successfully!.....")
text_splitter=CharacterTextSplitter(chunk_size=400, chunk_overlap=50,separator="\n")
docs=text_splitter.create_documents([raw_text])
print(f"text splitting into {len(docs)} chunks.....")

print("\n loading hugging face Embeddings locally!....")
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("\n Creating local ChromaDb Vector Store!...")

vector_store = Chroma.from_documents(docs,embedding_model)
print("\n Vector Database is Ready!....")
user_query = input("\n Ask BharatVoice (Scale version)......")
print("\n ChromaDB is fetching relevent data!...")
relevant_docs = vector_store.similarity_search(user_query,k=2)
context_chunks=""
for i,docs in enumerate(relevant_docs):
    context_chunks += f"\n Chunks {i+1} :\n{docs.page_content}\n"

print("\n Debugging -> retrieved chunks passed to LLM")
print(context_chunks)
print("\n")
print("\n")
system_prompt=f"""
You are BharatVoice, an AI assistant for Om Sai Medical Store in Nashik.
Strictly answer the user's question based ONLY on the provided Context below. 
If the answer is not present in the Context, reply with "Sorry, mujhe is baare mein nahi pata."
Do not hallucinate. Reply in a natural, friendly tone (Hinglish/Hindi/Marathi).
Context:
{context_chunks}
"""

try:
    print("Groq api call in progress!...")
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[

          {"role":"system","content":system_prompt},
          {"role":"user","content":user_query}

    ],
   temperature=0.2


    )
    print("\n Response!.....")
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Api call failed {e}")
        
