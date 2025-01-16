# raggle
======================================================================
For this approach **a2**:

Problems in approach a1(VANILLA RAG):
- only one retrieval step
- Semantic similarity is computed with the user query and the documents.

But, we can explore the possibility of Agentic RAG using smolagents/Pydantic agents.

- Implement agentic_rag, which would integrate agents(for dynamic planning approach) and RAG(dynamic data) + Web search as one of the tool.
- agents
    - Explore smolagents to integrate RAG and web_search.
    - Make a router which would choose between RAG and web search
    - If the query does not need anything from the document uploaded then,
    - Web Search
        - use smolagents to
            - rewrite,search the query,
            - get these results via scrapping/Crawl4AI,
            - Process the results(chunking,etc)
            - [#TODO] How to handle table/images on the website - Read Crawl4AI docs / unstructed.io docs
            - Push everything to Chromadb and lets call it reteriver 1
    - If document data is needed,then
        - Parse, chunk, process chunks, Push the data to chroma db
        - Lets call it as retriever 2.
    - Given these two tools first integrate and get answers.
    - Add tools such as weather, calculator, and other simple tools[#TODO]
    - Make a mini agent which would decide to flush out non required chunks out of the web_search vectordb and accomodate new chunks for follow up questions.


- Explore the idea of giving memory to the agents and pushing in web_search vector_store inside them because it is relatively smaller.
- Option to explore the entire vectorDb because that would contain the data used for this research
- may be export the results as a PDF ==> Research Agent



======================================================================
For this approach **a1**:

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
