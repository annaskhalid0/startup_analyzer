import streamlit as st
import requests
import json
import time
import pandas as pd
import re
from datetime import datetime
from io import BytesIO
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Configuration
API_BASE_URL = "http://52.4.244.178:8000"  # Change to your deployed URL

# IMMEDIATE CSS injection to prevent blue flash + Enhanced animations
st.markdown("""
<style>
/* Immediate background override */
html, body, .stApp, [data-testid="stAppViewContainer"], .main, .block-container {
    background-color: #FAF9F6 !important;
}

/* Enhanced Header Styling */
.animated-header {
    background: linear-gradient(135deg, #3D5A40 0%, #5A7C65 50%, #3D5A40 100%);
    background-size: 200% 200%;
    animation: gradientShift 4s ease infinite;
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    margin: 20px auto;
    max-width: 900px;
    box-shadow: 0 10px 30px rgba(61, 90, 64, 0.3);
    position: relative;
    overflow: hidden;
}

.animated-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
    animation: shimmer 3s infinite;
    transform: rotate(45deg);
}

.header-title {
    color: white !important;
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    animation: titlePulse 2s ease-in-out infinite alternate;
    position: relative;
    z-index: 2;
}

.header-subtitle {
    color: rgba(255,255,255,0.9) !important;
    font-size: 1.1rem;
    margin: 10px 0 0 0;
    font-weight: 500;
    animation: subtitleFade 3s ease-in-out infinite alternate;
    position: relative;
    z-index: 2;
}

/* Floating AI Elements */
.ai-elements {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    pointer-events: none;
    z-index: 1;
}

.ai-particle {
    position: absolute;
    color: rgba(255,255,255,0.6);
    font-size: 1.2rem;
    animation: float 6s ease-in-out infinite;
}

.ai-particle:nth-child(1) {
    top: 20%;
    left: 10%;
    animation-delay: 0s;
}

.ai-particle:nth-child(2) {
    top: 60%;
    right: 15%;
    animation-delay: 2s;
}

.ai-particle:nth-child(3) {
    bottom: 30%;
    left: 20%;
    animation-delay: 4s;
}

.ai-particle:nth-child(4) {
    top: 40%;
    right: 25%;
    animation-delay: 1s;
}

/* Background AI Animation */
.ai-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: -1;
    opacity: 0.05;
}

.ai-circuit {
    position: absolute;
    width: 2px;
    height: 100px;
    background: linear-gradient(to bottom, transparent, #3D5A40, transparent);
    animation: circuitFlow 4s linear infinite;
}

.ai-circuit:nth-child(1) {
    left: 10%;
    animation-delay: 0s;
}

.ai-circuit:nth-child(2) {
    left: 30%;
    animation-delay: 1s;
}

.ai-circuit:nth-child(3) {
    left: 50%;
    animation-delay: 2s;
}

.ai-circuit:nth-child(4) {
    left: 70%;
    animation-delay: 3s;
}

.ai-circuit:nth-child(5) {
    left: 90%;
    animation-delay: 0.5s;
}

/* Startup screen styles */
.startup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: #FAF9F6 !important;
    z-index: 999999;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.ai-animation {
    width: 120px;
    height: 120px;
    margin-bottom: 30px;
    position: relative;
}

.ai-circle {
    width: 120px;
    height: 120px;
    border: 4px solid #3D5A40;
    border-radius: 50%;
    position: relative;
    animation: rotate 2s linear infinite;
}

.ai-circle::before {
    content: '';
    position: absolute;
    top: -4px;
    left: -4px;
    right: -4px;
    bottom: -4px;
    border: 4px solid transparent;
    border-top: 4px solid #D97D54;
    border-radius: 50%;
    animation: rotate 1.5s linear infinite reverse;
}

.ai-brain {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 48px;
    animation: pulse 2s ease-in-out infinite;
}

.startup-title {
    color: #3D5A40 !important;
    font-size: 42px;
    font-weight: 800;
    margin: 20px 0;
    letter-spacing: 2px;
    animation: fadeInUp 1s ease-out 0.5s both;
}

.startup-subtitle {
    color: #2C2C2C !important;
    font-size: 18px;
    opacity: 0.8;
    animation: fadeInUp 1s ease-out 1s both;
}

.loading-dots {
    display: inline-block;
    animation: fadeInUp 1s ease-out 1.5s both;
}

.loading-dots span {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #3D5A40;
    margin: 0 2px;
    animation: bounce 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
.loading-dots span:nth-child(3) { animation-delay: 0s; }

@keyframes rotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes pulse {
    0%, 100% { transform: translate(-50%, -50%) scale(1); }
    50% { transform: translate(-50%, -50%) scale(1.1); }
}

@keyframes fadeInUp {
    0% {
        opacity: 0;
        transform: translateY(30px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes bounce {
    0%, 80%, 100% {
        transform: scale(0);
    }
    40% {
        transform: scale(1);
    }
}

.fade-out {
    animation: fadeOut 0.8s ease-out forwards;
}

@keyframes fadeOut {
    0% { opacity: 1; }
    100% { opacity: 0; visibility: hidden; }
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for startup screen
if 'startup_screen_shown' not in st.session_state:
    st.session_state.startup_screen_shown = False

# Show startup screen BEFORE anything else
if not st.session_state.startup_screen_shown:
    # Create startup screen
    startup_container = st.empty()
    
    with startup_container.container():
        st.markdown("""
        <div class="startup-overlay" id="startupScreen">
            <div class="ai-animation">
                <div class="ai-circle">
                    <div class="ai-brain">🧠</div>
                </div>
            </div>
            <h1 class="startup-title">AI STARTUP ANALYZER</h1>
            <p class="startup-subtitle">Powered by Advanced AI • Analyzing Your Vision</p>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Wait for 3 seconds
    time.sleep(3)
    
    # Fade out and clear
    st.markdown("""
    <script>
    const startupScreen = document.getElementById('startupScreen');
    if (startupScreen) {
        startupScreen.classList.add('fade-out');
        setTimeout(() => {
            startupScreen.style.display = 'none';
        }, 800);
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Clear the startup screen
    startup_container.empty()
    
    # Mark as shown and rerun to show main app
    st.session_state.startup_screen_shown = True
    st.rerun()

#CSS file connection
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/style.css")

st.set_page_config(
    page_title="AI Startup Evaluation System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Add background AI animation
    st.markdown("""
    <div class="ai-background">
        <div class="ai-circuit"></div>
        <div class="ai-circuit"></div>
        <div class="ai-circuit"></div>
        <div class="ai-circuit"></div>
        <div class="ai-circuit"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Replace the old title with animated header
    st.markdown("""
    <div class="animated-header">
        <div class="ai-elements">
            <div class="ai-particle">🤖</div>
            <div class="ai-particle">⚡</div>
            <div class="ai-particle">🧠</div>
            <div class="ai-particle">🚀</div>
        </div>
        <h1 class="header-title">🚀 AI Startup Evaluation System</h1>
        <p class="header-subtitle">Hybrid AI Pipeline: Fine-tuned Models + Groq Llama 70B Enhancement</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")
        
        if st.button("🔄 Check System Health"):
            check_system_health()
        
        st.markdown("---")
        
        # Settings
        st.header("📋 Settings")
        enhance_questions = st.checkbox("Enhance Questions with Groq", value=True)
        enhance_evaluation = st.checkbox("Enhance Evaluation with Groq", value=True)
        
        st.info("💡 **Pipeline Flow:**\n1. Fine-tuned model generates questions\n2. Groq enhances questions (optional)\n3. Fine-tuned model evaluates\n4. Groq enhances evaluation (recommended)")
        
        st.markdown("---")
        
        if st.button("🧹 Clear All Data"):
            clear_all_data()

    # Initialize session state
    init_session_state()
    
    # Main workflow
    col1, col2 = st.columns([1, 1])
    
    with col1:
        step1_startup_info()
    
    with col2:
        if st.session_state.startup_info:
            display_startup_summary()
        else:
            st.info("👈 Please fill in startup information first")
    
    # Step 2: Questions
    if st.session_state.startup_info and st.session_state.questions:
        step2_answer_questions(enhance_evaluation)
    
    # Step 3: Results
    if st.session_state.evaluation_result:
        step3_display_results()

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        "startup_info": None,
        "questions": [],
        "raw_questions": [],
        "answers": [],
        "evaluation_result": None,
        "system_health": None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def check_system_health():
    """Check system health and display status"""
    try:
        with st.spinner("Checking system health..."):
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                st.session_state.system_health = health_data
                
                st.success("✅ System is healthy!")
                
                # Display detailed status
                with st.expander("📊 Detailed System Status"):
                    st.json(health_data)
                
                # Groq status
                groq_status = health_data.get("groq", {})
                if groq_status.get("groq_configured"):
                    if groq_status.get("connection_test"):
                        st.success("✅ Groq API is working")
                    else:
                        st.warning("⚠️ Groq configured but connection failed")
                else:
                    st.error("❌ Groq not configured")
            else:
                st.error(f"❌ System health check failed: {response.status_code}")
                
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Cannot connect to system: {str(e)}")
        st.info("Make sure the FastAPI server is running")

def step1_startup_info():
    """Step 1: Collect startup information"""
    st.header("📋 Step 1: Startup Information")
    
    with st.form("startup_form", clear_on_submit=False):
        name = st.text_input(
            "Startup Name *", 
            placeholder="e.g., TechFlow AI",
            help="Enter your startup's name"
        )
        
        industry = st.text_input(
            "Industry *", 
            placeholder="e.g., FinTech, EdTech, HealthTech, AgriTech",
            help="What industry does your startup operate in?"
        )
        
        pitch = st.text_area(
            "Startup Pitch *", 
            placeholder="Describe what your startup does, the problem it solves, and your unique solution. Include key metrics if available...",
            height=120,
            help="Provide a clear and comprehensive description"
        )
        
        col1_inner, col2_inner = st.columns(2)
        with col1_inner:
            founded_year = st.text_input(
                "Founded Year *", 
                placeholder="e.g., 2023",
                help="When was the startup founded?"
            )
        
        with col2_inner:
            funding = st.text_input(
                "Funding Raised *", 
                placeholder="e.g., $500K, Seed, Pre-revenue",
                help="Funding stage or amount raised"
            )
        
        submitted = st.form_submit_button("🎯 Generate Questions", use_container_width=True)
    
    if submitted:
        if not all([name, industry, pitch, founded_year, funding]):
            st.error("⚠️ Please fill in all required fields!")
        elif len(pitch) < 20:
            st.error("⚠️ Please provide a more detailed pitch (at least 20 characters)")
        else:
            generate_questions_flow(name, industry, pitch, founded_year, funding)

def generate_questions_flow(name, industry, pitch, founded_year, funding):
    """Handle the question generation flow"""
    startup_data = {
        "name": name,
        "industry": industry, 
        "pitch": pitch,
        "founded_year": founded_year,
        "funding": funding
    }
    
    with st.spinner("🤖 AI is generating tailored questions... This may take 30-60 seconds"):
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate-questions",
                json=startup_data,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Store in session state
                st.session_state.startup_info = startup_data
                st.session_state.questions = result["questions"]
                st.session_state.raw_questions = result.get("raw_questions", [])
                
                # Show success message with details
                method = result["method_used"]
                processing_time = result["processing_time"]
                
                st.success(f"✅ Generated {result['count']} questions in {processing_time:.1f}s using {method.replace('_', ' ')}")
                
                # Show methodology info
                if method.endswith("enhanced"):
                    st.info("💡 Questions were enhanced by Groq Llama 70B for better quality")
                
                st.rerun()
                
            else:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"❌ Question generation failed: {error_detail}")
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The AI might be processing a complex request.")
        except Exception as e:
            st.error(f"❌ Question generation failed: {str(e)}")

def display_startup_summary():
    """Display startup information summary"""
    st.header("📊 Startup Summary")
    
    info = st.session_state.startup_info
    
    st.markdown(f"**🏢 Name:** {info['name']}")
    st.markdown(f"**🏭 Industry:** {info['industry']}")
    st.markdown(f"**📅 Founded:** {info['founded_year']}")
    st.markdown(f"**💰 Funding:** {info['funding']}")
    
    with st.expander("📝 Full Pitch"):
        st.write(info['pitch'])
    
    # Questions status
    if st.session_state.questions:
        st.success(f"✅ {len(st.session_state.questions)} questions generated")
        
        with st.expander("👀 Preview Questions"):
            for i, q in enumerate(st.session_state.questions, 1):
                st.write(f"{i}. {q}")
    else:
        st.info("⏳ Generate questions to proceed")

def step2_answer_questions(enhance_evaluation):
    """Step 2: Answer questions"""
    st.markdown("---")
    st.header("❓ Step 2: Answer Questions")
    
    st.info("💡 Provide detailed answers for better evaluation quality")
    
    with st.form("questions_form"):
        answers = []
        
        for i, question in enumerate(st.session_state.questions, 1):
            st.subheader(f"Question {i}")
            st.write(question)
            
            answer = st.text_area(
                f"Your answer:",
                key=f"answer_{i}",
                height=100,
                placeholder="Provide a detailed answer..."
            )
            answers.append(answer)
        
        submitted = st.form_submit_button("🚀 Generate Evaluation", use_container_width=True)
    
    if submitted:
        # Validate answers
        empty_answers = [i+1 for i, ans in enumerate(answers) if not ans.strip()]
        
        if empty_answers:
            st.error(f"⚠️ Please answer all questions. Missing answers for questions: {', '.join(map(str, empty_answers))}")
        else:
            generate_evaluation(answers, enhance_evaluation)

def generate_evaluation(answers, enhance_evaluation):
    """Generate startup evaluation"""
    evaluation_data = {
        "startup": st.session_state.startup_info,
        "questions": st.session_state.questions,
        "answers": answers,
        "enhance_with_groq": enhance_evaluation
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("🔍 AI is analyzing your startup..."):
        try:
            # Update progress
            progress_bar.progress(25)
            status_text.text("📊 Fine-tuned model generating evaluation...")
            
            response = requests.post(
                f"{API_BASE_URL}/evaluate-startup",
                json=evaluation_data,
                timeout=180  # 3 minutes timeout
            )
            
            progress_bar.progress(75)
            status_text.text("🚀 Groq enhancing evaluation..." if enhance_evaluation else "📝 Finalizing evaluation...")
            
            if response.status_code == 200:
                result = response.json()
                
                progress_bar.progress(100)
                status_text.text("✅ Evaluation completed!")
                
                # Store results
                st.session_state.evaluation_result = result
                st.session_state.answers = answers
                
                # Show success message
                method = result["method_used"]
                processing_time = result["processing_time"]
                
                st.success(f"✅ Evaluation completed in {processing_time:.1f}s using {method.replace('_', ' ')}")
                
                # Clear progress indicators
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                st.rerun()
                
            else:
                progress_bar.empty()
                status_text.empty()
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"❌ Evaluation failed: {error_detail}")
                
        except requests.exceptions.Timeout:
            progress_bar.empty()
            status_text.empty()
            st.error("⏱️ Evaluation timed out. The process might take longer for complex evaluations.")
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Evaluation failed: {str(e)}")

def step3_display_results():
    """Step 3: Display evaluation results"""
    st.markdown("---")
    st.header("📈 Step 3: Evaluation Results")
    
    result = st.session_state.evaluation_result
    
    # Method indicator
    method = result["method_used"]
    if method.endswith("enhanced"):
        st.success("🚀 Enhanced with Groq Llama 70B")
    elif method.endswith("error"):
        st.warning("⚠️ Groq enhancement failed, showing fine-tuned model output")
    else:
        st.info("📊 Using fine-tuned model only")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Final Report", "🔍 Technical Details", "📋 Q&A Summary"])
    
    with tab1:
        display_final_report(result)
    
    with tab2:
        display_technical_details(result)
    
    with tab3:
        display_qa_summary()

# Add these helper functions before display_final_report
def parse_evaluation_to_table(evaluation_text):
    """Parse evaluation text into structured data and extract overall assessment"""
    if not evaluation_text:
        return pd.DataFrame(), ""
    
    # Split text into lines and find numbered criteria
    lines = evaluation_text.split('\n')
    criteria_data = []
    overall_assessment = ""
    
    current_criterion = None
    current_score = None
    current_evaluation = []
    collecting_overall = False
    overall_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for overall assessment section
        if re.search(r'overall|summary|conclusion|assessment|recommendation', line.lower()) and not re.match(r'^\d+\.\s+', line):
            collecting_overall = True
            overall_lines.append(line)
            continue
        
        if collecting_overall:
            overall_lines.append(line)
            continue
            
        # Look for numbered criteria (1. 2. 3. etc.)
        if re.match(r'^\d+\.\s+', line):
            # Save previous criterion if exists
            if current_criterion:
                criteria_data.append({
                    'Criterion': current_criterion,
                    'Score': current_score or 'N/A',
                    'Evaluation': ' '.join(current_evaluation)
                })
            
            # Extract criterion name and score
            parts = line.split(':')
            if len(parts) >= 2:
                criterion_part = parts[0]
                rest = ':'.join(parts[1:]).strip()
                
                # Extract criterion name (remove number)
                current_criterion = re.sub(r'^\d+\.\s+', '', criterion_part).strip()
                
                # Look for score in the rest
                score_match = re.search(r'(\d+(?:\.\d+)?)/10|Score:\s*(\d+(?:\.\d+)?)', rest)
                if score_match:
                    current_score = score_match.group(1) or score_match.group(2)
                else:
                    current_score = 'N/A'
                
                # Start collecting evaluation text
                current_evaluation = [rest]
            else:
                current_criterion = re.sub(r'^\d+\.\s+', '', line).strip()
                current_score = 'N/A'
                current_evaluation = []
        else:
            # Continue collecting evaluation text
            if current_criterion and line and not collecting_overall:
                current_evaluation.append(line)
    
    # Add the last criterion
    if current_criterion:
        criteria_data.append({
            'Criterion': current_criterion,
            'Score': current_score or 'N/A',
            'Evaluation': ' '.join(current_evaluation)
        })
    
    # Process overall assessment
    if overall_lines:
        overall_assessment = ' '.join(overall_lines)
    
    # If no structured data found, create a simple table
    if not criteria_data:
        # Try to extract any meaningful content
        sentences = [s.strip() for s in evaluation_text.split('.') if s.strip()]
        for i, sentence in enumerate(sentences[:10], 1):  # Limit to 10 items
            criteria_data.append({
                'Criterion': f'Point {i}',
                'Score': 'N/A',
                'Evaluation': sentence
            })
    
    return pd.DataFrame(criteria_data), overall_assessment

def generate_pdf_report(df, startup_info, result):
    """Generate PDF report with proper formatting and colors"""
    if not PDF_AVAILABLE:
        return None
    
    buffer = BytesIO()
    # Set creamy white background
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          leftMargin=0.75*inch, rightMargin=0.75*inch,
                          topMargin=1*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Title with olive color
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#808000'),  # Olive color
        alignment=1  # Center alignment
    )
    story.append(Paragraph(f"Startup Evaluation Report: {startup_info['name']}", title_style))
    story.append(Spacer(1, 12))
    
    # Startup info with olive text
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        textColor=colors.HexColor('#808000'),  # Olive color
        fontSize=11
    )
    story.append(Paragraph(f"<b>Industry:</b> {startup_info['industry']}", info_style))
    story.append(Paragraph(f"<b>Founded:</b> {startup_info['founded_year']}", info_style))
    story.append(Paragraph(f"<b>Funding:</b> {startup_info['funding']}", info_style))
    story.append(Paragraph(f"<b>Evaluation Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", info_style))
    story.append(Spacer(1, 20))
    
    # Table with proper text wrapping
    if not df.empty:
        table_data = [['Criterion', 'Score', 'Evaluation']]
        for _, row in df.iterrows():
            # Wrap text properly for PDF
            criterion = Paragraph(str(row['Criterion']), ParagraphStyle('CellStyle', 
                                 parent=styles['Normal'], fontSize=9, 
                                 textColor=colors.HexColor('#808000')))
            score = Paragraph(str(row['Score']), ParagraphStyle('CellStyle', 
                            parent=styles['Normal'], fontSize=9, 
                            textColor=colors.HexColor('#808000'), alignment=1))
            evaluation = Paragraph(str(row['Evaluation']), ParagraphStyle('CellStyle', 
                                 parent=styles['Normal'], fontSize=9, 
                                 textColor=colors.HexColor('#808000')))
            table_data.append([criterion, score, evaluation])
        
        # Adjust column widths for better text wrapping
        table = Table(table_data, colWidths=[1.8*inch, 0.8*inch, 3.4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#808000')),  # Olive header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#F5F5DC')),  # Creamy white text
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5DC')),  # Creamy white background
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#808000')),  # Olive grid lines
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def display_final_report(result):
    """Display the final evaluation report in table format with mobile responsiveness"""
    st.subheader("🎯 Comprehensive Startup Evaluation")
    
    evaluation_text = result.get("evaluation", "No evaluation available")
    
    # Parse evaluation into table format and extract overall assessment
    df, overall_assessment = parse_evaluation_to_table(evaluation_text)
    
    if not df.empty:
        st.markdown("### 📊 Evaluation Results Table")
        
        # Add comprehensive mobile-responsive CSS
        st.markdown("""
        <style>
        /* Mobile-first responsive design */
        .stDataFrame {
            font-size: 12px;
            overflow-x: auto;
            width: 100%;
        }
        
        /* Mobile devices (up to 768px) */
        @media (max-width: 768px) {
            .stDataFrame {
                font-size: 10px;
            }
            
            .stDataFrame table {
                min-width: 100%;
                font-size: 10px;
            }
            
            .stDataFrame th, .stDataFrame td {
                padding: 4px 2px !important;
                word-wrap: break-word;
                white-space: normal;
                max-width: 120px;
            }
            
            /* Make evaluation column scrollable on mobile */
            .stDataFrame td:last-child {
                max-width: 200px;
                overflow: hidden;
                text-overflow: ellipsis;
            }
        }
        
        /* Tablet devices (769px to 1024px) */
        @media (min-width: 769px) and (max-width: 1024px) {
            .stDataFrame {
                font-size: 11px;
            }
            
            .stDataFrame th, .stDataFrame td {
                padding: 6px 4px !important;
            }
        }
        
        /* Desktop devices (1025px and up) */
        @media (min-width: 1025px) {
            .stDataFrame {
                font-size: 12px;
            }
        }
        
        .stDataFrame [data-testid="stDataFrameResizeHandle"] {
            display: block;
        }
        
        .stDataFrame div[data-testid="column"] div[data-testid="stMarkdownContainer"] p {
            word-wrap: break-word;
            white-space: normal;
        }
        
        /* Mobile-responsive overall assessment */
        .overall-assessment-header {
            color: #808000;
            font-size: 18px;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .overall-assessment-box {
            background-color: #F5F5DC;
            color: #808000;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #808000;
            margin-bottom: 20px;
            font-size: 14px;
            line-height: 1.6;
            word-wrap: break-word;
        }
        
        /* Mobile adjustments for overall assessment */
        @media (max-width: 768px) {
            .overall-assessment-header {
                font-size: 16px;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            
            .overall-assessment-box {
                padding: 12px;
                font-size: 12px;
                line-height: 1.5;
                margin-bottom: 15px;
            }
        }
        
        /* Download buttons responsive layout */
        @media (max-width: 768px) {
            .stColumns {
                flex-direction: column;
            }
            
            .stColumns > div {
                width: 100% !important;
                margin-bottom: 10px;
            }
            
            .stDownloadButton button {
                width: 100%;
                font-size: 12px;
                padding: 8px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display table with mobile-optimized configuration
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=400,
            column_config={
                "Criterion": st.column_config.TextColumn(
                    "Criterion",
                    width="small",  # Smaller width for mobile
                    help="Evaluation criterion"
                ),
                "Score": st.column_config.TextColumn(
                    "Score",
                    width="small"
                ),
                "Evaluation": st.column_config.TextColumn(
                    "Assessment",  # Shorter header for mobile
                    width="large",
                    help="Scroll horizontally to view full content"
                )
            }
        )
        
        # Display Overall Assessment below the table with mobile responsiveness
        if overall_assessment:
            st.markdown('<div class="overall-assessment-header">📋 Overall Assessment</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="overall-assessment-box">{overall_assessment}</div>', unsafe_allow_html=True)
        
    else:
        # Fallback to original text display with mobile optimization
        st.markdown("### 📄 Evaluation Report")
        st.text_area(
            "",
            value=evaluation_text,
            height=400,  # Reduced height for mobile
            help="AI-generated comprehensive evaluation"
        )
    
    # Mobile-responsive download options
    st.markdown("### 📥 Download Options")
    
    # Check if we're on mobile (approximate)
    is_mobile = st.session_state.get('is_mobile', False)
    
    if st.checkbox("📱 Mobile Layout", help="Check this for better mobile experience"):
        # Stack download buttons vertically for mobile
        if st.download_button(
            label="📥 Download Report (TXT)",
            data=evaluation_text,
            file_name=f"{st.session_state.startup_info['name']}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        ):
            st.success("Report downloaded!")
        
        if not df.empty:
            csv_data = df.to_csv(index=False)
            if st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"{st.session_state.startup_info['name']}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            ):
                st.success("CSV downloaded!")
        
        # PDF download
        if not df.empty:
            try:
                if PDF_AVAILABLE:
                    pdf_data = generate_pdf_report(df, st.session_state.startup_info, result)
                    if pdf_data and st.download_button(
                        label="📄 Download PDF",
                        data=pdf_data,
                        file_name=f"{st.session_state.startup_info['name']}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    ):
                        st.success("PDF downloaded!")
                else:
                    st.button("📄 Download PDF", disabled=True, help="ReportLab not installed", use_container_width=True)
            except Exception as e:
                st.button("📄 Download PDF", disabled=True, help=f"Error: {str(e)}", use_container_width=True)
        
        # JSON download
        full_data = {
            "startup_info": st.session_state.startup_info,
            "evaluation": evaluation_text,
            "timestamp": datetime.now().isoformat()
        }
        if st.download_button(
            label="📋 Download JSON",
            data=json.dumps(full_data, indent=2),
            file_name=f"{st.session_state.startup_info['name']}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        ):
            st.success("JSON downloaded!")
    
    else:
        # Desktop layout with columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.download_button(
                label="📥 Download Report (TXT)",
                data=evaluation_text,
                file_name=f"{st.session_state.startup_info['name']}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            ):
                st.success("Report downloaded!")
        
        with col2:
            if not df.empty:
                csv_data = df.to_csv(index=False)
                if st.download_button(
                    label="📊 Download CSV",
                    data=csv_data,
                    file_name=f"{st.session_state.startup_info['name']}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                ):
                    st.success("CSV downloaded!")
        
        with col3:
            if not df.empty:
                try:
                    if PDF_AVAILABLE:
                        pdf_data = generate_pdf_report(df, st.session_state.startup_info, result)
                        if pdf_data and st.download_button(
                            label="📄 Download PDF",
                            data=pdf_data,
                            file_name=f"{st.session_state.startup_info['name']}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        ):
                            st.success("PDF downloaded!")
                    else:
                        st.button("📄 Download PDF", disabled=True, help="ReportLab not installed")
                except Exception as e:
                    st.button("📄 Download PDF", disabled=True, help=f"Error: {str(e)}")
        
        with col4:
            full_data = {
                "startup_info": st.session_state.startup_info,
                "evaluation": evaluation_text,
                "timestamp": datetime.now().isoformat()
            }
            if st.download_button(
                label="📋 Download JSON",
                data=json.dumps(full_data, indent=2),
                file_name=f"{st.session_state.startup_info['name']}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            ):
                st.success("JSON downloaded!")
    
    # Generate new evaluation button
    if st.button("🔄 Generate New Evaluation", use_container_width=True):
        st.session_state.evaluation_result = None
        st.rerun()

def display_technical_details(result):
    """Display technical details with fixed text color"""
    # Add CSS to fix text color in technical details
    st.markdown("""
    <style>
    .technical-details {
        color: #808000 !important; /* Olive color */
    }
    .technical-details h3 {
        color: #3D5A40 !important;
    }
    .technical-details .stMetric {
        color: #808000 !important;
    }
    .technical-details .stMetric > div {
        color: #808000 !important;
    }
    .technical-details .stMetric label {
        color: #808000 !important;
    }
    .technical-details .stMetric [data-testid="metric-container"] {
        color: #808000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="technical-details">', unsafe_allow_html=True)
    st.subheader("🔧 Technical Processing Details")
    
    # Processing info
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Processing Time", f"{result['processing_time']:.2f}s")
        st.metric("Method Used", result["method_used"].replace("_", " ").title())
    
    with col2:
        st.metric("Questions Processed", len(result["questions_used"]))
        st.metric("Timestamp", result["timestamp"].split("T")[1][:8])
    
    # Raw evaluation if available
    if result.get("raw_evaluation"):
        st.markdown("### 🔍 Raw Model Output")
        st.text_area(
            "Output from fine-tuned evaluation model:",
            value=result["raw_evaluation"],
            height=400,
            help="This is the raw output before Groq enhancement"
        )
        
        st.info("💡 The final report above combines this raw output with Groq Llama 70B enhancement for better structure and analysis.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_qa_summary():
    """Display Q&A summary"""
    st.subheader("📋 Questions & Answers Summary")
    
    for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers), 1):
        with st.expander(f"Q{i}: {q[:60]}{'...' if len(q) > 60 else ''}"):
            st.markdown(f"**Question:** {q}")
            st.markdown(f"**Answer:** {a}")
            
            # Word count
            word_count = len(a.split())
            if word_count < 10:
                st.warning("⚠️ Short answer - consider providing more detail")
            elif word_count > 100:
                st.success("✅ Comprehensive answer")

def clear_all_data():
    """Clear all session data"""
    if st.button("⚠️ Confirm Clear All", type="primary"):
        for key in ["startup_info", "questions", "raw_questions", "answers", "evaluation_result"]:
            if key in st.session_state:
                if key in ["questions", "raw_questions", "answers"]:
                    st.session_state[key] = []
                else:
                    st.session_state[key] = None
        
        st.success("🧹 All data cleared!")
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main()