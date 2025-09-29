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

JOB_PARSING_PROMPT = ChatPromptTemplate.from_template("""
You are an expert HR assistant specializing in job requirement analysis. Extract structured information from the following job description.

Job Description:
{job_description}

Please extract the following information and return it as a JSON object:

{{
    "job_title": "Job title",
    "company": "Company name if mentioned",
    "location": "Job location",
    "employment_type": "Full-time, Part-time, Contract, etc.",
    "experience_level": "Entry, Mid, Senior, Executive level",
    "job_summary": "Brief summary of the role",
    "required_skills": [
        "List of required technical and professional skills"
    ],
    "preferred_skills": [
        "List of preferred/nice-to-have skills"
    ],
    "required_experience": [
        {{
            "area": "Area of experience (e.g., 'Software Development')",
            "years": "Minimum years required",
            "details": "Specific experience requirements"
        }}
    ],
    "required_education": [
        {{
            "level": "Education level (e.g., 'Bachelor's Degree')",
            "field": "Field of study if specified",
            "required": true
        }}
    ],
    "preferred_education": [
        {{
            "level": "Preferred education level",
            "field": "Field of study if specified",
            "required": false
        }}
    ],
    "required_certifications": [
        "List of required certifications"
    ],
    "preferred_certifications": [
        "List of preferred certifications"
    ],
    "responsibilities": [
        "Key job responsibilities and duties"
    ],
    "technologies": [
        "Specific technologies, tools, platforms mentioned"
    ],
    "soft_skills": [
        "Communication, leadership, teamwork, etc."
    ],
    "benefits": [
        "Salary range, benefits, perks mentioned"
    ],
    "team_size": "Team size or reporting structure if mentioned",
    "travel_requirements": "Travel requirements if mentioned",
    "remote_work": "Remote work policy if mentioned"
}}

Important:
- Distinguish between "required" and "preferred" qualifications
- If any information is not available, use null or empty array as appropriate
- Extract specific years of experience when mentioned
- Be precise about technical requirements vs nice-to-haves
- Do not hallucinate information not present in the job description
""")

def parse_job_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse job description using LLM to extract structured requirements.

    Args:
        state: Current workflow state containing job_description

    Returns:
        Updated state with job_requirements
    """
    try:
        job_description = state.get("job_description")
        if not job_description:
            return {
                **state,
                "error_message": "No job description provided"
            }

        # Use LLM to parse job description
        chain = JOB_PARSING_PROMPT | llm
        response = chain.invoke({"job_description": job_description})

        # Parse JSON response
        try:
            job_requirements = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            # Fallback: try to extract JSON from response
            content = response.content
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                try:
                    job_requirements = json.loads(content[start_idx:end_idx])
                except json.JSONDecodeError:
                    return {
                        **state,
                        "error_message": "Failed to parse job requirements from LLM response"
                    }
            else:
                return {
                    **state,
                    "error_message": "Invalid JSON format in LLM response"
                }

        return {
            **state,
            "job_requirements": job_requirements,
            "current_step": "job_parsed"
        }

    except Exception as e:
        logger.error(f"Error in parse_job_node: {str(e)}")
        return {
            **state,
            "error_message": f"Job parsing failed: {str(e)}"
        }