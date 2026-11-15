import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env(path=ROOT / '.env'):
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())


@dataclass
class Settings:
    base_url: str = 'http://127.0.0.1:11434'
    chat_model: str = 'qwen2.5:1.5b'
    embed_model: str = 'nomic-embed-text'
    timeout: float = 120
    attempts: int = 3
    runtime: Path = ROOT / '.runtime'
    fallbacks: tuple = ()

    @classmethod
    def from_env(cls):
        load_env()
        return cls(
            base_url=os.getenv('OLLAMA_BASE_URL', cls.base_url).rstrip('/'),
            chat_model=os.getenv('CHAT_MODEL', cls.chat_model),
            embed_model=os.getenv('EMBED_MODEL', cls.embed_model),
            timeout=float(os.getenv('REQUEST_TIMEOUT', '120')),
            attempts=max(1, int(os.getenv('MAX_ATTEMPTS', '3'))),
            fallbacks=tuple(m.strip() for m in os.getenv('FALLBACK_MODELS', '').split(',') if m.strip()),
        )
