from typing import Protocol
import re
import logging
from flowctl.models import Node

logger = logging.getLogger(__name__)


class Processor(Protocol):
    """Interface for prompt/content processors."""
    
    def process(self, content: str, context: dict) -> str:
        """Transform content before execution.
        
        Args:
            content: The prompt/content to process
            context: Execution context with 'node', 'run_dir', etc.
            
        Returns:
            Processed content
        """
        ...


class PromptProcessor:
    """Processor that injects I/O sections from node definitions."""
    
    def process(self, content: str, context: dict) -> str:
        if not isinstance(content, str):
            return content
        
        node = context.get("node")
        if not node:
            return content
        
        if node.executor == "bash":
            return content
        
        try:
            cleaned = self._remove_existing_sections(content)
            input_section = self._generate_input_section(node.inputs)
            output_section = self._generate_output_section(node.outputs)
            
            sections = []
            if input_section:
                sections.append(input_section)
            if output_section:
                sections.append(output_section)
            
            if sections:
                header = "\n\n".join(sections)
                return f"{header}\n\n{cleaned}"
            
            return cleaned
        except Exception as e:
            logger.warning(f"Processor failed for node: {e}")
            return content
    
    def _remove_existing_sections(self, content: str) -> str:
        try:
            input_pattern = r'(?i)^## input.*?(?=^## |\Z)'
            output_pattern = r'(?i)^## output.*?(?=^## |\Z)'
            
            cleaned = re.sub(input_pattern, '', content, flags=re.MULTILINE | re.DOTALL)
            cleaned = re.sub(output_pattern, '', cleaned, flags=re.MULTILINE | re.DOTALL)
            
            if cleaned != content:
                return cleaned.strip()
            return content
        except Exception as e:
            logger.warning(f"Failed to remove sections: {e}")
            return content
    
    def _generate_input_section(self, inputs: dict[str, str]) -> str:
        if not inputs:
            return ""
        
        lines = ["## Input", ""]
        for key, filename in inputs.items():
            lines.append(f"- {key}: Read from {filename}")
        
        return "\n".join(lines)
    
    def _generate_output_section(self, outputs: dict[str, str]) -> str:
        if not outputs:
            return ""
        
        lines = ["## Output", ""]
        for key, filename in outputs.items():
            lines.append(f"- {key}: Write to {filename}")
        
        return "\n".join(lines)