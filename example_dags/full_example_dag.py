from airflow import DAG, utils
from airflow.operators.datamechanics import DataMechanicsOperator

args = {
    "owner": "airflow",
    "email": ["airflow@example.com"],
    "depends_on_past": False,
    "start_date": utils.dates.days_ago(0, second=1),
}


dag = DAG(dag_id="full-example", default_args=args, schedule_interval=None)

parallel_0_task = DataMechanicsOperator(
    task_id="parallel-0",
    dag=dag,
    config_overrides={
        "type": "Scala",
        "mainApplicationFile": "gs://dm-demo-data/code/scala-word-count-assembly-0.0.1.jar",
        "mainClass": "co.datamechanics.scalawordcount.CountingApp",
        "arguments": [
            "gs://dm-demo-data/data/words-dataset/words_*.log",
            "gs://dm-demo-data/output/dictionary_0_{{ ts_nodash }}.txt",
        ],
    },
)

parallel_1_task = DataMechanicsOperator(
    task_id="parallel-1",
    dag=dag,
    config_overrides={
        "type": "Scala",
        "mainApplicationFile": "gs://dm-demo-data/code/scala-word-count-assembly-0.0.1.jar",
        "mainClass": "co.datamechanics.scalawordcount.CountingApp",
        "arguments": [
            "gs://dm-demo-data/data/words-dataset/words_*.log",
            "gs://dm-demo-data/output/dictionary_1_{{ ts_nodash }}.txt",
        ],
    },
)

spark_pi_task = DataMechanicsOperator(
    task_id="spark-pi",
    dag=dag,
    config_overrides={
        "type": "Scala",
        "sparkVersion": "3.0.0",
        "mainApplicationFile": "local:///opt/spark/examples/jars/spark-examples_2.12-3.0.0.jar",
        "mainClass": "org.apache.spark.examples.SparkPi",
        "arguments": ["10000"],
    },
)

failed_app_task = DataMechanicsOperator(
    task_id="failed-app",
    dag=dag,
    config_overrides={
        "type": "Scala",
        "mainApplicationFile": "gs://dm-demo-data/FOO/scala-word-count-assembly-0.0.1.jar",  # This path does not exist
        "mainClass": "co.datamechanics.scalawordcount.CountingApp",
        "arguments": [
            "gs://dm-demo-data/data/words-dataset/words_*.log",
            "gs://dm-demo-data/output/dictionary_f_{{ ts_nodash }}.txt",
        ],
    },
)

failed_submission_task = DataMechanicsOperator(
    task_id="failed-submission",
    dag=dag,
    config_overrides={
        "type": "Scala",
        "sparkVersion": "3.0.0",
        "mainApplicationFile": "local:///opt/spark/examples/jars/spark-examples_2.12-3.0.0.jar",
        "mainClass": "org.apache.spark.examples.SparkPi",
        "arguments": ["10000"],
        "foo": "bar",  # This field does not exist
    },
)

spark_pi_task.set_upstream([parallel_0_task, parallel_1_task])
failed_app_task.set_upstream(spark_pi_task)
failed_submission_task.set_upstream(spark_pi_task)
