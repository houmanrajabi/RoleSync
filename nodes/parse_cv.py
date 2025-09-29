from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any
import json
import logging
import os
from dotenv import load_dotenv
from utils.pdf_parser import extract_text_from_pdf

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

CV_PARSING_PROMPT = ChatPromptTemplate.from_template("""
You are an expert HR assistant specializing in CV analysis. Extract structured information from the following CV text.

CV Text:
{cv_text}

Please extract the following information and return it as a JSON object:

{{
    "name": "Full name of the person",
    "email": "Email address",
    "phone": "Phone number",
    "location": "Current location/address",
    "summary": "Professional summary or objective",
    "skills": [
        "List of technical and professional skills"
    ],
    "experience": [
        {{
            "title": "Job title",
            "company": "Company name",
            "location": "Job location",
            "start_date": "Start date",
            "end_date": "End date or 'Present'",
            "duration": "Duration (e.g., '2 years 3 months')",
            "responsibilities": ["Key responsibilities and achievements"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree type and field",
            "institution": "Educational institution",
            "location": "Institution location",
            "graduation_date": "Graduation date or expected date",
            "gpa": "GPA if mentioned",
            "relevant_coursework": ["Relevant courses if mentioned"]
        }}
    ],
    "certifications": [
        {{
            "name": "Certification name",
            "issuer": "Issuing organization",
            "date": "Date obtained",
            "expiry": "Expiry date if applicable"
        }}
    ],
    "projects": [
        {{
            "name": "Project name",
            "description": "Brief description",
            "technologies": ["Technologies used"],
            "date": "Project date or duration"
        }}
    ],
    "languages": [
        {{
            "language": "Language name",
            "proficiency": "Proficiency level"
        }}
    ]
}}

Important:
- If any information is not available, use null or empty array as appropriate
- Ensure all dates are in a consistent format
- Extract as much relevant detail as possible
- Be accurate and do not hallucinate information
""")

def parse_cv_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse CV text using LLM to extract structured information.

    Args:
        state: Current workflow state containing cv_file_path

    Returns:
        Updated state with cv_text and cv_data
    """
    try:
        cv_file_path = state.get("cv_file_path")
        if not cv_file_path:
            return {
                **state,
                "error_message": "No CV file path provided"
            }

        # Extract text from PDF
        cv_text = extract_text_from_pdf(cv_file_path)
        if not cv_text:
            return {
                **state,
                "error_message": "Failed to extract text from CV PDF"
            }

        # Use LLM to parse CV text
        chain = CV_PARSING_PROMPT | llm
        response = chain.invoke({"cv_text": cv_text})

        # Parse JSON response
        try:
            cv_data = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            # Fallback: try to extract JSON from response
            content = response.content
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                try:
                    cv_data = json.loads(content[start_idx:end_idx])
                except json.JSONDecodeError:
                    return {
                        **state,
                        "error_message": "Failed to parse CV data from LLM response"
                    }
            else:
                return {
                    **state,
                    "error_message": "Invalid JSON format in LLM response"
                }

        return {
            **state,
            "cv_text": cv_text,
            "cv_data": cv_data,
            "current_step": "cv_parsed"
        }

    except Exception as e:
        logger.error(f"Error in parse_cv_node: {str(e)}")
        return {
            **state,
            "error_message": f"CV parsing failed: {str(e)}"
        }