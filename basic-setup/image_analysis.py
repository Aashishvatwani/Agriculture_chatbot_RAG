import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from key_manager import GeminiKeyManager
from typing import Union

load_dotenv()

class AgriImageAnalyzer:
    def __init__(self):
        """Initialize the Gemini Vision analyzer with key rotation"""
        self.key_manager = GeminiKeyManager()
        self.model_name = 'gemini-2.5-flash'

    def analyze_image(self, image_input: Union[str, Image.Image], custom_prompt: str = None) -> str:
        """
        Analyze an agricultural image using Gemini with key rotation.
        
        Args:
            image_input: Path to the image file OR a PIL Image object
            custom_prompt: Optional specific question about the image
            
        Returns:
            str: The analysis text or error message
        """
        try:
            if isinstance(image_input, str):
                if not os.path.exists(image_input):
                    return "Error: Image file not found at the specified path."
                img = Image.open(image_input)
            elif isinstance(image_input, Image.Image):
                img = image_input
            else:
                return "Error: Invalid image input. Must be a path or PIL Image."

            # Default agricultural prompt if none provided
            if not custom_prompt:
                prompt = """
                You are an agricultural expert. Analyze this image and provide a detailed report including:
                1. Identification of the crop, plant, or soil condition shown.
                2. Detection of any visible diseases, pests, nutrient deficiencies, or physical damage.
                3. Assessment of the overall health or stage of growth.
                4. Recommended actions or treatments if issues are found.
                5. give context in less than 100 words
                Format the response clearly with headers.
                """
            else:
                prompt = custom_prompt
            
            # Generate content using Gemini with automatic retry/rotation
            def call_model():
                model = self.key_manager.get_valid_model(self.model_name)
                return model.generate_content([prompt, img])

            response = self.key_manager.execute_with_retry(call_model)
            
            if response and response.text:
                return response.text
            else:
                return "No analysis could be generated for this image."
            
        except Exception as e:
            return f"Error processing image analysis: {str(e)}"

if __name__ == "__main__":
    # Simple test execution
    analyzer = AgriImageAnalyzer()
    print("AgriImageAnalyzer initialized. Use analyze_image(path) to test.")
