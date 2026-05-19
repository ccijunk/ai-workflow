import tempfile
from pathlib import Path
import pytest

from flowctl.executors.bash import BashExecutor
from flowctl.executors.base import ExecutorInput


SCRIPTS_DIR = Path(__file__).parent.parent / ".flows" / "scripts"


@pytest.fixture
def workflow_dir_with_mock_scripts(tmp_path):
    workflow_dir = tmp_path / ".flows"
    scripts_dir = workflow_dir / "scripts"
    scripts_dir.mkdir(parents=True)
    
    mock_fetch_issue = """#!/bin/bash
set -euo pipefail
ISSUE_URL="$1"
echo "# Mock Issue Title" > "$RUN_DIR/requirement.md"
echo "" >> "$RUN_DIR/requirement.md"
echo "Mock body content" >> "$RUN_DIR/requirement.md"
"""
    (scripts_dir / "fetch-issue.sh").write_text(mock_fetch_issue)
    (scripts_dir / "fetch-issue.sh").chmod(0o755)
    
    mock_create_branch = """#!/bin/bash
set -euo pipefail
REQUIREMENT="$1"
REPO_ROOT="$2"
ISSUE_URL="$3"
echo "issue-9" > "$RUN_DIR/branch-name.txt"
"""
    (scripts_dir / "create-branch.sh").write_text(mock_create_branch)
    (scripts_dir / "create-branch.sh").chmod(0o755)
    
    mock_create_pr = """#!/bin/bash
set -euo pipefail
REQUIREMENT="$1"
BRANCH_NAME="$2"
REPO_ROOT="$3"
echo "https://github.com/example/repo/pull/123" > "$RUN_DIR/pr-url.txt"
"""
    (scripts_dir / "create-pr.sh").write_text(mock_create_pr)
    (scripts_dir / "create-pr.sh").chmod(0o755)
    
    return workflow_dir


@pytest.fixture
def workflow_dir_with_real_scripts(tmp_path):
    workflow_dir = tmp_path / ".flows"
    scripts_dir = workflow_dir / "scripts"
    scripts_dir.mkdir(parents=True)
    
    for script_name in ["fetch-issue.sh", "create-branch.sh", "create-pr.sh"]:
        src = SCRIPTS_DIR / script_name
        if src.exists():
            dst = scripts_dir / script_name
            dst.write_text(src.read_text())
            dst.chmod(0o755)
    
    return workflow_dir


class TestFetchIssueScript:
    def test_fetch_issue_extracts_data(self, workflow_dir_with_mock_scripts):
        executor = BashExecutor(script_path="fetch-issue.sh", timeout_seconds=60)
        
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "issue-url.txt").write_text("https://github.com/example/repo/issues/9")
            
            inp = ExecutorInput(
                role="github",
                prompt="Fetch GitHub issue",
                prompt_path="",
                skill_paths=[],
                inputs={"issue_url": "issue-url.txt"},
                outputs={"requirement": "requirement.md"},
                run_dir=run_dir,
                workflow_dir=workflow_dir_with_mock_scripts,
            )
            
            result = executor.execute(inp)
            
            assert result.returncode == 0
            assert "requirement" in result.outputs
            
            requirement_content = result.outputs["requirement"]
            assert "# Mock Issue Title" in requirement_content
            assert "Mock body content" in requirement_content

    def test_fetch_issue_invalid_url(self, workflow_dir_with_real_scripts):
        executor = BashExecutor(script_path="fetch-issue.sh", timeout_seconds=60)
        
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "issue-url.txt").write_text("not-a-valid-url")
            
            inp = ExecutorInput(
                role="github",
                prompt="Fetch GitHub issue",
                prompt_path="",
                skill_paths=[],
                inputs={"issue_url": "issue-url.txt"},
                outputs={"requirement": "requirement.md"},
                run_dir=run_dir,
                workflow_dir=workflow_dir_with_real_scripts,
            )
            
            with pytest.raises(RuntimeError, match="exit code"):
                executor.execute(inp)

    def test_fetch_issue_missing_input(self, workflow_dir_with_mock_scripts):
        executor = BashExecutor(script_path="fetch-issue.sh", timeout_seconds=60)
        
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            
            inp = ExecutorInput(
                role="github",
                prompt="Fetch GitHub issue",
                prompt_path="",
                skill_paths=[],
                inputs={"issue_url": "missing.txt"},
                outputs={"requirement": "requirement.md"},
                run_dir=run_dir,
                workflow_dir=workflow_dir_with_mock_scripts,
            )
            
            result = executor.execute(inp)
            assert result.returncode == 0


