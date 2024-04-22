import os
import sys
import time
import pdfplumber
import openai
import re
import random
import json
import textstat
from typing import List, Dict, Tuple, Optional
openai.api_key = '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'

MAX_TOKENS_PER_REQUEST = 4096  # Safe limit for tokens per request
user_points = 0  # Initialize user points
class QuestionController:
    def __init__(self,filepath):
        self.filepath=filepath
        self.runMCQGenerator(filepath)
