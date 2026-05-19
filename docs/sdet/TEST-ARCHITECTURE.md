# Test Architecture for SDET

## Overview

This document describes the testability architecture of flowctl for Software Development Engineers in Test (SDET). The architecture enables verification of prompt processing via dry-run without executing real AI agents.

## Testability Design

### Core Principle: Runner → Processor → Executor

```
┌─────────────────────────────────────────────────────────────────┐
│                         RUNNER                                  │
│  1. Load workflow definition                                    │
│  2. For each node:                                              │
│     a. Load prompt file                                         │
│     b. Call Processor.process()                                 │
│     c. Create ExecutorInput(prompt=processed_content)           │
│     d. Call Executor.execute()                                  │
│  3. Validate artifacts                                          │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐         ┌───────────┐        ┌───────────┐
    │ Loader  │         │ Processor │        │ Executor  │
    └─────────┘         └───────────┘        └───────────┘
                              │                    │
                              ▼                    ▼
                        ┌──────────┐         ┌──────────┐
                        │ Prompt   │         │ Echo     │ (dry-run)
                        │ Assembly │         │ Adapter  │
                        └──────────┘         └──────────┘
                                                   │
                                                   ▼
                                            ┌──────────┐
                                            │ stdout   │
                                            │ (visible │
                                            │ for test)│
                                            └──────────┘
```

### Key Testability Features

1. **Processor is external** - Called by Runner, not hidden inside Executor
2. **ExecutorInput receives processed content** - `prompt: str` (not `prompt_path: str`)
3. **EchoAdapter shows processed prompt** - Dry-run displays result in stdout
4. **Processor is a Protocol** - Can mock/replace for unit testing

## Test Strategies

### Level 1: Unit Tests (Processor)

**Location:** `tests/test_processor.py`

**What to test:**
- Section removal (Input/Output)
- Section generation from node.inputs/outputs
- Case-insensitive matching
- Bash executor skip logic
- Error handling (graceful degradation)

**Example test case:**

```python
# tests/sdet/test_processor_unit.py

from flowctl.processor import PromptProcessor
from flowctl.models import Node

class TestPromptProcessorUnit:
    """SDET unit tests for PromptProcessor."""
    
    def test_input_section_format(self):
        """Verify input section follows expected format."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"requirement": "req.md", "design": "design.md"},
            outputs={},
        )
        
        result = processor.process("# Task", {"node": node})
        
        # SDET: Verify exact format matches specification
        assert "## Input\n\n- requirement: Read from req.md\n- design: Read from design.md" in result
    
    def test_output_section_format(self):
        """Verify output section follows expected format."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={},
            outputs={"impl": "impl.md", "test": "test.md"},
        )
        
        result = processor.process("# Task", {"node": node})
        
        assert "## Output\n\n- impl: Write to impl.md\n- test: Write to test.md" in result
    
    def test_section_removes_existing_manual_content(self):
        """Verify manual I/O sections are completely removed."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"req": "req.md"},
            outputs={},
        )
        
        prompt = """
# Task

## Input

This is old manual input text that should be removed.
It may have multiple lines.

## Task

Actual task content.
"""
        
        result = processor.process(prompt, {"node": node})
        
        # SDET: Critical - old content must not leak into processed prompt
        assert "old manual input text" not in result
        assert "should be removed" not in result
    
    def test_bash_executor_nodes_skip_processing(self):
        """Verify bash executor nodes are not processed."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            executor="bash",  # Bash executor
            inputs={"req": "req.md"},
            outputs={"result": "result.md"},
        )
        
        prompt = "# Script Task"
        
        result = processor.process(prompt, {"node": node})
        
        # SDET: Bash nodes use scripts, not prompts - must skip
        assert result == "# Script Task"
        assert "## Input" not in result
        assert "## Output" not in result
    
    def test_empty_inputs_outputs_no_sections(self):
        """Verify no sections added when inputs/outputs are empty."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={},
            outputs={},
        )
        
        prompt = "# Task"
        
        result = processor.process(prompt, {"node": node})
        
        assert "## Input" not in result
        assert "## Output" not in result
        assert result == "# Task"
```

