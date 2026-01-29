from model2.pattern_recognition import identify_patterns
from model3.contextual_analysis import apply_context

def run(data, age=None, gender=None):
    patterns = identify_patterns(data)
    return apply_context(patterns, age, gender)
