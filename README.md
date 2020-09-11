# Data Mechanics Airflow integration

## Spin up Airflow

If you haven't got `just` on your machine already, install it with

```bash
brew install just
```

Then run Airflow with

```bash
just serve
```

> The script will ask you to install `docker-compose` if you haven't got it on your machine already.
> You can find it [here](https://docs.docker.com/install/).

> The first run will be long because Docker images are downloaded.

Shut down Airflow with `Ctrl+C`.

## Before the demo: one-time operations

Open Airflow at [http://localhost:8080](http://localhost:8080).

These are some of the gotchas you might run into when you're not used to Airflow.

1. Activate the DAGs you want to run by toggling their state from `Off` to `On` (on the left in the `DAGs` page)
2. Create a Data Mechanics connection. To do this, click on `Admin` in the navbar, then `Connections` in the dropdown menu, then go to the `Create` tab. The connection should have `datamechanics_default` as connection name, `https://demo.datamechanics.co/` as host, and our usual API key for the demo cluster as password. Leave the rest blank.

> As long as you don't trash the anonymous Docker compose volume on which the airflow db is persisted, you shouldn't have to repeat the operations above, even if you restart Airflow.

## Do the demo

1. Open Airflow at [http://localhost:8080](http://localhost:8080).
2. Open the DAG `full-example`.
3. Switch to `Graph view`
4. Trigger the DAG (`Trigger DAG`)
5. Explain that the first two tasks are run in parallel (you can show the dashboard at this point)
6. The two last tasks are meant to fail. Click on the failed execution of the `failed-app` task, click on `View logs`, and show that the URL to the dashboard is provided in the logs

## Turn this demo into a library

The code that should be turned into an Airflow plugin library is contained in folder `plugins/`.
