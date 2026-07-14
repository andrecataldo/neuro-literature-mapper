from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from neuro_mapper.config import load_config
from neuro_mapper.export import export_records_csv, export_rows_csv
from neuro_mapper.pipeline import run_api_search
from neuro_mapper.venue_search import generate_venue_searches


def cmd_search(args: argparse.Namespace) -> None:
    load_dotenv()
    config = load_config(args.config)
    records = run_api_search(config)
    export_records_csv(records, args.output)
    print(f"Arquivo gerado: {args.output}")
    print(f"Registros únicos: {len(records)}")


def cmd_venue_search(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    rows = generate_venue_searches(config)
    export_rows_csv(rows, args.output)
    print(f"Arquivo gerado: {args.output}")
    print(f"Buscas direcionadas: {len(rows)}")


def cmd_all(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    search_output = output_dir / "resultados_neuro.csv"
    venues_output = output_dir / "buscas_venues.csv"

    cmd_venue_search(argparse.Namespace(config=args.config, output=venues_output))
    cmd_search(argparse.Namespace(config=args.config, output=search_output))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Neuro Literature Mapper")
    subparsers = parser.add_subparsers(required=True)

    search = subparsers.add_parser("search", help="Executa buscas automatizadas em APIs abertas.")
    search.add_argument("--config", required=True)
    search.add_argument("--output", required=True)
    search.set_defaults(func=cmd_search)

    venue = subparsers.add_parser("venue-search", help="Gera buscas direcionadas por venue.")
    venue.add_argument("--config", required=True)
    venue.add_argument("--output", required=True)
    venue.set_defaults(func=cmd_venue_search)

    all_cmd = subparsers.add_parser("all", help="Gera buscas por venue e executa busca por APIs.")
    all_cmd.add_argument("--config", required=True)
    all_cmd.add_argument("--output-dir", required=True)
    all_cmd.set_defaults(func=cmd_all)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
