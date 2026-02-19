import os
import re
from collections import defaultdict

def extract_claim_id(filename):
    """
    Extracts the unique Claim ID (e.g., 'BLR-0425-PA-0037318') from the filename.
    Returns 'Unknown_Group' if no pattern matches.
    """
    # Regex Breakdown:
    # [A-Z]{3}  : 3 Letters (e.g., BLR)
    # \d{4}     : 4 Digits (e.g., 0425)
    # [A-Z]{2}  : 2 Letters (e.g., PA or CL)
    # \d+       : Any number of digits (e.g., 0037318)
    pattern = r"([A-Z]{3}-\d{4}-[A-Z]{2}-\d+)"
    
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    return "Misc_Reports"

def group_files_by_patient(directory):
    """
    Returns a dictionary: { 'CLAIM_ID': ['path/to/img1.png', 'path/to/img2.png'] }
    """
    grouped_files = defaultdict(list)
    
    # List all png and jpg files
    valid_extensions = ('.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir(directory) if f.lower().endswith(valid_extensions)]
    
    for f in files:
        claim_id = extract_claim_id(f)
        full_path = os.path.join(directory, f)
        grouped_files[claim_id].append(full_path)
        
    return grouped_files
