import pytest
from pydantic import ValidationError
from flowctl.models import Node, RoleConfig


def test_node_command_with_bash_executor():
    node = Node(
        role="test",
        prompt="test.md",
        executor="bash",
        command="scripts/test.sh",
    )
    assert node.executor == "bash"
    assert node.command == "scripts/test.sh"


def test_node_command_missing_for_bash():
    with pytest.raises(ValidationError, match="executor='bash' must have 'command'"):
        Node(
            role="test",
            prompt="test.md",
            executor="bash",
        )


def test_node_command_with_other_executor():
    with pytest.raises(ValidationError, match="'command' field is only allowed"):
        Node(
            role="test",
            prompt="test.md",
            executor="opencode",
            command="scripts/test.sh",
        )


def test_node_command_without_executor():
    with pytest.raises(ValidationError, match="'command' field is only allowed"):
        Node(
            role="test",
            prompt="test.md",
            command="scripts/test.sh",
        )


def test_node_timeout_default():
    node = Node(
        role="test",
        prompt="test.md",
        executor="bash",
        command="scripts/test.sh",
    )
    assert node.timeout_seconds == 60


def test_node_timeout_custom():
    node = Node(
        role="test",
        prompt="test.md",
        executor="bash",
        command="scripts/test.sh",
        timeout_seconds=120,
    )
    assert node.timeout_seconds == 120


def test_node_timeout_negative():
    with pytest.raises(ValidationError, match="timeout_seconds must be positive"):
        Node(
            role="test",
            prompt="test.md",
            executor="bash",
            command="scripts/test.sh",
            timeout_seconds=-10,
        )


def test_node_timeout_zero():
    with pytest.raises(ValidationError, match="timeout_seconds must be positive"):
        Node(
            role="test",
            prompt="test.md",
            executor="bash",
            command="scripts/test.sh",
            timeout_seconds=0,
        )


def test_role_config_executor():
    role = RoleConfig(
        name="github",
        model="default",
        executor="bash",
    )
    assert role.executor == "bash"


def test_role_config_no_executor():
    role = RoleConfig(
        name="test",
        model="default",
    )
    assert role.executor is None