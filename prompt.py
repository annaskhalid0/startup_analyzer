def build_question_prompt(startup):
    """Build prompt for question generation model"""
    return (
        f"<s>[INST] Analyze this startup:\n"
        f"Name: {startup['name']}\n"
        f"Industry: {startup['industry']}\n"
        f"Pitch: {startup['pitch']}\n"
        f"Founded Year: {startup['founded_year']}\n"
        f"Funding: {startup['funding']}\n\n"
        "Ask 10 smart questions (7 VC-style + 3 industry-specific). Include 1 question to judge founder capability. [/INST]\n"
    )

def build_evaluation_prompt(startup, questions, answers):
    """Build simplified evaluation prompt for fine-tuned model"""
    vc_qs = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions[:7])])
    ind_qs = "\n".join([f"{i+8}. {q}" for i, q in enumerate(questions[7:])])
    ans = "\n".join([f"{i+1}. {a}" for i, a in enumerate(answers)])

    return (
        "<s>[INST] Evaluate this startup based on the information provided:\n\n"
        f"Startup Info:\n"
        f"Name: {startup['name']}\n"
        f"Industry: {startup['industry']}\n"
        f"Pitch: {startup['pitch']}\n"
        f"Founded Year: {startup['founded_year']}\n"
        f"Funding: {startup['funding']}\n\n"
        f"VC Questions:\n{vc_qs}\n\n"
        f"Industry-Specific Questions:\n{ind_qs}\n\n"
        f"Founder Answers:\n{ans}\n\n"
        "Provide a startup evaluation covering key business metrics, traction, team, market potential, and risks. [/INST]\n"
    )

def build_groq_enhancement_prompt(startup, questions, answers, raw_evaluation):
    """Build prompt for Groq Llama 70B to enhance the evaluation"""
    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
    answers_text = "\n".join([f"{i+1}. {a}" for i, a in enumerate(answers)])
    
    return f"""You are a senior VC analyst with 15+ years of experience evaluating startups. Based on the startup information and raw evaluation below, create a comprehensive, professional startup evaluation report.

STARTUP INFORMATION:
- Name: {startup['name']}
- Industry: {startup['industry']} 
- Pitch: {startup['pitch']}
- Founded: {startup['founded_year']}
- Funding: {startup['funding']}

QUESTIONS ASKED:
{questions_text}

FOUNDER'S ANSWERS:
{answers_text}

RAW AI EVALUATION:
{raw_evaluation}

TASK: Create a structured VC-style evaluation report covering these 15 key metrics (provide score 1-10, strength, weakness, and improvement tip for each):

1. Market Size & Opportunity
2. Product-Market Fit  
3. Competitive Advantage
4. Traction & Growth
5. Revenue Model & Unit Economics
6. Financial Health & Runway
7. Team Strength & Experience
8. Scalability Potential
9. Technology & Innovation
10. Customer Acquisition Strategy
11. Risk Assessment
12. Regulatory & Compliance
13. ESG & Social Impact
14. Investment Attractiveness
15. Future Growth Potential

FORMAT REQUIREMENTS:
- Start with "STARTUP EVALUATION REPORT" as header
- For each metric: "X. [Metric Name]: [Score]/10 — [Analysis]. Strength: [specific strength]. Weakness: [specific weakness]. Improvement: [actionable tip]."
- End with "Overall Assessment" paragraph (6-8 lines with investment recommendation)
- Be specific, use data from answers, and provide actionable insights
- Maintain professional VC tone throughout

Create a comprehensive evaluation that would be suitable for presenting to an investment committee."""

def build_groq_question_enhancement_prompt(startup, raw_questions):
    """Build prompt for Groq to enhance/validate questions"""
    return f"""You are a senior VC partner. Review and enhance these AI-generated questions for evaluating a startup.

STARTUP INFORMATION:
- Name: {startup['name']}
- Industry: {startup['industry']}
- Pitch: {startup['pitch']}
- Founded: {startup['founded_year']}
- Funding: {startup['funding']}

RAW AI-GENERATED QUESTIONS:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(raw_questions)])}

TASK: Provide exactly 10 refined, high-quality questions that follow this structure:
- 7 VC-style questions (focusing on business model, traction, financials, market, scalability, team, competition)
- 2 industry-specific questions (tailored to {startup['industry']})
- 1 founder capability question

REQUIREMENTS:
- Questions should be sharp, specific, and reveal key insights
- Avoid generic questions - make them relevant to this specific startup
- Ensure questions help assess investment potential
- Number each question 1-10
- Focus on metrics, data, and concrete evidence

Provide only the 10 refined questions, numbered 1-10."""

def parse_questions_from_response(response):
    """Parse questions from model response"""
    lines = response.strip().split("\n")
    questions = []
    
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.lower().startswith('q')):
            # Remove question numbering and clean up
            if ". " in line:
                parts = line.split(". ", 1)
                if len(parts) > 1:
                    question = parts[1].strip()
                else:
                    question = line.strip()
            elif line.lower().startswith('q'):
                # Handle Q1: format
                if ":" in line:
                    question = line.split(":", 1)[1].strip()
                else:
                    question = line
            else:
                question = line
            
            # Clean up the question
            question = question.strip()
            if question and not question.endswith('?'):
                question += '?'
            
            if question and len(question) > 10:  # Ensure it's a meaningful question
                questions.append(question)
    
    return questions[:10]  # Return max 10 questions

def validate_startup_data(startup):
    """Validate startup data before processing"""
    required_fields = ['name', 'industry', 'pitch', 'founded_year', 'funding']
    
    for field in required_fields:
        if field not in startup or not startup[field] or not startup[field].strip():
            return False, f"Missing or empty field: {field}"
    
    # Basic validation
    try:
        year = int(startup['founded_year'])
        if year < 1900 or year > 2030:
            return False, "Invalid founded year"
    except ValueError:
        return False, "Founded year must be a number"
    
    if len(startup['pitch']) < 20:
        return False, "Pitch is too short"
    
    return True, "Valid"

def format_evaluation_response(evaluation_text):
    """Format the evaluation response for better readability"""
    if not evaluation_text:
        return "No evaluation generated."
    
    # Add some basic formatting
    lines = evaluation_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Add spacing for numbered points
            if line[0].isdigit() and '. ' in line:
                formatted_lines.append('\n' + line)
            # Add spacing for Overall Assessment
            elif line.lower().startswith('overall'):
                formatted_lines.append('\n' + line)
            else:
                formatted_lines.append(line)
    
    return '\n'.join(formatted_lines).strip()