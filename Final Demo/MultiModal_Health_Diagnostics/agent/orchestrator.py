"""
Multi-Model Health Diagnostics Orchestrator
Coordinates the entire analysis pipeline
"""

import os
from datetime import datetime

# Import ingestion modules
from ingestion.parser import parse_pdf, parse_csv, parse_image
from ingestion.extractor import extract_lab_data

# Import model classes (NOT functions)
from models.model1_interpreter import Model1Interpreter
from models.model2_ml_risk import Model2MLRisk
from models.model3_contextual import Model3Contextual

# Import synthesis and report generation
from synthesis.findings_synthesizer import HealthSynthesizer
from report.generator import ReportGenerator


class MultiModelOrchestrator:
    def __init__(self):
        """Initialize all models and components"""
        self.model1 = Model1Interpreter()
        self.model2 = Model2MLRisk()
        self.model3 = Model3Contextual()
        self.synthesizer = HealthSynthesizer()
        self.report_generator = ReportGenerator()

    def orchestrate(self, raw_content, source_type, age, gender, pregnant, name, query):
        """
        Main orchestration method

        Args:
            raw_content: File path or text content
            source_type: 'pdf', 'image', 'csv', 'text'
            age: Patient age
            gender: 'male' or 'female'
            pregnant: Boolean
            name: Patient name
            query: User query/question

        Returns:
            dict: Complete analysis result
        """
        execution_log = []

        try:
            # Step 1: Parse input
            execution_log.append("Step 1: Parsing input...")
            if source_type == 'pdf':
                text = parse_pdf(raw_content)
            elif source_type == 'image':
                text = parse_image(raw_content)
            elif source_type == 'csv':
                text = parse_csv(raw_content)
            else:  # text
                text = str(raw_content) if raw_content else ""

            execution_log.append(f"✓ Extracted {len(text)} characters")

            # Step 2: Extract structured data
            execution_log.append("Step 2: Extracting lab parameters...")
            lab_data = extract_lab_data(text)
            execution_log.append(f"✓ Extracted {len(lab_data)} parameters: {list(lab_data.keys())}")

            # Step 3: Prepare patient info
            patient_info = {
                'name': name,
                'age': age,
                'gender': gender.lower(),
                'pregnant': pregnant
            }

            # Step 4: Run Model 1 (Clinical Rules)
            execution_log.append("Step 3: Running Model 1 (Clinical Rules)...")
            model1_result = self.model1.analyze(lab_data, patient_info)
            execution_log.append(f"✓ Model 1 complete")

            # Step 5: Run Model 2 (ML Risk)
            execution_log.append("Step 4: Running Model 2 (ML Risk Assessment)...")
            model2_result = self.model2.analyze(lab_data, patient_info)
            execution_log.append(f"✓ Model 2 complete")

            # Step 6: Run Model 3 (Contextual Synthesis)
            execution_log.append("Step 5: Running Model 3 (Contextual Analysis)...")
            model3_result = self.model3.analyze(lab_data, patient_info, model1_result, model2_result)
            execution_log.append(f"✓ Model 3 complete")

            # Step 7: Synthesize results
            execution_log.append("Step 6: Synthesizing results...")
            synthesis = self.synthesizer.synthesize(
                lab_data=lab_data,
                patient_info=patient_info,
                model1_output=model1_result,
                model2_output=model2_result,
                model3_output=model3_result,
                query=query
            )
            execution_log.append(f"✓ Synthesis complete")

            # Step 8: Generate report
            execution_log.append("Step 7: Generating report...")
            report = self.report_generator.generate(
                patient_info=patient_info,
                lab_data=lab_data,
                analysis=synthesis,
                query=query
            )
            execution_log.append(f"✓ Report generated")

            # Calculate confidence
            confidence = self._calculate_confidence(lab_data, synthesis)

            return {
                'status': 'success',
                'analysis': synthesis,
                'report': report,
                'confidence': confidence,
                'execution_log': execution_log,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            execution_log.append(f"✗ Error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'execution_log': execution_log,
                'timestamp': datetime.now().isoformat()
            }

    def _calculate_confidence(self, lab_data, synthesis):
        """Calculate overall confidence score"""
        # Base confidence on data completeness
        total_params = 10  # Expected parameters
        found_params = len(lab_data)
        completeness = min((found_params / total_params) * 100, 100)  # Cap at 100
        
        # Factor in risk consistency across models
        risks = synthesis.get('risks', {})
        if risks:
            # Check variance in risk labels
            high_risk_count = sum(1 for r in risks.values() if r.get('label') == 'high')
            moderate_risk_count = sum(1 for r in risks.values() if r.get('label') == 'moderate')
            
            if high_risk_count > 3:
                reliability = 70  # Multiple high risks suggest serious issues
            elif moderate_risk_count > 3:
                reliability = 80
            else:
                reliability = 90  # Mostly low risks
        else:
            reliability = 50
        
        # Combined score (capped at 100)
        confidence_score = min((completeness * 0.6) + (reliability * 0.4), 100)
        
        # Determine confidence level
        if confidence_score >= 80:
            level = 'high'
        elif confidence_score >= 60:
            level = 'moderate'
        else:
            level = 'low'
        
        return {
            'score': round(confidence_score, 1),
            'level': level,
            'data_completeness': round(completeness, 1),
            'reliability': round(reliability, 1)
        }


# Create singleton instance
orchestrator = MultiModelOrchestrator()
