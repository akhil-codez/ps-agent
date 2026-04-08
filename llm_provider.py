import os
import logging
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Unified LLM provider with automatic fallback.
    Priority: Gemini (primary) → Groq Mixtral (fallback)
    
    Usage:
        llm = LLMProvider()
        response = llm.generate("Your prompt here")
    """
    
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY', '')
        self.groq_key = os.getenv('GROQ_API_KEY', '')
        self.groq_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self._gemini_configured = False
        self._groq_client = None
        
        self._setup_providers()
    
    def _setup_providers(self):
        """Initialize both LLM providers"""
        logger.info("=== LLM Provider Diagnostics ===")
        logger.info(f"GEMINI_API_KEY present: {bool(self.gemini_key)}")
        logger.info(f"GROQ_API_KEY present: {bool(self.groq_key)}")
        logger.info(f"GEMINI_API_KEY length: {len(self.gemini_key) if self.gemini_key else 0}")
        logger.info(f"GROQ_API_KEY length: {len(self.groq_key) if self.groq_key else 0}")
        
        if self.gemini_key:
            logger.info(f"GEMINI_API_KEY prefix: {self.gemini_key[:10]}...")
        else:
            logger.warning("GEMINI_API_KEY is EMPTY or None")
            
        if self.groq_key:
            logger.info(f"GROQ_API_KEY prefix: {self.groq_key[:10]}...")
        else:
            logger.warning("GROQ_API_KEY is EMPTY or None")
        
        # Setup Gemini
        if GEMINI_AVAILABLE:
            logger.info(f"GEMINI_AVAILABLE package: True")
        else:
            logger.warning("GEMINI_AVAILABLE package: False")
        
        if GEMINI_AVAILABLE and self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self._gemini_configured = True
                logger.info("✓ Gemini configured successfully")
            except Exception as e:
                logger.warning(f"✗ Gemini configuration failed: {e}")
        else:
            if not GEMINI_AVAILABLE:
                logger.warning("✗ Gemini skipped: package not available")
            if not self.gemini_key:
                logger.warning("✗ Gemini skipped: GEMINI_API_KEY is empty")
        
        # Setup Groq
        if GROQ_AVAILABLE:
            logger.info(f"GROQ_AVAILABLE package: True")
        else:
            logger.warning("GROQ_AVAILABLE package: False")
        
        if GROQ_AVAILABLE and self.groq_key and self.groq_key != 'gsk_your_groq_api_key_here':
            try:
                self._groq_client = Groq(api_key=self.groq_key)
                logger.info("✓ Groq configured successfully")
            except Exception as e:
                logger.warning(f"✗ Groq configuration failed: {e}")
        else:
            if not GROQ_AVAILABLE:
                logger.warning("✗ Groq skipped: package not available")
            elif not self.groq_key:
                logger.warning("✗ Groq skipped: GROQ_API_KEY is empty")
            elif self.groq_key == 'gsk_your_groq_api_key_here':
                logger.warning("✗ Groq skipped: placeholder key detected")
    
    def generate(self, prompt: str, language: str = 'english', **kwargs) -> str:
        """
        Generate response with automatic fallback.
        
        Args:
            prompt: The prompt to send to the LLM
            language: 'english' or 'malayalam' (generates directly in the language)
            
        Returns:
            str: Generated response text
            
        Raises:
            Exception: If both providers fail
        """
        logger.info("=== Generate Request ===")
        logger.info(f"Gemini configured: {self._gemini_configured}")
        logger.info(f"Groq client available: {bool(self._groq_client)}")
        
        # Try Gemini first
        if self._gemini_configured:
            try:
                response = self._generate_gemini(prompt, language=language, **kwargs)
                logger.info("Response generated via Gemini")
                return response
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a quota/rate limit error
                if '429' in error_msg or 'quota' in error_msg.lower() or 'rate' in error_msg.lower():
                    logger.warning(f"Gemini quota exceeded ({e}), trying Groq fallback...")
                else:
                    logger.warning(f"Gemini error ({e}), trying Groq fallback...")
        
        # Fallback to Groq
        if self._groq_client:
            try:
                response = self._generate_groq(prompt, language=language, **kwargs)
                logger.info("Response generated via Groq (fallback)")
                return response
            except Exception as e:
                logger.error(f"Groq also failed: {e}")
                raise Exception(f"Both LLM providers failed. Gemini: unavailable/quota, Groq: {e}")
        
        # No fallback available
        if self._gemini_configured:
            raise Exception(f"Gemini failed: {e}")
        else:
            raise Exception("No LLM provider configured. Set GEMINI_API_KEY or GROQ_API_KEY in .env")
    
    def _generate_gemini(self, prompt: str, language: str = 'english', **kwargs) -> str:
        """Generate response using Gemini"""
        from google.generativeai import GenerativeModel
        
        model_name = kwargs.get('model', 'gemini-2.5-flash')
        model = GenerativeModel(model_name)
        
        # Build messages for language-specific generation
        messages = []
        
        # Add system instruction for Malayalam
        if language == 'malayalam':
            messages.append({
                "role": "user",
                "parts": [{"text": "You are a helpful assistant that responds in Malayalam. Use Malayalam script (മലയാളം) and preserve all formatting, line breaks, bullets, and structure in your response. Do not translate code blocks, technical terms, or proper nouns."}]
            })
        
        messages.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        generation_config = kwargs.get('generation_config', None)
        
        if generation_config:
            response = model.generate_content(messages, generation_config=generation_config)
        else:
            response = model.generate_content(messages)
        
        return response.text
    
    def _generate_groq(self, prompt: str, language: str = 'english', **kwargs) -> str:
        """Generate response using Groq Mixtral"""
        if not self._groq_client:
            raise Exception("Groq client not initialized")
        
        model = kwargs.get('model', self.groq_model)
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2048)
        
        # Build messages for language-specific generation
        messages = []
        
        # Add system message for Malayalam
        if language == 'malayalam':
            messages.append({
                "role": "system",
                "content": "You are a helpful assistant that responds in Malayalam. Use Malayalam script (മലയാളം) and preserve all formatting, line breaks, bullets, and structure in your response. Do not translate code blocks, technical terms, or proper nouns."
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        chat_completion = self._groq_client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return chat_completion.choices[0].message.content
    
    def generate_with_metadata(self, prompt: str, **kwargs) -> dict:
        """
        Generate response with provider metadata.
        
        Returns:
            dict: {
                'text': response,
                'provider': 'gemini' or 'groq',
                'fallback_used': bool,
                'model': model used
            }
        """
        result = {
            'provider': 'unknown',
            'fallback_used': False,
            'model': kwargs.get('model', 'gemini-2.5-flash')
        }
        
        # Try Gemini first
        if self._gemini_configured:
            try:
                result['text'] = self._generate_gemini(prompt, **kwargs)
                result['provider'] = 'gemini'
                result['model'] = kwargs.get('model', 'gemini-2.5-flash')
                return result
            except Exception as e:
                if '429' not in str(e) and 'quota' not in str(e).lower():
                    # Non-quota error, don't fallback
                    raise
                result['fallback_used'] = True
        
        # Fallback to Groq
        if self._groq_client:
            result['text'] = self._generate_groq(prompt, **kwargs)
            result['provider'] = 'groq'
            result['model'] = self.groq_model
            return result
        
        raise Exception("No LLM provider available")
    
    def is_gemini_available(self) -> bool:
        """Check if Gemini is configured"""
        return self._gemini_configured
    
    def is_groq_available(self) -> bool:
        """Check if Groq is configured"""
        return self._groq_client is not None
    
    def get_status(self) -> dict:
        """Get status of both providers"""
        return {
            'gemini': {
                'configured': self._gemini_configured,
                'has_key': bool(self.gemini_key)
            },
            'groq': {
                'configured': self._groq_client is not None,
                'has_key': bool(self.groq_key and self.groq_key != 'gsk_your_groq_api_key_here'),
                'model': self.groq_model
            }
        }


# Global instance (lazy initialization)
_llm_provider = None

def get_llm_provider() -> LLMProvider:
    """Get or create the global LLM provider instance"""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProvider()
    return _llm_provider


if __name__ == "__main__":
    print("=== LLM Provider Test ===\n")
    
    provider = LLMProvider()
    status = provider.get_status()
    
    gemini_status = "[OK]" if status['gemini']['configured'] else "[X]"
    groq_status = "[OK]" if status['groq']['configured'] else "[X]"
    
    print(f"Gemini: {gemini_status}")
    print(f"Groq: {groq_status} ({status['groq']['model']})")
    print()
    
    # Test generation
    if status['gemini']['configured'] or status['groq']['configured']:
        print("Testing generation...")
        try:
            response = provider.generate("Say 'Hello from LLM Provider!' in exactly those words.")
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No LLM provider configured")
    
    print("\n=== Test Complete ===")
