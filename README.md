# CV Job Match Analyzer

A modular Flask application integrated with LangGraph that orchestrates a multi-step, human-in-the-loop workflow for analyzing job fit. Upload your CV, confirm extracted data, input job descriptions, and get comprehensive match analysis powered by AI.

## Features

- **PDF CV Processing**: Upload PDF CVs and extract structured data using AI
- **Human-in-the-loop Validation**: Review and confirm extracted CV information before analysis
- **Job Description Analysis**: Parse job requirements and qualifications automatically
- **Comprehensive Matching**: AI-powered comparison between CV and job requirements
- **Detailed Reporting**: Get match scores, skill analysis, recommendations, and development plans
- **Professional UI**: Clean, responsive web interface with modern design

## Tech Stack

- **Backend**: Flask, LangGraph, OpenAI GPT-4
- **PDF Processing**: PyPDF2
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Integration**: LangChain, OpenAI API

## Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Access the web interface**
   Open your browser and go to `http://localhost:5000`

3. **Upload your CV**
   - Upload a PDF version of your CV
   - The AI will extract structured information

4. **Confirm extracted data**
   - Review and edit the extracted information
   - Add or modify skills, experience, education, etc.

5. **Input job description**
   - Paste the job description you want to match against
   - Include all requirements and qualifications

6. **Get analysis results**
   - Receive detailed match analysis
   - View skill alignments, gaps, and recommendations
   - Print or save the report

## Project Structure

```
cv_job_match/
├── app.py                # Main Flask application
├── graph.py              # LangGraph workflow definition
├── nodes/                # Workflow node implementations
│   ├── parse_cv.py       # CV parsing with AI
│   ├── confirm_cv.py     # Human confirmation node
│   ├── parse_job.py      # Job description parsing
│   ├── compare.py        # CV-Job comparison analysis
│   └── summary.py        # Final analysis generation
├── templates/            # HTML templates
│   ├── index.html        # Home page
│   ├── confirm_cv.html   # CV confirmation page
│   ├── job_input.html    # Job description input
│   └── result.html       # Results display
├── static/               # CSS and JS files
│   ├── style.css         # Main stylesheet
│   └── confirm.js        # CV confirmation interactions
├── utils/                # Utility functions
│   └── pdf_parser.py     # PDF text extraction
├── uploads/              # Temporary file storage
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md            # This file
```

## Workflow

1. **PDF Upload & Parsing**: User uploads CV PDF → AI extracts structured data
2. **Human Validation**: User reviews and confirms extracted information
3. **Job Input**: User provides job description for comparison
4. **AI Analysis**: System compares CV against job requirements
5. **Results**: Comprehensive match analysis with recommendations

## API Endpoints

- `GET /` - Home page with CV upload
- `POST /upload_cv` - Process uploaded CV PDF
- `POST /confirm_cv` - Handle confirmed CV data
- `POST /analyze_job` - Analyze job match
- `GET /cleanup` - Clean up session data

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4 access
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `FLASK_ENV`: Environment (development/production)
- `MAX_CONTENT_LENGTH`: Maximum file upload size (default: 16MB)

### Model Configuration

The application uses GPT-4 by default. You can modify the model in the node files:

```python
llm = ChatOpenAI(model="gpt-4", temperature=0)
```

## Features in Detail

### CV Processing
- Extracts personal information, skills, experience, education, certifications
- Handles various PDF formats and layouts
- Validates and structures unorganized CV data

### Job Analysis
- Parses job descriptions for requirements and qualifications
- Distinguishes between required vs. preferred skills
- Extracts experience levels, education requirements, technologies

### Match Analysis
- Comprehensive skill comparison with evidence from CV
- Experience relevance assessment
- Education and certification matching
- Risk assessment and hiring recommendations
- Development plan suggestions

### Reporting
- Executive summary with match score and recommendation
- Detailed skill gap analysis
- Interview focus areas
- Reference check recommendations
- Professional development roadmap

## License

This project is licensed under the MIT License 

## Security Notes

- CV data is processed locally and not stored permanently
- Sessions are cleaned up after analysis