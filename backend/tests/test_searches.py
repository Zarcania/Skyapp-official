import pytest
from fastapi.testclient import TestClient

# Import the app from server_supabase
import importlib.util
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
mod_path = BACKEND_DIR / 'server_supabase.py'
spec = importlib.util.spec_from_file_location('server_supabase', str(mod_path))
server_supabase = importlib.util.module_from_spec(spec)
sys.modules['server_supabase'] = server_supabase
spec.loader.exec_module(server_supabase)

app = server_supabase.app
client = TestClient(app)

class DummyAuth:
    def __init__(self, user_id, role="TECHNICIEN", company_id="comp-1"):
        self.user_id = user_id
        self.role = role
        self.company_id = company_id

@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    async def fake_get_user_from_token(credentials=None):
        return {"id": "user-1", "email": "t@t.com", "role": "TECHNICIEN", "company_id": "comp-1"}
    monkeypatch.setattr(server_supabase, 'get_user_from_token', fake_get_user_from_token)

@pytest.fixture(autouse=True)
def mock_supabase_service(monkeypatch):
    class DummyQuery:
        def __init__(self):
            self._filters = []
            self._ordered = False
        def select(self, *args, **kwargs):
            return self
        def order(self, *args, **kwargs):
            self._ordered = True
            return self
        def eq(self, field, value):
            self._filters.append((field, value))
            return self
        def execute(self):
            # minimal fake data
            return type('Res', (), {"data": [{"id": "d1", "status": "DRAFT", "company_id": "comp-1", "user_id": "user-1"}]})
    class DummyService:
        def table(self, name):
            return DummyQuery()
    monkeypatch.setattr(server_supabase, 'supabase_service', DummyService())


def test_list_drafts():
    res = client.get('/api/searches', params={'status': 'DRAFT'})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert any(item.get('status') == 'DRAFT' for item in data)
