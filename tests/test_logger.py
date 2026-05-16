import pytest
from pathlib import Path
import json
from flowctl.logger import WorkflowLogger, LogEntry


def test_logger_creates_log_file():
    run_dir = Path("/tmp/test-logger-run")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    logger = WorkflowLogger("test-run", run_dir)
    logger.log_workflow_start(workflow="test-workflow", executor="EchoAdapter")
    
    log_file = run_dir / "execution.log"
    assert log_file.exists()
    
    log_file.unlink()
    run_dir.rmdir()


def test_logger_json_format():
    run_dir = Path("/tmp/test-logger-json")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    logger = WorkflowLogger("test-json", run_dir, log_level="INFO", log_format="json")
    logger.log_workflow_start(workflow="test", executor="EchoAdapter", initial_context={"key": "value"})
    logger.log_node_start("node1", "developer", "prompt.md", [], {"input": "data"})
    logger.log_node_end("node1", "completed", {"output": "result"})
    logger.log_workflow_end("completed")
    
    log_file = run_dir / "execution.log"
    content = log_file.read_text()
    lines = content.strip().split("\n")
    
    assert len(lines) == 4
    
    entry = json.loads(lines[0])
    assert entry["event"] == "workflow_start"
    assert entry["workflow"] == "test"
    assert entry["executor"] == "EchoAdapter"
    assert entry["inputs"] == {"key": "value"}
    
    entry = json.loads(lines[1])
    assert entry["event"] == "node_start"
    assert entry["node"] == "node1"
    assert entry["role"] == "developer"
    
    entry = json.loads(lines[2])
    assert entry["event"] == "node_end"
    assert entry["state"] == "completed"
    assert "duration_ms" in entry
    
    entry = json.loads(lines[3])
    assert entry["event"] == "workflow_end"
    assert entry["status"] == "completed"
    
    log_file.unlink()
    run_dir.rmdir()


def test_logger_text_format():
    run_dir = Path("/tmp/test-logger-text")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    logger = WorkflowLogger("test-text", run_dir, log_level="INFO", log_format="text")
    logger.log_workflow_start(workflow="test", executor="EchoAdapter")
    logger.log_node_start("node1", "developer", "prompt.md")
    logger.log_node_end("node1", "completed")
    
    log_file = run_dir / "execution.log"
    content = log_file.read_text()
    
    assert "[INFO] [workflow_start]" in content
    assert "[INFO] [node_start] node=node1" in content
    assert "[INFO] [node_end] node=node1 state=completed" in content
    
    log_file.unlink()
    run_dir.rmdir()


def test_logger_transition():
    run_dir = Path("/tmp/test-logger-trans")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    logger = WorkflowLogger("test-trans", run_dir, log_level="DEBUG", log_format="json")
    logger.log_transition("node1", "node2", "pass == 'yes'", matched=True)
    logger.log_transition("node1", "node3", "pass == 'no'", matched=False)
    
    log_file = run_dir / "execution.log"
    content = log_file.read_text()
    lines = content.strip().split("\n")
    
    entry = json.loads(lines[0])
    assert entry["event"] == "transition"
    assert entry["from_node"] == "node1"
    assert entry["to_node"] == "node2"
    assert entry["condition"] == "pass == 'yes'"
    assert entry["matched"] is True
    
    entry = json.loads(lines[1])
    assert entry["matched"] is False
    
    log_file.unlink()
    run_dir.rmdir()


def test_logger_error():
    run_dir = Path("/tmp/test-logger-err")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    logger = WorkflowLogger("test-err", run_dir, log_level="ERROR", log_format="json")
    logger.log_node_failure("node1", RuntimeError("Test error"))
    
    log_file = run_dir / "execution.log"
    content = log_file.read_text()
    
    entry = json.loads(content)
    assert entry["event"] == "node_failure"
    assert entry["state"] == "failed"
    assert entry["error"] == "Test error"
    assert entry["level"] == "ERROR"
    
    log_file.unlink()
    run_dir.rmdir()


def test_log_pause(tmp_path):
    from flowctl.logger import WorkflowLogger
    
    logger = WorkflowLogger("test-run", tmp_path, "INFO", "json")
    logger.log_pause("human_confirm_clarify")
    
    log_content = (tmp_path / "execution.log").read_text()
    assert "pause" in log_content
    assert "human_confirm_clarify" in log_content