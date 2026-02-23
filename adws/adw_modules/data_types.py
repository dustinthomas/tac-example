"""Data types for GitHub API responses, Claude Code agent, and ADW state."""

import re
from datetime import datetime
from enum import Enum
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

# Supported slash commands for issue classification
IssueClassSlashCommand = Literal["/chore", "/bug", "/feature"]

# All slash commands used in the ADW system
SlashCommand = Literal[
    # Issue classification commands
    "/chore",
    "/bug",
    "/feature",
    # ADW workflow commands
    "/classify_issue",
    "/find_plan_file",
    "/generate_branch_name",
    "/commit",
    "/pull_request",
    "/implement",
    # SDLC phase commands
    "/test",
    "/resolve_failed_test",
    "/review",
    "/document",
    "/patch",
    "/classify_adw",
    "/prepare_app",
    "/conditional_docs",
]


class GitHubUser(BaseModel):
    """GitHub user model."""

    id: Optional[str] = None
    login: str
    name: Optional[str] = None
    is_bot: bool = Field(default=False, alias="is_bot")


class GitHubLabel(BaseModel):
    """GitHub label model."""

    id: str
    name: str
    color: str
    description: Optional[str] = None


class GitHubMilestone(BaseModel):
    """GitHub milestone model."""

    id: str
    number: int
    title: str
    description: Optional[str] = None
    state: str


class GitHubComment(BaseModel):
    """GitHub comment model."""

    id: str
    author: GitHubUser
    body: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class GitHubIssueListItem(BaseModel):
    """GitHub issue model for list responses (simplified)."""

    number: int
    title: str
    body: str
    labels: List[GitHubLabel] = []
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class GitHubIssue(BaseModel):
    """GitHub issue model."""

    number: int
    title: str
    body: str
    state: str
    author: GitHubUser
    assignees: List[GitHubUser] = []
    labels: List[GitHubLabel] = []
    milestone: Optional[GitHubMilestone] = None
    comments: List[GitHubComment] = []
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    closed_at: Optional[datetime] = Field(None, alias="closedAt")
    url: str

    class Config:
        populate_by_name = True

    def extract_image_urls(self) -> List[str]:
        """Extract image URLs from issue body (HTML img tags and Markdown images)."""
        urls: List[str] = []
        # HTML <img src="...">
        urls.extend(re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', self.body))
        # Markdown ![alt](url)
        urls.extend(re.findall(r'!\[[^\]]*\]\(([^)]+)\)', self.body))
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: List[str] = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique.append(url)
        return unique


class AgentPromptRequest(BaseModel):
    """Claude Code agent prompt configuration."""

    prompt: str
    adw_id: str
    agent_name: str = "ops"
    model: Literal["sonnet", "opus"] = "opus"
    image_paths: List[str] = Field(default_factory=list)
    dangerously_skip_permissions: bool = False
    output_file: str


class AgentPromptResponse(BaseModel):
    """Claude Code agent response."""

    output: str
    success: bool
    session_id: Optional[str] = None


class AgentTemplateRequest(BaseModel):
    """Claude Code agent template execution request."""

    agent_name: str
    slash_command: SlashCommand
    args: List[str]
    adw_id: str
    image_paths: List[str] = Field(default_factory=list)
    model: Literal["sonnet", "opus"] = "sonnet"


class ClaudeCodeResultMessage(BaseModel):
    """Claude Code JSONL result message (last line)."""

    type: str
    subtype: str
    is_error: bool
    duration_ms: int
    duration_api_ms: int
    num_turns: int
    result: str
    session_id: str
    total_cost_usd: float


# --- ADW State Types ---


class ADWWorkflow(str, Enum):
    """ADW workflow types."""

    PLAN_BUILD = "plan_build"
    PLAN_BUILD_TEST = "plan_build_test"
    PLAN_BUILD_REVIEW = "plan_build_review"
    PLAN_BUILD_TEST_REVIEW = "plan_build_test_review"
    SDLC = "sdlc"
    PATCH = "patch"


class TestResult(BaseModel):
    """Result from a single test suite run."""

    suite: str  # e.g., "frontend_typecheck", "frontend_test", "backend_test"
    passed: bool
    output: str
    error: Optional[str] = None


class E2ETestResult(BaseModel):
    """Aggregate result from /test command."""

    all_passed: bool
    results: List[TestResult]
    attempt: int = 1


class ReviewIssue(BaseModel):
    """A single issue found during code review."""

    file: str
    line: Optional[int] = None
    severity: Literal["blocker", "warning", "suggestion"]
    description: str


class ReviewResult(BaseModel):
    """Result from /review command."""

    approved: bool
    issues: List[ReviewIssue] = []
    screenshots: List[str] = Field(default_factory=list)
    summary: str
    attempt: int = 1


class DocumentationResult(BaseModel):
    """Result from /document command."""

    files_created: List[str] = []
    summary: str


class ADWPhase(str, Enum):
    """Phases in the ADW pipeline."""

    CLASSIFY = "classify"
    BRANCH = "branch"
    PLAN = "plan"
    BUILD = "build"
    TEST = "test"
    REVIEW = "review"
    DOCUMENT = "document"
    PR = "pr"


class ADWStateData(BaseModel):
    """Persistent ADW state between phases.

    Serialized to agents/{adw_id}/adw_state.json.
    """

    adw_id: str
    issue_number: str
    workflow: ADWWorkflow = ADWWorkflow.PLAN_BUILD
    issue_class: Optional[IssueClassSlashCommand] = None
    branch_name: Optional[str] = None
    plan_file: Optional[str] = None
    current_phase: ADWPhase = ADWPhase.CLASSIFY
    completed_phases: List[ADWPhase] = []
    test_results: List[E2ETestResult] = []
    review_results: List[ReviewResult] = []
    documentation: Optional[DocumentationResult] = None
    pr_url: Optional[str] = None
    error: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