### Level 2: Integration Tests (Runner + Processor + EchoAdapter)

**Location:** `tests/test_runner.py`

**What to test:**
- End-to-end prompt assembly in dry-run
- Processor called by Runner
- EchoAdapter output format
- Workflow definition → processed prompt flow

**Example test case:**

```python
# tests/sdet/test_integration_dry_run.py

from flowctl.models import WorkflowDef, Node, Transition
from flowctl.runner import run_workflow
from pathlib import Path

class TestDryRunIntegration:
    """SDET integration tests for dry-run testability."""
    
    def test_dry_run_shows_processed_prompt_header(self, tmp_path):
        """Verify dry-run stdout contains PROCESSED PROMPT marker."""
        wf = WorkflowDef(
            version="1",
            nodes={
                "test_node": Node(
                    role="developer",
                    prompt="test.md",
                    inputs={"req": "req.md"},
                    outputs={"result": "result.md"},
                ),
            },
            transitions=[
                Transition(from_="__start__", to="test_node"),
                Transition(from_="test_node", to="__end__"),
            ],
            roles={},
        )
        
        workflow_dir = tmp_path / "workflow"
        workflow_dir.mkdir()
        (workflow_dir / "test.md").write_text("# Task\n\n## Task\n\nDo work.")
        
        run_dir = tmp_path / "run"
        
        result = run_workflow(wf, run_dir, dry_run=True, workflow_dir=workflow_dir)
        
        # SDET: Verify testability marker is present
        assert "PROCESSED PROMPT" in result.stdout
    
    def test_dry_run_shows_injected_input_section(self, tmp_path):
        """Verify injected Input section appears in dry-run stdout."""
        wf = WorkflowDef(
            version="1",
            nodes={
                "node": Node(
                    role="dev",
                    prompt="p.md",
                    inputs={"requirement": "requirement.md"},
                    outputs={},
                ),
            },
            transitions=[
                Transition(from_="__start__", to="node"),
                Transition(from_="node", to="__end__"),
            ],
            roles={},
        )
        
        workflow_dir = tmp_path / "wf"
        workflow_dir.mkdir()
        (workflow_dir / "p.md").write_text("# Task")
        
        result = run_workflow(wf, tmp_path / "run", dry_run=True, workflow_dir=workflow_dir)
        
        # SDET: Verify exact injected content
        assert "## Input" in result.stdout
        assert "requirement: Read from requirement.md" in result.stdout
    
    def test_dry_run_shows_injected_output_section(self, tmp_path):
        """Verify injected Output section appears in dry-run stdout."""
        wf = WorkflowDef(
            version="1",
            nodes={
                "node": Node(
                    role="dev",
                    prompt="p.md",
                    inputs={},
                    outputs={"design_md": "docs/design.md"},
                ),
            },
            transitions=[
                Transition(from_="__start__", to="node"),
                Transition(from_="node", to="__end__"),
            ],
            roles={},
        )
        
        workflow_dir = tmp_path / "wf"
        workflow_dir.mkdir()
        (workflow_dir / "p.md").write_text("# Task")
        
        result = run_workflow(wf, tmp_path / "run", dry_run=True, workflow_dir=workflow_dir)
        
        assert "## Output" in result.stdout
        assert "design_md: Write to docs/design.md" in result.stdout
    
    def test_dry_run_preserves_original_prompt_content(self, tmp_path):
        """Verify original prompt content is preserved after processing."""
        wf = WorkflowDef(
            version="1",
            nodes={
                "node": Node(
                    role="dev",
                    prompt="p.md",
                    inputs={"req": "req.md"},
                    outputs={"res": "res.md"},
                ),
            },
            transitions=[
                Transition(from_="__start__", to="node"),
                Transition(from_="node", to="__end__"),
            ],
            roles={},
        )
        
        workflow_dir = tmp_path / "wf"
        workflow_dir.mkdir()
        (workflow_dir / "p.md").write_text("""
# Design Task

## Notes

Important context here.

## Task

1. Analyze requirements
2. Create design
""")
        
        result = run_workflow(wf, tmp_path / "run", dry_run=True, workflow_dir=workflow_dir)
        
        # SDET: Original content must be preserved
        assert "# Design Task" in result.stdout
        assert "## Notes" in result.stdout
        assert "Important context here" in result.stdout
        assert "## Task" in result.stdout
        assert "Analyze requirements" in result.stdout
    
    def test_dry_run_removes_manual_io_sections(self, tmp_path):
        """Verify manual Input/Output sections are removed and replaced."""
        wf = WorkflowDef(
            version="1",
            nodes={
                "node": Node(
                    role="dev",
                    prompt="p.md",
                    inputs={"requirement": "requirement.md"},
                    outputs={"design": "design.md"},
                ),
            },
            transitions=[
                Transition(from_="__start__", to="node"),
                Transition(from_="node", to="__end__"),
            ],
            roles={},
        )
        
        workflow_dir = tmp_path / "wf"
        workflow_dir.mkdir()
        (workflow_dir / "p.md").write_text("""
# Task

## Input

OLD MANUAL INPUT - this should be removed.

## Output

OLD MANUAL OUTPUT - this should be removed.

## Task

Real task content.
""")
        
        result = run_workflow(wf, tmp_path / "run", dry_run=True, workflow_dir=workflow_dir)
        
        # SDET: Critical - manual sections must not leak
        assert "OLD MANUAL INPUT" not in result.stdout
        assert "OLD MANUAL OUTPUT" not in result.stdout
        
        # SDET: But injected sections should be present
        assert "requirement: Read from requirement.md" in result.stdout
        assert "design: Write to design.md" in result.stdout
```

