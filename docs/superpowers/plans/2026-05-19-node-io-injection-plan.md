# Node Input/Output Injection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a PromptProcessor that dynamically injects input/output sections into prompts from node definitions.

**Architecture:** Separate processor component with regex-based section removal, Markdown generation, and executor integration. Minimal changes to existing code, no new dependencies.

**Tech Stack:** Python, regex (re module), Pydantic (existing), pytest (existing)

---

## File Structure

**Created files:**
- `src/flowctl/prompt_processor.py` - PromptProcessor implementation (single responsibility: transform prompts)
- `tests/test_prompt_processor.py` - Unit tests for processor

**Modified files:**
- `src/flowctl/executors/opencode.py` - Integration: import and call processor

**Optional cleanup (separate task after core implementation):**
- `.flows/prompts/*.md` - Remove manual Input/Output sections

---

### Task 1: Create PromptProcessor skeleton

**Files:**
- Create: `src/flowctl/prompt_processor.py`

- [ ] **Step 1: Create empty processor class with imports**

```python
import re
import logging
from typing import Optional
from flowctl.models import Node

logger = logging.getLogger(__name__)


class PromptProcessor:
    def process(self, node: Node, prompt_content: str) -> str:
        pass
    
    def _remove_existing_sections(self, content: str) -> str:
        pass
    
    def _generate_input_section(self, inputs: dict[str, str]) -> str:
        pass
    
    def _generate_output_section(self, outputs: dict[str, str]) -> str:
        pass
    
    def _should_process(self, node: Node) -> bool:
        pass
```

- [ ] **Step 2: Commit skeleton**

```bash
git add src/flowctl/prompt_processor.py
git commit -m "feat: add PromptProcessor skeleton for dynamic I/O injection"
```

---

### Task 2: Implement _should_process method

**Files:**
- Modify: `src/flowctl/prompt_processor.py:22-24`
- Create: `tests/test_prompt_processor.py`

- [ ] **Step 1: Write failing test for bash executor skip**

```python
import pytest
from flowctl.models import Node
from flowctl.prompt_processor import PromptProcessor


def test_should_process_skips_bash_executor():
    processor = PromptProcessor()
    node = Node(
        role="github",
        executor="bash",
        command="scripts/fetch-issue.sh"
    )
    
    result = processor._should_process(node)
    
    assert result is False


def test_should_process_returns_true_for_opencode():
    processor = PromptProcessor()
    node = Node(
        role="developer",
        prompt="prompts/implement.md",
        executor="opencode"
    )
    
    result = processor._should_process(node)
    
    assert result is True


def test_should_process_returns_true_for_human():
    processor = PromptProcessor()
    node = Node(
        role="human",
        prompt="prompts/human-confirm.md",
        executor="human"
    )
    
    result = processor._should_process(node)
    
    assert result is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_prompt_processor.py::test_should_process_skips_bash_executor -v`
Expected: FAIL with "AttributeError: 'NoneType' object has no attribute 'is False'"

Run: `uv run pytest tests/test_prompt_processor.py::test_should_process_returns_true_for_opencode -v`
Expected: FAIL with similar error

Run: `uv run pytest tests/test_prompt_processor.py::test_should_process_returns_true_for_human -v`
Expected: FAIL with similar error

- [ ] **Step 3: Implement _should_process**

```python
def _should_process(self, node: Node) -> bool:
    return node.executor != "bash"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_prompt_processor.py::test_should_process -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_prompt_processor.py src/flowctl/prompt_processor.py
git commit -m "feat: implement _should_process to skip bash nodes"
```

---

### Task 3: Implement _generate_input_section method

**Files:**
- Modify: `src/flowctl/prompt_processor.py:18-20`
- Modify: `tests/test_prompt_processor.py`

- [ ] **Step 1: Write failing test for input section generation**

