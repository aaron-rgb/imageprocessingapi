from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

# Load model + processor once at startup
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def caption_image(image_path: str) -> str:
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=20)
        return processor.decode(out[0], skip_special_tokens=True)
    except Exception as e:
        return f"captioning error: {e}"
