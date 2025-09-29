from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Dict, Any
from nodes.parse_cv import parse_cv_node
from nodes.confirm_cv import confirm_cv_node
from nodes.parse_job import parse_job_node
from nodes.compare import compare_node
from nodes.summary import summary_node

class WorkflowState(TypedDict):
    cv_file_path: str
    cv_text: str
    cv_data: Dict[str, Any]
    confirmed_cv_data: Dict[str, Any]
    job_description: str
    job_requirements: Dict[str, Any]
    comparison_result: Dict[str, Any]
    final_analysis: Dict[str, Any]
    session_id: str
    current_step: str
    error_message: str

def create_workflow():
    # Create the state graph
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("parse_cv", parse_cv_node)
    workflow.add_node("confirm_cv", confirm_cv_node)
    workflow.add_node("parse_job", parse_job_node)
    workflow.add_node("compare", compare_node)
    workflow.add_node("summary", summary_node)

    # Add edges
    workflow.add_edge(START, "parse_cv")
    workflow.add_edge("parse_cv", "confirm_cv")

    # Direct flow - no conditional edges for now since we handle confirmation in Flask
    workflow.add_edge("confirm_cv", END)

    workflow.add_edge("parse_job", "compare")
    workflow.add_edge("compare", "summary")
    workflow.add_edge("summary", END)

    # Compile the workflow
    return workflow.compile()