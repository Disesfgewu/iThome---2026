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
        self._cache: Dict[str, str] = {}

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

        # Format template with provided variables if any
        if kwargs:
            try:
                return raw_template.format(**kwargs)
            except KeyError:
                # If formatting fails due to missing keys, return raw template safely
                return raw_template
        return raw_template

    def _read_file_sync(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

prompt_manager = AsyncPromptManager()
