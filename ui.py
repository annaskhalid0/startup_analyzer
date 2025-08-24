import streamlit as st
import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://0.0.0.0:8000"  # Change to your deployed URL

st.set_page_config(
    page_title="AI Startup Evaluation System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🚀 AI Startup Evaluation System")
    st.markdown("**Hybrid AI Pipeline: Fine-tuned Models + Groq Llama 70B Enhancement**")
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
                st.error(f"❌ Error generating questions: {error_detail}")
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The models might be loading. Please try again.")
        except Exception as e:
            st.error(f"❌ Request failed: {str(e)}")

def display_startup_summary():
    """Display startup summary"""
    st.header("📊 Startup Summary")
    info = st.session_state.startup_info
    
    st.markdown(f"""
    **Company:** {info['name']}  
    **Industry:** {info['industry']}  
    **Founded:** {info['founded_year']}  
    **Funding:** {info['funding']}  
    
    **Pitch:**  
    {info['pitch']}
    """)
    
    # Show questions if generated
    if st.session_state.questions:
        with st.expander(f"📝 Generated Questions ({len(st.session_state.questions)})"):
            for i, q in enumerate(st.session_state.questions, 1):
                st.write(f"**{i}.** {q}")

def step2_answer_questions(enhance_evaluation):
    """Step 2: Answer questions"""
    st.markdown("---")
    st.header("❓ Step 2: Answer Questions")
    st.markdown("*Please provide detailed, honest answers. Include specific metrics and data where possible.*")
    
    answers = []
    
    with st.form("answer_form"):
        # Create tabs for better organization
        if len(st.session_state.questions) >= 7:
            tab1, tab2 = st.tabs(["💼 VC Questions (1-7)", "🏭 Industry Questions (8-10)"])
            
            with tab1:
                for i, question in enumerate(st.session_state.questions[:7], 1):
                    st.markdown(f"**Question {i}:**")
                    answer = st.text_area(
                        question,
                        key=f"vc_q_{i}",
                        placeholder="Provide a detailed answer with specific examples and metrics...",
                        height=100
                    )
                    answers.append(answer)
            
            with tab2:
                for i, question in enumerate(st.session_state.questions[7:], 8):
                    st.markdown(f"**Question {i}:**")
                    answer = st.text_area(
                        question,
                        key=f"ind_q_{i}",
                        placeholder="Provide a detailed answer with specific examples and metrics...",
                        height=100
                    )
                    answers.append(answer)
        else:
            # If less than 7 questions, show all in one section
            for i, question in enumerate(st.session_state.questions, 1):
                st.markdown(f"**Question {i}:**")
                answer = st.text_area(
                    question,
                    key=f"q_{i}",
                    placeholder="Provide a detailed answer with specific examples and metrics...",
                    height=100
                )
                answers.append(answer)
        
        st.markdown("---")
        
        col1_eval, col2_eval, col3_eval = st.columns([2, 1, 1])
        
        with col1_eval:
            evaluate = st.form_submit_button("🎯 Generate Evaluation Report", use_container_width=True)
        
    
    if evaluate:
        # Check if all questions are answered
        unanswered = [i+1 for i, ans in enumerate(answers) if not ans.strip()]
        if unanswered:
            st.warning(f"⚠️ Please answer questions: {', '.join(map(str, unanswered))}")
        else:
            evaluate_startup_flow(answers, enhance_evaluation)

def evaluate_startup_flow(answers, enhance_evaluation):
    """Handle startup evaluation flow"""
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

def display_final_report(result):
    """Display the final evaluation report"""
    st.subheader("🎯 Comprehensive Startup Evaluation")
    
    evaluation_text = result.get("evaluation", "No evaluation available")
    
    # Display the evaluation in a nice format
    st.markdown("### 📄 Evaluation Report")
    st.text_area(
        "",
        value=evaluation_text,
        height=600,
        help="AI-generated comprehensive evaluation"
    )
    
    # Download options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.download_button(
            label="📥 Download Report (TXT)",
            data=evaluation_text,
            file_name=f"{st.session_state.startup_info['name']}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        ):
            st.success("Report downloaded!")
    
    with col2:
        # Create JSON export
        full_data = {
            "startup_info": st.session_state.startup_info,
            "questions": st.session_state.questions,
            "answers": st.session_state.answers,
            "evaluation": evaluation_text,
            "method_used": result["method_used"],
            "timestamp": result["timestamp"]
        }
        
        if st.download_button(
            label="📊 Download Full Data (JSON)",
            data=json.dumps(full_data, indent=2),
            file_name=f"{st.session_state.startup_info['name']}_full_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        ):
            st.success("Full data exported!")
    
    with col3:
        if st.button("🔄 Generate New Evaluation"):
            st.session_state.evaluation_result = None
            st.rerun()

def display_technical_details(result):
    """Display technical details"""
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