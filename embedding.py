import torch
from transformers import BertTokenizer, BertModel
from typing import List

# Initialize the tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def tokenize_and_chunk(text: str, max_length: int) -> List[torch.Tensor]:
    # Tokenize the text and split it into chunks that fit the model's max input size
    tokens = tokenizer.tokenize(text)
    token_chunks = [tokens[i: i + max_length] for i in range(0, len(tokens), max_length)]
    return [tokenizer.encode_plus(chunk, max_length=max_length, truncation=True, padding='max_length', return_tensors="pt") for chunk in token_chunks]

def generate_embeddings(model_inputs: List[torch.Tensor]) -> List[torch.Tensor]:
    # Generate embeddings for each chunk of tokens
    with torch.no_grad():  # Disable gradient computation for inference
        # The input_ids generated by the BertTokenizer (or any other tokenizer from the Hugging Face Transformers library) represent the location of each token in the tokenizer’s vocabulary.

        embeddings = [model(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask']) for inputs in model_inputs]
    return [emb.pooler_output for emb in embeddings]

def process_documents(documents: List[str], max_length: int = 512) -> List[List[torch.Tensor]]:
    # Process each document to generate embeddings
    doc_embeddings = []
    for doc in documents:
        inputs = tokenize_and_chunk(doc, max_length) # Each of the input has a shape of 512 * 1.
        embeddings = generate_embeddings(inputs)
        doc_embeddings.append(embeddings)
    return doc_embeddings

# Example documents (each containing more than 512 tokens)
documents = [
    "The quick brown fox jumps over the lazy dog. " * 100,
    "All human beings are born free and equal in dignity and rights. " * 100
]

# Process the documents
doc_embeddings = process_documents(documents)

# Print the shape of the embeddings for the first document
print("Embeddings for the first document:")
for i, emb in enumerate(doc_embeddings[0]):
    print(f"Chunk {i + 1} embedding shape: {emb.shape}")