### Level 3: E2E Tests (CLI + Full Workflow)

**Location:** `tests/sdet/test_e2e_cli.py`

**What to test:**
- `flowctl run --dry-run` CLI output
- Full workflow execution with multiple nodes
- Real workflow YAML files

**Example test case:**

```python
# tests/sdet/test_e2e_cli.py

from click.testing import CliRunner
from flowctl.cli import main
from pathlib import Path

class TestE2ECLI:
    """SDET E2E tests for CLI dry-run."""
    
    def test_cli_dry_run_shows_processed_prompt(self, tmp_path):
        """Verify CLI --dry-run shows processed prompt."""
        # Setup workflow
        workflow_dir = tmp_path / ".flows"
        workflow_dir.mkdir()
        
        workflows_dir = workflow_dir / "workflows"
        workflows_dir.mkdir()
        
        (workflows_dir / "test.yaml").write_text("""
version: "1"
nodes:
  test_node:
    role: developer
    prompt: prompts/test.md
    inputs:
      requirement: requirement.md
    outputs:
      result: result.md
transitions:
  - from: __start__
    to: test_node
  - from: test_node
    to: __end__
""")
        
        prompts_dir = workflow_dir / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "test.md").write_text("# Task\n\n## Task\n\nDo work.")
        
        # Run CLI
        cli_runner = CliRunner()
        result = cli_runner.invoke(
            main,
            ["run", "--dry-run", "--workflow-dir", str(workflow_dir)],
            catch_exceptions=False,
        )
        
        # SDET: Verify CLI output contains testability markers
        assert result.exit_code == 0
        assert "PROCESSED PROMPT" in result.output
        assert "requirement: Read from requirement.md" in result.output
    
    def test_cli_dry_run_multi_node_workflow(self, tmp_path):
        """Verify CLI --dry-run processes all nodes in workflow."""
        workflow_dir = tmp_path / ".flows"
        workflow_dir.mkdir()
        
        workflows_dir = workflow_dir / "workflows"
        workflows_dir.mkdir()
        
        (workflows_dir / "pipeline.yaml").write_text("""
version: "1"
nodes:
  node1:
    role: dev
    prompt: prompts/step1.md
    inputs:
      input: input.md
    outputs:
      intermediate: intermediate.md
  node2:
    role: dev
    prompt: prompts/step2.md
    inputs:
      intermediate: intermediate.md
    outputs:
      final: final.md
transitions:
  - from: __start__
    to: node1
  - from: node1
    to: node2
  - from: node2
    to: __end__
""")
        
        prompts_dir = workflow_dir / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "step1.md").write_text("# Step 1")
        (prompts_dir / "step2.md").write_text("# Step 2")
        
        cli_runner = CliRunner()
        result = cli_runner.invoke(
            main,
            ["run", "--dry-run", "--workflow-dir", str(workflow_dir)],
        )
        
        # SDET: Both nodes should be processed
        assert result.exit_code == 0
        # Both nodes' prompts should appear
        assert "# Step 1" in result.output or "Step 1" in result.output
        assert "# Step 2" in result.output or "Step 2" in result.output
```

