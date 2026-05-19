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
        if not inputs:
            return ""
        
        lines = ["## Input", ""]
        for key, filename in inputs.items():
            lines.append(f"- {key}: Read from {filename}")
        
        return "\n".join(lines)
    
    def _generate_output_section(self, outputs: dict[str, str]) -> str:
        pass
    
    def _should_process(self, node: Node) -> bool:
        return node.executor != "bash"