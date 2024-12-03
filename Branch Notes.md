# raggle
For this approach a1:
### Focused on implmenting web search
Steps/Map:
1. Accept the query in CLI
    1.1. Accept this query in a UI
2. Query transformation/Re-writing
    - Can be delayed for the entire cycle to be complete.
3. Web Search Results
4. Parse and chunk the results
    - Realised that instead of storing Response items as list, its better if we store it as a dictorinary with url as key. --Done
5. Store in FAISS/VectorDB
    - Choosed Chromadb as its easier implmentation
6. Dense Reterive chunks
7. Deduplicate and rerank elements [#TODO: RERANKING ]
8. Augument and Sumarise using a LLM.
