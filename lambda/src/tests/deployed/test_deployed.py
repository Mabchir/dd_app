# -*- coding: utf-8 -*-
import json
import os
import structlog
import requests

import pytest
import yaml
from pytest import param

with open(f"{os.path.dirname(__file__)}/../../../samconfig.yaml", "rb") as f:
    samconfig_dict = yaml.safe_load(f)

logger = structlog.get_logger()

DEPLOY_ENV = os.getenv("DEPLOY_ENV", "default")
API_URL = os.getenv("API_URL", "<API_URL>")

sessions = [
    {
        "session_id": "get_session_success",
        "payload": {
            "httpMethod": "GET",
            "pathParameters": {"id": "test-session-id"},
        },
        "expected_body": json.dumps({
            "users": [
                {"name": "Seth", "role": "Wizard"},
                {"name": "Hank", "role": "Warrior"}
            ],
            "dialogue": []
        })
    },
    {
        "session_id": "get_session_not_found",
        "payload": {
            "httpMethod": "GET",
            "pathParameters": {"id": "non-existent-session"},
        },
        "expected_body": json.dumps({"error": "Session not found"})
    },
    {
        "session_id": "post_session_new",
        "payload": {
            "httpMethod": "POST",
            "pathParameters": {"id": "new-session-id"},
            "body": json.dumps({
                "users": [
                    {"name": "Seth", "role": "Wizard"},
                    {"name": "Hank", "role": "Warrior"}
                ],
                "user": "Seth",
                "msg": "I cast a fireball at the orc."
            })
        },
        "expected_body": '"The orc is engulfed in flames."'  # This is a placeholder. Actual response will vary.
    },
        {
        "session_id": "post_session_without_msg",
        "payload": {
            "httpMethod": "POST",
            "pathParameters": {"id": "new-session-id"},
            "body": json.dumps({
                "users": [
                    {"name": "Seth", "role": "Wizard"},
                    {"name": "Hank", "role": "Warrior"}
                ],
            })
        },
        "expected_body": '"Something about each user"'  # This is a placeholder. Actual response will vary.
    },
    {
        "session_id": "post_session_existing",
        "payload": {
            "httpMethod": "POST",
            "pathParameters": {"id": "existing-session-id"},
            "body": json.dumps({
                "user": "Hank",
                "msg": "I charge at the orc with my sword."
            })
        },
        "expected_body": '"You slash the orc, and it falls defeated."'  # This is a placeholder. Actual response will vary.
    },
    {
        "session_id": "post_invalid_method",
        "payload": {
            "httpMethod": "PUT",
            "pathParameters": {"id": "test-session-id"},
        },
        "expected_body": json.dumps({"error": "Method not allowed"})
    },
    {
        "session_id": "post_missing_parameters",
        "payload": {
            "httpMethod": "POST",
            "pathParameters": {"id": "test-session-id"},
            "body": json.dumps({"msg": "I look around."})
        },
        "expected_body": json.dumps({"error": "KeyError: 'user'"})  # Assuming this is the error message when 'user' is missing
    }
]


@pytest.mark.parametrize("session", [
    param(session, id=session["session_id"]) for session in sessions
])
def test_api(session):
    url = f"{API_URL}/{session['payload']['pathParameters']['id']}"
    method = session['payload']['httpMethod']
    
    logger.info("Sending request", url=url, method=method, session_id=session['session_id'])
    
    if method == 'GET':
        response = requests.get(url)
    elif method == 'POST':
        body = json.loads(session['payload'].get('body', '{}'))
        response = requests.post(url, json=body)
    else:
        response = requests.request(method, url)
    
    logger.info("Received response", 
                status_code=response.status_code, 
                content=response.text,
                session_id=session['session_id'])
    
    assert response.status_code == 200, f"Unexpected status code for session {session['session_id']}"
    
    logger.info(f"response.text: {response.text}")
