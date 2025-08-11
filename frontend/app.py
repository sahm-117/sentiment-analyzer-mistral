# Sentiment Analyzer - Streamlit Frontend
# Created by: Olamide (Sahm-117)
# Created on: 2025-08-11
# Purpose: User interface for AI sentiment analysis service

import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Sentiment Analyzer",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
BACKEND_URL = "http://localhost:8000"

def check_backend_health():
    """Check if the FastAPI backend is running and healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
    except requests.exceptions.RequestException:
        pass
    return False, None

def analyze_sentiment(text, model=None):
    """Send text to backend for sentiment analysis"""
    try:
        data = {"text": text}
        if model:
            data["model"] = model
            
        response = requests.post(
            f"{BACKEND_URL}/analyze/",
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error_detail = "Unknown error"
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", error_detail)
            except:
                error_detail = response.text
            return False, {"error": f"Server error ({response.status_code}): {error_detail}"}
            
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout. The server is taking too long to respond."}
    except requests.exceptions.RequestException as e:
        return False, {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        return False, {"error": f"Unexpected error: {str(e)}"}

def get_sentiment_color(sentiment):
    """Get color for sentiment display"""
    sentiment_lower = sentiment.lower()
    if "positive" in sentiment_lower:
        return "#28a745"  # Green
    elif "negative" in sentiment_lower:
        return "#dc3545"  # Red
    else:
        return "#ffc107"  # Yellow for neutral/unknown

def get_sentiment_emoji(sentiment):
    """Get emoji for sentiment"""
    sentiment_lower = sentiment.lower()
    if "positive" in sentiment_lower:
        return "😊"
    elif "negative" in sentiment_lower:
        return "😞"
    else:
        return "😐"

def main():
    # Header
    st.title("😊 Sentiment Analyzer")
    st.markdown("**AI-powered sentiment analysis using Mistral model via Ollama**")
    
    # Created by watermark
    st.markdown("---")
    st.markdown("*Created by: Olamide (Sahm-117) | " + datetime.now().strftime("%Y-%m-%d") + "*")
    st.markdown("---")
    
    # Sidebar for system status and configuration
    with st.sidebar:
        st.header("⚙️ System Status")
        
        # Check backend health
        health_placeholder = st.empty()
        
        with st.spinner("Checking system status..."):
            is_healthy, health_data = check_backend_health()
        
        if is_healthy:
            health_placeholder.success("✅ Backend service is running")
            
            with st.expander("📊 Service Details"):
                st.json(health_data)
            
            # Model selection if multiple models available
            available_models = health_data.get("available_models", [])
            if available_models:
                selected_model = st.selectbox(
                    "🤖 Select Model:",
                    options=["default"] + available_models,
                    help="Choose which AI model to use for sentiment analysis"
                )
            else:
                selected_model = "default"
                st.warning("⚠️ No models found. Using default configuration.")
        else:
            health_placeholder.error("❌ Backend service is not available")
            selected_model = "default"
            st.error("Please ensure the FastAPI backend is running on port 8000")
            st.code("cd backend && python main.py")
        
        st.markdown("---")
        st.header("📋 How to Use")
        st.markdown("""
        1. **Enter text** in the main area
        2. **Click Analyze** to process
        3. **Review** the sentiment result
        4. **Try different** text samples
        """)
        
        st.markdown("---")
        st.header("💡 Examples")
        example_texts = [
            "I love this product! It's amazing!",
            "This is terrible and disappointing.",
            "The weather is okay today.",
            "Not sure how I feel about this."
        ]
        
        for i, example in enumerate(example_texts, 1):
            if st.button(f"Example {i}", key=f"example_{i}", use_container_width=True):
                st.session_state.example_text = example
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This tool uses the Mistral AI model hosted locally via Ollama 
        to analyze text sentiment. Results are classified as:
        
        - **😊 Positive**: Happy, good, excellent
        - **😞 Negative**: Sad, bad, terrible  
        - **😐 Neutral**: Mixed, okay, average
        
        All processing happens locally for privacy.
        """)
    
    # Main content area
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.header("📝 Text Input")
        
        # Use example text if selected
        default_text = st.session_state.get('example_text', '')
        
        user_text = st.text_area(
            "Enter text to analyze:",
            value=default_text,
            height=200,
            placeholder="Type or paste the text you want to analyze for sentiment...",
            help="Enter any text (3-5,000 characters) to analyze its sentiment.",
            key="main_text_input"
        )
        
        # Clear example text after using it
        if default_text and user_text == default_text:
            st.session_state.example_text = ''
        
        # Character count
        if user_text:
            char_count = len(user_text)
            word_count = len(user_text.split())
            
            if char_count < 3:
                st.warning(f"⚠️ Text too short: {char_count} characters (minimum: 3)")
            elif char_count > 5000:
                st.error(f"❌ Text too long: {char_count} characters (maximum: 5,000)")
            else:
                st.info(f"📊 Characters: {char_count:,} | Words: {word_count:,}")
        
        # Analyze button
        analyze_button = st.button(
            "🔍 Analyze Sentiment",
            type="primary",
            disabled=not user_text or len(user_text.strip()) < 3 or len(user_text) > 5000 or not is_healthy,
            use_container_width=True
        )
    
    with col2:
        st.header("📊 Analysis Result")
        
        if analyze_button and user_text:
            result_placeholder = st.empty()
            
            with result_placeholder.container():
                st.info("🔄 Analyzing sentiment...")
                progress_bar = st.progress(0)
                
                # Simulate progress while waiting for response
                for i in range(10):
                    time.sleep(0.05)
                    progress_bar.progress((i + 1) * 10)
                
                # Get sentiment analysis from backend
                model_param = selected_model if selected_model != "default" else None
                success, result = analyze_sentiment(user_text, model_param)
                
                progress_bar.progress(100)
                
            result_placeholder.empty()
            
            if success:
                sentiment = result.get("sentiment", "Unknown")
                confidence = result.get("confidence", "medium")
                
                # Display sentiment with color and emoji
                sentiment_color = get_sentiment_color(sentiment)
                sentiment_emoji = get_sentiment_emoji(sentiment)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, {sentiment_color}20, {sentiment_color}10); 
                            border-radius: 15px; border-left: 5px solid {sentiment_color}; margin: 20px 0;">
                    <h1 style="color: {sentiment_color}; margin: 0; font-size: 3em;">{sentiment_emoji}</h1>
                    <h2 style="color: {sentiment_color}; margin: 10px 0;">{sentiment}</h2>
                    <p style="color: #666; margin: 5px 0;">Confidence: {confidence.title()}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Analysis details
                with st.expander("🔍 Analysis Details"):
                    col_detail1, col_detail2 = st.columns(2)
                    
                    with col_detail1:
                        st.metric("Sentiment", sentiment)
                        st.metric("Confidence", confidence.title())
                    
                    with col_detail2:
                        st.metric("Input Length", f"{result.get('input_length', 0)} chars")
                        st.metric("Model Used", result.get('model_used', 'Unknown').split(':')[0].title())
                    
                    # Show raw model response
                    raw_response = result.get('raw_response', '')
                    if raw_response and raw_response != sentiment:
                        st.text_area("Raw Model Response:", value=raw_response, height=60, disabled=True)
                
                # Action buttons
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("🔄 Analyze Again", use_container_width=True):
                        st.rerun()
                
                with col_btn2:
                    if st.button("📋 Copy Result", use_container_width=True):
                        result_text = f"Text: {user_text[:100]}...\nSentiment: {sentiment} ({confidence} confidence)"
                        st.code(result_text, language=None)
                        st.success("Result ready to copy!")
                
            else:
                st.error("❌ Error analyzing sentiment")
                st.error(result.get("error", "Unknown error occurred"))
                
                # Show troubleshooting tips
                with st.expander("🔧 Troubleshooting"):
                    st.markdown("""
                    **Common issues:**
                    - Backend service not running: `python backend/main.py`
                    - Ollama service not running: `ollama serve`
                    - No models available: `ollama pull mistral:7b-instruct`
                    - Text too long or short (3-5,000 characters)
                    - Network connectivity issues
                    """)
        
        elif not is_healthy:
            st.warning("⚠️ Cannot analyze sentiment - backend service unavailable")
            st.markdown("""
            **To fix this:**
            1. Start the FastAPI backend: `python backend/main.py`
            2. Ensure Ollama is running: `ollama serve`
            3. Download Mistral model: `ollama pull mistral:7b-instruct`
            """)
        
        else:
            st.info("👈 Enter text in the left panel and click 'Analyze Sentiment' to get started!")
            
            # Show some sample results as examples
            st.markdown("### 💡 Sample Results")
            sample_results = [
                ("😊", "Positive", "#28a745"),
                ("😞", "Negative", "#dc3545"),
                ("😐", "Neutral", "#ffc107")
            ]
            
            for emoji, sentiment, color in sample_results:
                st.markdown(f"""
                <div style="padding: 10px; margin: 5px 0; background: {color}20; 
                           border-radius: 8px; border-left: 3px solid {color};">
                    <strong>{emoji} {sentiment}</strong> - Example classification
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("*This application runs entirely on your local machine for privacy and security.*")

if __name__ == "__main__":
    main()