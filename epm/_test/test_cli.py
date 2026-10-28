"""Tests for `epm.cli`"""

import pytest

import epm
from epm import cli

@pytest.fixture
def pip_calls(monkeypatch):
    """Record pip commands instead of running them"""
    calls = []
    def fake(*args):
        calls.append(list(args))
        return 0
    monkeypatch.setattr(cli,"_pip",fake)
    return calls

def test_version(capsys):
    assert cli.main(["--version"]) == cli.E_OK
    assert capsys.readouterr().out.strip() == epm.__version__

def test_help_option(capsys):
    assert cli.main(["--help"]) == cli.E_OK
    out = capsys.readouterr().out
    for command in cli.COMMANDS:
        assert command in out

def test_no_command():
    assert cli.main([]) == cli.E_SYNTAX

def test_invalid_command():
    assert cli.main(["open","epm"]) == cli.E_SYNTAX

def test_index(catalog,capsys): # pylint: disable=unused-argument
    assert cli.main(["index"]) == cli.E_OK
    out = capsys.readouterr().out
    assert "released" in out and "unreleased" not in out
    assert cli.main(["index","--all"]) == cli.E_OK
    assert "unreleased" in capsys.readouterr().out

def test_index_pattern(catalog,capsys): # pylint: disable=unused-argument
    assert cli.main(["index","-a","unrel"]) == cli.E_OK
    rows = capsys.readouterr().out.splitlines()[2:]
    assert [x.split()[0] for x in rows] == ["unreleased"]

def test_install(catalog,pip_calls): # pylint: disable=unused-argument
    assert cli.main(["install","released"]) == cli.E_OK
    assert pip_calls == [["install","git+https://github.com/eudoxys/released"]]

def test_upgrade(catalog,pip_calls): # pylint: disable=unused-argument
    assert cli.main(["upgrade","released"]) == cli.E_OK
    assert pip_calls == [["install","--upgrade","git+https://github.com/eudoxys/released"]]

def test_install_requires_name(catalog,pip_calls): # pylint: disable=unused-argument
    assert cli.main(["install"]) == cli.E_SYNTAX
    assert not pip_calls

def test_install_not_found(catalog,pip_calls,capsys): # pylint: disable=unused-argument
    assert cli.main(["install","missing"]) == cli.E_NOTFOUND
    assert "no packages match 'missing'" in capsys.readouterr().err
    assert not pip_calls

def test_install_failed(catalog,monkeypatch): # pylint: disable=unused-argument
    monkeypatch.setattr(cli,"_pip",lambda *args: 1)
    assert cli.main(["install","released"]) == cli.E_FAILED

def test_list(catalog,monkeypatch,capsys): # pylint: disable=unused-argument
    monkeypatch.setattr(cli,"_installed",lambda: {"released":"1.2.3","numpy":"2.0"})
    assert cli.main(["list"]) == cli.E_OK
    assert capsys.readouterr().out.splitlines() == ["released 1.2.3"]

def test_uninstall(catalog,monkeypatch,pip_calls): # pylint: disable=unused-argument
    monkeypatch.setattr(cli,"_installed",lambda: {"released":"1.2.3"})
    assert cli.main(["uninstall","released"]) == cli.E_OK
    assert pip_calls == [["uninstall","-y","released"]]

def test_uninstall_not_installed(catalog,monkeypatch,pip_calls): # pylint: disable=unused-argument
    monkeypatch.setattr(cli,"_installed",dict)
    assert cli.main(["uninstall","released"]) == cli.E_FAILED
    assert cli.main(["uninstall","numpy"]) == cli.E_FAILED # not a Eudoxys package
    assert not pip_calls

def test_exception(monkeypatch,capsys):
    def fail(args):
        raise RuntimeError("boom")
    monkeypatch.setitem(cli._COMMANDS,"index",fail) # pylint: disable=protected-access
    assert cli.main(["index"]) == cli.E_EXCEPTION
    assert "ERROR [epm]: RuntimeError boom" in capsys.readouterr().err
    with pytest.raises(RuntimeError):
        cli.main(["index","--debug"])

@pytest.mark.parametrize("older,newer",[
    ("0.9.1","0.10.0"),
    ("1.2","1.2.1"),
    ("1.0.0rc1","1.0.0"),
    ("0.0.0","0.0.1"),
    ("26.9.0","26.10.0"),
    ])
def test_version_key(older,newer):
    assert cli._version_key(older) < cli._version_key(newer) # pylint: disable=protected-access

def test_version_key_equal():
    assert cli._version_key("1.2") == cli._version_key("1.2.0") # pylint: disable=protected-access

def test_checkup(catalog,monkeypatch,capsys): # pylint: disable=unused-argument
    monkeypatch.setattr(cli,"_installed",lambda: {"released":"1.2.0","numpy":"0.1"})
    assert cli.main(["checkup"]) == cli.E_OK
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split() == ["Product","Installed","Latest"]
    assert [x.split() for x in lines[2:]] == [["released","1.2.0","1.2.3"]]

def test_checkup_up_to_date(catalog,monkeypatch,pip_calls,capsys): # pylint: disable=unused-argument
    monkeypatch.setattr(cli,"_installed",lambda: {"released":"1.2.3","unreleased":"0.0.0"})
    assert cli.main(["checkup"]) == cli.E_OK
    assert capsys.readouterr().out == ""
    assert not pip_calls

def test_checkup_pattern(catalog,monkeypatch,capsys): # pylint: disable=unused-argument
    monkeypatch.setattr(cli,"_installed",lambda: {"released":"1.0","noproject":"0.1"})
    assert cli.main(["checkup","no"]) == cli.E_OK # no pyproject.toml -> skipped
    assert capsys.readouterr().out == ""
