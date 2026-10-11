.PHONY: install pipeline dagster dashboard test clean

install:
	pip install -r requirements.txt

pipeline:
	python run_pipeline.py

dagster:
	dagster dev -f orchestration/pipeline.py

dashboard:
	streamlit run dashboard/app.py

test:
	pytest tests/ -v

clean:
	rm -rf data/*.duckdb raw_data/*.csv dbt_project/target dbt_project/logs
