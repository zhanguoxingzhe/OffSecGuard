"""Pipeline orchestration — Plan + Executor + Gates."""

from .plan import build_run_plan, RunPlan
from .executor import ExecutionContext, PipelineExecutor
