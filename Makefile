start-milvus:
	bash standalone_embed.sh start

stop-milvus:
	bash standalone_embed.sh stop

delete-milvus-data:
	bash standalone_embed.sh delete

run:
	python3 -m src.app

llm:
	ollama serve