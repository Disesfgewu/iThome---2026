import os
import asyncio
from typing import Dict, Any, Optional

class AsyncPromptManager:
    """
    Asynchronous System Prompt Manager.
    Loads system prompt markdown templates dynamically from `docs/system_prompts/`.
    Supports async file reading, memory caching, and variable interpolation.
    """
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Default to unimock-ai/docs/system_prompts
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "system_prompts"))
        self.base_dir = base_dir
        self._cache: Dict[str, str] = {}  # Raw file content cache (cleared on restart)

    async def get_system_prompt(self, prompt_name: str, **kwargs: Any) -> str:
        """
        Asynchronously loads system prompt by file name (e.g., 'question_generation').
        If prompt_name does not end with '.md', appends '.md'.
        """
        filename = prompt_name if prompt_name.endswith(".md") else f"{prompt_name}.md"
        filepath = os.path.join(self.base_dir, filename)

        if filepath in self._cache:
            raw_template = self._cache[filepath]
        else:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"System prompt template file not found at: {filepath}")
            
            # Read file asynchronously
            raw_template = await asyncio.to_thread(self._read_file_sync, filepath)
            self._cache[filepath] = raw_template

        # Strip markdown heading lines (lines starting with #) and blank lines at top
        lines = raw_template.splitlines()
        content_lines = [l for l in lines if not l.strip().startswith('#')]
        clean_template = '\n'.join(content_lines).strip()

        # Format template with provided variables, filling missing keys with empty string
        if kwargs:
            import re
            placeholders = re.findall(r'\{(\w+)\}', clean_template)
            fill_kwargs = {p: kwargs.get(p, '') for p in placeholders}
            try:
                return clean_template.format(**fill_kwargs)
            except Exception:
                return clean_template
        return clean_template

    def _read_file_sync(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

prompt_manager = AsyncPromptManager()
