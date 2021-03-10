# Data Mechanics Airflow Plugin

An Airflow plugin to launch and monitor Spark applications on the Data Mechanics platform.

## Environment

* Python >= 3.5
* apache-airflow >= 1.10.x. Compatible with Airflow 2.

## Installation and usage

A tutorial to configure and use this plugin is available in the [Data Mechanics docs](https://docs.datamechanics.co/docs/airflow-plugin).

The main difference between Airflow 1 and Airflow 2 is how to import the plugin:
```python
# Airflow 1
from airflow.operators.datamechanics import DataMechanicsOperator

# Airflow 2
from datamechanics_airflow_plugin.operator import DataMechanicsOperator
```

## Example DAGs

You can see example DAGs for [Airflow 1](https://github.com/datamechanics/datamechanics_airflow_plugin/tree/master/example_dags_airflow1) and [Airflow 2](https://github.com/datamechanics/datamechanics_airflow_plugin/tree/master/example_dags_airflow2).

## Development

[Development instructions](DEVELOPMENT.md).
