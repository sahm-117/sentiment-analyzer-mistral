# Sentiment Analyzer - FastAPI Backend
# Created by: Olamide (Sahm-117)
# Created on: 2025-08-11
# Purpose: Sentiment analysis API using Mistral model via Ollama

from fastapi import FastAPI, Form, HTTPException
import requests
import json
from datetime import datetime
import re

app = FastAPI(
    title="Sentiment Analyzer API",
    description="AI-powered sentiment analysis using Mistral model via Ollama",
    version="1.0.0"
)

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "mistral:7b-instruct"

def clean_response(text):
    """Clean and extract sentiment from model response"""
    text = text.strip().lower()
    
    # Look for sentiment keywords
    if any(word in text for word in ['positive', 'happy', 'good', 'great', 'excellent', 'wonderful']):
        return "Positive"
    elif any(word in text for word in ['negative', 'sad', 'bad', 'terrible', 'awful', 'horrible']):
        return "Negative"
    elif any(word in text for word in ['neutral', 'mixed', 'okay', 'average']):
        return "Neutral"
    
    # If response contains just the sentiment
    if 'positive' in text:
        return "Positive"
    elif 'negative' in text:
        return "Negative"
    elif 'neutral' in text:
        return "Neutral"
    
    # Default fallback
    return text.capitalize() if text else "Neutral"

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_available_models():
    """Get list of available models from Ollama"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except requests.exceptions.RequestException:
        pass
    return []

@app.get("/")
async def root():
    """Basic health check"""
    return {
        "message": "Sentiment Analyzer API is running",
        "timestamp": datetime.now().isoformat(),
        "created_by": "Olamide (Sahm-117)",
        "model": "Mistral via Ollama"
    }

@app.get("/health")
async def health_check():
    """Detailed health check with system status"""
    ollama_status = check_ollama_service()
    available_models = get_available_models() if ollama_status else []
    
    return {
        "status": "healthy" if ollama_status else "degraded",
        "ollama_service": "running" if ollama_status else "not available",
        "available_models": available_models,
        "default_model": DEFAULT_MODEL,
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0"
    }

@app.post("/analyze/")
async def analyze_sentiment(text: str = Form(...), model: str = Form(None)):
    """
    Analyze sentiment of input text using Mistral model
    
    Args:
        text: Input text to analyze (required)
        model: Model name to use (optional, defaults to mistral:7b-instruct)
    
    Returns:
        JSON response with sentiment analysis results
    """
    # Input validation
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text input is required")
    
    text = text.strip()
    if len(text) < 3:
        raise HTTPException(status_code=400, detail="Text too short (minimum 3 characters)")
    
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (maximum 5,000 characters)")
    
    # Check Ollama service
    if not check_ollama_service():
        raise HTTPException(
            status_code=503, 
            detail="Ollama service is not available. Please ensure Ollama is running."
        )
    
    # Determine which model to use
    model_to_use = model if model else DEFAULT_MODEL
    available_models = get_available_models()
    
    # If specified model not available, use first available or default
    if available_models and model_to_use not in available_models:
        model_to_use = available_models[0]
    
    # Create sentiment analysis prompt
    prompt = f"""Analyze the sentiment of the following text and respond with ONLY one word: Positive, Negative, or Neutral.

Text: "{text}"

Sentiment:"""
    
    try:
        # Make request to Ollama
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_to_use,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent results
                    "max_tokens": 10
                }
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama API error: {response.status_code}"
            )
        
        result = response.json()
        raw_sentiment = result.get("response", "").strip()
        
        if not raw_sentiment:
            raise HTTPException(
                status_code=500,
                detail="Empty response from model"
            )
        
        # Clean and standardize the response
        cleaned_sentiment = clean_response(raw_sentiment)
        
        return {
            "sentiment": cleaned_sentiment,
            "confidence": "high" if cleaned_sentiment in ["Positive", "Negative", "Neutral"] else "medium",
            "model_used": model_to_use,
            "input_text": text,
            "input_length": len(text),
            "raw_response": raw_sentiment,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Request timeout. The model is taking too long to respond."
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to Ollama service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during sentiment analysis: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Sentiment Analyzer API...")
    print("📊 Created by: Olamide (Sahm-117)")
    print("📅 Created on: 2025-08-11")
    print("🤖 Model: Mistral via Ollama")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)