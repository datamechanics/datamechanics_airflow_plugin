FROM apache/airflow:2.0.1

# This is a fix for https://github.com/apache/airflow/issues/14266
# TODO: remove once a new version of `apache/airflow` is released and this bug fixed
RUN pip uninstall  --yes azure-storage && \
    pip install -U azure-storage-blob apache-airflow-providers-microsoft-azure==1.1.0

# Copying the folder and installing with -e will enable auto-refresh in the docker-compose
# based dev environment.
COPY --chown=airflow:airflow . /opt/datamechanics_airflow_plugin/
RUN pip install --user -e /opt/datamechanics_airflow_plugin/
