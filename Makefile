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

streamlit:
	streamlit run app.py -- -de True

streamlit-new:
	streamlit run app.py -- -c True -de True

streamlit-add:
	streamlit run app.py -- -c True -d '["file.json"]' -de True