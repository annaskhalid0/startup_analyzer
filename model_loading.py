import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import os
import logging

logger = logging.getLogger(__name__)

BASE_MODEL = "meta-llama/Meta-Llama-3-8B"
QUESTION_ADAPTER = "saimqureshi656/startups-question-generation"
EVAL_ADAPTER = "saimqureshi656/llama3-8b-startup-evaluator-lora"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Global variables to cache models
_tokenizer = None
_question_model = None
_eval_model = None

def get_bnb_config():
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        logger.info("Loading tokenizer...")
        _tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL, 
            use_auth_token=True, 
            use_fast=False
        )
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token
        logger.info("Tokenizer loaded successfully!")
    return _tokenizer

def get_question_model():
    global _question_model
    if _question_model is None:
        logger.info("Loading question generation model...")
        tokenizer = get_tokenizer()  # Ensure tokenizer is loaded
        
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=get_bnb_config(),
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        _question_model = PeftModel.from_pretrained(base_model, QUESTION_ADAPTER)
        logger.info("Question model loaded successfully!")
    return _question_model

def get_eval_model():
    global _eval_model
    if _eval_model is None:
        logger.info("Loading evaluation model...")
        tokenizer = get_tokenizer()  # Ensure tokenizer is loaded
        
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=get_bnb_config(),
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        _eval_model = PeftModel.from_pretrained(base_model, EVAL_ADAPTER)
        logger.info("Evaluation model loaded successfully!")
    return _eval_model

def generate_response(model, prompt: str, max_new_tokens: int = 1024, temperature: float = 0.7) -> str:
    """Generate response from model with proper token handling"""
    tokenizer = get_tokenizer()
    
    try:
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids=input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
                repetition_penalty=1.1,
                length_penalty=1.0,
            )
        
        # Extract only the generated tokens (excluding the input)
        generated_tokens = outputs[0][len(input_ids[0]):]
        response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"Error generating response: {str(e)}"

def cleanup_models():
    """Free up GPU memory by clearing models"""
    global _question_model, _eval_model, _tokenizer
    
    if _question_model is not None:
        del _question_model
        _question_model = None
    
    if _eval_model is not None:
        del _eval_model
        _eval_model = None
    
    if _tokenizer is not None:
        del _tokenizer
        _tokenizer = None
    
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    logger.info("Models cleaned up successfully!")

def get_model_info():
    """Get information about loaded models"""
    return {
        "base_model": BASE_MODEL,
        "question_adapter": QUESTION_ADAPTER,
        "eval_adapter": EVAL_ADAPTER,
        "device": DEVICE,
        "cuda_available": torch.cuda.is_available(),
        "models_loaded": {
            "tokenizer": _tokenizer is not None,
            "question_model": _question_model is not None,
            "eval_model": _eval_model is not None
        }
    }