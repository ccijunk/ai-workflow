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