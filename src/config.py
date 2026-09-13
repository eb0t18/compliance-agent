"""
Configuration for the compliance evaluation agent.
Reads the Anthropic API key from an environment variable — never hardcode it.
"""

import os

# Load from environment. Set this before running:
#   export ANTHROPIC_API_KEY="sk-ant-..."          (Mac/Linux)
#   $env:ANTHROPIC_API_KEY="sk-ant-..."             (Windows PowerShell)
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

if not API_KEY:
    raise EnvironmentError(
        "ANTHROPIC_API_KEY is not set. Set it as an environment variable "
        "before running this script."
    )

# Model used for the bulk control evaluation — cheap, fast, plenty capable
# for this structured classification task.
EVAL_MODEL = "claude-haiku-4-5-20251001"

# Model used only for the single "deep dive" control in the demo, if you
# want one control evaluated with more thorough reasoning.
DEEP_DIVE_MODEL = "claude-sonnet-5"

API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