## Test Case Directory Structure

```
tests/
├── sdet/                           # SDET-specific test cases
│   ├── test_processor_unit.py      # Level 1: Processor unit tests
│   ├── test_integration_dry_run.py # Level 2: Runner integration tests
│   ├── test_e2e_cli.py             # Level 3: CLI E2E tests
│   ├── test_edge_cases.py          # Edge case and error handling tests
│   └── test_performance.py         # Performance benchmarks
├── test_processor.py               # Existing processor tests
├── test_runner.py                  # Existing runner tests (includes integration)
├── test_executors.py               # Executor tests
└── ...
```

## Testability Checklist

When adding new features, verify:

| Feature | Testability Requirement |
|---------|------------------------|
| New processor | Unit tests in `tests/sdet/test_processor_unit.py` |
| Runner change | Integration test in `tests/sdet/test_integration_dry_run.py` |
| CLI change | E2E test in `tests/sdet/test_e2e_cli.py` |
| Edge case | Test in `tests/sdet/test_edge_cases.py` |

## Mocking Strategy

### Mocking Processor

```python
from unittest.mock import Mock
from flowctl.processor import Processor

def test_with_mock_processor():
    """Test Runner with mock processor."""
    mock_processor = Mock(spec=Processor)
    mock_processor.process.return_value = "Mock processed prompt"
    
    # Inject mock into Runner
    result = run_workflow(
        wf, 
        run_dir, 
        processor=mock_processor,  # If Runner accepts processor param
        dry_run=True,
    )
    
    # Verify mock was called
    mock_processor.process.assert_called_once()
```

### Mocking Executor

```python
from flowctl.executors import EchoAdapter

def test_with_mock_executor():
    """Test Runner with mock executor."""
    mock_executor = Mock(spec=EchoAdapter)
    mock_executor.execute.return_value = ExecutorResult(
        outputs={"result": "mock"},
        returncode=0,
        stdout="Mock output",
        stderr="",
    )
    
    result = run_workflow(wf, run_dir, adapter=mock_executor)
    
    mock_executor.execute.assert_called_once()
```

## Performance Testing

```python
# tests/sdet/test_performance.py

import time
from flowctl.processor import PromptProcessor
from flowctl.models import Node

class TestProcessorPerformance:
    """SDET performance benchmarks."""
    
    def test_processor_performance_large_prompt(self):
        """Benchmark processor with large prompt (1000+ lines)."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="large.md",
            inputs={"req": "req.md"},
            outputs={"result": "result.md"},
        )
        
        # Generate large prompt
        large_prompt = "\n".join([f"Line {i}" for i in range(1000)])
        
        start = time.perf_counter()
        for _ in range(100):  # 100 iterations
            result = processor.process(large_prompt, {"node": node})
        elapsed = time.perf_counter() - start
        
        # SDET: Must complete 100 iterations in < 1 second
        assert elapsed < 1.0
        assert "## Input" in result
    
    def test_processor_performance_many_inputs(self):
        """Benchmark processor with many inputs (50+ keys)."""
        processor = PromptProcessor()
        
        # Generate 50 inputs
        inputs = {f"input_{i}": f"file_{i}.md" for i in range(50)}
        node = Node(role="dev", prompt="test.md", inputs=inputs, outputs={})
        
        prompt = "# Task"
        
        start = time.perf_counter()
        result = processor.process(prompt, {"node": node})
        elapsed = time.perf_counter() - start
        
        # SDET: Must complete in < 100ms
        assert elapsed < 0.1
        assert all(f"input_{i}: Read from file_{i}.md" in result for i in range(50))
```