```python
def test_generate_input_section_with_inputs():
    processor = PromptProcessor()
    inputs = {
        "requirement": "requirement.md",
        "architecture": "ARCHITECTURE.md"
    }
    
    result = processor._generate_input_section(inputs)
    
    expected = """## Input

- requirement: Read from requirement.md
- architecture: Read from ARCHITECTURE.md"""
    
    assert result == expected


def test_generate_input_section_empty():
    processor = PromptProcessor()
    inputs = {}
    
    result = processor._generate_input_section(inputs)
    
    assert result == ""


def test_generate_input_section_single_input():
    processor = PromptProcessor()
    inputs = {"clarify": "clarify.md"}
    
    result = processor._generate_input_section(inputs)
    
    expected = """## Input

- clarify: Read from clarify.md"""
    
    assert result == expected
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_prompt_processor.py::test_generate_input_section -v`
Expected: FAIL with "AssertionError" or empty string comparison

- [ ] **Step 3: Implement _generate_input_section**

```python
def _generate_input_section(self, inputs: dict[str, str]) -> str:
    if not inputs:
        return ""
    
    lines = ["## Input", ""]
    for key, filename in inputs.items():
        lines.append(f"- {key}: Read from {filename}")
    
    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_prompt_processor.py::test_generate_input_section -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_prompt_processor.py src/flowctl/prompt_processor.py
git commit -m "feat: implement _generate_input_section for dynamic inputs"
```

---

### Task 4: Implement _generate_output_section method

**Files:**
- Modify: `src/flowctl/prompt_processor.py:20-22`
- Modify: `tests/test_prompt_processor.py`

- [ ] **Step 1: Write failing test for output section generation**

```python
def test_generate_output_section_with_outputs():
    processor = PromptProcessor()
    outputs = {
        "design_md": "docs/design.md",
        "test_design_md": "docs/test-design.md"
    }
    
    result = processor._generate_output_section(outputs)
    
    expected = """## Output

- design_md: Write to docs/design.md
- test_design_md: Write to docs/test-design.md"""
    
    assert result == expected


def test_generate_output_section_empty():
    processor = PromptProcessor()
    outputs = {}
    
    result = processor._generate_output_section(outputs)
    
    assert result == ""


def test_generate_output_section_single_output():
    processor = PromptProcessor()
    outputs = {"implementation_md": "implementation.md"}
    
    result = processor._generate_output_section(outputs)
    
    expected = """## Output

- implementation_md: Write to implementation.md"""
    
    assert result == expected
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_prompt_processor.py::test_generate_output_section -v`
Expected: FAIL with "AssertionError"

- [ ] **Step 3: Implement _generate_output_section**

```python
def _generate_output_section(self, outputs: dict[str, str]) -> str:
    if not outputs:
        return ""
    
    lines = ["## Output", ""]
    for key, filename in outputs.items():
        lines.append(f"- {key}: Write to {filename}")
    
    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_prompt_processor.py::test_generate_output_section -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_prompt_processor.py src/flowctl/prompt_processor.py
git commit -m "feat: implement _generate_output_section for dynamic outputs"
```

---

### Task 5: Implement _remove_existing_sections method

**Files:**
- Modify: `src/flowctl/prompt_processor.py:14-16`
- Modify: `tests/test_prompt_processor.py`

- [ ] **Step 1: Write failing test for section removal**

