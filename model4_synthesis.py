"""
FILE: model4_findings_synthesis_engine.py
PURPOSE: Model 4 - Synthesize clinical findings from Models 1, 2, and 3
STATUS: Complete, Production Ready
"""

import json
from typing import Dict, List, Any

class FindingsSynthesisEngine:
    """
    Synthesizes findings from Models 1, 2, and 3 into comprehensive clinical findings.
    
    Model 1 Output: Parameter classifications (High/Low/Normal)
    Model 2 Output: Pattern detection and risk assessment
    Model 3 Output: Age-gender context
    
    This Model 4: Combines all into structured clinical findings
    """
    
    def __init__(self):
        """Initialize findings synthesis engine."""
        # Map parameter statuses to clinical findings
        self.finding_templates = {
            "Hemoglobin": {
                "Low": "Low hemoglobin suggesting anemia",
                "High": "Elevated hemoglobin - possible polycythemia",
                "Normal": "Hemoglobin within normal range"
            },
            "WhiteBloodCells": {
                "Low": "Reduced white blood cells - immunosuppression risk",
                "High": "Elevated white blood cells indicating infection or inflammation",
                "Normal": "White blood cells within normal range"
            },
            "PlateletCount": {
                "Low": "Low platelet count - increased bleeding risk",
                "High": "Elevated platelet count - thrombosis risk",
                "Normal": "Platelet count within normal range"
            }
        }
        
        # Map patterns to affected body systems
        self.system_mapping = {
            "Anemia Risk": "Hematologic",
            "Infection Risk": "Immune",
            "Bleeding Disorder": "Hematologic",
            "Thrombosis Risk": "Cardiovascular",
            "Diabetes Risk": "Metabolic",
            "Cardiovascular Risk": "Cardiovascular"
        }

    def extract_findings(self, model1_output: Dict) -> List[str]:
        """
        Extract clinical findings from Model 1 parameter classifications.
        
        Args:
            model1_output: {"Hemoglobin": "Low", "WhiteBloodCells": "High", ...}
            
        Returns:
            List of clinical finding descriptions
        """
        findings = []
        
        for param, status in model1_output.items():
            if param in self.finding_templates:
                if status in self.finding_templates[param]:
                    finding = self.finding_templates[param][status]
                    if status != "Normal":  # Only add abnormal findings
                        findings.append(finding)
        
        return findings

    def extract_affected_systems(self, model2_patterns: List[str]) -> List[str]:
        """
        Extract affected body systems from Model 2 patterns.
        
        Args:
            model2_patterns: ["Anemia Risk", "Infection Risk", ...]
            
        Returns:
            List of affected body systems
        """
        systems = []
        
        for pattern in model2_patterns:
            if pattern in self.system_mapping:
                system = self.system_mapping[pattern]
                if system not in systems:  # Avoid duplicates
                    systems.append(system)
        
        return systems

    def synthesize_findings(self, model1: Dict, model2: Dict, model3: Dict = None) -> Dict[str, Any]:
        """
        Synthesize comprehensive clinical findings from all models.
        
        Args:
            model1: Parameter classifications
                    {"Hemoglobin": "Low", "WhiteBloodCells": "High", ...}
            model2: Pattern detection results
                    {"patterns": ["Anemia Risk", "Infection Risk"],
                     "risk_score": 4,
                     "risk_level": "High"}
            model3: Optional context (age/gender)
                    {"age": 55, "gender": "Male", "age_group": "SENIOR"}
        
        Returns:
            Synthesized findings dictionary
        """
        
        # Extract findings from Model 1
        clinical_findings = self.extract_findings(model1)
        
        # Extract affected systems from Model 2
        patterns = model2.get("patterns", [])
        affected_systems = self.extract_affected_systems(patterns)
        
        # Compile synthesis
        synthesis = {
            "key_findings": clinical_findings,
            "detected_patterns": patterns,
            "overall_risk": model2.get("risk_level", "Unknown"),
            "risk_score": model2.get("risk_score", 0),
            "affected_systems": affected_systems,
            "total_findings": len(clinical_findings),
            "severity": self._determine_severity(model2.get("risk_score", 0)),
            "clinical_summary": self._generate_clinical_summary(clinical_findings, affected_systems)
        }
        
        # Add context if provided
        if model3:
            synthesis["context"] = {
                "age": model3.get("age"),
                "gender": model3.get("gender"),
                "age_group": model3.get("age_group")
            }
        
        return synthesis

    def _determine_severity(self, risk_score: int) -> str:
        """
        Determine clinical severity based on risk score.
        
        Args:
            risk_score: Numeric risk score (0-10)
            
        Returns:
            Severity level (Low/Moderate/High/Critical)
        """
        if risk_score <= 2:
            return "Low"
        elif risk_score <= 4:
            return "Moderate"
        elif risk_score <= 7:
            return "High"
        else:
            return "Critical"

    def _generate_clinical_summary(self, findings: List[str], systems: List[str]) -> str:
        """
        Generate a clinical summary statement.
        
        Args:
            findings: List of clinical findings
            systems: List of affected systems
            
        Returns:
            Clinical summary text
        """
        if not findings:
            return "All parameters within normal range."
        
        systems_text = ", ".join(systems) if systems else "Multiple systems"
        findings_count = len(findings)
        
        return f"Patient presents with {findings_count} abnormal findings affecting {systems_text} system(s)."


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize engine
    engine = FindingsSynthesisEngine()
    
    # Sample inputs from Models 1, 2, 3
    model1_output = {
        "Hemoglobin": "Low",
        "WhiteBloodCells": "High",
        "PlateletCount": "Low"
    }
    
    model2_output = {
        "patterns": ["Anemia Risk", "Infection Risk", "Bleeding Disorder"],
        "risk_score": 7,
        "risk_level": "High"
    }
    
    model3_context = {
        "age": 55,
        "gender": "Male",
        "age_group": "SENIOR"
    }
    
    # Synthesize findings
    result = engine.synthesize_findings(model1_output, model2_output, model3_context)
    
    # Display results
    print("\n" + "="*70)
    print("MODEL 4: FINDINGS SYNTHESIS ENGINE OUTPUT")
    print("="*70)
    print(f"\nClinical Summary: {result['clinical_summary']}")
    print(f"\nKey Findings ({result['total_findings']} total):")
    for i, finding in enumerate(result['key_findings'], 1):
        print(f"  {i}. {finding}")
    print(f"\nDetected Patterns: {', '.join(result['detected_patterns'])}")
    print(f"Affected Systems: {', '.join(result['affected_systems'])}")
    print(f"Risk Score: {result['risk_score']}/10")
    print(f"Overall Risk: {result['overall_risk']}")
    print(f"Severity: {result['severity']}")
    print(f"Patient Age: {result['context']['age']} ({result['context']['age_group']})")
    print(f"Patient Gender: {result['context']['gender']}")
    print("\n" + "="*70)
    
    # Show JSON output
    print("\nJSON Output:")
    print(json.dumps(result, indent=2))
