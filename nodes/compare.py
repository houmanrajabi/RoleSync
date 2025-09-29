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

COMPARISON_PROMPT = ChatPromptTemplate.from_template("""
You are an expert HR analyst specializing in candidate evaluation. Analyze how well a candidate's CV matches a job's requirements.

Candidate CV Data:
{cv_data}

Job Requirements:
{job_requirements}

Please provide a comprehensive analysis and return it as a JSON object:

{{
    "overall_match_score": "Percentage score (0-100) indicating overall fit",
    "match_level": "Excellent/Good/Fair/Poor",
    "skills_analysis": {{
        "matching_skills": [
            {{
                "skill": "Skill name",
                "cv_evidence": "Evidence from CV",
                "job_requirement": "How it matches job requirement",
                "match_strength": "Strong/Moderate/Weak"
            }}
        ],
        "missing_required_skills": [
            {{
                "skill": "Missing required skill",
                "importance": "Critical/High/Medium/Low",
                "alternative_skills": ["Related skills candidate has"]
            }}
        ],
        "additional_skills": [
            {{
                "skill": "Extra skill candidate has",
                "value": "How this adds value to the role"
            }}
        ]
    }},
    "experience_analysis": {{
        "total_years_experience": "Candidate's total years",
        "required_years": "Job's required years",
        "experience_match": "Exceeds/Meets/Below requirements",
        "relevant_experience": [
            {{
                "role": "Previous role",
                "relevance": "How it relates to target job",
                "skills_gained": ["Key skills from this role"]
            }}
        ],
        "experience_gaps": [
            "Areas where candidate lacks experience"
        ]
    }},
    "education_analysis": {{
        "meets_requirements": true,
        "candidate_education": ["Candidate's education"],
        "required_education": ["Job's education requirements"],
        "education_match": "Explanation of how education aligns"
    }},
    "certification_analysis": {{
        "matching_certifications": ["Certifications that match"],
        "missing_certifications": ["Required certifications candidate lacks"],
        "additional_certifications": ["Extra certifications candidate has"]
    }},
    "strengths": [
        "Key strengths that make candidate attractive"
    ],
    "concerns": [
        "Potential concerns or red flags"
    ],
    "growth_potential": "Assessment of candidate's growth potential",
    "cultural_fit_indicators": [
        "Indicators of potential cultural fit"
    ],
    "recommendations": {{
        "hiring_recommendation": "Strong Hire/Hire/No Hire/Need More Info",
        "interview_focus_areas": [
            "Areas to explore in interview"
        ],
        "development_areas": [
            "Skills/areas for potential development"
        ]
    }}
}}

Important:
- Be objective and evidence-based in your analysis
- Consider both technical and soft skill requirements
- Provide specific examples from the CV when possible
- Be realistic about match percentages
- Consider transferable skills and potential for growth
- Highlight both positives and areas of concern
""")

def compare_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare CV data against job requirements using LLM analysis.

    Args:
        state: Current workflow state containing confirmed_cv_data and job_requirements

    Returns:
        Updated state with comparison_result
    """
    try:
        confirmed_cv_data = state.get("confirmed_cv_data")
        job_requirements = state.get("job_requirements")

        if not confirmed_cv_data:
            return {
                **state,
                "error_message": "No confirmed CV data available for comparison"
            }

        if not job_requirements:
            return {
                **state,
                "error_message": "No job requirements available for comparison"
            }

        # Convert data to JSON strings for the prompt
        cv_data_str = json.dumps(confirmed_cv_data, indent=2)
        job_requirements_str = json.dumps(job_requirements, indent=2)

        # Use LLM to perform comparison analysis
        chain = COMPARISON_PROMPT | llm
        response = chain.invoke({
            "cv_data": cv_data_str,
            "job_requirements": job_requirements_str
        })

        # Parse JSON response
        try:
            comparison_result = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            # Fallback: try to extract JSON from response
            content = response.content
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                try:
                    comparison_result = json.loads(content[start_idx:end_idx])
                except json.JSONDecodeError:
                    return {
                        **state,
                        "error_message": "Failed to parse comparison result from LLM response"
                    }
            else:
                return {
                    **state,
                    "error_message": "Invalid JSON format in LLM response"
                }

        return {
            **state,
            "comparison_result": comparison_result,
            "current_step": "comparison_complete"
        }

    except Exception as e:
        logger.error(f"Error in compare_node: {str(e)}")
        return {
            **state,
            "error_message": f"Comparison analysis failed: {str(e)}"
        }