```python
def test_remove_existing_sections_removes_input():
    processor = PromptProcessor()
    content = """# Design

## Input

Read the requirement.

## Task

Do something.
"""
    
    result = processor._remove_existing_sections(content)
    
    assert "## Input" not in result
    assert "Read the requirement" not in result
    assert "# Design" in result
    assert "## Task" in result


def test_remove_existing_sections_removes_output():
    processor = PromptProcessor()
    content = """# Test

## Output

Write to file.

## Task

Complete.
"""
    
    result = processor._remove_existing_sections(content)
    
    assert "## Output" not in result
    assert "Write to file" not in result
    assert "# Test" in result
    assert "## Task" in result


def test_remove_existing_sections_removes_both():
    processor = PromptProcessor()
    content = """# Prompt

## Input

Read input.

## Output

Write output.

## Task

Execute.
"""
    
    result = processor._remove_existing_sections(content)
    
    assert "## Input" not in result
    assert "## Output" not in result
    assert "Read input" not in result
    assert "Write output" not in result
    assert "# Prompt" in result
    assert "## Task" in result


def test_remove_existing_sections_no_sections():
    processor = PromptProcessor()
    content = """# Prompt

## Task

Just a task.
"""
    
    result = processor._remove_existing_sections(content)
    
    assert result == content


def test_remove_existing_sections_case_insensitive():
    processor = PromptProcessor()
    content = """# Test

## input

Some text.

## output

More text.

## Task
"""
    
    result = processor._remove_existing_sections(content)
    
    assert "## input" not in result
    assert "## output" not in result
    assert "Some text" not in result
    assert "More text" not in result


def test_remove_existing_sections_preserves_other_content():
    processor = PromptProcessor()
    content = """# Title

Some intro text.

## Input

Read this.

## Task

1. Step one
2. Step two

## Notes

Important notes.

## Output

Write that.
"""
    
    result = processor._remove_existing_sections(content)
    
    assert "# Title" in result
    assert "Some intro text" in result
    assert "## Task" in result
    assert "1. Step one" in result
    assert "## Notes" in result
    assert "Important notes" in result
    assert "## Input" not in result
    assert "## Output" not in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_prompt_processor.py::test_remove_existing_sections -v`
Expected: FAIL with "AssertionError"

- [ ] **Step 3: Implement _remove_existing_sections**

```python
def _remove_existing_sections(self, content: str) -> str:
    try:
        input_pattern = r'^## [Ii]nput.*?(?=^## |\Z)'
        output_pattern = r'^## [Oo]utput.*?(?=^## |\Z)'
        
        content = re.sub(input_pattern, '', content, flags=re.MULTILINE)
        content = re.sub(output_pattern, '', content, flags=re.MULTILINE)
        
        return content.strip()
    except Exception as e:
        logger.warning(f"Failed to remove existing sections: {e}")
        return content
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_prompt_processor.py::test_remove_existing_sections -v`
Expected: 6 PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_prompt_processor.py src/flowctl/prompt_processor.py
git commit -m "feat: implement _remove_existing_sections with regex"
```

---

### Task 6: Implement process method (main entry point)

**Files:**
- Modify: `src/flowctl/prompt_processor.py:10-12`
- Modify: `tests/test_prompt_processor.py`

- [ ] **Step 1: Write failing test for process method**

```python
def test_process_with_inputs_and_outputs():
    processor = PromptProcessor()
    node = Node(
        role="developer",
        prompt="prompts/test.md",
        inputs={"requirement": "requirement.md", "design": "docs/design.md"},
        outputs={"implementation": "implementation.md"}
    )
    prompt = "# Test\n\n## Task\n\nDo something."
    
    result = processor.process(node, prompt)
    
    assert result.startswith("## Input")
    assert "requirement: Read from requirement.md" in result
    assert "design: Read from docs/design.md" in result
    assert "## Output" in result
    assert "implementation: Write to implementation.md" in result
    assert "# Test" in result
    assert "## Task" in result


def test_process_removes_existing_sections():
    processor = PromptProcessor()
    node = Node(
        role="architect",
        prompt="prompts/design.md",
        inputs={"clarify": "clarify.md"},
        outputs={"design_md": "docs/design.md"}
    )
    prompt = """# Design

## Input

Read the clarify file manually.

## Output

Write design manually.

## Task

Create design.
"""
    
    result = processor.process(node, prompt)
    
    assert "Read the clarify file manually" not in result
    assert "Write design manually" not in result
    assert "clarify: Read from clarify.md" in result
    assert "design_md: Write to docs/design.md" in result


def test_process_skips_bash_executor():
    processor = PromptProcessor()
    node = Node(
        role="github",
        executor="bash",
        command="scripts/fetch-issue.sh",
        inputs={"issue_url": "issue-url.txt"},
        outputs={"requirement": "requirement.md"}
    )
    prompt = "# Fetch\n\n## Task\n\nFetch issue."
    
    result = processor.process(node, prompt)
    
    assert result == prompt
    assert "## Input" not in result
    assert "## Output" not in result


