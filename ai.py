import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from config import Config
import prompts

class AIService:
    """
    Modular AI Service abstraction supporting:
    1. Local Ollama (open-weight models running on student machine)
    2. Cloud Open-Weight APIs (Groq, OpenRouter, Together AI, HuggingFace)
    3. Intelligent Fallback / Heuristic Mode (when LLM server is unreachable)
    """

    def __init__(self):
        self.provider = Config.AI_PROVIDER
        self.ollama_url = Config.OLLAMA_BASE_URL
        self.ollama_model = Config.OLLAMA_MODEL
        self.api_key = Config.API_KEY
        self.api_url = Config.API_BASE_URL
        self.model_name = Config.MODEL_NAME

    def check_connection(self) -> Dict[str, Any]:
        """
        Check connectivity to the configured AI backend service.
        """
        if self.provider == "ollama":
            try:
                url = f"{self.ollama_url.rstrip('/')}/api/tags"
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode('utf-8'))
                        models = [m.get("name") for m in data.get("models", [])]
                        return {
                            "connected": True,
                            "provider": "Ollama (Local Open-Weight)",
                            "details": f"Connected to {self.ollama_url}. Available models: {', '.join(models) if models else 'None'}",
                            "models": models
                        }
            except Exception as e:
                return {
                    "connected": False,
                    "provider": "Ollama (Local)",
                    "details": f"Cannot connect to Ollama at {self.ollama_url}. Error: {str(e)}",
                    "suggestion": "Please ensure Ollama is installed and running (`ollama serve`)."
                }

        elif self.provider == "openai_compatible":
            if not self.api_key or self.api_key == "your_api_key_here":
                return {
                    "connected": False,
                    "provider": "Open-Weight API (Cloud)",
                    "details": "API Key is missing or default.",
                    "suggestion": "Set API_KEY in environment or .env file."
                }
            return {
                "connected": True,
                "provider": "Open-Weight API (Cloud)",
                "details": f"Configured for model {self.model_name} via {self.api_url}",
                "suggestion": "Ready for inference."
            }

        return {
            "connected": True,
            "provider": "Built-in Extractive Engine",
            "details": "Running in offline fallback mode.",
            "suggestion": "Configure Ollama or Open-Weight API key for LLM generation."
        }

    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call local Ollama instance via HTTP API."""
        url = f"{self.ollama_url.rstrip('/')}/api/generate"
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
        payload = {
            "model": self.ollama_model,
            "prompt": full_prompt,
            "stream": False
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            return res_data.get("response", "").strip()

    def _call_openai_compatible(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Cloud Open-Weight LLM Endpoint (OpenAI API standard)."""
        url = f"{self.api_url.rstrip('/')}/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.3
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            choices = res_data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return ""

    def _fallback_generator(self, prompt: str, context: str = "", system_prompt: str = "") -> str:
        """
        Smart offline fallback when AI backend is unreachable.
        Extracts high-value information from context or returns structured response.
        """
        if "Explain" in system_prompt or "simple language" in system_prompt:
            return f"### Simplified Explanation (Fallback Mode)\n\n**Concept**: {prompt}\n\n**Key Note**: *Your local AI backend (Ollama) or API key is not connected yet, but here is what was found in your study notes:*\n\n> {context[:500] if context else 'No document context available.'}\n\n*Tip: Start Ollama (`ollama run llama3.2`) to get full AI generated analogies!*"

        if context.strip():
            return f"### Answer derived from Notes (Offline Mode)\n\nBased on your uploaded notes:\n\n{context[:800]}\n\n---\n*Note: To get dynamic conversational synthesis, start your local Ollama server or configure your Open-Weight API key in settings.*"
        
        return "I couldn't connect to an active AI provider (Ollama or API). Please ensure Ollama is running (`ollama run llama3.2`) or configure an API key in `.env`."

    def generate(self, prompt: str, context: str = "", system_prompt: str = "") -> str:
        """
        Main interface for generating responses from selected AI provider.
        """
        if self.provider == "ollama":
            try:
                return self._call_ollama(prompt=prompt, system_prompt=system_prompt)
            except Exception as e:
                # Graceful fallback if Ollama call fails
                return self._fallback_generator(prompt, context, system_prompt)

        elif self.provider == "openai_compatible":
            try:
                if self.api_key and self.api_key != "your_api_key_here":
                    return self._call_openai_compatible(prompt=prompt, system_prompt=system_prompt)
                else:
                    return self._fallback_generator(prompt, context, system_prompt)
            except Exception as e:
                return self._fallback_generator(prompt, context, system_prompt)

        else:
            return self._fallback_generator(prompt, context, system_prompt)

# Global AI Service Instance
ai_service = AIService()
