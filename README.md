## Mental Health Chatbot

Retrieval Augmented Generation (RAG) combines the power of LLMs with external knowledge base. 

![RAG](images/rag.png)

## How to run

1. Install Ollama and Mistral
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run mistral
```

2. Run Ollama
```bash
make llm
```

3. Start Milvus (Docker should be running)
```bash
make start-milvus
```

4. Create a virtual env and install requirements
```bash
conda create -n llm python==3.9.16
conda activate llm
pip install -r "requirements.txt"
```

5. Run app
```bash
make streamlit-new # For first time
make streamlit # After vector db has been created
```

5.