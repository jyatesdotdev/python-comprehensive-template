from python_template.core.config import settings
from python_template.db.session import engine


def test_engine_echo_follows_settings():
    assert engine.echo == settings.DB_ECHO
