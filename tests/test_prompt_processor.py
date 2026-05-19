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