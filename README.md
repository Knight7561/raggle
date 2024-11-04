# raggle

## Overview

Your Project Name is a command-line conversational AI tool built on Retrieval-Augmented Generation (RAG) principles. It searches the web for information based on user queries and processes the results to provide informative responses.

### Git branch Index
- [main](https://github.com/Knight7561/raggle/tree/main): Main showcase code
- [develop](https://github.com/Knight7561/raggle/tree/develop): Code under current development
- [idea-pitch](https://github.com/Knight7561/raggle/tree/idea-pitch) : Branch to document Ideas
- [A1](https://github.com/Knight7561/raggle/tree/a1): Idea 1 of implementation.

## Features

- **Command-Line Interface**: Interact with the application through simple command-line commands.
- **Web Search Functionality**: Query the web and obtain generated responses.
- **Output to File**: Save responses in a text file for easy access.
- **RAG Implementation**: Uses a structured approach to enhance response quality.

## Workflow - Approach 1

1. **Query Input**: Accept the query via command line (future UI support planned).
2. **Query Transformation**: Rewrite or transform the query as needed (this can be delayed until later stages).
3. **Web Search**: Perform a web search based on the transformed query.
4. **Results Parsing and Chunking**: 
   - Store search results as a dictionary with URLs as keys for better organization.
5. **Storage**: Use Chromadb for storing the processed results in a Vector Database.
6. **Dense Retrieval**: Retrieve relevant chunks from the stored data.
7. **Deduplication and Reranking**: 
   - Implement logic to deduplicate and rerank retrieved elements.
8. **Augmentation and Summarization**: Use a language model (LLM) to augment and summarize the final output.

## Getting Started

### Prerequisites

- [Python](https://www.python.org/) (version 3.x)
- Required Python packages (see below)

### Installation

1. Clone the repository:
   ```git clone https://github.com/Knight7561/raggle.git```
2. Navigate to the project directory:
```cd raggle```
3. Install required packages:
```pip install -r requirements.txt```

### Usage
To run the application, use the following command:

```python main.py -q "Your query here"```


Example:
```python main.py -q "What is the capital of France?"```

The response will be printed to the console and also saved in temp/output.txt.
