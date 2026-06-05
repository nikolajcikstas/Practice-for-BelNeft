"""Генерация аналитических отчётов (Pandas + Matplotlib + Seaborn)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd
import seaborn as sns
from sqlalchemy import create_engine, text

from app.db_url import get_database_url

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "/app/reports"))
REPORT_CATALOG = (
    {"id": "top_skills", "title": "Топ-5 наиболее востребованных навыков"},
    {"id": "booking_load", "title": "Средняя загрузка переговорной по дням недели"},
)


def get_engine():
    return create_engine(get_database_url())


def top_skills(engine) -> pd.DataFrame:
    query = text("""
        SELECT s.name AS skill, s.category, COUNT(es.id) AS total
        FROM employee_skills es
        JOIN skills s ON s.id = es.skill_id
        GROUP BY s.id, s.name, s.category
        ORDER BY total DESC
        LIMIT 5
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def booking_load_by_weekday(engine) -> pd.DataFrame:
    query = text("""
        SELECT EXTRACT(DOW FROM start_time) AS dow,
               ROUND(AVG(EXTRACT(EPOCH FROM (end_time - start_time)) / 3600.0), 2) AS avg_hours
        FROM bookings
        GROUP BY dow
        ORDER BY dow
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    day_names = {0: "Вс", 1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб"}
    df["day"] = df["dow"].astype(int).map(day_names)
    return df


def _save_figure(fig: plt.Figure, name: str, fmt: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{name}.{fmt}"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _plot_top_skills(df: pd.DataFrame, fmt: str) -> Path | None:
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 5))
    palette = sns.color_palette("Blues_d", len(df))
    bars = ax.barh(df["skill"], df["total"], color=palette)
    ax.bar_label(bars, padding=4, fontsize=11)
    ax.set_xlabel("Количество назначений")
    ax.set_title("Топ-5 наиболее востребованных навыков", fontsize=14, fontweight="bold", pad=12)
    ax.invert_yaxis()
    sns.despine(left=True, bottom=False)
    return _save_figure(fig, "top_skills", fmt)


def _plot_booking_load(df: pd.DataFrame, fmt: str) -> Path | None:
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 5))
    palette = sns.color_palette("Greens_d", len(df))
    ax.bar(df["day"], df["avg_hours"], color=palette)
    ax.set_ylabel("Средняя нагрузка (часы)")
    ax.set_title("Средняя загрузка переговорной по дням недели", fontsize=14, fontweight="bold", pad=12)
    for i, (day, val) in enumerate(zip(df["day"], df["avg_hours"])):
        ax.text(i, val + 0.02, str(val), ha="center", va="bottom", fontsize=10)
    sns.despine()
    return _save_figure(fig, "booking_load", fmt)


def generate_reports(fmt: str = "png") -> list[dict]:
    if fmt not in {"png", "pdf"}:
        raise ValueError("format must be png or pdf")

    engine = get_engine()
    generated: list[dict] = []

    skills_path = _plot_top_skills(top_skills(engine), fmt)
    if skills_path:
        generated.append(_file_meta(skills_path, "top_skills", fmt))

    load_path = _plot_booking_load(booking_load_by_weekday(engine), fmt)
    if load_path:
        generated.append(_file_meta(load_path, "booking_load", fmt))

    return generated


def _file_meta(path: Path, report_id: str, fmt: str) -> dict:
    stat = path.stat()
    title = next((item["title"] for item in REPORT_CATALOG if item["id"] == report_id), report_id)
    return {
        "id": report_id,
        "title": title,
        "format": fmt,
        "filename": path.name,
        "size_bytes": stat.st_size,
        "generated_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
    }


def list_reports() -> list[dict]:
    items: list[dict] = []
    for entry in REPORT_CATALOG:
        for fmt in ("png", "pdf"):
            path = REPORTS_DIR / f"{entry['id']}.{fmt}"
            if not path.exists():
                continue
            items.append(_file_meta(path, entry["id"], fmt))
    return items


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
