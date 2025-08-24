from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import asyncio
import json
from datetime import datetime

# Import our modules
from model_loading import (
    get_question_model, 
    get_eval_model, 
    generate_response, 
    get_model_info,
    cleanup_models
)
from prompt import (
    build_question_prompt, 
    build_evaluation_prompt,
    build_groq_enhancement_prompt,
    build_groq_question_enhancement_prompt,
    parse_questions_from_response,
    validate_startup_data,
    format_evaluation_response
)
from groq import get_groq_client, test_groq_setup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Startup Evaluation System",
    description="Hybrid AI system using fine-tuned models + Groq Llama 70B for comprehensive startup evaluation",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class StartupInfo(BaseModel):
    name: str
    industry: str
    pitch: str
    founded_year: str
    funding: str

class EvaluationRequest(BaseModel):
    startup: StartupInfo
    questions: List[str]
    answers: List[str]
    enhance_with_groq: bool = True

class EvaluationResponse(BaseModel):
    evaluation: str
    raw_evaluation: Optional[str] = None
    questions_used: List[str]
    method_used: str
    processing_time: float
    timestamp: str

class QuestionResponse(BaseModel):
    questions: List[str]
    raw_questions: Optional[List[str]] = None
    count: int
    method_used: str
    processing_time: float

# Global variables for caching
startup_evaluations = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting AI Startup Evaluation System...")
    
    # Test Groq setup
    groq_status = test_groq_setup()
    logger.info(f"Groq status: {groq_status}")
    
    if groq_status.get("groq_configured"):
        logger.info("✅ Groq client is ready!")
    else:
        logger.warning("⚠️ Groq client not configured. Set GROQ_API_KEY environment variable.")
    
    logger.info("🚀 Application startup complete!")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_info = get_model_info()
    groq_status = test_groq_setup()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models": model_info,
        "groq": groq_status
    }