## Debugging Test Failures

### Common Issues

1. **"PROCESSED PROMPT" not in stdout**
   - Check: Is dry_run=True passed to run_workflow?
   - Check: Is EchoAdapter being used?

2. **Old manual sections still present**
   - Check: Regex patterns in `_remove_existing_sections`
   - Check: Case sensitivity (Input vs input)

3. **Injected sections missing**
   - Check: node.inputs/outputs are non-empty
   - Check: node.executor != "bash"

### Debug Commands

```bash
# Run dry-run and inspect output
flowctl run --dry-run --workflow-dir .flows

# Run specific SDET test
pytest tests/sdet/test_processor_unit.py -v

# Run all SDET tests
pytest tests/sdet/ -v

# Run with coverage
pytest tests/sdet/ --cov=flowctl.processor --cov=flowctl.runner
```

## SDET Test Workflow

### Dedicated Test Workflow

Location: `tests/sdet/workflows/sdet-dry-run-test.yaml`

**Purpose:** End-to-end test workflow specifically designed for SDET dry-run verification.

**Run Command:**

```bash
# Using run_id and workflow_dir
flowctl run --dry-run \
  --workflow-dir tests/sdet \
  --run-id sdet-test-001 \
  tests/sdet/workflows/sdet-dry-run-test.yaml

# Or use the SDET test script
./tests/sdet/run-dry-run-test.sh
```

**Test Cases:**

| Node | Test Case | Expected Behavior |
|------|-----------|-------------------|
| `test_basic_input` | Single input injection | `## Input` with one key |
| `test_basic_output` | Single output injection | `## Output` with one key |
| `test_multiple_inputs` | Multiple inputs (3) | All inputs in order |
| `test_multiple_outputs` | Multiple outputs (3) | All outputs in order |
| `test_both_io` | Both Input/Output | Both sections present |
| `test_section_removal` | Remove old sections | Old content NOT in output |
| `test_nested_paths` | Nested file paths | Paths preserved (docs/deep/) |
| `test_bash_skip` | Bash executor skip | Uses script, not prompt |
| `test_empty_io` | Empty inputs/outputs | No sections added |
| `test_integration` | Full integration | All features combined |

**Test Prompts:**

Location: `tests/sdet/prompts/test-*.md`

Each prompt includes:
- Purpose description
- Expected output specification
- Verification checklist
- Original content to preserve

**Test Artifacts:**

Location: `tests/sdet/test-artifacts/`

Input files created by test script for workflow nodes.

### SDET Test Script

Location: `tests/sdet/run-dry-run-test.sh`

**Usage:**

```bash
# Run SDET dry-run test suite
./tests/sdet/run-dry-run-test.sh

# Output saved to: tests/sdet/runs/<run-id>/dry-run-output.txt
```

**Script Parameters:**

- `--workflow-dir tests/sdet` - Points to SDET test workflow directory
- `--run-id sdet-test-YYYYMMDD-HHMMSS` - Unique run ID for results
- `--dry-run` - Mock execution mode

**Script Steps:**

1. **Create test artifacts** - Generate input files in `tests/sdet/test-artifacts/`
2. **Run dry-run** - Execute `flowctl run` with SDET workflow
3. **Verify results** - Check 10 test cases against expected output

**Verification Output:**

