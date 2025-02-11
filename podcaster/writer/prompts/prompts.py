import os
from pathlib import Path
from podcaster.config import config

class Prompts:
    _instance = None
    _prompts = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Prompts, cls).__new__(cls)
            cls._load_prompts()
        return cls._instance

    @classmethod
    def _load_prompts(cls):
        """Load all prompt files from the configured prompt directory"""
        prompt_dir = Path(os.path.join(config.get('projectRoot'), config.get('promptDirectory', 'prompts')))
        
        # Load all .md files from the prompt directory
        for file_path in prompt_dir.glob('*.md'):
            prompt_name = file_path.stem  # filename without extension
            with open(file_path, 'r') as f:
                cls._prompts[prompt_name] = f.read()

    @classmethod
    def get(cls, prompt_name, default=None):
        """Get a prompt by name"""
        if cls._prompts is None:
            cls._load_prompts()
        return cls._prompts.get(prompt_name, default)

    @classmethod
    def list_prompts(cls):
        """List all available prompts"""
        if cls._prompts is None:
            cls._load_prompts()
        return list(cls._prompts.keys())

prompts = Prompts()