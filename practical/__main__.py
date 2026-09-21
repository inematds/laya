import argparse
import json
import os
import sys
from pathlib import Path
from .engine import Engine, evaluate


def main():
    p = argparse.ArgumentParser(description='Laya INEMA — triagem local em português')
    p.add_argument('--device', choices=['cpu', 'cuda', 'mps'], default='cpu')
    p.add_argument('--threshold', type=float, default=.85)
    p.add_argument('--model-path', help='Checkpoint local opcional, já baixado')
    sub = p.add_subparsers(dest='command', required=True)
    triage = sub.add_parser('triage'); triage.add_argument('--message', required=True); triage.add_argument('--subject', default='')
    ev = sub.add_parser('evaluate'); ev.add_argument('--dataset', default=str(Path(__file__).with_name('tickets.jsonl'))); ev.add_argument('--output')
    serve = sub.add_parser('serve'); serve.add_argument('--port', type=int, default=8765)
    sub.add_parser('download')
    args = p.parse_args()
    os.environ.setdefault('USE_TF', '0')
    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    engine = Engine(args.device, args.threshold, args.model_path)
    if args.command == 'serve':
        import uvicorn
        from .server import create_app
        uvicorn.run(create_app(engine), host='127.0.0.1', port=args.port)
        return
    try:
        if args.command == 'download':
            engine._load(); result = {'loaded': engine.router.loaded, 'device': str(engine.router.load('multilingual').device)}
        elif args.command == 'evaluate': result = evaluate(engine, args.dataset)
        else: result = engine.predict(args.message, args.subject)
        data = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
        if getattr(args, 'output', None): Path(args.output).write_text(data+'\n')
        print(data)
    except (ValueError, OSError, RuntimeError, KeyError) as e:
        print(f'Erro: {e}', file=sys.stderr); sys.exit(1)

if __name__ == '__main__': main()