def test_process_empty_inputs_outputs():
    processor = PromptProcessor()
    node = Node(
        role="tester",
        prompt="prompts/test.md",
        inputs={},
        outputs={}
    )
    prompt = "# Test\n\n## Task\n\nRun tests."
    
    result = processor.process(node, prompt)
    
    assert "## Input" not in result
    assert "## Output" not in result
    assert "# Test" in result


def test_process_only_inputs():
    processor = PromptProcessor()
    node = Node(
        role="reader",
        prompt="prompts/read.md",
        inputs={"data": "data.md"},
        outputs={}
    )
    prompt = "# Read\n\n## Task\n\nRead data."
    
    result = processor.process(node, prompt)
    
    assert "## Input" in result
    assert "data: Read from data.md" in result
    assert "## Output" not in result


def test_process_only_outputs():
    processor = PromptProcessor()
    node = Node(
        role="writer",
        prompt="prompts/write.md",
        inputs={},
        outputs={"result": "result.md"}
    )
    prompt = "# Write\n\n## Task\n\nWrite result."
    
    result = processor.process(node, prompt)
    
    assert "## Input" not in result
    assert "## Output" in result
    assert "result: Write to result.md" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_prompt_processor.py::test_process -v`
Expected: FAIL with "AssertionError"

- [ ] **Step 3: Implement process method**

```python
def process(self, node: Node, prompt_content: str) -> str:
    if not self._should_process(node):
        return prompt_content
    
    try:
        cleaned_content = self._remove_existing_sections(prompt_content)
        
        input_section = self._generate_input_section(node.inputs)
        output_section = self._generate_output_section(node.outputs)
        
        sections = []
        if input_section:
            sections.append(input_section)
        if output_section:
            sections.append(output_section)
        
        if sections:
            header = "\n\n".join(sections)
            return f"{header}\n\n{cleaned_content}"
        
        return cleaned_content
    except Exception as e:
        logger.warning(f"Failed to process prompt for node: {e}")
        return prompt_content
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_prompt_processor.py::test_process -v`
Expected: 6 PASS

- [ ] **Step 5: Run all processor tests to verify everything passes**

Run: `uv run pytest tests/test_prompt_processor.py -v`
Expected: All tests pass (18 total tests)

- [ ] **Step 6: Commit**

```bash
git add tests/test_prompt_processor.py src/flowctl/prompt_processor.py
git commit -m "feat: implement process method with full integration"
```

---

### Task 7: Integrate PromptProcessor into OpencodeAdapter

**Files:**
- Read: `src/flowctl/executors/opencode.py`
- Modify: `src/flowctl/executors/opencode.py`

- [ ] **Step 1: Read OpencodeAdapter to understand current structure**

Run: Read the file to find `_load_prompt` method and imports section

- [ ] **Step 2: Add PromptProcessor import at top of opencode.py**

Find the imports section (after existing imports) and add:

```python
from flowctl.prompt_processor import PromptProcessor
```

- [ ] **Step 3: Initialize processor in OpencodeAdapter.__init__**

Find the `__init__` method and add initialization:

```python
def __init__(self, model: Optional[str] = None, agent: Optional[str] = None):
    self.model = model
    self.agent = agent
    self.processor = PromptProcessor()
```

- [ ] **Step 4: Modify _load_prompt to use processor**

Find the `_load_prompt` method. After reading the prompt file content, add processor call. The method should look like:

```python
def _load_prompt(self, prompt_path: str, node: Node) -> str:
    try:
        with open(prompt_path, 'r') as f:
            prompt_content = f.read()
        
        processed_prompt = self.processor.process(node, prompt_content)
        
        return processed_prompt
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {prompt_path}")
        raise
