import os
from groq import Groq
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq client with API key"""
        # Method 1: Use parameter
        # Method 2: Use environment variable
        # Method 3: Use hardcoded key (not recommended for production)
        
        self.api_key = (
            api_key or 
            os.getenv('GROQ_API_KEY') or
            "gsk_YOUR_ACTUAL_GROQ_API_KEY_HERE"  # 🔥 Replace with your actual key
        )
        
        if not self.api_key or self.api_key == "gsk_YOUR_ACTUAL_GROQ_API_KEY_HERE":
            raise ValueError(
                "❌ Groq API Key not found! Please:\n"
                "1. Set environment variable: export GROQ_API_KEY='your_key'\n"
                "2. Or replace the hardcoded key in groq_client.py\n"
                "3. Get your key from: https://console.groq.com/"
            )
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-70b-versatile"
        
        logger.info(f"🚀 Groq client initialized with key: {self.api_key[:8]}...{self.api_key[-4:]}")

    def enhance_evaluation(self, prompt: str, max_retries: int = 3) -> str:
        """Call Groq API to enhance evaluation with retry logic"""
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Groq API (attempt {attempt + 1}/{max_retries})...")
                
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model=self.model,
                    temperature=0.3,
                    max_tokens=3000,
                    top_p=0.9,
                    stream=False
                )
                
                response = chat_completion.choices[0].message.content
                
                if response and len(response.strip()) > 50:
                    logger.info("Groq API call successful")
                    return response.strip()
                else:
                    logger.warning("Groq returned empty or very short response")
                    if attempt == max_retries - 1:
                        return "Error: Groq returned insufficient content"
                
            except Exception as e:
                logger.error(f"Groq API error (attempt {attempt + 1}): {str(e)}")
                
                if attempt == max_retries - 1:
                    return f"Error: Failed to get enhanced evaluation after {max_retries} attempts. Last error: {str(e)}"
                
                # Wait before retrying (exponential backoff)
                wait_time = (2 ** attempt) + 1
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        return "Error: Maximum retries exceeded"

    def enhance_questions(self, prompt: str, max_retries: int = 3) -> str:
        """Call Groq API to enhance questions with retry logic"""
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Groq API for question enhancement (attempt {attempt + 1}/{max_retries})...")
                
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model=self.model,
                    temperature=0.4,
                    max_tokens=1500,
                    top_p=0.9,
                    stream=False
                )
                
                response = chat_completion.choices[0].message.content
                
                if response and len(response.strip()) > 50:
                    logger.info("Groq question enhancement successful")
                    return response.strip()
                else:
                    logger.warning("Groq returned empty or very short response for questions")
                    if attempt == max_retries - 1:
                        return "Error: Groq returned insufficient content"
                
            except Exception as e:
                logger.error(f"Groq API error for questions (attempt {attempt + 1}): {str(e)}")
                
                if attempt == max_retries - 1:
                    return f"Error: Failed to enhance questions after {max_retries} attempts. Last error: {str(e)}"
                
                # Wait before retrying
                wait_time = (2 ** attempt) + 1
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        return "Error: Maximum retries exceeded"

    def test_connection(self) -> bool:
        """Test connection to Groq API"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": "Hello! Just testing the connection. Please respond with 'Connection successful!'"
                    }
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=50
            )
            
            response = chat_completion.choices[0].message.content
            logger.info(f"Groq connection test response: {response}")
            
            return "successful" in response.lower()
            
        except Exception as e:
            logger.error(f"Groq connection test failed: {str(e)}")
            return False

    def get_model_info(self) -> dict:
        """Get information about the Groq model being used"""
        return {
            "model": self.model,
            "provider": "Groq",
            "api_key_set": bool(self.api_key),
            "api_key_preview": self.api_key[:8] + "..." if self.api_key else None
        }

# Singleton instance
_groq_client = None

def get_groq_client(api_key: Optional[str] = None) -> GroqClient:
    """Get singleton Groq client instance"""
    global _groq_client
    
    if _groq_client is None:
        _groq_client = GroqClient(api_key)
    
    return _groq_client

def test_groq_setup() -> dict:
    """Test Groq setup and return status"""
    try:
        client = get_groq_client()
        connection_ok = client.test_connection()
        
        return {
            "groq_configured": True,
            "connection_test": connection_ok,
            "model_info": client.get_model_info(),
            "status": "ready" if connection_ok else "configured_but_connection_failed"
        }
        
    except Exception as e:
        return {
            "groq_configured": False,
            "error": str(e),
            "status": "error",
            "suggestion": "Please set GROQ_API_KEY environment variable"
        }