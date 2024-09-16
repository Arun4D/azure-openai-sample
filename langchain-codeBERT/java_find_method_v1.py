from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np

import re

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['clean_up_tokenization_spaces'] = 'False'


# Load the model and tokenizer
model_name = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_code_embeddings(methods):
    code_embeddings = []
    name_embeddings = []
    method_names = []  # To store method names corresponding to embeddings
    for method in methods:
        method_code = method["code"]
        method_name = method["name"]
        chunk_method_name_embedding = get_codebert_embeddings(method_name)
        name_embeddings.append(chunk_method_name_embedding)
        chunk_method_code_embedding = get_codebert_embeddings(method_code)
        code_embeddings.append(chunk_method_code_embedding)
        method_names.append(method_name)
    return code_embeddings, name_embeddings, method_names

def create_faiss_index(embeddings, method_names):
    dim = embeddings[0].shape[0]  # Dimension of the embeddings
    embeddings = np.array([emb / np.linalg.norm(emb) for emb in embeddings])  # Normalize embeddings
    index = faiss.IndexFlatIP(dim)  # Create a FAISS index for cosine similarity
    index.add(embeddings)  # Add embeddings to the index
    return index, method_names


def search_faiss_index(query_embedding, index, method_names, method_codes, k=1):
    
    query_embedding = query_embedding / np.linalg.norm(query_embedding)  # Normalize the query
    query_embedding = np.array([query_embedding])
    distances, indices = index.search(query_embedding, k)
    
    # Print shapes for debugging
    print(f"Distances shape: {distances.shape}")
    print(f"Indices shape: {indices.shape}")
    print(f"Distances: {distances}")
    print(f"Indices: {indices}")
    print(f"method_names: {method_names}")

       # Collect the search results
    results = []
    for i in range(k):
        idx = indices[0][i]  # Extract the index from the search result
        if idx >= 0 and idx < len(method_names):  # Ensure the index is valid
            method_name = method_names[idx]
            method_code = next((code["code"] for code in method_codes if code["name"] == method_name), "Code not found")
            
            # Append method name, code, and distance (which represents similarity score)
            results.append((method_name, method_code, distances[0][i]))
        else:
            # Handle invalid results with placeholder values
            results.append(("Unknown Method", "Code not found", float('inf')))

    return results

def get_codebert_embeddings(prompt):
    inputs = tokenizer(prompt, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        query_embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
        # Normalize the query embedding
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        return query_embedding

    
def chunk_code(code, chunk_size=512):
    lines = code.split('\n')
    chunks = []
    current_chunk = []

    for line in lines:
        current_chunk.append(line)
        if len(' '.join(current_chunk)) > chunk_size:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

def extract_methods_from_file(file_path):
    # Regular expression to match Java methods, including static methods
    method_pattern = re.compile(
        r'((public|protected|private)?\s*(static)?\s*[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*\{(?:[^{}]*|\{[^{}]*\})*?\})',
        re.DOTALL
    )
    
    # Read the contents of the Java file
    with open(file_path, 'r') as file:
        java_code = file.read()
    
    # Find all methods in the file
    methods = method_pattern.findall(java_code)
    
    # Return the full method code for each match
    return [method[0] for method in methods]

def extract_method_name(method_code):
    # Regular expression to extract method name
    name_pattern = re.compile(r'\b\w+\s+(\w+)\s*\(')
    method_name_match = name_pattern.search(method_code)
    return method_name_match.group(1) if method_name_match else None

def extract_methods_from_src(src_folder):
    # Traverse the src folder and find all .java files
    src_all_methods = [] 
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                print(f"Extracting methods from: {file_path}")
                
                # Extract methods from the current Java file
                methods = extract_methods_from_file(file_path)
                methods_map = []
                for method_code in methods:
                    method_name = extract_method_name(method_code)
                    methods_map.append({"name": method_name, "code": method_code})
            
                src_all_methods = src_all_methods + methods_map
    return src_all_methods

src_folder = 'src'
code_chunks = extract_methods_from_src(src_folder)

# Generate embeddings and create FAISS index
code_embeddings, name_embeddings, method_names = get_code_embeddings(code_chunks)
faiss_index, method_names = create_faiss_index(name_embeddings, method_names)

# Example query prompt
query_prompt = "calculateSum"
query_embedding = get_codebert_embeddings(query_prompt)

# Search in FAISS index
results = search_faiss_index(query_embedding, faiss_index, method_names, code_chunks)

for result in results:
    print(f"Method Name: {result[0]}")
    print(f"Method Code: {result[1]}")
    print(f"Distance: {result[2]}")




