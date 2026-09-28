import os
import base64
import io
import requests
from dotenv import load_dotenv
from PIL import Image
from typing import Union

load_dotenv()


class AgriImageAnalyzer:
    def __init__(self):
        """Initialize the image analyzer using OpenRouter API"""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        self.api_base = "https://openrouter.ai/api/v1"
        # Use Qwen2.5-VL for vision/image analysis on OpenRouter
        self.vision_model = os.getenv("OPENROUTER_VISION_MODEL", "qwen/qwen-2.5-vl-7b-instruct:free")

    def _image_to_base64(self, img: Image.Image, fmt: str = "JPEG") -> str:
        """Convert a PIL Image to a base64-encoded data URI."""
        buf = io.BytesIO()
        # Convert RGBA to RGB for JPEG
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        img.save(buf, format=fmt)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        mime = "image/jpeg" if fmt.upper() == "JPEG" else f"image/{fmt.lower()}"
        return f"data:{mime};base64,{b64}"

    def analyze_image(self, image_input: Union[str, Image.Image], custom_prompt: str = None) -> str:
        """
        Analyze an agricultural image using OpenRouter vision model.

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
                prompt = (
                    "You are an agricultural expert. Analyze this image and provide a detailed report including:\n"
                    "1. Identification of the crop, plant, or soil condition shown.\n"
                    "2. Detection of any visible diseases, pests, nutrient deficiencies, or physical damage.\n"
                    "3. Assessment of the overall health or stage of growth.\n"
                    "4. Recommended actions or treatments if issues are found.\n"
                    "5. Give context in less than 100 words.\n"
                    "Format the response clearly with headers."
                )
            else:
                prompt = custom_prompt

            # Convert image to base64 data URI
            image_data_uri = self._image_to_base64(img)

            # Build the OpenRouter API request (OpenAI-compatible vision format)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "AgriSearch Bot",
            }

            payload = {
                "model": self.vision_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_data_uri},
                            },
                        ],
                    }
                ],
                "max_tokens": 1024,
            }

            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            # Extract the assistant's reply
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "No analysis could be generated for this image.")
            else:
                return "No analysis could be generated for this image."

        except Exception as e:
            return f"Error processing image analysis: {str(e)}"


if __name__ == "__main__":
    # Simple test execution
    analyzer = AgriImageAnalyzer()
    print("AgriImageAnalyzer initialized (OpenRouter). Use analyze_image(path) to test.")
