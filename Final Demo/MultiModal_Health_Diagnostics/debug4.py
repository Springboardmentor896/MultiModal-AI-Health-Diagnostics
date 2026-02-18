from agent.orchestrator import orchestrator

result = orchestrator.orchestrate(
    raw_content="""
    Hemoglobin (Hb) 12.5
    Total RBC count 5.2
    Total WBC count 9000
    Platelet Count 150000
    Neutrophils 60
    Lymphocytes 31
    """,
    source_type='text',
    age=21,
    gender='male',
    pregnant=False,
    name='Patient',
    query='analyze my report'
)

analysis = result['analysis']
print("=== synthesis keys ===")
print(list(analysis.keys()))
print("\n=== synthesis_summary keys ===")
print(list(analysis.get('synthesis_summary', {}).keys()))
print("\n=== synthesis_summary values ===")
print(analysis.get('synthesis_summary', {}))
