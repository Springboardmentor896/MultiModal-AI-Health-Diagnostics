import os
import sys
from dotenv import load_dotenv

# Import modules
from ingestion.images_parser import extract_text
from extraction.parameter_extraction import extract_parameters
from extraction.patient_info_extractor import extract_patient_info
from models.parameter_interpreter import ParameterInterpreter
from models.context_analyzer import ContextAnalyzer
from models.pattern_recognition import PatternRecognizer
from models.recommendation_engine import RecommendationEngine
from models.report_synthesizer import ReportSynthesizer
from models.qa_engine import QAEngine

load_dotenv()

class MedicalAgentOrchestrator:
    def __init__(self, data_dir=None, api_key=None, ollama_model="llama3"):
        # --- PATH LOGIC ---
        # 1. Determine Project Root (Go up 2 levels from models/main_orchestrator.py)
        current_file = os.path.abspath(__file__)
        models_dir = os.path.dirname(current_file)
        project_root = os.path.dirname(models_dir)
        
        # 2. Define Paths based on your structure
        self.ref_params_path = os.path.join(project_root, "validation", "reference_parameter.json")
        self.rec_kb_path = os.path.join(project_root, "validation", "recommendation_kb.json")
        
        # Cache goes in 'data/' folder
        self.data_dir = os.path.join(project_root, "data")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.rec_cache_path = os.path.join(self.data_dir, "rec_cache.json")

        print(f"⚡ Initializing Agent (Gemini + {ollama_model})...")
        print(f"   📂 Ref KB:   {self.ref_params_path}")
        print(f"   📂 Rec KB:   {self.rec_kb_path}")
        print(f"   💾 Cache:    {self.rec_cache_path}")
        
        # Verify Paths
        if not os.path.exists(self.ref_params_path):
            print(f"⚠️ CRITICAL: Reference Parameter file missing at {self.ref_params_path}")
        if not os.path.exists(self.rec_kb_path):
            print(f"⚠️ Warning: Recommendation KB missing at {self.rec_kb_path} (Fallback will fail)")

        # 3. Initialize Modules
        self.interpreter = ParameterInterpreter(self.ref_params_path)
        self.context_engine = ContextAnalyzer()
        self.pattern_engine = PatternRecognizer()
        
        # Pass both cache path AND fallback KB path
        self.rec_engine = RecommendationEngine(
            api_key=api_key, 
            cache_file=self.rec_cache_path,
            fallback_file=self.rec_kb_path
        )
        self.synthesizer = ReportSynthesizer(model_name=ollama_model)
        self.qa_engine = QAEngine(model_name=ollama_model)
        
        print("✅ System Ready.")

    def run_pipeline(self, image_path):
        result = {"success": False, "error": None}

        try:
            print(f"   -> Processing: {os.path.basename(image_path)}")
            # Ingestion
            raw_text = extract_text(image_path)
            profile = extract_patient_info(raw_text)
            
            # Extraction
            extracted = extract_parameters(raw_text, kb_path=self.ref_params_path)
            if not extracted:
                 print("   ⚠️ No parameters extracted. Check image quality.")

            # Analysis
            analyzed = self.interpreter.analyze(extracted)
            refined = self.context_engine.refine_analysis(
                analyzed, 
                patient_age=profile['age'], 
                patient_gender=profile['gender'],
                is_pregnant=profile['is_pregnant']
            )
            risks = self.pattern_engine.evaluate_risks(refined)

            # AI Generation (Uses Cache + Fallback)
            recs = self.rec_engine.generate_recommendations(risks, refined, profile)
            final_report = self.synthesizer.generate_report(profile, risks, recs, refined)

            # Chat Context
            self.qa_engine.set_context(profile, risks, refined, final_report)

            result.update({
                "success": True, "profile": profile, "data": refined, 
                "risks": risks, "recommendations": recs, "report": final_report
            })

        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Pipeline Error: {e}")

        return result

    def chat(self, question):
        return self.qa_engine.ask_question(question)
