import json
import time

from typing import Dict, Optional, Union

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from .hook import DataMechanicsHook
from .application_state import ApplicationStateType

XCOM_APP_NAME_KEY = "app_name"
XCOM_APP_PAGE_URL_KEY = "app_page_url"


class DataMechanicsOperator(BaseOperator):
    """
    Submits a Spark app to Data Mechanics using the `POST /api/apps` API endpoint.
    """

    # Used in airflow.models.BaseOperator
    template_fields = (
        "app_name",
        "job_name",
        "config_template_name",
        "config_overrides",
    )
    template_ext = (".json",)
    # Data Mechanics brand color (blue) under white text
    ui_color = "#1CB1C2"
    ui_fgcolor = "#fff"

    @apply_defaults
    def __init__(
        self,
        app_name: Optional[str] = None,
        job_name: Optional[str] = None,
        config_template_name: Optional[str] = None,
        config_overrides: Optional[Union[Dict, str]] = None,
        dm_conn_id: str = "datamechanics_default",
        polling_period_seconds: int = 10,
        dm_retry_limit: int = 3,
        dm_retry_delay: int = 1,
        do_xcom_push: bool = False,
        **kwargs,
    ):
        """
        Creates a new ``DataMechanicsOperator``.
        """
        super().__init__(**kwargs)

        self.dm_conn_id = dm_conn_id
        self.polling_period_seconds = polling_period_seconds
        self.dm_retry_limit = dm_retry_limit
        self.dm_retry_delay = dm_retry_delay
        self.app_name = None  # will be set from the API response
        self._payload_app_name = app_name
        self.job_name = job_name
        self.config_template_name = config_template_name
        self.config_overrides = config_overrides
        self.do_xcom_push = do_xcom_push
        self.payload = {}

        if self.job_name is None:
            self.log.info(
                "Setting job name to task id because `job_name` argument is not specified"
            )
            self.job_name = kwargs["task_id"]

    def _get_hook(self):
        return DataMechanicsHook(
            self.dm_conn_id,
            retry_limit=self.dm_retry_limit,
            retry_delay=self.dm_retry_delay,
        )

    def _build_payload(self):
        self.payload["jobName"] = self.job_name
        if self._payload_app_name is not None:
            self.payload["appName"] = self._payload_app_name
        if self.config_template_name is not None:
            self.payload["configTemplateName"] = self.config_template_name

        # templated config overrides dict pulled from xcom is a json str
        if self.config_overrides is not None:
            if isinstance(self.config_overrides, str):
                # json standard requires double quotes
                self.config_overrides = json.loads(
                    self.config_overrides.replace("'", '"')
                )
            self.payload["configOverrides"] = self.config_overrides

    def execute(self, context):
        self._build_payload()
        hook = self._get_hook()
        self.app_name = hook.submit_app(self.payload)
        self._monitor_app(hook, context)

    def on_kill(self):
        hook = self._get_hook()
        hook.kill_app(self.app_name)
        self.log.info(
            "Task: %s with app name: %s was requested to be cancelled.",
            self.task_id,
            self.app_name,
        )

    def _monitor_app(self, hook, context):

        if self.do_xcom_push:
            context["ti"].xcom_push(key=XCOM_APP_NAME_KEY, value=self.app_name)
        self.log.info("App submitted with app_name: %s", self.app_name)
        app_page_url = hook.get_app_page_url(self.app_name)
        if self.do_xcom_push:
            context["ti"].xcom_push(key=XCOM_APP_PAGE_URL_KEY, value=app_page_url)

        while True:
            app = hook.get_app(self.app_name)
            app_state = _get_state_from_app(app)
            self.log.info("View app details at %s", app_page_url)
            if app_state.simplified.is_terminal:
                if app_state.simplified.is_successful:
                    self.log.info("%s completed successfully.", self.task_id)
                    return
                else:
                    error_message = "{t} failed with terminal state: {s}".format(
                        t=self.task_id, s=app_state.value
                    )
                    raise AirflowException(error_message)
            else:
                self.log.info("%s in app state: %s", self.task_id, app_state.value)
                self.log.info("Sleeping for %s seconds.", self.polling_period_seconds)
                time.sleep(self.polling_period_seconds)


def _get_state_from_app(app):
    return ApplicationStateType(app.get("status", {}).get("state", ""))
