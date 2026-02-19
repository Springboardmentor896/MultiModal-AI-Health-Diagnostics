import os
import json
import hashlib
from google import genai
from google.genai import types

class RecommendationEngine:
    def __init__(self, api_key=None, cache_file=None, fallback_file=None):
        self.cache_file = cache_file or "data/rec_cache.json"
        self.fallback_file = fallback_file
        self.cache = self._load_cache()
        self.fallback_kb = self._load_fallback()
        
        key = api_key or os.getenv("GOOGLE_API_KEY")
        if key:
            self.client = genai.Client(api_key=key)
        else:
            self.client = None

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def _load_fallback(self):
        if self.fallback_file and os.path.exists(self.fallback_file):
            try:
                with open(self.fallback_file, 'r') as f: return json.load(f)
            except: 
                print("⚠️ Failed to load Fallback KB")
        return {}

    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️ Cache Save Error: {e}")

    def _generate_cache_key(self, risks, profile):
        risk_str = ",".join(sorted([r['Condition'] for r in risks]))
        raw_key = f"{profile['age']}-{profile['gender']}-{profile['is_pregnant']}-{risk_str}"
        return hashlib.md5(raw_key.encode()).hexdigest()

    def _get_fallback_advice(self, risks):
        """Generates advice from local JSON if API fails"""
        print("   ⚠️ Using Local Fallback KB")
        rec = {"diet": [], "lifestyle": [], "medical": []}
        
        conditions = self.fallback_kb.get('conditions', {})
        for risk in risks:
            cond_name = risk['Condition']
            # Find matching key in KB
            matched = False
            for k, v in conditions.items():
                if k in cond_name:
                    rec['diet'].extend(v.get('diet', []))
                    rec['lifestyle'].extend(v.get('lifestyle', []))
                    rec['medical'].extend(v.get('medical', []))
                    matched = True
                    break
            
            if not matched:
                rec['medical'].append(f"Consult doctor regarding {cond_name}")

        # Default advice if empty
        if not any(rec.values()):
            rec['medical'] = ["Consult your physician for interpretation."]
            
        return rec

    def generate_recommendations(self, risks, refined_data, profile):
        # 1. CHECK CACHE (Fast & Free)
        cache_key = self._generate_cache_key(risks, profile)
        if cache_key in self.cache:
            print("   ⚡ (Cache Hit) Returning saved recommendations.")
            return self.cache[cache_key]

        # 2. CHECK CLIENT
        if not self.client:
            return self._get_fallback_advice(risks)

        # 3. PREPARE PROMPT
        abnormalities = [
            f"{d['Standard_Name']}: {d['Value']} {d['Unit']} ({d['Flag']})" 
            for d in refined_data if d['Status'] == 'Abnormal'
        ]
        
        prompt = f"""
        Act as a Medical Advisor.
        Patient: {profile['age']} year old {profile['gender']}, Pregnant: {profile['is_pregnant']}.
        Risks Identified: {[r['Condition'] for r in risks]}
        Abnormal Labs: {", ".join(abnormalities)}
        
        Task: Provide specific recommendations in JSON format with keys: 'diet', 'lifestyle', 'medical'.
        Keep it concise (3 bullet points per category).
        """

        try:
            print("   🌐 (API Call) Querying Gemini 2.5 Flash...")
            # --- MODEL NAME UPDATED HERE ---
            response = self.client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json'
                )
            )
            
            if response.parsed:
                result = response.parsed
            else:
                result = json.loads(response.text)
            
            # Save to Cache
            self.cache[cache_key] = result
            self._save_cache()
            return result
            
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            return self._get_fallback_advice(risks)
