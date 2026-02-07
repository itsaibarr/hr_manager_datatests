# CSV data loader

import pandas as pd
from pathlib import Path
from typing import List

from .candidate import CandidateProfile


def load_candidates(csv_path: str | Path) -> List[CandidateProfile]:
    """Load candidates from cleaned CSV file."""
    df = pd.read_csv(csv_path)
    candidates = []
    
    for idx, (_, row) in enumerate(df.iterrows()):
        row_dict = row.to_dict()
        row_dict["_row_index"] = idx  # Pass index for ID
        candidate = CandidateProfile.from_csv_row(row_dict)
        candidates.append(candidate)
    
    return candidates


def load_candidates_df(csv_path: str | Path) -> pd.DataFrame:
    """Load candidates as DataFrame for analysis."""
    return pd.read_csv(csv_path)
