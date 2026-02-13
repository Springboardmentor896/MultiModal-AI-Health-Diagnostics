
## Evaluation Metrics – Milestone 3 (Updated)

### 1. Summary Coherence
- Measures how accurately synthesized summaries reflect extracted findings.
- Target: >95% accuracy.

### 2. Recommendation Relevance
- Ensures each recommendation is directly linked to an identified clinical finding.
- Target: >90% relevance.

### 3. Actionability Score
- Evaluates whether recommendations include clear, actionable steps
  (diet, lifestyle, diagnostic tests, follow-up).
- Target: >90%.

### 4. Pattern Accuracy
- Measures correctness of detected clinical patterns
  (e.g., anemia, diabetes risk, thrombocytopenia).
- Compared against expert-annotated ground truth.
- Target: >90%.

### 5. Risk Score Plausibility
- Verifies whether assigned risk levels (Low/Moderate/High)
  logically align with the severity and number of findings.
- Reviewed using predefined clinical rules.

### 6. Expert Review
- Clinical expert manually reviews:
  - Synthesized summaries
  - Generated recommendations
  - Risk levels
- Feedback used to refine synthesis and recommendation rules.

### Evaluation Method
- Input: OCR mock outputs derived from real lab reports.
- Process:
  1. Generate synthesized findings.
  2. Produce personalized recommendations.
  3. Evaluate using metrics above.
- Success Criteria:
  - High clinical consistency
  - Clear traceability from findings → recommendations → risk score.
