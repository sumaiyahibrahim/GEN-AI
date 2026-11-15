import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from internship.exercises import run_week
if __name__ == '__main__':
    run_week(1)
