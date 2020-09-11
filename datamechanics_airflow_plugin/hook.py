from airflow.hooks.base_hook import BaseHook
from airflow import __version__
from airflow.exceptions import AirflowException

from urllib.parse import urljoin

import requests
import time
from requests import exceptions as requests_exceptions


SUBMIT_APP_ENDPOINT = ("POST", "api/apps/")
GET_APP_ENDPOINT = ("GET", "api/apps/{}")
DELETE_APP_ENDPOINT = ("DELETE", "api/apps/{}")

USER_AGENT_HEADER = {"user-agent": "airflow-{v}".format(v=__version__)}


class DataMechanicsHook(BaseHook):
    def __init__(
        self,
        dm_conn_id="datamechanics_default",
        timeout_seconds=180,
        retry_limit=3,
        retry_delay=1.0,
    ):
        self.dm_conn_id = dm_conn_id
        self.dm_conn = self.get_connection(dm_conn_id)
        self.timeout_seconds = timeout_seconds
        if retry_limit < 1:
            raise ValueError("Retry limit must be greater than equal to 1")
        self.retry_limit = retry_limit
        self.retry_delay = retry_delay

    def _do_api_call(self, endpoint_info, payload=None):
        """
        Utility function to perform an API call with retries
        :param endpoint_info: Tuple of method and endpoint
        :type endpoint_info: tuple[string, string]
        :param payload: Parameters for this API call.
        :type payload: dict
        :return: If the api call returns a OK status code,
            this function returns the response in JSON. Otherwise,
            we throw an AirflowException.
        :rtype: dict
        """
        method, endpoint = endpoint_info

        api_key = self.dm_conn.password
        url = urljoin(self.dm_conn.host, endpoint)
        headers = {**USER_AGENT_HEADER, "X-API-Key": api_key}

        if method == "GET":
            request_func = requests.get
        elif method == "POST":
            request_func = requests.post
        elif method == "DELETE":
            request_func = requests.delete
        else:
            raise AirflowException("Unexpected HTTP Method: " + method)

        attempt_num = 1
        while True:
            try:
                response = request_func(
                    url, json=payload, headers=headers, timeout=self.timeout_seconds
                )
                response.raise_for_status()
                return response.json()
            except requests_exceptions.RequestException as e:
                if not _retryable_error(e):
                    # In this case, the user probably made a mistake.
                    # Don't retry.
                    raise AirflowException(
                        "Response: {0}, Status Code: {1}".format(
                            e.response.content, e.response.status_code
                        )
                    )

                self._log_request_error(attempt_num, e)

            if attempt_num == self.retry_limit:
                raise AirflowException(
                    (
                        "API requests to Data Mechanics failed {} times. "
                        + "Giving up."
                    ).format(self.retry_limit)
                )

            attempt_num += 1
            time.sleep(self.retry_delay)

    def _log_request_error(self, attempt_num, error):
        self.log.error(
            "Attempt %s API Request to Data Mechanics failed with reason: %s",
            attempt_num,
            error,
        )

    def submit_app(self, payload):
        response = self._do_api_call(SUBMIT_APP_ENDPOINT, payload)
        return response["appName"]

    def get_app(self, app_name):
        method, path = GET_APP_ENDPOINT
        filled_endpoint = (method, path.format(app_name))
        response = self._do_api_call(filled_endpoint)
        return response

    def kill_app(self, app_name):
        method, path = DELETE_APP_ENDPOINT
        filled_endpoint = (method, path.format(app_name))
        response = self._do_api_call(filled_endpoint)
        return response

    def get_app_page_url(self, app_name):
        return urljoin(self.dm_conn.host, "dashboard/apps/{}".format(app_name))


def _retryable_error(exception):
    return isinstance(
        exception, (requests_exceptions.ConnectionError, requests_exceptions.Timeout)
    ) or (exception.response is not None and exception.response.status_code >= 500)
