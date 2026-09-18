"""Small real-provider adapters. Test doubles live exclusively in tests."""
from dataclasses import dataclass
import json
from urllib.parse import quote

import httpx

from codebase.config import Settings
from codebase.state import TutorResponse


class ModelError(Exception):
    def __init__(self, code, retryable=False):
        super().__init__(code)  # Never propagate a provider body, URL query or key.
        self.code, self.retryable = code, retryable


@dataclass
class Completion:
    text: str
    usage: dict
    request_id: str | None = None


class ModelClient:
    def __init__(self, settings: Settings, transport=None):
        self.settings = settings
        self.transport = transport

    def complete(self, system, payload):
        s = self.settings
        if s.configuration_error():
            raise ModelError('configuration_missing')
        content = json.dumps(payload, ensure_ascii=False)
        schema = payload.get('response_schema', TutorResponse.model_json_schema())
        headers = {'Content-Type': 'application/json'}
        if s.provider == 'gemini':
            url = s.base_url.rstrip('/') + '/models/' + quote(s.model, safe='-_.') + ':generateContent'
            headers['x-goog-api-key'] = s.api_key.get_secret_value()
            body = {'systemInstruction': {'parts': [{'text': system}]},
                    'contents': [{'role': 'user', 'parts': [{'text': content}]}],
                    'generationConfig': {'responseMimeType': 'application/json',
                                         'maxOutputTokens': s.max_output_tokens}}
            if s.temperature is not None:
                body['generationConfig']['temperature'] = s.temperature
        else:
            url = s.base_url.rstrip('/') + '/chat/completions'
            if s.api_key.get_secret_value():
                headers['Authorization'] = 'Bearer ' + s.api_key.get_secret_value()
            body = {'model': s.model, 'messages': [{'role': 'system', 'content': system},
                                                  {'role': 'user', 'content': content}],
                    s.token_parameter: s.max_output_tokens}
            if s.response_format == 'json_schema':
                body['response_format'] = {'type': 'json_schema', 'json_schema':
                                          {'name': 'tutor_response', 'strict': True, 'schema': schema}}
            elif s.response_format == 'json_object':
                body['response_format'] = {'type': 'json_object'}
            if s.temperature is not None:
                body['temperature'] = s.temperature
        try:
            with httpx.Client(timeout=s.timeout, transport=self.transport, follow_redirects=False) as client:
                response = client.post(url, headers=headers, json=body)
        except httpx.TimeoutException:
            raise ModelError('provider_timeout', retryable=True) from None
        except httpx.HTTPError:
            raise ModelError('provider_connection', retryable=True) from None
        if response.status_code >= 300:
            raise ModelError(f'provider_http_{response.status_code}',
                             retryable=response.status_code == 429 or response.status_code >= 500)
        try:
            data = response.json()
            if s.provider == 'gemini':
                candidate = data['candidates'][0]
                if candidate.get('finishReason') != 'STOP':
                    raise ModelError('provider_incomplete')
                text = ''.join(p.get('text', '') for p in candidate['content']['parts'] if not p.get('thought'))
                return Completion(text, data.get('usageMetadata', {}), response.headers.get('x-request-id'))
            choice = data['choices'][0]
            if choice.get('finish_reason') != 'stop' or choice['message'].get('refusal'):
                raise ModelError('provider_incomplete_or_refusal')
            text = choice['message']['content']
            if not isinstance(text, str):
                raise ValueError('missing text')
            return Completion(text, data.get('usage', {}), response.headers.get('x-request-id') or data.get('id'))
        except (ValueError, KeyError, IndexError, TypeError):
            raise ModelError('provider_invalid_response', retryable=True) from None
