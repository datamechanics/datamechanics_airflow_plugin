from airflow import DAG, utils
from datamechanics_airflow_plugin.operator import DataMechanicsOperator

args = {
    "owner": "airflow",
    "email": ["airflow@example.com"],
    "depends_on_past": False,
    "start_date": utils.dates.days_ago(0, second=1),
}


dag = DAG(dag_id="failed-app", default_args=args, schedule_interval=None)

word_count_task = DataMechanicsOperator(
    task_id="failed-word-count",
    dag=dag,
    config_overrides={
        "type": "Scala",
        "mainApplicationFile": "gs://dm-demo-data/FOO/scala-word-count-assembly-0.0.1.jar",  # This path does not exist
        "mainClass": "co.datamechanics.scalawordcount.CountingApp",
        "arguments": [
            "gs://dm-demo-data/data/words-dataset/words_*.log",
            "gs://dm-demo-data/output/dictionary_{{ ts_nodash }}.txt",
        ],
    },
)
