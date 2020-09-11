from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint
import sys

from .hook import DataMechanicsHook
from .operator import DataMechanicsOperator


plugin_name = "datamechanics"


bp = Blueprint(
    plugin_name,
    __name__,
    template_folder="templates",  # registers airflow/plugins/templates as a Jinja template folder
    static_folder="static",
    static_url_path="/static/" + plugin_name,
)


class DataMechanicsPlugin(AirflowPlugin):
    name = plugin_name
    operators = [DataMechanicsOperator]
    hooks = [DataMechanicsHook]
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = [bp]
    menu_links = []