```
========================================
SDET Dry-Run Test Suite
========================================

Project Dir:  /path/to/project
SDET Dir:     /path/to/project/tests/sdet
Workflow Dir: /path/to/project/tests/sdet
Run ID:       sdet-test-20260519-140000
Results Dir:  /path/to/project/tests/sdet/runs/sdet-test-20260519-140000

Test 1: Basic Input Injection
  ✓ PASS: Input section injected

Test 2: Basic Output Injection
  ✓ PASS: Output section injected

...

========================================
Test Summary
========================================
Passed: 10
Failed: 0
Run ID: sdet-test-20260519-140000
Output: tests/sdet/runs/sdet-test-20260519-140000/dry-run-output.txt

✓ All SDET dry-run tests passed!
```

### Manual Test Commands

```bash
# Run SDET workflow in dry-run mode
flowctl run --dry-run --workflow-dir .flows --workflow sdet-dry-run-test

# View specific node output
flowctl run --dry-run --workflow-dir .flows --workflow sdet-dry-run-test | grep "test_basic_input"

# Check section removal
flowctl run --dry-run --workflow-dir .flows --workflow sdet-dry-run-test | grep -v "THIS IS OLD MANUAL"

# Verify nested paths preserved
flowctl run --dry-run --workflow-dir .flows --workflow sdet-dry-run-test | grep "docs/deep"
```

## SDET Test Directory Structure

```
tests/sdet/
├── workflows/
│   └── sdet-dry-run-test.yaml       # SDET test workflow (10 nodes)
├── prompts/
│   ├── sdet-base.md                 # Base role prompt
│   ├── test-basic-input.md          # Test 1 prompt
│   ├── test-basic-output.md         # Test 2 prompt
│   ├── test-multiple-inputs.md      # Test 3 prompt
│   ├── test-multiple-outputs.md     # Test 4 prompt
│   ├── test-both-io.md              # Test 5 prompt
│   ├── test-section-removal.md      # Test 6 prompt (has old sections)
│   ├── test-nested-paths.md         # Test 7 prompt
│   ├── test-empty-io.md             # Test 9 prompt
│   └── test-integration.md          # Test 10 prompt
├── test-artifacts/                   # Test input files (created by script)
│   ├── requirement.md
│   ├── architecture.md
│   ├── design.md
│   ├── input-a.md
│   ├── input-b.md
│   ├── input-c.md
│   ├── new-input.md
│   ├── script-input.md
│   └── docs/
│       └ deep/
│         └── input.md               # Nested input
├── runs/
│   └ sdet-test-YYYYMMDD-HHMMSS/     # Run results (by run_id)
│     └ dry-run-output.txt           # Captured test output
│     └ test-results/                # Mock output artifacts
│       ├── basic-input-result.md
│       ├── design.md
│       ├── impl.md
│       └ ...
├── run-dry-run-test.sh              # SDET test runner script
└── test_processor_unit.py           # Processor unit tests (21 tests)

scripts/
└── sdet-test-script.sh              # Bash executor test script (optional)
```

## Quick Start for SDETs

```bash
# 1. Run automated SDET test suite
./tests/sdet/run-dry-run-test.sh

# 2. Run pytest tests
pytest tests/sdet/test_processor_unit.py -v

# 3. Manual dry-run verification with run_id
flowctl run --dry-run \
  --workflow-dir tests/sdet \
  --run-id sdet-test-001 \
  tests/sdet/workflows/sdet-dry-run-test.yaml

# 4. Check specific feature
flowctl run --dry-run \
  --workflow-dir tests/sdet \
  --run-id sdet-test-002 \
  tests/sdet/workflows/sdet-dry-run-test.yaml | grep "## Input"

# 5. View results
cat tests/sdet/runs/sdet-test-*/dry-run-output.txt
```

## References

- **Architecture:** `ARCHITECTURE.md` - Section 4 (Processor System)
- **Design Spec:** `docs/superpowers/specs/2026-05-19-node-io-injection-design.md`
- **Implementation:** `src/flowctl/processor.py`, `src/flowctl/runner.py`
- **Example Tests:** `tests/test_processor.py`, `tests/test_runner.py::test_processor_in_dry_run_shows_assembled_prompt`
- **SDET Workflow:** `tests/sdet/workflows/sdet-dry-run-test.yaml`
- **SDET Script:** `tests/sdet/run-dry-run-test.sh`