# raggle
For this approach a1:

Steps/Map for VANILLA RAG:
1. Accept the query in CLI
    1.1. Accept this query in a UI
    - [Skipped to last, focus is on getting the thing working]
2. Query transformation/Re-writing
    - [Complete]
3. Web Search Results
4. Parse and chunk the results
    - Realised that instead of storing Response items as list, its better if we store it as a dictorinary with url as key. --Done
5. Store in FAISS/VectorDB
    - Choosed Chromadb as its easier implmentation
6. Dense Reterive chunks
7. Deduplicate and rerank elements
8. Augument and Sumarise using a LLM.
9. Implment Citation in the response.
    - [Moved to other branch]

Futhur plans:
- Improve the Vanilla RAG by implmenting Agentic RAG, Citiation results.
