from pathlib import Path
from typing import Literal
from urllib.parse import urlparse
import os

from dotenv import dotenv_values
from pydantic import BaseModel, Field, SecretStr

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseModel):
    provider: Literal['compatible', 'gemini', 'ollama'] = 'compatible'
    base_url: str = 'https://api.openai.com/v1'
    model: str = ''
    api_key: SecretStr = SecretStr('')
    response_format: Literal['json_schema', 'json_object', 'none'] = 'json_object'
    temperature: float | None = None
    timeout: float = Field(default=45, gt=0, le=120)
    max_output_tokens: int = Field(default=2200, ge=256, le=8192)
    token_parameter: Literal['max_completion_tokens', 'max_tokens'] = 'max_completion_tokens'
    source_path: Path = ROOT / 'data/d1-slide-hackathon.html'

    @classmethod
    def from_env(cls):
        # Reread on every setup; changing .env doesn't mutate or expose process env.
        env = {**dotenv_values(ROOT / '.env'), **os.environ}
        provider = env.get('TUTOR_PROVIDER', 'compatible')
        default_url = {'gemini': 'https://generativelanguage.googleapis.com/v1beta',
                       'ollama': 'http://localhost:11434/v1'}.get(provider, 'https://api.openai.com/v1')
        key = env.get('TUTOR_API_KEY') or env.get('GEMINI_API_KEY' if provider == 'gemini' else 'OPENAI_API_KEY', '')
        source = Path(env.get('TUTOR_SOURCE') or 'data/d1-slide-hackathon.html')
        base_url = (env.get('TUTOR_BASE_URL') or env.get('OPENAI_BASE_URL') or default_url).rstrip('/')
        if provider in {'compatible', 'ollama'} and not urlparse(base_url).path:
            base_url += '/v1'
        return cls(provider=provider, base_url=base_url,
                   model=env.get('TUTOR_MODEL') or env.get('OPENAI_MODEL', ''), api_key=key,
                   response_format=env.get('TUTOR_RESPONSE_FORMAT') or 'json_object',
                   temperature=float(env['TUTOR_TEMPERATURE']) if env.get('TUTOR_TEMPERATURE') else None,
                   timeout=float(env.get('TUTOR_TIMEOUT_SECONDS') or 45),
                   max_output_tokens=int(env.get('TUTOR_MAX_OUTPUT_TOKENS') or 2200),
                   token_parameter=env.get('TUTOR_TOKEN_PARAMETER') or 'max_completion_tokens',
                   source_path=source if source.is_absolute() else ROOT / source)

    def configuration_error(self):
        if not self.model.strip():
            return 'Cần cấu hình TUTOR_MODEL trong .env.'
        if self.provider != 'ollama' and not self.api_key.get_secret_value():
            return 'Cần cấu hình TUTOR_API_KEY trong .env.'
        u = urlparse(self.base_url)
        if u.username or u.password or u.query or u.fragment:
            return 'Base URL không được chứa thông tin đăng nhập, query hoặc fragment.'
        if u.scheme != 'https' and not (u.scheme == 'http' and u.hostname in {'localhost', '127.0.0.1', '::1'}):
            return 'API phải dùng HTTPS (HTTP chỉ dành cho localhost).'
        if self.provider == 'gemini' and u.hostname != 'generativelanguage.googleapis.com':
            return 'Gemini native cần endpoint generativelanguage.googleapis.com.'
        return None

    def public(self):
        return self.model_dump(mode='json', exclude={'api_key', 'source_path'})
