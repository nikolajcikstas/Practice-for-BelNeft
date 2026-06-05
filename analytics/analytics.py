#!/usr/bin/env python3
"""
Скрипт аналитики и отчётности.
Запуск: python analytics.py [--pdf]
"""

import argparse
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sqlalchemy import create_engine, text

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://portal:portal@localhost:5432/portal")
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", str(Path(__file__).parent.parent / "reports")))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def get_engine():
    return create_engine(DATABASE_URL)


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


def save_figure(fig: plt.Figure, name: str, fmt: str):
    path = REPORTS_DIR / f"{name}.{fmt}"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Сохранено: {path}")


def plot_top_skills(df: pd.DataFrame, fmt: str):
    fig, ax = plt.subplots(figsize=(10, 5))
    palette = sns.color_palette("Blues_d", len(df))
    bars = ax.barh(df["skill"], df["total"], color=palette)
    ax.bar_label(bars, padding=4, fontsize=11)
    ax.set_xlabel("Количество назначений")
    ax.set_title("Топ-5 наиболее востребованных навыков", fontsize=14, fontweight="bold", pad=12)
    ax.invert_yaxis()
    sns.despine(left=True, bottom=False)
    save_figure(fig, "top_skills", fmt)


def plot_booking_load(df: pd.DataFrame, fmt: str):
    fig, ax = plt.subplots(figsize=(10, 5))
    palette = sns.color_palette("Greens_d", len(df))
    ax.bar(df["day"], df["avg_hours"], color=palette)
    ax.set_ylabel("Средняя нагрузка (часы)")
    ax.set_title("Средняя загрузка переговорной по дням недели", fontsize=14, fontweight="bold", pad=12)
    for i, (day, val) in enumerate(zip(df["day"], df["avg_hours"])):
        ax.text(i, val + 0.02, str(val), ha="center", va="bottom", fontsize=10)
    sns.despine()
    save_figure(fig, "booking_load", fmt)


def main():
    parser = argparse.ArgumentParser(description="Аналитика портала компетенций")
    parser.add_argument("--pdf", action="store_true", help="Сохранить в PDF вместо PNG")
    args = parser.parse_args()
    fmt = "pdf" if args.pdf else "png"

    engine = get_engine()

    print("Подключение к БД...")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("OK")

    print(f"\nФормат вывода: {fmt.upper()}")

    print("\nТоп-5 навыков:")
    df_skills = top_skills(engine)
    if df_skills.empty:
        print("  Нет данных")
    else:
        print(df_skills.to_string(index=False))
        plot_top_skills(df_skills, fmt)

    print("\nЗагрузка переговорной по дням недели:")
    df_load = booking_load_by_weekday(engine)
    if df_load.empty:
        print("  Нет данных")
    else:
        print(df_load[["day", "avg_hours"]].to_string(index=False))
        plot_booking_load(df_load, fmt)

    print(f"\nГотово. Отчёты в папке: {REPORTS_DIR}")


if __name__ == "__main__":
    main()
