import argparse
import importlib.util
import json
import sys
from dataclasses import replace
from pathlib import Path
from .client import OllamaClient, ModelError
from .config import Settings, ROOT


def main():
    parser = argparse.ArgumentParser(description='Local GenAI internship toolkit')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='Check dependencies, Ollama and downloaded models')
    index = sub.add_parser('index')
    index.add_argument('paths', nargs='*', help='PDF/TXT/Markdown files; defaults to fictional sample corpus')
    ask = sub.add_parser('ask')
    ask.add_argument('question')
    run = sub.add_parser('run')
    run.add_argument('--week', type=int, required=True, choices=range(1, 9))
    sub.add_parser('evaluate')
    args = parser.parse_args()
    try:
        if args.command == 'doctor':
            modules = ['chromadb', 'pypdf', 'streamlit', 'langchain_ollama', 'langchain_chroma']
            missing = [name for name in modules if importlib.util.find_spec(name) is None]
            print('Python:', sys.version.split()[0])
            print('Missing packages:', ', '.join(missing) or 'none')
            settings = replace(Settings.from_env(), timeout=2, attempts=1)
            client = OllamaClient(settings)
            tags = client.health()
            names = {item['name'] for item in tags.get('models', [])}
            required = {settings.chat_model, settings.embed_model}
            absent = [m for m in required if m not in names and m + ':latest' not in names]
            print('Missing models:', ', '.join(absent) or 'none')
            return 1 if missing or absent else 0
        if args.command == 'run':
            from .exercises import run_week
            run_week(args.week)
        else:
            from .rag import KnowledgeBase, answer_question
            kb = KnowledgeBase()
            if args.command == 'index':
                from .documents import load_chunks
                paths = [Path(p) for p in args.paths] if args.paths else sorted((ROOT / 'data/sample_docs').glob('*.md'))
                print('Indexed chunks:', kb.index(load_chunks(paths)))
            elif args.command == 'ask':
                print(json.dumps(answer_question(kb, args.question), indent=2))
            else:
                from .exercises import evaluate, save_json
                output = ROOT / 'artifacts/capstone/evaluation.json'
                save_json(output, evaluate(kb))
                print(output)
    except (ModelError, ValueError, RuntimeError, ImportError, OSError, KeyError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
