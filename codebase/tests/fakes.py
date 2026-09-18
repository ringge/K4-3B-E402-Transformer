"""Explicit UI test doubles; they do not evaluate model intent recognition."""
import json

from codebase.model_client import Completion


def routed_reply(reply, route='help'):
    def complete(system, payload):
        if payload['response_schema']['title'] == 'TurnRoute':
            return Completion(json.dumps({'intent': route, 'learner_quote': payload['user_input']}), {})
        return Completion(reply.model_dump_json(), {})
    return complete
