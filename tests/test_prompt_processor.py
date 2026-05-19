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