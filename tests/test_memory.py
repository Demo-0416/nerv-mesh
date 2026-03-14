"""Tests for the memory store."""

from nerv_mesh.memory import MemoryStore


def test_empty_store_returns_no_context(tmp_path):
    store = MemoryStore(path=tmp_path / "mem.json")
    assert store.get_context() == ""


def test_add_and_retrieve_facts(tmp_path):
    store = MemoryStore(path=tmp_path / "mem.json", inject_limit=2)
    store.add_facts([
        {"content": "User prefers Python", "confidence": 0.9},
        {"content": "Project uses FastAPI", "confidence": 0.8},
        {"content": "Low confidence fact", "confidence": 0.1},
    ])
    context = store.get_context()
    assert "User prefers Python" in context
    assert "Project uses FastAPI" in context
    assert "Low confidence fact" not in context  # below inject_limit=2


def test_persistence_across_instances(tmp_path):
    path = tmp_path / "mem.json"
    store1 = MemoryStore(path=path)
    store1.add_facts([{"content": "persisted fact", "confidence": 0.9}])

    store2 = MemoryStore(path=path)
    assert "persisted fact" in store2.get_context()


def test_trim_to_max_facts(tmp_path):
    store = MemoryStore(path=tmp_path / "mem.json", max_facts=3)
    facts = [{"content": f"fact-{i}", "confidence": i * 0.1} for i in range(10)]
    store.add_facts(facts)
    assert len(store._facts) == 3
