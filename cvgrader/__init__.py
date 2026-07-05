"""ats-resume-checker: grade a resume the way real ATS pipelines and recruiters do."""
from .score import grade, to_dict, Report

__version__ = "0.1.0"
__all__ = ["grade", "to_dict", "Report", "__version__"]
