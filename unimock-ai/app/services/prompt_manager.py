import os
import asyncio
from typing import Dict, Any, Optional, Tuple

class AsyncPromptManager:
    """
    Asynchronous System Prompt Manager.
    Loads system prompt markdown templates dynamically from `docs/system_prompts/`.
    Supports async file reading, mtime-aware automatic cache invalidation, and variable interpolation.
    """
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Default to unimock-ai/docs/system_prompts
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "system_prompts"))
        self.base_dir = base_dir
        self._cache: Dict[str, Tuple[float, str]] = {}  # filepath -> (mtime, content)

    def clear_cache(self):
        """Manually flush prompt cache."""
        self._cache.clear()

    async def get_system_prompt(self, prompt_name: str, **kwargs: Any) -> str:
        """
        Asynchronously loads system prompt by file name (e.g., 'question_generation').
        Automatically reloads from disk if the template file has been modified.
        """
        filename = prompt_name if prompt_name.endswith(".md") else f"{prompt_name}.md"
        filepath = os.path.join(self.base_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"System prompt template file not found at: {filepath}")

        # Check mtime to determine if cached template is still valid
        current_mtime = os.path.getmtime(filepath)
        if filepath in self._cache and self._cache[filepath][0] == current_mtime:
            raw_template = self._cache[filepath][1]
        else:
            # Read file asynchronously and update cache
            raw_template = await asyncio.to_thread(self._read_file_sync, filepath)
            self._cache[filepath] = (current_mtime, raw_template)

        # Strip markdown heading lines (lines starting with #) and blank lines at top
        lines = raw_template.splitlines()
        content_lines = [l for l in lines if not l.strip().startswith('#')]
        clean_template = '\n'.join(content_lines).strip()

        # Format template by safely replacing {key} placeholders without crashing on unescaped braces
        import re
        result = clean_template
        if kwargs:
            for key, val in kwargs.items():
                result = result.replace(f"{{{key}}}", str(val if val is not None else ""))
        # Strip any remaining unpopulated {placeholder} tags
        result = re.sub(r'\{[a-zA-Z0-9_]+\}', '', result)
        return result

    def _read_file_sync(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

prompt_manager = AsyncPromptManager()
