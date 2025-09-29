from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any
import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

SUMMARY_PROMPT = ChatPromptTemplate.from_template("""
You are an expert HR consultant. Create a comprehensive, actionable summary report for a job fit analysis.

Comparison Analysis:
{comparison_result}

Job Title: {job_title}
Candidate Name: {candidate_name}

Create a final summary report as a JSON object:

{{
    "executive_summary": "2-3 sentence overview of the candidate's fit",
    "match_score": "Overall percentage match (0-100)",
    "recommendation": "Strong Hire/Hire/Maybe/No Hire",
    "key_highlights": [
        "3-5 most compelling reasons to consider this candidate"
    ],
    "main_concerns": [
        "2-3 primary areas of concern or skill gaps"
    ],
    "skill_summary": {{
        "strong_matches": ["Top 5 skills that strongly align"],
        "skill_gaps": ["Top 3 critical missing skills"],
        "transferable_skills": ["Skills that could transfer to missing areas"]
    }},
    "experience_summary": {{
        "relevant_experience": "Summary of most relevant experience",
        "experience_level": "Junior/Mid/Senior level assessment",
        "growth_trajectory": "Assessment of career progression"
    }},
    "next_steps": {{
        "interview_recommended": true,
        "interview_focus": [
            "Key areas to explore in interview"
        ],
        "reference_check_focus": [
            "Areas to verify with references"
        ],
        "skills_assessment": [
            "Technical skills to test/validate"
        ]
    }},
    "development_plan": {{
        "immediate_training_needs": [
            "Skills/knowledge to develop first 90 days"
        ],
        "long_term_development": [
            "Areas for 6-12 month development"
        ]
    }},
    "salary_considerations": {{
        "market_positioning": "Below/At/Above market rate expectation",
        "negotiation_factors": [
            "Factors that might affect salary negotiation"
        ]
    }},
    "risk_assessment": {{
        "low_risk_factors": ["Factors that reduce hiring risk"],
        "medium_risk_factors": ["Moderate risk considerations"],
        "high_risk_factors": ["Significant risk factors"]
    }},
    "timeline_recommendation": "Suggested decision timeline",
    "additional_notes": "Any other relevant observations"
}}

Important:
- Make the summary actionable and decision-focused
- Be balanced - highlight both strengths and concerns
- Provide specific, evidence-based recommendations
- Consider the business impact of the hiring decision
- Include practical next steps for the hiring process
""")

def summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate final comprehensive summary and recommendations.

    Args:
        state: Current workflow state containing comparison_result and other data

    Returns:
        Updated state with final_analysis
    """
    try:
        comparison_result = state.get("comparison_result")
        if not comparison_result:
            return {
                **state,
                "error_message": "No comparison result available for summary"
            }

        # Extract job title and candidate name from previous data
        job_requirements = state.get("job_requirements", {})
        confirmed_cv_data = state.get("confirmed_cv_data", {})

        job_title = job_requirements.get("job_title", "Unknown Position")
        candidate_name = confirmed_cv_data.get("name", "Unknown Candidate")

        # Convert comparison result to JSON string for the prompt
        comparison_result_str = json.dumps(comparison_result, indent=2)

        # Use LLM to generate final summary
        chain = SUMMARY_PROMPT | llm
        response = chain.invoke({
            "comparison_result": comparison_result_str,
            "job_title": job_title,
            "candidate_name": candidate_name
        })

        # Parse JSON response
        try:
            final_analysis = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            # Fallback: try to extract JSON from response
            content = response.content
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                try:
                    final_analysis = json.loads(content[start_idx:end_idx])
                except json.JSONDecodeError:
                    return {
                        **state,
                        "error_message": "Failed to parse final analysis from LLM response"
                    }
            else:
                return {
                    **state,
                    "error_message": "Invalid JSON format in LLM response"
                }

        # Add metadata to final analysis
        final_analysis["metadata"] = {
            "analysis_date": state.get("session_id", ""),
            "job_title": job_title,
            "candidate_name": candidate_name,
            "workflow_version": "1.0"
        }

        return {
            **state,
            "final_analysis": final_analysis,
            "current_step": "analysis_complete"
        }

    except Exception as e:
        logger.error(f"Error in summary_node: {str(e)}")
        return {
            **state,
            "error_message": f"Summary generation failed: {str(e)}"
        }