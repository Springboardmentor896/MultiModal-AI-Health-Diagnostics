def build_patient_context(age, sex, pregnant=False):
    """
    Returns patient context category
    """
    if pregnant:
        return "pregnant"
    return sex.lower()