@app.post("/generate-questions", response_model=QuestionResponse)
async def generate_questions(data: StartupInfo):
    """Generate questions for startup evaluation"""
    start_time = datetime.now()
    
    try:
        # Validate input
        is_valid, error_msg = validate_startup_data(data.dict())
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Generating questions for startup: {data.name}")
        
        # Step 1: Generate questions using fine-tuned model
        prompt = build_question_prompt(data.dict())
        model = get_question_model()
        raw_output = generate_response(model, prompt, max_new_tokens=1024, temperature=0.7)
        
        # Parse questions from raw output
        raw_questions = parse_questions_from_response(raw_output)
        
        logger.info(f"Fine-tuned model generated {len(raw_questions)} questions")
        
        # Step 2: Enhance with Groq (optional fallback)
        final_questions = raw_questions
        method_used = "fine_tuned_only"
        
        try:
            groq_client = get_groq_client()
            enhancement_prompt = build_groq_question_enhancement_prompt(data.dict(), raw_questions)
            enhanced_output = groq_client.enhance_questions(enhancement_prompt)
            
            if not enhanced_output.startswith("Error:"):
                enhanced_questions = parse_questions_from_response(enhanced_output)
                if len(enhanced_questions) >= 8:  # Ensure we got good questions
                    final_questions = enhanced_questions[:10]
                    method_used = "fine_tuned_plus_groq_enhanced"
                    logger.info("Questions enhanced with Groq successfully")
                else:
                    logger.warning("Groq enhancement didn't produce enough questions, using original")
            else:
                logger.warning(f"Groq enhancement failed: {enhanced_output}")
                
        except Exception as e:
            logger.warning(f"Groq enhancement failed, using fine-tuned only: {str(e)}")
        
        # Ensure we have exactly 10 questions
        if len(final_questions) < 10:
            # Pad with generic questions if needed
            generic_questions = [
                "What is your customer acquisition strategy?",
                "How do you plan to achieve profitability?",
                "What are your biggest risks and how do you mitigate them?"
            ]
            while len(final_questions) < 10 and generic_questions:
                final_questions.append(generic_questions.pop(0))
        
        final_questions = final_questions[:10]  # Ensure exactly 10
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Questions generated successfully in {processing_time:.2f} seconds")
        
        return QuestionResponse(
            questions=final_questions,
            raw_questions=raw_questions if method_used.endswith("enhanced") else None,
            count=len(final_questions),
            method_used=method_used,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

@app.post("/evaluate-startup", response_model=EvaluationResponse)
async def evaluate_startup(data: EvaluationRequest):
    """Evaluate startup using hybrid approach"""
    start_time = datetime.now()
    
    try:
        # Validate input
        is_valid, error_msg = validate_startup_data(data.startup.dict())
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        if len(data.questions) != len(data.answers):
            raise HTTPException(status_code=400, detail="Number of questions and answers must match")
        
        if len(data.questions) < 5:
            raise HTTPException(status_code=400, detail="At least 5 questions required for evaluation")
        
        logger.info(f"Evaluating startup: {data.startup.name}")
        
        # Step 1: Generate raw evaluation using fine-tuned model
        eval_prompt = build_evaluation_prompt(data.startup.dict(), data.questions, data.answers)
        eval_model = get_eval_model()
        raw_evaluation = generate_response(eval_model, eval_prompt, max_new_tokens=4000, temperature=0.6)
        
        logger.info("Raw evaluation generated by fine-tuned model")
        
        # Step 2: Always enhance with Groq (this is the pipeline you requested)
        final_evaluation = raw_evaluation
        method_used = "fine_tuned_only"
        
        if data.enhance_with_groq:
            try:
                groq_client = get_groq_client()
                enhancement_prompt = build_groq_enhancement_prompt(
                    data.startup.dict(), 
                    data.questions, 
                    data.answers, 
                    raw_evaluation
                )
                
                enhanced_evaluation = groq_client.enhance_evaluation(enhancement_prompt)
                
                if not enhanced_evaluation.startswith("Error:"):
                    final_evaluation = enhanced_evaluation
                    method_used = "fine_tuned_plus_groq_enhanced"
                    logger.info("Evaluation enhanced with Groq successfully")
                else:
                    logger.warning(f"Groq enhancement failed: {enhanced_evaluation}")
                    final_evaluation = f"ORIGINAL MODEL EVALUATION:\n\n{raw_evaluation}\n\nNOTE: Groq enhancement failed - {enhanced_evaluation}"
                    
            except Exception as e:
                logger.warning(f"Groq enhancement failed: {str(e)}")
                final_evaluation = f"ORIGINAL MODEL EVALUATION:\n\n{raw_evaluation}\n\nNOTE: Groq enhancement failed due to: {str(e)}"
                method_used = "fine_tuned_with_groq_error"
        
        # Format the final evaluation
        final_evaluation = format_evaluation_response(final_evaluation)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Cache the result
        cache_key = f"{data.startup.name}_{hash(str(data.questions))}"
        startup_evaluations[cache_key] = {
            "result": final_evaluation,
            "timestamp": datetime.now(),
            "method": method_used
        }
        
        logger.info(f"Evaluation completed successfully in {processing_time:.2f} seconds using {method_used}")
        
        return EvaluationResponse(
            evaluation=final_evaluation,
            raw_evaluation=raw_evaluation if method_used.endswith("enhanced") else None,
            questions_used=data.questions,
            method_used=method_used,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error evaluating startup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate startup: {str(e)}")

@app.get("/cached-evaluations")
async def get_cached_evaluations():
    """Get list of cached evaluations"""
    cached = []
    for key, value in startup_evaluations.items():
        cached.append({
            "key": key,
            "timestamp": value["timestamp"].isoformat(),
            "method": value["method"]
        })
    return {"cached_evaluations": cached, "count": len(cached)}

@app.delete("/cached-evaluations")
async def clear_cached_evaluations():
    """Clear all cached evaluations"""
    count = len(startup_evaluations)
    startup_evaluations.clear()
    return {"message": f"Cleared {count} cached evaluations"}

@app.post("/test-groq")
async def test_groq():
    """Test Groq API connection"""
    try:
        groq_client = get_groq_client()
        test_result = groq_client.test_connection()
        
        if test_result:
            return {"status": "success", "message": "Groq API is working correctly"}
        else:
            return {"status": "failed", "message": "Groq API connection test failed"}
            
    except Exception as e:
        return {"status": "error", "message": f"Groq test error: {str(e)}"}

@app.post("/cleanup")
async def cleanup_system():
    """Clean up GPU memory and cached data"""
    try:
        # Clear model cache
        cleanup_models()
        
        # Clear evaluation cache
        eval_count = len(startup_evaluations)
        startup_evaluations.clear()
        
        return {
            "message": "System cleanup completed",
            "cleared_evaluations": eval_count,
            "gpu_memory_cleared": True
        }
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return {"message": f"Cleanup failed: {str(e)}", "status": "error"}

@app.get("/system-info")
async def get_system_info():
    """Get comprehensive system information"""
    model_info = get_model_info()
    groq_status = test_groq_setup()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "models": model_info,
        "groq": groq_status,
        "cached_evaluations": len(startup_evaluations),
        "available_endpoints": [
            "/generate-questions",
            "/evaluate-startup", 
            "/health",
            "/test-groq",
            "/cleanup",
            "/system-info",
            "/cached-evaluations"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)