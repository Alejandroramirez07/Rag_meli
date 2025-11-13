import PyPDF2
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional
import io
import re

class PDFProductExtractor:
    """Extract product information from PDF catalogs"""
    
    def __init__(self):
        self.supported_categories = [
            "Figuras de accion", "Calzoncillos", "Medias", "Panties", 
            "Morrales", "Pijamas", "Relojes de pulso", "Bolsos"
        ]
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract all text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def parse_product_sections(self, text: str) -> List[Dict]:
        """Parse PDF text into product sections"""
        products = []
        
        # Split by common product separators
        sections = re.split(r'\n\s*\n|\d+\.\s+', text)
        
        for section in sections:
            if self._is_product_section(section):
                product = self._parse_product_data(section)
                if product:
                    products.append(product)
        
        return products
    
    def _is_product_section(self, text: str) -> bool:
        """Check if text section contains product information"""
        # Look for product indicators
        indicators = [
            'precio', 'código', 'sku', 'producto', 'descripción',
            'título', 'características', 'especificaciones'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in indicators) and len(text.strip()) > 50
    
    def _parse_product_data(self, section: str) -> Optional[Dict]:
        """Parse individual product data from text section"""
        try:
            product = {}
            lines = [line.strip() for line in section.split('\n') if line.strip()]
            
            # Extract title (usually first meaningful line)
            if lines:
                product['title'] = lines[0]
            
            # Extract price
            price_pattern = r'\$?\s*(\d+[.,]\d+|\d+)'
            prices = re.findall(price_pattern, section)
            if prices:
                product['price'] = prices[0]
            
            # Extract code/SKU
            code_patterns = [
                r'código:\s*(\w+)',
                r'sku:\s*(\w+)',
                r'referencia:\s*(\w+)',
                r'código\s+(\w+)'
            ]
            for pattern in code_patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    product['code'] = match.group(1)
                    break
            
            # Extract category based on keywords
            product['category'] = self._detect_category(section)
            
            # Extract specifications
            product['specifications'] = self._extract_specifications(section)
            
            return product if product.get('title') else None
            
        except Exception as e:
            st.warning(f"Error parsing product section: {e}")
            return None
    
    def _detect_category(self, text: str) -> str:
        """Detect product category from text"""
        text_lower = text.lower()
        
        category_keywords = {
            "Celulares y Smartphones": [
            'smartphone', 'celular', 'iphone', 'samsung', 'xiaomi',
            'motorola', 'oppo', 'realme', 'pixel', 'android', 'ios',
            '5g', '4g', 'teléfono', 'móvil', 'mobile', 'galaxy',
            'redmi', 'reno', 'snapdragon', 'mediatek', 'batería',
            'pantalla', 'cámara', 'ram', 'almacenamiento'],
            "Figuras de accion": ['figura', 'acción', 'articulado', 'coleccionable', 'mcfarlane', 'neca', 'bandai'],
            "Calzoncillos": ['boxer', 'calzoncillo', 'tanga', 'ropa interior', 'algodón', 'microfibra'],
            "Medias": ['media', 'calcetín', 'sock', 'tobillera', 'baleta'],
            "Panties": ['panty', 'pantie', 'cachetero', 'faja', 'control'],
            "Morrales": ['morral', 'mochila', 'bolso', 'laptop', 'portátil'],
            "Relojes de pulso": ['reloj', 'pulsera', 'cronógrafo', 'analógico', 'digital'],
            "Bolsos": ['bolso', 'cartera', 'mano', 'cuero', 'sintético']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "Otros"
    
    def _extract_specifications(self, text: str) -> Dict:
        """Extract product specifications"""
        specs = {}
        text_lower = text.lower()
        
        # Material detection
        materials = ['algodón', 'poliéster', 'microfibra', 'pvc', 'plástico', 'metal', 'cuero']
        for material in materials:
            if material in text_lower:
                specs['material'] = material
                break
        
        # Size detection
        size_pattern = r'talla\s*:\s*(\w+)|talla\s+(\w+)|size\s*:\s*(\w+)'
        size_match = re.search(size_pattern, text_lower)
        if size_match:
            specs['size'] = size_match.group(1) or size_match.group(2) or size_match.group(3)
        
        # Color detection
        color_pattern = r'color\s*:\s*(\w+)|color\s+(\w+)'
        color_match = re.search(color_pattern, text_lower)
        if color_match:
            specs['color'] = color_match.group(1) or color_match.group(2)
        
        return specs

def process_pdf_catalog(pdf_file) -> pd.DataFrame:
    """Main function to process PDF catalog and return DataFrame"""
    extractor = PDFProductExtractor()
    
    # Extract text from PDF
    text = extractor.extract_text_from_pdf(pdf_file)
    
    # Parse products
    products = extractor.parse_product_sections(text)
    
    # Convert to DataFrame
    if products:
        df = pd.DataFrame(products)
        return df
    else:
        raise Exception("No products found in PDF")