```

Note: Check if _load_prompt already passes `node` parameter. If not, update method signature and all call sites.

- [ ] **Step 5: Verify Node parameter is passed to _load_prompt**

Check the execute method in OpencodeAdapter to ensure node is passed when calling _load_prompt. If _load_prompt is called without node parameter, update the call site:

```python
prompt_content = self._load_prompt(prompt_path, executor_input.node)
```

Note: Check ExecutorInput model to verify it has a `node` field. If not, add it to ExecutorInput in `base.py`.

- [ ] **Step 6: Run existing executor tests to verify integration**

Run: `uv run pytest tests/test_executors.py -v`
Expected: All existing tests pass (no changes to test expectations)

- [ ] **Step 7: Commit integration**

```bash
git add src/flowctl/executors/opencode.py
git commit -m "feat: integrate PromptProcessor into OpencodeAdapter"
```

---

### Task 8: Run full test suite and verify

**Files:**
- None (verification step)

- [ ] **Step 1: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: All tests pass including new processor tests

- [ ] **Step 2: Run lint check**

Run: `uv run ruff check src/`
Expected: No errors

- [ ] **Step 3: Run type check (if mypy configured)**

Run: `uv run mypy src/flowctl/prompt_processor.py` (if applicable)
Expected: No type errors

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete node input/output injection feature"
```

---

### Task 9: Update example prompt (optional cleanup)

**Files:**
- Modify: `.flows/prompts/design.md`
- Modify: `.flows/prompts/implement.md`

- [ ] **Step 1: Remove manual Input/Output sections from design.md**

Remove the existing "## Input" and "## Output" sections from `.flows/prompts/design.md`, keeping only task-specific content:

```markdown
# Design Phase

You are the architect role. Create a technical design based on the clarified requirements.

## Task

1. Analyze the requirements and existing codebase structure
2. Design the technical solution including:
   - Architecture changes
   - New components/modules
   - API changes
   - Data model changes
3. Document the design

## Notes

Write the design document with:
- Overview
- Architecture diagram (if applicable)
- Component design
- Implementation plan
- Risk assessment
```

- [ ] **Step 2: Remove manual Input/Output sections from implement.md**

Remove the existing "## Input" section from `.flows/prompts/implement.md`:

```markdown
# Implement Phase

You are the developer role. Implement the code changes based on the design and test plan.

## Task

1. Create implementation plan in `implementation.md`
2. **Write/Edit actual code files** in the repo:
   - Use edit tool to modify existing files
   - Use write tool to create new files
   - Follow the design.md architecture
   - Ensure code is complete and functional
3. Write tests as specified in test-design.md
4. Run tests to verify implementation: `uv run pytest tests/ -v`
5. Commit changes with bash tool:
   - `git add -A`
   - `git commit -m "feat: implement <feature-name>"`

## Verification (REQUIRED)

After implementing, you MUST verify:
1. Run tests: `uv run pytest tests/ -v`
2. Run lint: `uv run ruff check .`
3. Run type check: `uv run mypy src/` (if applicable)

If any fail, FIX THEM before writing implementation.md.

## Output Format

Create two files:

1. `implementation.md` - Implementation plan with:
   - Files modified/created
   - Key code changes
   - Test coverage

2. `changes.md` - Summary of actual changes:
   - What was implemented
   - Files changed
   - Commit hash

## Important

- You MUST write/edit actual code files, not just plan
- Code must be complete and functional
- Tests must pass after implementation
- Commit after successful implementation
```

Note: The "## Output Format" section should remain - this describes what the output should look like, not the filename mapping.

- [ ] **Step 3: Commit cleanup**

```bash
git add .flows/prompts/design.md .flows/prompts/implement.md
git commit -m "docs: remove manual I/O sections from prompts"
```

---

## Summary

**Total tasks:** 9
**Total test cases:** 18 (in test_prompt_processor.py)
**Files created:** 2 (prompt_processor.py, test_prompt_processor.py)
**Files modified:** 2 (opencode.py, optional prompt cleanup)
**Commits:** 9

**Success criteria:**
- All unit tests pass
- All existing executor tests pass
- Full test suite passes
- Lint passes
- PromptProcessor correctly injects sections for opencode nodes
- Bash nodes skip processing
- Backward compatible with existing workflows