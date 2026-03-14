"""Tests for builtin, search, and web tools."""

from nerv_mesh.tools.builtin import file_edit, file_read
from nerv_mesh.tools.search import glob_search, grep_search

# ── file_edit ─────────────────────────────────────────────────────────────

def test_file_edit_basic(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world")
    result = file_edit.invoke({"path": str(f), "old_string": "world", "new_string": "nerv"})
    assert "Replaced" in result
    assert f.read_text() == "hello nerv"


def test_file_edit_not_found(tmp_path):
    result = file_edit.invoke({
        "path": str(tmp_path / "nope.txt"),
        "old_string": "a",
        "new_string": "b",
    })
    assert "not found" in result.lower()


def test_file_edit_not_unique(tmp_path):
    f = tmp_path / "dup.txt"
    f.write_text("aaa")
    result = file_edit.invoke({"path": str(f), "old_string": "a", "new_string": "b"})
    assert "3 times" in result


def test_file_edit_no_match(tmp_path):
    f = tmp_path / "miss.txt"
    f.write_text("hello")
    result = file_edit.invoke({"path": str(f), "old_string": "xyz", "new_string": "abc"})
    assert "not found" in result.lower()


# ── file_read with offset/limit ──────────────────────────────────────────

def test_file_read_with_offset(tmp_path):
    f = tmp_path / "lines.txt"
    f.write_text("line1\nline2\nline3\nline4\n")
    result = file_read.invoke({"path": str(f), "offset": 1, "limit": 2})
    assert "line2" in result
    assert "line3" in result
    assert "line1" not in result
    assert "line4" not in result


# ── grep_search ───────────────────────────────────────────────────────────

def test_grep_search_basic(tmp_path):
    (tmp_path / "a.py").write_text("def hello():\n    pass\n")
    (tmp_path / "b.py").write_text("def world():\n    pass\n")
    result = grep_search.invoke({"pattern": "def hello", "path": str(tmp_path)})
    assert "a.py" in result
    assert "hello" in result


def test_grep_search_with_include(tmp_path):
    (tmp_path / "a.py").write_text("match here")
    (tmp_path / "b.txt").write_text("match here too")
    result = grep_search.invoke({"pattern": "match", "path": str(tmp_path), "include": "*.py"})
    assert "a.py" in result
    assert "b.txt" not in result


def test_grep_search_no_match(tmp_path):
    (tmp_path / "a.py").write_text("nothing")
    result = grep_search.invoke({"pattern": "zzzzz", "path": str(tmp_path)})
    assert "No matches" in result


# ── glob_search ───────────────────────────────────────────────────────────

def test_glob_search_basic(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("")
    (tmp_path / "src" / "util.py").write_text("")
    (tmp_path / "readme.md").write_text("")
    result = glob_search.invoke({"pattern": "**/*.py", "path": str(tmp_path)})
    assert "main.py" in result
    assert "util.py" in result
    assert "readme.md" not in result


def test_glob_search_no_match(tmp_path):
    result = glob_search.invoke({"pattern": "*.xyz", "path": str(tmp_path)})
    assert "No files" in result
