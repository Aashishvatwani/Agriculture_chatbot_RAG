import os
import queue
from dotenv import load_dotenv
import google.generativeai as genai
from threading import Lock

load_dotenv()

class GeminiKeyManager:
    def __init__(self, key_list=None):
        """
        Initialize the key manager with a list of API keys.
        If minimal keys are provided, it tries to load 'GOOGLE_API_KEY' from env as a fallback/starter.
        """
        self.key_queue = queue.Queue()
        self.lock = Lock()
        self.current_key = None
        
        # Load keys from argument or environment
        if key_list:
            for key in key_list:
                self.key_queue.put(key.strip())
        else:
            # Fallback: try to load multiple keys from env var, comma-separated
            env_keys = os.getenv("GOOGLE_API_KEYS_POOL")  # e.g. "KEY1,KEY2,KEY3"
            if env_keys:
                for key in env_keys.split(','):
                    if key.strip():
                        self.key_queue.put(key.strip())
            
            # Also try the standard single key if pool is empty
            if self.key_queue.empty():
                single_key = os.getenv("GOOGLE_API_KEY")
                if single_key:
                    self.key_queue.put(single_key)
        
        # Initialize the first key
        self._rotate_key()

    def _rotate_key(self):
        """Get the next key from the queue and set it as active."""
        with self.lock:
            if self.key_queue.empty():
                if self.current_key:
                     print("Warning: No more fresh keys in queue. Retrying with current key.")
                     return False
                else:
                    raise ValueError("No API keys available in the pool.")
            
            # If we had a key, put it back at the end of the queue (round-robin)
            # OR discard it if you want to perform strictly "expire and burn". 
            # Here we implement round-robin assuming quota limits might reset.
            # If you want to permanently discard invalid keys, remove this line:
            if self.current_key:
                self.key_queue.put(self.current_key)
            
            self.current_key = self.key_queue.get()
            print(f"Switched to API Key ending in ...{self.current_key[-4:]}")
            
            # Re-configure global genai with new key
            genai.configure(api_key=self.current_key)
            return True

    def get_valid_model(self, model_name='gemini-1.5-flash'):
        """
        Returns a configured GenerativeModel. 
        Wrap your generate calls with retry/rotation logic using execute_with_retry().
        """
        return genai.GenerativeModel(model_name)

    def execute_with_retry(self, func, *args, **kwargs):
        """
        Executes a function (like model.generate_content) and handles key expiration/quota errors by rotating keys.
        
        Args:
            func: The callable function (e.g., model.generate_content)
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The result of the function call.
        """
        max_retries = self.key_queue.qsize() + 1
        attempts = 0
        
        while attempts < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                # Check for common quota/auth errors
                if "429" in error_str or "quota" in error_str or "key" in error_str or "permission" in error_str:
                    print(f"Key error encountered: {e}. Rotating key...")
                    if not self._rotate_key():
                        # If rotation fails (no keys left to switch to), re-raise
                        raise e
                    attempts += 1
                else:
                    # If it's a different error (e.g. invalid input), don't verify key, just raise
                    raise e
        
        raise RuntimeError("All API keys in pool exhausted or failed.")
