import json
import os
import re

class ParameterInterpreter:
    def __init__(self, ref_params_path):
        self.kb = self._load_json(ref_params_path)
        self.alias_map = self._build_alias_map()
        
    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {}

    def _build_alias_map(self):
        alias_map = {}
        for canonical_name, data in self.kb.items():
            alias_map[canonical_name.lower()] = canonical_name
            if 'aliases' in data:
                for alias in data['aliases']:
                    alias_map[alias.lower()] = canonical_name
        return alias_map

    def normalize_name(self, raw_name):
        """Matches OCR name to Canonical JSON key."""
        raw_lower = raw_name.lower().strip()
        clean_raw = re.sub(r'[^\w\s]', '', raw_lower)
        
        if clean_raw in self.alias_map:
            return self.alias_map[clean_raw]

        sorted_aliases = sorted(self.alias_map.keys(), key=len, reverse=True)
        
        for alias in sorted_aliases:
            if re.search(rf"\b{re.escape(alias)}\b", raw_lower) or \
               re.search(rf"\b{re.escape(alias)}\b", clean_raw):
                return self.alias_map[alias]

        return None

    def _parse_ocr_range(self, range_str):
        if not range_str or "unavailable" in range_str.lower():
            return None, None
        try:
            dash_match = re.search(r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)', range_str)
            if dash_match: return float(dash_match.group(1)), float(dash_match.group(2))
            if '<' in range_str:
                val = re.search(r'(\d+(?:\.\d+)?)', range_str)
                if val: return 0.0, float(val.group(1))
        except:
            pass
        return None, None

    def analyze(self, extracted_data):
        analyzed_data = []
        
        for item in extracted_data:
            canonical_name = self.normalize_name(item['Parameter'])
            
            if canonical_name:
                item['Standard_Name'] = canonical_name
                ref_data = self.kb[canonical_name]
                ref_min, ref_max = ref_data.get('min'), ref_data.get('max')
                item['Standard_Unit'] = ref_data.get('unit', item['Unit'])
                source = "Standard"
            else:
                item['Standard_Name'] = item['Parameter']
                ref_min, ref_max = None, None
                item['Standard_Unit'] = item['Unit']
                source = "Unknown"

            val = item['Value']
            ocr_range = item.get('Range', 'Unavailable')
            
            status = "Normal"
            flag = "Within Limits"

            if ref_min is None:
                ref_min, ref_max = self._parse_ocr_range(ocr_range)
                source = "Report"

            if ref_min is not None and ref_max is not None:
                if val < ref_min:
                    status = "Abnormal"
                    flag = "Low"
                elif val > ref_max:
                    status = "Abnormal"
                    flag = "High"
                else:
                    status = "Normal"
                    flag = "Within Limits"
                
                if source == "Report":
                    flag += f" (Ref: {ocr_range})"
            else:
                flag = "Range Unavailable"
                if source == "Unknown":
                    status = "Review"

            item['Status'] = status
            item['Flag'] = flag
            
            analyzed_data.append(item)
            
        return analyzed_data
