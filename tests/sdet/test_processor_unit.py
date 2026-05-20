"""SDET Unit Tests for PromptProcessor.

These tests verify the PromptProcessor component at the unit level,
focusing on input/output section generation, removal, and edge cases.
"""

import pytest
from flowctl.processor import PromptProcessor
from flowctl.models import Node


class TestPromptProcessorInputSection:
    """Tests for Input section generation."""
    
    def test_single_input_correct_format(self):
        """Verify single input follows exact format."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"requirement": "requirement.md"},
            outputs={},
        )
        
        result = processor.process("# Task", {"node": node})
        
        expected = "## Input\n\n- requirement: Read from requirement.md"
        assert expected in result
    
    def test_multiple_inputs_ordered(self):
        """Verify multiple inputs appear in declaration order."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={
                "requirement": "requirement.md",
                "architecture": "ARCHITECTURE.md",
                "design": "design.md",
            },
            outputs={},
        )
        
        result = processor.process("# Task", {"node": node})
        
        lines = result.split("\n")
        input_section_start = lines.index("## Input")
        
        # SDET: Verify order matches definition
        assert lines[input_section_start + 2] == "- requirement: Read from requirement.md (run_dir: requirement.md)"
        assert lines[input_section_start + 3] == "- architecture: Read from ARCHITECTURE.md (run_dir: ARCHITECTURE.md)"
        assert lines[input_section_start + 4] == "- design: Read from design.md (run_dir: design.md)"
    
    def test_input_with_nested_path(self):
        """Verify input with nested path preserves full path."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"design": "docs/architecture/design.md"},
            outputs={},
        )
        
        result = processor.process("# Task", {"node": node})
        
        assert "design: Read from docs/architecture/design.md" in result


class TestPromptProcessorOutputSection:
    """Tests for Output section generation."""
    
    def test_single_output_correct_format(self):
        """Verify single output follows exact format."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={},
            outputs={"implementation": "impl.md"},
        )
        
        result = processor.process("# Task", {"node": node})
        
        expected = "## Output\n\n- implementation: Write to impl.md"
        assert expected in result
    
    def test_output_with_nested_path(self):
        """Verify output with nested path preserves full path."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={},
            outputs={"design_md": "docs/design.md"},
        )
        
        result = processor.process("# Task", {"node": node})
        
        assert "design_md: Write to docs/design.md" in result


class TestPromptProcessorSectionRemoval:
    """Tests for removal of existing Input/Output sections."""
    
    def test_removes_existing_input_section(self):
        """Verify existing Input section is completely removed."""
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

Old manual input that should be removed.

## Task

Actual content.
"""
        
        result = processor.process(prompt, {"node": node})
        
        # SDET: Critical - old content must not leak
        assert "Old manual input" not in result
        assert "should be removed" not in result
    
    def test_removes_existing_output_section(self):
        """Verify existing Output section is completely removed."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={},
            outputs={"result": "result.md"},
        )
        
        prompt = """
# Task

## Output

Old manual output that should be removed.

## Task

Actual content.
"""
        
        result = processor.process(prompt, {"node": node})
        
        assert "Old manual output" not in result
    
    def test_removes_both_sections(self):
        """Verify both Input and Output sections are removed."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"in": "in.md"},
            outputs={"out": "out.md"},
        )
        
        prompt = """
## Input

Old input.

## Output

Old output.

## Task

Content.
"""
        
        result = processor.process(prompt, {"node": node})
        
        assert "Old input" not in result
        assert "Old output" not in result
        assert "in: Read from in.md" in result
        assert "out: Write to out.md" in result
    
    def test_case_insensitive_removal(self):
        """Verify removal works for case variations."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"req": "req.md"},
            outputs={},
        )
        
        # Test lowercase
        prompt_lower = """
## input

Old content.

## task

Content.
"""
        result_lower = processor.process(prompt_lower, {"node": node})
        assert "Old content" not in result_lower
        
        # Test uppercase
        prompt_upper = """
## INPUT

Old content.

## TASK

Content.
"""
        result_upper = processor.process(prompt_upper, {"node": node})
        assert "Old content" not in result_upper
    
    def test_preserves_other_sections(self):
        """Verify other sections (Notes, Context, etc.) are preserved."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"req": "req.md"},
            outputs={},
        )
        
        prompt = """
# Task

## Notes

Important context.

## Context

Additional info.

## Task

Do work.
"""
        
        result = processor.process(prompt, {"node": node})
        
        assert "## Notes" in result
        assert "Important context" in result
        assert "## Context" in result
        assert "Additional info" in result


