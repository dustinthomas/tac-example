"""Claude Code agent module for executing prompts programmatically."""

import subprocess
import sys
import os
import json
import re
import urllib.request
from typing import Optional, List, Dict, Any, Tuple, Literal
from dotenv import load_dotenv
from adw_modules.data_types import (
    AgentPromptRequest,
    AgentPromptResponse,
    AgentTemplateRequest,
    ClaudeCodeResultMessage,
)

# Load environment variables
load_dotenv()

# Get Claude Code CLI path from environment
CLAUDE_PATH = os.getenv("CLAUDE_CODE_PATH", "claude")

# Model mapping per slash command — opus for complex tasks, sonnet for routine
SLASH_COMMAND_MODEL_MAP: Dict[str, Literal["sonnet", "opus"]] = {
    # Complex tasks → opus
    "/implement": "opus",
    "/review": "opus",
    "/feature": "opus",
    "/bug": "opus",
    "/chore": "opus",
    "/patch": "opus",
    "/resolve_failed_test": "opus",
    # Routine tasks → sonnet
    "/classify_issue": "sonnet",
    "/classify_adw": "sonnet",
    "/commit": "sonnet",
    "/pull_request": "sonnet",
    "/find_plan_file": "sonnet",
    "/generate_branch_name": "sonnet",
    "/test": "sonnet",
    "/document": "sonnet",
    "/prepare_app": "sonnet",
    "/conditional_docs": "sonnet",
}


def get_model_for_command(slash_command: str) -> Literal["sonnet", "opus"]:
    """Get the recommended model for a given slash command."""
    return SLASH_COMMAND_MODEL_MAP.get(slash_command, "sonnet")


def check_claude_installed() -> Optional[str]:
    """Check if Claude Code CLI is installed. Return error message if not."""
    try:
        result = subprocess.run(
            [CLAUDE_PATH, "--version"], capture_output=True, text=True
        )
        if result.returncode != 0:
            return f"Error: Claude Code CLI is not installed. Expected at: {CLAUDE_PATH}"
    except FileNotFoundError:
        return f"Error: Claude Code CLI is not installed. Expected at: {CLAUDE_PATH}"
    return None


