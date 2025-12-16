import requests
import json
from PyPDF2 import PdfReader
import math
import pickle
import os
from functools import lru_cache

# --- Data Structures ---
class Message:
    def __init__(self, content, is_user=False):
        self.content = content
        self.is_user = is_user

class SimpleVectorStore:
    def __init__(self, text_chunks, embeddings):
        self.text_chunks = text_chunks
        self.embeddings = embeddings

    def similarity_search(self, query_embedding, k=3):
        # Cosine similarity
        scores = []
        for i, emb in enumerate(self.embeddings):
            dot_product = sum(a * b for a, b in zip(query_embedding, emb))
            norm_a = math.sqrt(sum(a * a for a in query_embedding))
            norm_b = math.sqrt(sum(b * b for b in emb))
            score = dot_product / (norm_a * norm_b) if norm_a and norm_b else 0
            scores.append((score, self.text_chunks[i]))
        
        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:k]]
    
    def save(self, filepath):
        """Save vectorstore to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump({'chunks': self.text_chunks, 'embeddings': self.embeddings}, f)
    
    @staticmethod
    def load(filepath):
        """Load vectorstore from disk"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            return SimpleVectorStore(data['chunks'], data['embeddings'])

class SimpleChain:
    def __init__(self, vectorstore, api_token):
        self.vectorstore = vectorstore
        self.api_token = api_token
        self.history = []

    def __call__(self, inputs):
        question = inputs['question']
        self.history.append(Message(question, is_user=True))

        # 1. Get query embedding
        query_emb = query_huggingface_embedding(question, self.api_token)
        if not query_emb:
             return {'chat_history': self.history}

        # 2. Retrieve relevant docs
        context_docs = self.vectorstore.similarity_search(query_emb)
        context_text = "\n\n".join(context_docs)

        # 3. Generate Answer
        answer = query_huggingface_generation(question, context_text, self.api_token)
        
        self.history.append(Message(answer, is_user=False))
        return {'chat_history': self.history}

# --- PDF & Text Processing ---

def get_pdf_text(file_paths):
    text = ""
    for file_path in file_paths:
        try:
            if isinstance(file_path, str) and file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text += f.read() + "\n\n"
            else:
                pdf_reader = PdfReader(file_path)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error reading file: {e}")
            pass 
    return text

def get_text_chunks(text):
    # Reduced chunk size for faster processing
    chunk_size = 500  # Reduced from 1000
    overlap = 100     # Reduced from 200
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

# --- API Calls with Caching ---

@lru_cache(maxsize=1000)
def query_huggingface_embedding(text, token):
    """Cached embedding function"""
    api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            api_url, 
            headers=headers, 
            json={"inputs": text, "options": {"wait_for_model": True}},
            timeout=10
        )
        if response.status_code == 200:
            return tuple(response.json())  # Convert to tuple for caching
        else:
            return ()
    except:
        return ()

def query_huggingface_generation(question, context, token):
    api_url = "https://api-inference.huggingface.co/models/google/flan-t5-xxl"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Shorten context aggressively for speed
    max_context_length = 1000  # Reduced from 2000
    if len(context) > max_context_length:
        context = context[:max_context_length] + "..."
    
    prompt = f"Answer briefly based on context.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,  # Reduced from 200
            "temperature": 0.7,
            "return_full_text": False
        },
        "options": {
            "wait_for_model": True
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and 'generated_text' in result[0]:
                    return result[0]['generated_text']
                elif isinstance(result[0], str):
                    return result[0]
            elif isinstance(result, dict) and 'generated_text' in result:
                return result['generated_text']
            elif isinstance(result, str):
                return result
            
            return str(result)
        else:
            return f"Error: Could not generate answer (Status {response.status_code})"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Factories with Caching ---

def get_vectorstore(text_chunks, api_token, cache_file="vectorstore.pkl"):
    """Get vectorstore with disk caching"""
    
    # Check if cached version exists
    if os.path.exists(cache_file):
        try:
            print("Loading cached vectorstore...")
            return SimpleVectorStore.load(cache_file)
        except:
            pass
    
    print(f"Processing {len(text_chunks)} chunks...")
    embeddings = []
    
    # Batch process with progress
    for i, chunk in enumerate(text_chunks):
        if i % 10 == 0:
            print(f"Processing chunk {i}/{len(text_chunks)}")
        
        emb = query_huggingface_embedding(chunk, api_token)
        if emb and len(emb) > 0:
            embeddings.append(list(emb))
        else:
            embeddings.append([0.0]*384)
    
    vectorstore = SimpleVectorStore(text_chunks, embeddings)
    
    # Save to cache
    try:
        vectorstore.save(cache_file)
        print("Vectorstore cached!")
    except:
        pass
    
    return vectorstore

def get_conversation_chain(vectorstore, api_token):
    return SimpleChain(vectorstore, api_token)
