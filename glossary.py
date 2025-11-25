"""
Shared Glossary Module
Strictly applies glossary terms to text with override mode
"""

import csv
import re
from collections import OrderedDict
import os

class GlossaryLoader:
    """Load and manage glossary for domain-specific translations"""
    
    def __init__(self, glossary_path="glossary.csv"):
        """
        Initialize glossary loader
        
        Args:
            glossary_path: Path to glossary CSV file
        """
        self.glossary = OrderedDict()
        self.load_glossary(glossary_path)
    
    def load_glossary(self, glossary_path):
        """Load glossary from CSV file"""
        if not os.path.exists(glossary_path):
            print(f"Warning: Glossary file not found at {glossary_path}")
            return
        
        try:
            with open(glossary_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, quotechar='"', skipinitialspace=True)
                for row_num, row in enumerate(reader, 1):
                    if len(row) >= 2:
                        english = row[0].strip().strip('"')
                        telugu = row[1].strip().strip('"')
                        
                        # Skip empty entries
                        if not english or not telugu:
                            continue
                        
                        # Store original case
                        self.glossary[english] = telugu
                        
                        # Store uppercase version for case-insensitive matching
                        if english.upper() != english:
                            self.glossary[english.upper()] = telugu
                        
                        # Store lowercase version for case-insensitive matching
                        if english.lower() != english:
                            self.glossary[english.lower()] = telugu
            
            # Sort by length (longest first) to match longer phrases first
            self.glossary = OrderedDict(
                sorted(self.glossary.items(), key=lambda x: len(x[0]), reverse=True)
            )
            print(f"Loaded {len(self.glossary)} glossary entries")
        except Exception as e:
            print(f"Error loading glossary: {e}")
            self.glossary = OrderedDict()
    
    def apply_glossary(self, text, strict_mode=True):
        """
        Apply glossary replacements to text (case-insensitive) with strict word boundaries
        
        Args:
            text: Input text to process
            strict_mode: If True, glossary terms override everything (default: True)
            
        Returns:
            Text with glossary terms replaced
        """
        if not self.glossary or not text:
            return text
        
        result = text
        
        # Sort by length (longest first) to match longer phrases first
        sorted_terms = sorted(self.glossary.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Replace glossary terms with word boundaries for exact matching
        for english_term, telugu_term in sorted_terms:
            if not english_term or not telugu_term:
                continue
            
            # Escape special regex characters
            escaped_term = re.escape(english_term)
            
            # Use word boundaries to ensure exact word/phrase matching
            # This prevents partial matches within words
            # \b matches word boundaries (start/end of word)
            pattern = r'\b' + escaped_term + r'\b'
            
            # Replace all occurrences, case-insensitively
            result = re.sub(pattern, telugu_term, result, flags=re.IGNORECASE)
        
        return result

# Global glossary instance
_glossary_instance = None

def get_glossary():
    """Get or create global glossary instance"""
    global _glossary_instance
    if _glossary_instance is None:
        _glossary_instance = GlossaryLoader()
    return _glossary_instance

def apply_glossary(text, glossary=None, strict_mode=True):
    """
    Apply glossary to text
    
    Args:
        text: Text to process
        glossary: GlossaryLoader instance (optional, uses global if not provided)
        strict_mode: Strict override mode (default: True)
        
    Returns:
        Text with glossary applied
    """
    if glossary is None:
        glossary = get_glossary()
    return glossary.apply_glossary(text, strict_mode)

