"""
Receipt processing pipeline: OCR -> LLM parsing -> Classification.
"""
import os
import json
from pathlib import Path
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from app.config import settings
from app.llm import llm
from app.schemas import ReceiptExtracted, ReceiptClassification
import structlog

logger = structlog.get_logger()

# Set Tesseract command if configured
if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


class ReceiptProcessor:
    """Handles OCR and LLM-based processing of receipts."""
    
    def __init__(self):
        self.ocr_languages = settings.OCR_LANGUAGES
        
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from image or PDF using Tesseract OCR.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text
        """
        logger.info("Starting OCR extraction", file_path=file_path)
        
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext in ['.pdf']:
                return self._extract_from_pdf(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                return self._extract_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            logger.error("OCR extraction failed", error=str(e), file_path=file_path)
            raise
    
    def _extract_from_image(self, image_path: str) -> str:
        """Extract text from image file."""
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text with Tesseract
        text = pytesseract.image_to_string(
            image, 
            lang=self.ocr_languages,
            config='--psm 6'  # Assume uniform block of text
        )
        
        logger.info("OCR completed", text_length=len(text))
        return text.strip()
    
    def _extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300)
        
        texts = []
        for i, image in enumerate(images):
            logger.info("Processing PDF page", page=i+1, total_pages=len(images))
            text = pytesseract.image_to_string(
                image,
                lang=self.ocr_languages,
                config='--psm 6'
            )
            texts.append(text)
        
        full_text = "\n\n".join(texts).strip()
        logger.info("PDF OCR completed", pages=len(images), text_length=len(full_text))
        return full_text
    
    def parse_receipt_fields(self, raw_text: str) -> ReceiptExtracted:
        """
        Parse raw OCR text into structured fields using LLM.
        
        Args:
            raw_text: Raw text from OCR
            
        Returns:
            ReceiptExtracted schema
        """
        logger.info("Parsing receipt fields with LLM")
        
        # Load prompts
        system_prompt = self._load_prompt("receipt_parsing_system")
        user_prompt = self._load_prompt("receipt_parsing_user").format(raw_text=raw_text)
        
        try:
            response = llm.call(system_prompt, user_prompt)
            
            # Clean response (remove markdown code blocks if present)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            data = json.loads(response)
            return ReceiptExtracted(**data)
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response as JSON", error=str(e), response=response)
            # Return empty result
            return ReceiptExtracted(raw_confidence="low", notes=f"Parse error: {str(e)}")
        except Exception as e:
            logger.error("LLM parsing failed", error=str(e))
            return ReceiptExtracted(raw_confidence="low", notes=f"Error: {str(e)}")
    
    def classify_receipt(self, receipt_data: dict, raw_text: str) -> ReceiptClassification:
        """
        Classify receipt and check tax deduction eligibility.
        
        Args:
            receipt_data: Extracted receipt data
            raw_text: Original raw text for context
            
        Returns:
            ReceiptClassification schema
        """
        logger.info("Classifying receipt with LLM")
        
        system_prompt = self._load_prompt("classification_system")
        user_prompt = self._load_prompt("classification_user").format(
            receipt_json=json.dumps(receipt_data, ensure_ascii=False, indent=2)
        )
        
        try:
            response = llm.call(system_prompt, user_prompt)
            
            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            return ReceiptClassification(**data)
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse classification response", error=str(e))
            return ReceiptClassification(
                category="прочее",
                tax_deduction_possible="maybe",
                reasoning_short=f"Ошибка парсинга: {str(e)}"
            )
        except Exception as e:
            logger.error("Classification failed", error=str(e))
            return ReceiptClassification(
                category="прочее",
                tax_deduction_possible="maybe",
                reasoning_short=f"Ошибка: {str(e)}"
            )
    
    def generate_template(self, receipt_data: dict, classification: dict) -> dict:
        """
        Generate email template for accounting department.
        
        Args:
            receipt_data: Extracted receipt data
            classification: Classification results
            
        Returns:
            Dictionary with 'subject' and 'body'
        """
        logger.info("Generating email template with LLM")
        
        system_prompt = self._load_prompt("template_system")
        user_prompt = self._load_prompt("template_user").format(
            receipt_json=json.dumps(receipt_data, ensure_ascii=False, indent=2),
            classification_json=json.dumps(classification, ensure_ascii=False, indent=2)
        )
        
        try:
            response = llm.call(system_prompt, user_prompt)
            
            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            return data
            
        except Exception as e:
            logger.error("Template generation failed", error=str(e))
            return {
                "subject": "Заявление на возмещение расходов",
                "body": f"Прошу рассмотреть возможность возмещения расходов.\n\nОшибка генерации: {str(e)}"
            }
    
    def _load_prompt(self, prompt_name: str) -> str:
        """Load prompt from prompts directory."""
        prompts_dir = Path(__file__).parent.parent / "prompts"
        prompt_file = prompts_dir / f"{prompt_name}.txt"
        
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        else:
            logger.warning("Prompt file not found, using default", prompt_name=prompt_name)
            return self._get_default_prompt(prompt_name)
    
    def _get_default_prompt(self, prompt_name: str) -> str:
        """Get default hardcoded prompts as fallback."""
        defaults = {
            "receipt_parsing_system": """You are an expert accounting assistant. Receive raw OCR text extracted from a receipt or invoice and return JSON only (no commentary) strictly in the format described below. If any field cannot be reliably extracted, fill with null. Do not include additional keys.""",
            
            "receipt_parsing_user": """Raw OCR text:
\"\"\"
{raw_text}
\"\"\"

Return JSON with these fields:
{{
  "vendor": string | null,
  "date": "YYYY-MM-DD" | null,
  "total": float | null,
  "currency": string | null,
  "items": [{{"name": string|null, "qty": float|null, "price": float|null}}] | [],
  "tax_id": string|null,
  "payment_method": string|null,
  "raw_confidence": "low|medium|high",
  "notes": string|null
}}""",
            
            "classification_system": """You are an expert Russian accountant familiar with common rules for tax deductions and corporate expense classification. Given receipt JSON, decide category and whether it is potentially eligible for personal income tax deduction or company expense. Output JSON only.""",
            
            "classification_user": """Receipt JSON:
{receipt_json}

Return JSON:
{{
  "category": "командировочные|канцтовары|ремонт|медицинские|образование|прочее",
  "tax_deduction_possible": "yes|no|maybe",
  "reasoning_short": "2-3 sentence explanation in Russian (why yes/no/maybe)",
  "required_documents": ["list of required supporting docs"]
}}""",
            
            "template_system": """You are a professional who writes concise, formal letters to a company's accounting department. Given a receipt JSON and classification, generate a ready-to-send email body in Russian.""",
            
            "template_user": """Receipt JSON:
{receipt_json}

Classification:
{classification_json}

Return JSON:
{{
  "subject": "...",
  "body": "..."
}}"""
        }
        
        return defaults.get(prompt_name, "")


# Global instance
processor = ReceiptProcessor()