class TestPromptProcessorBashExecutor:
    """Tests for bash executor skip logic."""
    
    def test_bash_executor_skips_processing(self):
        """Verify bash executor nodes are not processed."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            executor="bash",
            command="scripts/test.sh",  # Required for bash executor
            inputs={"req": "req.md"},
            outputs={"result": "result.md"},
        )
        
        prompt = "# Script Task"
        
        result = processor.process(prompt, {"node": node})
        
        assert result == "# Script Task"
        assert "## Input" not in result
        assert "## Output" not in result
    
    def test_opencode_executor_is_processed(self):
        """Verify opencode executor nodes are processed."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            executor="opencode",
            inputs={"req": "req.md"},
            outputs={},
        )
        
        prompt = "# Task"
        
        result = processor.process(prompt, {"node": node})
        
        assert "## Input" in result
        assert "req: Read from req.md" in result
    
    def test_echo_executor_is_processed(self):
        """Verify echo executor nodes are processed."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            executor="echo",
            inputs={"req": "req.md"},
            outputs={},
        )
        
        prompt = "# Task"
        
        result = processor.process(prompt, {"node": node})
        
        assert "## Input" in result


class TestPromptProcessorEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_inputs_no_input_section(self):
        """Verify no Input section when inputs is empty."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={},
            outputs={"result": "result.md"},
        )
        
        prompt = "# Task"
        
        result = processor.process(prompt, {"node": node})
        
        assert "## Input" not in result
        assert "## Output" in result
    
    def test_empty_outputs_no_output_section(self):
        """Verify no Output section when outputs is empty."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"req": "req.md"},
            outputs={},
        )
        
        prompt = "# Task"
        
        result = processor.process(prompt, {"node": node})
        
        assert "## Input" in result
        assert "## Output" not in result
    
    def test_empty_inputs_and_outputs(self):
        """Verify no sections when both are empty."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={},
            outputs={},
        )
        
        prompt = "# Task"
        
        result = processor.process(prompt, {"node": node})
        
        assert result == "# Task"
        assert "## Input" not in result
        assert "## Output" not in result
    
    def test_no_node_in_context(self):
        """Verify returns original when no node in context."""
        processor = PromptProcessor()
        
        prompt = "# Task"
        
        result = processor.process(prompt, {})
        
        assert result == "# Task"
    
    def test_null_node_in_context(self):
        """Verify returns original when node is None."""
        processor = PromptProcessor()
        
        prompt = "# Task"
        
        result = processor.process(prompt, {"node": None})
        
        assert result == "# Task"
    
    def test_null_content(self):
        """Verify graceful handling of null content."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"req": "req.md"},
            outputs={},
        )
        
        result = processor.process(None, {"node": node})
        
        # SDET: Must return gracefully, not crash
        assert result == None
    
    def test_preserves_original_after_sections(self):
        """Verify original content after injected sections."""
        processor = PromptProcessor()
        node = Node(
            role="dev",
            prompt="test.md",
            inputs={"req": "req.md"},
            outputs={"result": "result.md"},
        )
        
        prompt = """
# Design Task

## Task

1. Analyze requirements
2. Create design
"""
        
        result = processor.process(prompt, {"node": node})
        
        # SDET: Structure: Input → Output → Original
        assert "# Design Task" in result
        assert "## Task" in result
        assert "Analyze requirements" in result


class TestPromptProcessorIntegration:
    """Integration tests combining multiple features."""
    
    def test_full_workflow_prompt_processing(self):
        """Verify complete processing with all features."""
        processor = PromptProcessor()
        node = Node(
            role="architect",
            prompt="prompts/design.md",
            inputs={
                "requirement": "requirement.md",
                "architecture": "ARCHITECTURE.md",
            },
            outputs={
                "design_md": "docs/design.md",
                "test_design_md": "docs/test-design.md",
            },
        )
        
        prompt = """
# Design Phase

## Input

This is old manual input - remove me.

## Notes

Important architecture constraints.

## Task

1. Analyze requirements
2. Create design document
3. Create test design
"""
        
        result = processor.process(prompt, {"node": node})
        
        # SDET: Verify complete transformation
        # 1. Old sections removed
        assert "old manual input" not in result
        assert "remove me" not in result
        
        # 2. New sections injected
        assert "## Input\n\n- requirement: Read from requirement.md" in result
        assert "- architecture: Read from ARCHITECTURE.md" in result
        assert "## Output\n\n- design_md: Write to docs/design.md" in result
        assert "- test_design_md: Write to docs/test-design.md" in result
        
        # 3. Original preserved
        assert "# Design Phase" in result
        assert "## Notes" in result
        assert "Important architecture constraints" in result
        assert "## Task" in result
        assert "Analyze requirements" in result
        
        # 4. Structure correct (Input → Output → Original)
        lines = result.split("\n")
        input_idx = lines.index("## Input")
        output_idx = lines.index("## Output")
        original_task_idx = [i for i, l in enumerate(lines) if "# Design Phase" in l][0]
        
        assert input_idx < output_idx < original_task_idx