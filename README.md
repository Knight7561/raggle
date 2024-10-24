# raggle
## Idea
- Main Idea is to build a AI powered Search engine, similar to perplexity. But, Since the exact implementation of the app is not open-sourced yet.
- This implementation is to clear my understanding of how an AI Search would be implemented from scratch. And, the goal is to build a app that would ideally function as a clone of perplexity app features,thus perplexity would be acting like a benchmark.

## Steps:
### Approach 1
- Accept a query from a model
- Use a LLM to query transformation using prompt engineering, may be a small model.
- Optional: May be use the principles of RAG Fusion, to query into multiple questions.
- For the rephrase query, do a google Search to get relevant results using SEARCH API, etc
- For each link, get the content:
    - Chunk the content, embed(Decide which embedding model) and put it in a vector database[Should I use vectorDb or FAISS].
    - Pick n docs from vector database w.r.t query similarity search.
    - Rerank the chunks.
    - Augment and send the relavant chunks with the query to the LLM(for now can use gemini and later change to llama)and get answer.
    - Use LLM as a Judge to see if the response actually answers the question or not. Iterate if needed.

### Approach 2:
- Notes: Instead/With VectorDB, How would it be adding a Graph RAG/Light RAG to these chunks.