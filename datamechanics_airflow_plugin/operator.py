import time

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
    template_fields = ("payload",)
    # Data Mechanics brand color (blue) under white text
    ui_color = "#1CB1C2"
    ui_fgcolor = "#fff"

    @apply_defaults
    def __init__(
        self,
        app_name=None,
        job_name=None,
        config_template_name=None,
        config_overrides=None,
        dm_conn_id="datamechanics_default",
        polling_period_seconds=10,
        dm_retry_limit=3,
        dm_retry_delay=1,
        do_xcom_push=False,
        **kwargs
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

        self.payload = {}
        if app_name is not None:
            self.payload["appName"] = app_name
        if job_name is None:
            self.log.info(
                "Setting job name to task id because `job_name` argument is not specified"
            )
        self.payload["jobName"] = job_name or kwargs["task_id"]
        if config_template_name is not None:
            self.payload["configTemplateName"] = config_template_name
        if config_overrides is not None:
            self.payload["configOverrides"] = config_overrides

        # self.payload = _deep_string_coerce(self.payload)
        self.do_xcom_push = do_xcom_push

    def _get_hook(self):
        return DataMechanicsHook(
            self.dm_conn_id,
            retry_limit=self.dm_retry_limit,
            retry_delay=self.dm_retry_delay,
        )

    def execute(self, context):
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
