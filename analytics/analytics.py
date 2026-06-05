#!/usr/bin/env python3
"""CLI-обёртка; логика в backend/app/analytics_service.py."""

from app.analytics_service import generate_reports

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Аналитика портала компетенций")
    parser.add_argument("--pdf", action="store_true", help="Сохранить в PDF вместо PNG")
    args = parser.parse_args()
    fmt = "pdf" if args.pdf else "png"
    result = generate_reports(fmt)
    print(f"Сгенерировано отчётов: {len(result)}")
    for item in result:
        print(f"  {item['filename']}")
