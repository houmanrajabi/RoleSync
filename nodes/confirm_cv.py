from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def confirm_cv_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Human-in-the-loop node for CV data confirmation.
    This node prepares the CV data for human review and waits for confirmation.

    Args:
        state: Current workflow state containing cv_data

    Returns:
        Updated state ready for human confirmation
    """
    try:
        cv_data = state.get("cv_data")
        if not cv_data:
            return {
                **state,
                "error_message": "No CV data available for confirmation"
            }

        # Format CV data for display in the web interface
        formatted_cv_data = format_cv_for_display(cv_data)

        return {
            **state,
            "formatted_cv_data": formatted_cv_data,
            "current_step": "awaiting_cv_confirmation",
            "requires_human_input": True
        }

    except Exception as e:
        logger.error(f"Error in confirm_cv_node: {str(e)}")
        return {
            **state,
            "error_message": f"CV confirmation preparation failed: {str(e)}"
        }

def format_cv_for_display(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format CV data for better display in the web interface.

    Args:
        cv_data: Raw CV data from parsing

    Returns:
        Formatted CV data for display
    """
    formatted = {
        "personal_info": {
            "name": cv_data.get("name", ""),
            "email": cv_data.get("email", ""),
            "phone": cv_data.get("phone", ""),
            "location": cv_data.get("location", ""),
            "summary": cv_data.get("summary", "")
        },
        "skills": cv_data.get("skills", []),
        "experience": [],
        "education": [],
        "certifications": [],
        "projects": cv_data.get("projects", []),
        "languages": cv_data.get("languages", [])
    }

    # Format experience entries
    for exp in cv_data.get("experience", []):
        formatted_exp = {
            "title": exp.get("title", ""),
            "company": exp.get("company", ""),
            "location": exp.get("location", ""),
            "start_date": exp.get("start_date", ""),
            "end_date": exp.get("end_date", ""),
            "duration": exp.get("duration", ""),
            "responsibilities": exp.get("responsibilities", [])
        }
        formatted["experience"].append(formatted_exp)

    # Format education entries
    for edu in cv_data.get("education", []):
        formatted_edu = {
            "degree": edu.get("degree", ""),
            "institution": edu.get("institution", ""),
            "location": edu.get("location", ""),
            "graduation_date": edu.get("graduation_date", ""),
            "gpa": edu.get("gpa", ""),
            "relevant_coursework": edu.get("relevant_coursework", [])
        }
        formatted["education"].append(formatted_edu)

    # Format certification entries
    for cert in cv_data.get("certifications", []):
        formatted_cert = {
            "name": cert.get("name", ""),
            "issuer": cert.get("issuer", ""),
            "date": cert.get("date", ""),
            "expiry": cert.get("expiry", "")
        }
        formatted["certifications"].append(formatted_cert)

    return formatted