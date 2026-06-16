import os
from dotenv import load_dotenv
from groq import Groq

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
groq_key = os.getenv("API_KEY")
if not groq_key:
    print("Error: API key nahi mila!")
    exit()

client = Groq(api_key=groq_key)
DATA_DIR = "data"
PERSIST_DIR = "vectorstore"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PERSIST_DIR, exist_ok=True)


def update_and_load_vector_store():
    print("Local Embedding Model Loading!.......")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding_model)

    all_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt') or f.endswith('.pdf')]
    if not all_files:
        print("Warning: data folder empty hai... query purane data pe chalegi")
        return vector_db

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    new_chunks_added = 0
    for file_name in all_files:
        file_path = os.path.join(DATA_DIR, file_name)
        existing_metadatas = vector_db.get(where={"source": file_path})

        if existing_metadatas and len(existing_metadatas['ids']) > 0:
            print(f"Skipping '{file_name}' — already parsed. No Rechunking......")
            continue

        print(f"New File detected! Processing '{file_name}'......")
        if file_name.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding="utf-8")

        file_docs = loader.load()
        file_chunks = text_splitter.split_documents(file_docs)
        vector_db.add_documents(file_chunks)
        new_chunks_added += len(file_chunks)
        print(f"Appended {len(file_chunks)} new chunks from '{file_name}'")

    if new_chunks_added > 0:
        print(f"Total {new_chunks_added} chunks permanently saved!")
    else:
        print("Database is up-to-date!")

    return vector_db


def translate_to_english(query):
    """
    Hinglish / Hindi / Marathi query ko English mein translate karta hai
    Taaki similarity search sahi se kaam kare
    """
    translate_prompt = f"""Translate the following query to English.
Return ONLY the translated query, nothing else. No explanation.
Query: {query}"""

    translation = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": translate_prompt}],
        temperature=0
    )
    english_query = translation.choices[0].message.content.strip()
    return english_query


if __name__ == "__main__":
    vector_store = update_and_load_vector_store()
    print("\nBharat Voice Engine at beta version!")
    print("=" * 100)

    while True:
        user_query = input("\nAsk BharatVoice (ya 'exit' likho bahar jaane ke liye): ")

        if user_query.lower() == 'exit':
            print("Aapka Din Shubh Rahe!")
            break

        if not user_query.strip():
            continue

        # Step 1 — Hinglish/Hindi/Marathi query ko English mein translate karo
        print("Translating query......")
        english_query = translate_to_english(user_query)
        print(f"Translated: {english_query}")

        # Step 2 — English query se relevant chunks dhundo
        relevant_docs = vector_store.similarity_search(english_query, k=4)

        # Step 3 — Chunks ko context mein compile karo
        context_chunks = ""
        for i, doc in enumerate(relevant_docs):
            context_chunks += f"\nChunk {i+1}:\n{doc.page_content}\n"

        # Step 4 — LLM ko context aur original query dono bhejo
        system_prompt = f"""
You are BharatVoice, a helpful AI assistant for Om Sai Medical Store in Nashik.
Strictly answer the user's question based ONLY on the provided Context below.
If the answer is not present in the Context, reply with "Sorry, mujhe is baare mein nahi pata."
Do not hallucinate or make up facts.
Reply in the SAME language the user asked in — Hinglish, Hindi, Marathi, or English.

Context:
{context_chunks}
"""

        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.2,
            )
            print("\nResponse:")
            print(completion.choices[0].message.content)
            print("-" * 100)

        except Exception as e:
            print(f"API call failed: {e}")