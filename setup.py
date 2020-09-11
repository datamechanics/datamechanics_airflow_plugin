#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as history_file:
    history = history_file.read()

requirements = ["requests", "apache-airflow>=1.10.0"]

setup_requirements = []

setup(
    author="Data Mechanics Engineering Team",
    author_email="engineering@datamechanics.co",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="An Airflow plugin to launch and monitor Spark applications on the Data Mechanics platform",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="datamechanics_airflow_plugin",
    name="datamechanics_airflow_plugin",
    packages=find_packages(
        include=["datamechanics_airflow_plugin", "datamechanics_airflow_plugin.*"]
    ),
    setup_requires=setup_requirements,
    url="https://github.com/datamechanics/datamechanics_airflow_plugin",
    version="1.0.6",
    zip_safe=False,
    entry_points={
        "airflow.plugins": [
            "datamechanics = datamechanics_airflow_plugin.plugin:DataMechanicsPlugin"
        ]
    },
)
