ISSUE_TYPES = [
    "wrong_answer",
    "slow_response",
    "missing_context",
    "tool_failure",
    "bad_retrieval",
    "user_escalation"
]

ROOT_CAUSES = {
    "wrong_answer": "model_reasoning_or_prompt_issue",
    "slow_response": "latency_or_infrastructure_bottleneck",
    "missing_context": "retrieval_or_context_pipeline_failure",
    "tool_failure": "external_tool_or_api_error",
    "bad_retrieval": "vector_search_or_embedding_issue",
    "user_escalation": "unresolved_or_repeated_failure"
}
