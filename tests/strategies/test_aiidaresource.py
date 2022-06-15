
"""Tests the resource strategy."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from oteapi.models import SessionUpdate

    from oteapi_aiida.strategies.aiidaresource import SessionUpdateAiiDAResource

def test_resource(static_files: "Path") -> None:
    """Test `file` download strategy on binary and text files.

    Test files are taken from filesamples.com.
    """
    import json

    from oteapi_aiida.strategies.aiidaresource import AiiDAResourceStrategy

    config = {
        "accessUrl": "http://localhost",
        "accessService": "AiiDA",
        "configuration": {

            "aiida_profile": {
                "profile_name": "oteapi2",
                "storage": {
                    "config": {
                        "database_name": "oteapi_thomas_456d55a3b5d8ef7f9e82ff83d1d35c5c",
                        "database_username": "aiida_qs_thomas_456d55a3b5d8ef7f9e82ff83d1d35c5c",
                        "database_password": "<SECRET>",
                    }
                }
            },
            "single_data_node_uuid" : "<ADD YOUR UUID>",

            "entity_url": "https://gist.githubusercontent.com/quaat/5aacd32351657c0f8f8c25a2de766417/raw/2e0ef76942822ac7af0478f872dadf4112c319e8/DLite-test"
        }
    }
    resource_initialize: "SessionUpdate" = AiiDAResourceStrategy(config).initialize()
    resource_get: "SessionUpdateAiiDAResource" = AiiDAResourceStrategy(config).get(
        resource_initialize
    )

    assert {**resource_initialize} == {}
    assert (resource_get.output['status'] == 'ok')
    assert (resource_get.uuid != None)

