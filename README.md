# Marmelad

**Marmelad** is an intelligent LangGraph-powered agent designed to assist with research, coding, and problem-solving
across various domains.

[![CI](https://github.com/shamspias/marmelad/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/shamspias/marmelad/actions/workflows/unit-tests.yml)
[![Integration Tests](https://github.com/shamspias/marmelad/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/shamspias/marmelad/actions/workflows/integration-tests.yml)

[![Open in - LangGraph Studio](https://img.shields.io/badge/Open_in-LangGraph_Studio-00324d.svg)](https://studio.langchain.com/templates/open?githubUrl=https://github.com/shamspias/marmelad)

## What it does

This project includes three key graphs:

- An **index** graph (`src/index_graph/graph.py`) to index document objects.
- A **retrieval** graph (`src/retrieval_graph/graph.py`) to handle chat history and respond with fetched documents.
- A **researcher** subgraph (part of the retrieval graph) for executing research
  plans (`src/retrieval_graph/researcher_graph/graph.py`).

### How it works

1. **Indexing Documents:**
   The index graph takes in document objects to index them. If no documents are provided, sample documents
   from `src/sample_docs.json` are indexed by default.

2. **Handling Queries:**
    - For LangChain-specific queries, the retrieval graph generates a research plan, passes it to the researcher
      subgraph, and fetches relevant documents.
    - For ambiguous queries, it seeks clarification.
    - For unrelated queries, it responds appropriately.

3. **Researcher Subgraph:**
    - Breaks down research plans into steps.
    - Generates search queries for each step and retrieves relevant documents in parallel.
    - Returns these documents to the retrieval graph to generate a response.

## Prerequisites

Ensure you have the following installed:

- Python 3.11+
- Docker
- A virtual environment tool

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/shamspias/marmelad.git
cd marmelad
```

### 2. Setup Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Use `venv\Scripts\activate` on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy and configure the environment variables:

```bash
cp example.env .env
# Edit .env to include necessary API keys and database URLs
```

### 5. Docker Setup

Ensure Docker is operational on your machine.

### 6. Install and Run LangGraph CLI

```bash
pip install langgraph-cli
langgraph up  # Initializes and runs the necessary services
```

### 7. Enable Memory

```bash
sudo sysctl vm.overcommit_memory=1
```

## Model Configuration

Specify the model provider and model name using the following formats:

| Provider Name   | Model Specification Format             |
|-----------------|----------------------------------------|
| Anthropic       | `anthropic/claude-3-5-sonnet`          |
| Anthropic       | `anthropic/claude-3-opus`              |
| Anthropic       | `anthropic/claude-3-haiku`             |
| Azure OpenAI    | `azure_openai/gpt-4o-realtime-preview` |
| Cohere          | `cohere/command-r-plus`                |
| Cohere          | `cohere/phi-3-vision-128k-instruct`    |
| Google VertexAI | `google_vertexai/gemini`               |
| Hugging Face    | `huggingface/bert-large`               |

### Enable Models in `project.toml`

To use specific models, enable their corresponding libraries in the `project.toml` file under dependencies:

```toml
dependencies = [
    "langgraph>=0.2.34",
    "langchain-openai>=0.2.2",
    "langchain-anthropic>=0.2.3",
    "langchain>=0.3.3",
    #    "langchain-fireworks>=0.2.1", # Uncomment to enable
    "python-dotenv>=1.0.1",
    #    "langchain-elasticsearch>=0.3.0", # Uncomment to enable
    #    "langchain-pinecone>=0.2.0", # Uncomment to enable
    "msgspec>=0.18.6",
    #    "langchain-mongodb>=0.2.0", # Uncomment to enable
    #    "langchain-cohere>=0.3.0", # Uncomment to enable Cohere models
    "langchain-postgres>=0.0.12",
    "httpx[socks]>=0.27.2",
    #    "langchain-google-genai>=2.0.1", # Uncomment to enable Google models
    "langchain-mistralai>=0.2.0",
    #    "gigachat>=0.1.35", # Uncomment to enable
    #    "langchain-community>=0.3.2", # Uncomment to enable
]
```

## Running the Application

### Using LangGraph CLI

To use a different database:

```bash
langgraph up
```

To connect to a pre-existing database:

```bash
langgraph up --postgres-uri postgresql+psycopg://user_name:password@localhost:port/marmelad_db
```

## Customization

1. **Change the retriever:** Modify the `retriever_provider` to use Elasticsearch, MongoDB, or Pinecone as per your
   requirements.

2. **Adjust models:** Update the `response_model`, `query_model`, and `embedding_model` in your configuration for
   different use cases.

3. **Extend functionality:** Add nodes or edges in the retrieval graph or customize prompts
   in `src/retrieval_graph/prompts.py` to tailor the agent's behavior.

## Troubleshooting

Refer to the Troubleshooting section in the documentation for common setup issues.