def parse_jsonl_output(output_file: str) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Parse JSONL output file and return all messages and the result message."""
    try:
        with open(output_file, "r") as f:
            messages = [json.loads(line) for line in f if line.strip()]

            result_message = None
            for message in reversed(messages):
                if message.get("type") == "result":
                    result_message = message
                    break

            return messages, result_message
    except Exception as e:
        print(f"Error parsing JSONL file: {e}", file=sys.stderr)
        return [], None


def convert_jsonl_to_json(jsonl_file: str) -> str:
    """Convert JSONL file to JSON array file."""
    json_file = jsonl_file.replace('.jsonl', '.json')

    messages, _ = parse_jsonl_output(jsonl_file)

    with open(json_file, 'w') as f:
        json.dump(messages, f, indent=2)

    print(f"Created JSON file: {json_file}")
    return json_file


def get_claude_env() -> Dict[str, str]:
    """Get only the required environment variables for Claude Code execution."""
    required_env_vars = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "CLAUDE_CODE_PATH": os.getenv("CLAUDE_CODE_PATH", "claude"),
        "CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR": os.getenv("CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR", "true"),
        "HOME": os.getenv("HOME"),
        "USER": os.getenv("USER"),
        "PATH": os.getenv("PATH"),
        "SHELL": os.getenv("SHELL"),
        "TERM": os.getenv("TERM"),
    }

    github_pat = os.getenv("GITHUB_PAT")
    if github_pat:
        required_env_vars["GITHUB_PAT"] = github_pat
        required_env_vars["GH_TOKEN"] = github_pat

    return {k: v for k, v in required_env_vars.items() if v is not None}


def save_prompt(prompt: str, adw_id: str, agent_name: str = "ops") -> None:
    """Save a prompt to the appropriate logging directory."""
    match = re.match(r'^(/\w+)', prompt)
    if not match:
        return

    slash_command = match.group(1)
    command_name = slash_command[1:]

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    prompt_dir = os.path.join(project_root, "agents", adw_id, agent_name, "prompts")
    os.makedirs(prompt_dir, exist_ok=True)

    prompt_file = os.path.join(prompt_dir, f"{command_name}.txt")
    with open(prompt_file, "w") as f:
        f.write(prompt)

    print(f"Saved prompt to: {prompt_file}")


def download_issue_images(image_urls: List[str], adw_id: str) -> List[str]:
    """Download images from issue URLs to local paths. Returns list of saved file paths."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    image_dir = os.path.join(project_root, "agents", adw_id, "images")
    os.makedirs(image_dir, exist_ok=True)

    saved_paths: List[str] = []
    for i, url in enumerate(image_urls):
        # Derive extension from URL or default to .png
        ext = os.path.splitext(url.split("?")[0])[1] or ".png"
        filename = f"issue_image_{i}{ext}"
        dest = os.path.join(image_dir, filename)

        try:
            # Try direct download first
            req = urllib.request.Request(url, headers={"User-Agent": "ADW-Agent/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(dest, "wb") as f:
                    f.write(resp.read())
            saved_paths.append(dest)
            print(f"Downloaded image: {dest}")
        except Exception as e:
            # Fall back to gh api for GitHub user-content URLs
            print(f"Direct download failed for {url}: {e}", file=sys.stderr)
            try:
                result = subprocess.run(
                    ["gh", "api", url, "--method", "GET"],
                    capture_output=True, timeout=30,
                )
                if result.returncode == 0 and result.stdout:
                    with open(dest, "wb") as f:
                        f.write(result.stdout)
                    saved_paths.append(dest)
                    print(f"Downloaded image via gh: {dest}")
                else:
                    print(f"gh api download also failed for {url}", file=sys.stderr)
            except Exception as e2:
                print(f"gh api fallback failed: {e2}", file=sys.stderr)

    return saved_paths


def prompt_claude_code(request: AgentPromptRequest) -> AgentPromptResponse:
    """Execute Claude Code with the given prompt configuration."""

    error_msg = check_claude_installed()
    if error_msg:
        return AgentPromptResponse(output=error_msg, success=False, session_id=None)

    save_prompt(request.prompt, request.adw_id, request.agent_name)

    output_dir = os.path.dirname(request.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    cmd = [CLAUDE_PATH, "-p", request.prompt]
    cmd.extend(["--model", request.model])
    cmd.extend(["--output-format", "stream-json"])
    cmd.append("--verbose")

    # Append image file paths to prompt so the agent can read them
    if request.image_paths:
        image_refs = [p for p in request.image_paths if os.path.isfile(p)]
        if image_refs:
            image_note = "\n\nReference images (use Read tool to view):\n" + "\n".join(
                f"- {os.path.abspath(p)}" for p in image_refs
            )
            cmd[2] = cmd[2] + image_note

    if request.dangerously_skip_permissions:
        cmd.append("--dangerously-skip-permissions")

    env = get_claude_env()

    try:
        with open(request.output_file, "w") as f:
            result = subprocess.run(
                cmd, stdout=f, stderr=subprocess.PIPE, text=True, env=env
            )

        if result.returncode == 0:
            print(f"Output saved to: {request.output_file}")

            messages, result_message = parse_jsonl_output(request.output_file)
            json_file = convert_jsonl_to_json(request.output_file)

            if result_message:
                session_id = result_message.get("session_id")
                is_error = result_message.get("is_error", False)
                result_text = result_message.get("result", "")

                return AgentPromptResponse(
                    output=result_text,
                    success=not is_error,
                    session_id=session_id
                )
            else:
                with open(request.output_file, "r") as f:
                    raw_output = f.read()
                return AgentPromptResponse(
                    output=raw_output,
                    success=True,
                    session_id=None
                )
        else:
            error_msg = f"Claude Code error: {result.stderr}"
            print(error_msg, file=sys.stderr)
            return AgentPromptResponse(output=error_msg, success=False, session_id=None)

    except subprocess.TimeoutExpired:
        error_msg = "Error: Claude Code command timed out after 5 minutes"
        print(error_msg, file=sys.stderr)
        return AgentPromptResponse(output=error_msg, success=False, session_id=None)
    except Exception as e:
        error_msg = f"Error executing Claude Code: {e}"
        print(error_msg, file=sys.stderr)
        return AgentPromptResponse(output=error_msg, success=False, session_id=None)


def execute_template(request: AgentTemplateRequest) -> AgentPromptResponse:
    """Execute a Claude Code template with slash command and arguments."""
    prompt = f"{request.slash_command} {' '.join(request.args)}"

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(project_root, "agents", request.adw_id, request.agent_name)
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "raw_output.jsonl")

    prompt_request = AgentPromptRequest(
        prompt=prompt,
        adw_id=request.adw_id,
        agent_name=request.agent_name,
        model=request.model,
        image_paths=request.image_paths,
        dangerously_skip_permissions=True,
        output_file=output_file,
    )

    return prompt_claude_code(prompt_request)
