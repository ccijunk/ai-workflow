import re
import logging
from typing import Optional
from flowctl.models import Node

logger = logging.getLogger(__name__)


class PromptProcessor:
    def process(self, node: Node, prompt_content: str) -> str:
        pass
    
    def _remove_existing_sections(self, content: str) -> str:
        try:
            input_pattern = r'^## [Ii]nput.*?(?=^## |\Z)'
            output_pattern = r'^## [Oo]utput.*?(?=^## |\Z)'
            
            new_content = re.sub(input_pattern, '', content, flags=re.MULTILINE | re.DOTALL)
            new_content = re.sub(output_pattern, '', new_content, flags=re.MULTILINE | re.DOTALL)
            
            if new_content != content:
                return new_content.strip()
            return content
        except Exception as e:
            logger.warning(f"Failed to remove existing sections: {e}")
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
    
    def _should_process(self, node: Node) -> bool:
        return node.executor != "bash"