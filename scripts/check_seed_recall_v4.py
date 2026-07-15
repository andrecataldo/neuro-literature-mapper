from __future__ import annotations

import argparse
import difflib
import re
import unicodedata
from pathlib import Path

import pandas as pd
import yaml


def normalize_title(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    text = text.casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def best_match(seed: str, candidates: list[str]) -> tuple[str, float]:
    normalized_seed = normalize_title(seed)
    best_title = ""
    best_score = 0.0

    for candidate in candidates:
        score = difflib.SequenceMatcher(
            None,
            normalized_seed,
            normalize_title(candidate),
        ).ratio()
        if score > best_score:
            best_title = candidate
            best_score = score

    return best_title, best_score


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica recall dos artigos-semente em um CSV."
    )
    parser.add_argument("csv_path")
    parser.add_argument(
        "--seeds",
        default="tests/seed_articles_neuro_v4.yaml",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.88,
    )
    args = parser.parse_args()

    dataframe = pd.read_csv(args.csv_path)
    titles = dataframe["title"].fillna("").astype(str).tolist()

    seeds_data = yaml.safe_load(
        Path(args.seeds).read_text(encoding="utf-8")
    )
    seeds = seeds_data.get("seeds", [])

    found = 0
    print("Artigos-semente:")
    print("-" * 100)

    for seed in seeds:
        expected_title = str(seed["title"])
        matched_title, score = best_match(expected_title, titles)
        status = "FOUND" if score >= args.threshold else "MISSING"
        if status == "FOUND":
            found += 1

        print(f"{status:7} | {score:0.3f} | {expected_title}")
        if matched_title:
            print(f"         melhor correspondência: {matched_title}")

    total = len(seeds)
    recall = found / total if total else 0.0
    print("-" * 100)
    print(f"Recall dos seeds: {found}/{total} = {recall:.1%}")

    return 0 if found == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
