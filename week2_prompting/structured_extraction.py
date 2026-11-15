import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from internship.client import OllamaClient
from internship.exercises import INVOICE_SCHEMA, validate_invoice

if __name__ == '__main__':
    text = input('Invoice-like text: ')
    result = OllamaClient().chat([
        {'role': 'system', 'content': 'Extract invoice fields as JSON. Use null for missing fields.'},
        {'role': 'user', 'content': text}], schema=INVOICE_SCHEMA, cache=False)
    print(json.dumps(validate_invoice(json.loads(result['message']['content'])), indent=2))