class TestCreateBranchScript:
    def test_create_branch_parses_issue(self, workflow_dir_with_mock_scripts):
        executor = BashExecutor(script_path="create-branch.sh", timeout_seconds=60)
        
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            
            (run_dir / "requirement.md").write_text("# Test requirement")
            (run_dir / "repo-root.txt").write_text("/tmp")
            (run_dir / "issue-url.txt").write_text("https://github.com/example/repo/issues/9")
            
            inp = ExecutorInput(
                role="github",
                prompt="Create branch from issue",
                prompt_path="",
                skill_paths=[],
                inputs={
                    "requirement": "requirement.md",
                    "repo_root": "repo-root.txt",
                    "issue_url": "issue-url.txt",
                },
                outputs={"branch_name": "branch-name.txt"},
                run_dir=run_dir,
                workflow_dir=workflow_dir_with_mock_scripts,
            )
            
            result = executor.execute(inp)
            
            assert result.returncode == 0
            assert "branch_name" in result.outputs
            assert "issue-9" in result.outputs["branch_name"]

    def test_create_branch_missing_repo_root(self, workflow_dir_with_real_scripts):
        executor = BashExecutor(script_path="create-branch.sh", timeout_seconds=60)
        
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            
            (run_dir / "requirement.md").write_text("# Test requirement")
            (run_dir / "issue-url.txt").write_text("https://github.com/example/repo/issues/9")
            
            inp = ExecutorInput(
                role="github",
                prompt="Create branch from issue",
                prompt_path="",
                skill_paths=[],
                inputs={
                    "requirement": "requirement.md",
                    "repo_root": "missing.txt",
                    "issue_url": "issue-url.txt",
                },
                outputs={"branch_name": "branch-name.txt"},
                run_dir=run_dir,
                workflow_dir=workflow_dir_with_real_scripts,
            )
            
            with pytest.raises(RuntimeError, match="exit code"):
                executor.execute(inp)


class TestCreatePRScript:
    def test_create_pr_writes_output(self, workflow_dir_with_mock_scripts):
        executor = BashExecutor(script_path="create-pr.sh", timeout_seconds=60)
        
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            
            (run_dir / "requirement.md").write_text("# Add feature")
            (run_dir / "branch-name.txt").write_text("issue-9")
            (run_dir / "repo-root.txt").write_text("/tmp")
            
            inp = ExecutorInput(
                role="github",
                prompt="Create pull request",
                prompt_path="",
                skill_paths=[],
                inputs={
                    "requirement": "requirement.md",
                    "branch_name": "branch-name.txt",
                    "repo_root": "repo-root.txt",
                },
                outputs={"pr_url": "pr-url.txt"},
                run_dir=run_dir,
                workflow_dir=workflow_dir_with_mock_scripts,
            )
            
            result = executor.execute(inp)
            
            assert result.returncode == 0
            assert "pr_url" in result.outputs
            assert "https://github.com" in result.outputs["pr_url"]

    def test_create_pr_missing_branch_name(self, workflow_dir_with_real_scripts):
        executor = BashExecutor(script_path="create-pr.sh", timeout_seconds=60)
        
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            
            (run_dir / "requirement.md").write_text("# Add feature")
            (run_dir / "repo-root.txt").write_text("/tmp")
            
            inp = ExecutorInput(
                role="github",
                prompt="Create pull request",
                prompt_path="",
                skill_paths=[],
                inputs={
                    "requirement": "requirement.md",
                    "branch_name": "missing.txt",
                    "repo_root": "repo-root.txt",
                },
                outputs={"pr_url": "pr-url.txt"},
                run_dir=run_dir,
                workflow_dir=workflow_dir_with_real_scripts,
            )
            
            with pytest.raises(RuntimeError, match="exit code"):
                executor.execute(inp)