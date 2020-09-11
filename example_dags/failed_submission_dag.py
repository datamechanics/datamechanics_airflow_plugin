from airflow import DAG, utils
from airflow.operators.datamechanics import DataMechanicsOperator

args = {
    "owner": "airflow",
    "email": ["airflow@example.com"],
    "depends_on_past": False,
    "start_date": utils.dates.days_ago(0, second=1),
}


dag = DAG(dag_id="failed-submission", default_args=args, schedule_interval=None)

spark_pi_task = DataMechanicsOperator(
    task_id="failed-spark-pi",
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
