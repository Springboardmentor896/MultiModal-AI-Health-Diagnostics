import re
import json
import difflib

class SmartExtractor:
    def __init__(self, kb_path):
        self.valid_params = self._load_knowledge_base(kb_path)
        
    def _load_knowledge_base(self, path):
        valid_set = set()
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                
            for key, details in data.items():
                valid_set.add(key.lower())
                if 'aliases' in details:
                    for alias in details['aliases']:
                        valid_set.add(alias.lower())
        except Exception as e:
            print(f"Warning: Could not load KB for filtering: {e}")
            
        return valid_set

    def _is_valid_parameter_name(self, extracted_name):
        extracted_name = extracted_name.lower()
        
        if extracted_name in self.valid_params:
            return True
            
        matches = difflib.get_close_matches(extracted_name, self.valid_params, n=1, cutoff=0.85)
        return bool(matches)

    def extract(self, ocr_text):
        extracted_data = []
        lines = ocr_text.split('\n')
        
        row_pattern = re.compile(r"^(?P<name>[a-zA-Z\(\)\s\/\-\.]+?)\s+(?P<val>\d+(\.\d+)?)\s*(?P<rest>.*)$")

        for line in lines:
            line = line.strip()
            if not line: continue

            line = re.sub(r'(\d)\s+\.\s+(\d)', r'\1.\2', line)

            match = row_pattern.search(line)
            if match:
                raw_name = match.group("name").strip()
                raw_val = float(match.group("val"))
                rest = match.group("rest").strip()

                if len(raw_name) > 2 and self._is_valid_parameter_name(raw_name):
                    
                    unit = rest.split()[0] if rest else ""
                    
                    extracted_data.append({
                        "Parameter": raw_name,
                        "Value": raw_val,
                        "Unit": unit,
                        "Range": rest
                    })

        return extracted_data

def extract_parameters(ocr_text, kb_path="../data/reference_parameter.json"):
    extractor = SmartExtractor(kb_path)
    return extractor.extract(ocr_text)
