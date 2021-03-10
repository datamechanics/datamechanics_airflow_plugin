# Dev environment

## Dependencies

Install the command runner `just` on your machine with

```bash
brew install just
```

Make sure you also have the following:

* docker
* docker-compose

## Spin up an Airflow 1 server

```bash
just serve_airflow1
```

## Spin up an Airflow 2 server

```bash
just serve_airflow2
```

## One-time operations

Open Airflow at [http://localhost:8080](http://localhost:8080).

These are some of the gotchas you might run into when you're not used to Airflow.

1. Activate the DAGs you want to run by toggling their state from `Off` to `On` (on the left in the `DAGs` page)
2. Create a Data Mechanics connection. To do this, click on `Admin` in the navbar, then `Connections` in the dropdown menu, then go to the `Create` tab. The connection should have `datamechanics_default` as connection name, a cluster URL as host, an API key for cluster as password. Use `HTTP` connection in the connection type. Leave the rest blank.

> As long as you don't trash the anonymous Docker compose volume on which the airflow db is persisted, you shouldn't have to repeat the operations above, even if you restart the Airflow server.

> This creation of a connection could be done programmatically in an init script. See [this section](https://docs.datamechanics.co/docs/airflow-plugin#install-the-data-mechanics-airflow-plugin) of the user documentation for an example.


## Reboot your environments

If you need to start afresh, run

```
just clear containers
```

Be careful, this will trash your DBs and you'll have to do the one-time operations above again.

## Known issues

The Airflow 2 server is super slow.
