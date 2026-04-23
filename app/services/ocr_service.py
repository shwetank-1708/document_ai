from pathlib import Path
from typing import List
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR

ocr_engine = PaddleOCR(use_angle_cls=True, lang="en")

def extract_text_from_image(image_path: str) -> str:
    # Load image and convert to RGB for better OCR quality
    try:
        image = Image.open(image_path).convert("RGB")
        image_np = np.array(image)
    except Exception:
        # Fallback to direct path if image loading fails
        image_np = image_path
    
    # Run OCR
    result = ocr_engine.ocr(image_np)
    
    extracted_lines: List[str] = []

    if not result:
        return ""
    
    # Extract text from OCRResult objects
    for ocr_result in result:
        try:
            # OCRResult is a dictionary-like object
            # Access rec_texts which contains the recognized text
            if hasattr(ocr_result, 'rec_texts'):
                # It's an OCRResult object with rec_texts attribute
                texts = ocr_result.rec_texts
                if texts:
                    extracted_lines.extend(texts)
            elif isinstance(ocr_result, dict) and 'rec_texts' in ocr_result:
                # Or it might be a dict
                texts = ocr_result['rec_texts']
                if texts:
                    extracted_lines.extend(texts)
        except (IndexError, TypeError, AttributeError, KeyError) as e:
            print(f"Error parsing OCR result: {e}")
            continue

    return "\n".join(extracted_lines).strip()

def convert_pdf_to_images(pdf_path: str, output_dir: str = "data/uploads") -> List[str]:
    pdf_file = fitz.open(pdf_path)
    image_paths = []
    pdf_stem = Path(pdf_path).stem

    for page_num in range(len(pdf_file)):
        page = pdf_file[page_num]
        pix = page.get_pixmap()
        image_path = Path(output_dir) / f"{pdf_stem}_page_{page_num + 1}.png"
        pix.save(str(image_path))
        image_paths.append(str(image_path))

    pdf_file.close()
    return image_paths

def extract_text_from_pdf(pdf_path: str) -> str:
    image_paths = convert_pdf_to_images(pdf_path)
    all_text = []

    for image_path in image_paths:
        page_text = extract_text_from_image(image_path)
        if page_text:
            all_text.append(page_text)

    return "\n\n".join(all_text).strip()

def extract_text(file_path: str) -> str:
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext in [".png", ".jpg", ".jpeg", ".webp"]:
        text = extract_text_from_image(file_path)
    elif file_ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    return text
