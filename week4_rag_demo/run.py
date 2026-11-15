import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from internship.exercises import run_week
if __name__ == '__main__':
    run_week(4)
