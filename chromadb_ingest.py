import json
import os
from dotenv import load_dotenv
load_dotenv()

import chromadb
from chromadb.config import Settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

CHROMA_PATH = os.path.join(os.path.dirname(__file__), 'chroma_db')
COLLECTION_NAME = 'kerala_gov_services'

def create_knowledge_chunks():
    with open('knowledge.json', 'r', encoding='utf-8') as f:
        knowledge = json.load(f)
    
    chunks = []
    ids = []
    
    for service_key, service_data in knowledge.items():
        service_name = service_data.get('name', service_key)
        description = service_data.get('description', '')
        
        subtypes = service_data.get('subtypes', {})
        if not subtypes:
            subtypes = {'default': service_data}
        
        for subtype_key, subtype_data in subtypes.items():
            chunk_id = f"{service_key}_{subtype_key}"
            
            chunk_text = f"""
Service: {service_name}
Type: {subtype_key}

Description: {description}

Documents Required: {', '.join(subtype_data.get('documents', []))}

Office: {subtype_data.get('office', 'Contact local authority')}

Fee: {subtype_data.get('fee', 'Varies')}

Timeline: {subtype_data.get('timeline', 'Contact office')}

Online Available: {subtype_data.get('online_available', False)}

Portal: {subtype_data.get('portal_link', 'N/A')}

Keywords: {', '.join(service_data.get('keywords', []))}
""".strip()
            
            chunks.append(chunk_text)
            ids.append(chunk_id)
    
    return chunks, ids

def ingest_to_chromadb():
    print("Initializing ChromaDB...")
    
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Kerala Government Services Knowledge Base"}
    )
    
    chunks, ids = create_knowledge_chunks()
    
    print(f"Created {len(chunks)} knowledge chunks")
    
    if collection.count() > 0:
        print("Clearing existing collection...")
        client.delete_collection(name=COLLECTION_NAME)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
    
    print("Generating embeddings...")
    
    api_key = os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        print("WARNING: GEMINI_API_KEY not set. Using random embeddings for testing.")
        import numpy as np
        for i, (chunk, chunk_id) in enumerate(zip(chunks, ids)):
            embedding = np.random.rand(768).tolist()
            collection.add(
                documents=[chunk],
                ids=[chunk_id],
                embeddings=[embedding]
            )
            if (i + 1) % 5 == 0:
                print(f"  Added {i + 1}/{len(chunks)} chunks...")
    else:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
        
        texts_for_embedding = chunks
        print("Generating embeddings (this may take a moment)...")
        embedding_vectors = embeddings.embed_documents(texts_for_embedding)
        
        collection.add(
            documents=chunks,
            ids=ids,
            embeddings=embedding_vectors
        )
    
    print(f"Successfully ingested {collection.count()} documents into ChromaDB")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Path: {CHROMA_PATH}")
    
    return collection

def search_knowledge(query: str, n_results: int = 3) -> list:
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except:
        print("Knowledge base not initialized. Run ingest_to_chromadb() first.")
        return []
    
    api_key = os.getenv('GEMINI_API_KEY', '')
    
    if api_key:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
        query_embedding = embeddings.embed_query(query)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
    else:
        import numpy as np
        random_embedding = np.random.rand(768).tolist()
        results = collection.query(
            query_embeddings=[random_embedding],
            n_results=n_results
        )
    
    formatted_results = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            formatted_results.append({
                'id': results['ids'][0][i],
                'content': doc,
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
    
    return formatted_results

if __name__ == "__main__":
    print("=== ChromaDB Ingestion ===")
    ingest_to_chromadb()
    
    print("\n=== Test Search ===")
    results = search_knowledge("birth certificate for newborn")
    print(f"Found {len(results)} results")
    for r in results:
        print(f"- {r['id']}")
