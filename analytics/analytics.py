#!/usr/bin/env python3
"""
Скрипт аналитики и отчётности.
Запуск: python analytics.py
"""

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://portal:portal@localhost:5432/portal")
REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


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


def plot_top_skills(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(df["skill"], df["total"], color="#4C72B0")
    ax.bar_label(bars, padding=4)
    ax.set_xlabel("Количество назначений")
    ax.set_title("Топ-5 наиболее востребованных навыков")
    ax.invert_yaxis()
    plt.tight_layout()
    path = REPORTS_DIR / "top_skills.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Сохранено: {path}")


def plot_booking_load(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["day"], df["avg_hours"], color="#55A868")
    ax.set_ylabel("Средняя нагрузка (часы)")
    ax.set_title("Средняя загрузка переговорной по дням недели")
    plt.tight_layout()
    path = REPORTS_DIR / "booking_load.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Сохранено: {path}")


def main():
    engine = get_engine()

    print("Подключение к БД...")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("OK")

    print("\nТоп-5 навыков:")
    df_skills = top_skills(engine)
    print(df_skills.to_string(index=False))
    plot_top_skills(df_skills)

    print("\nЗагрузка переговорной по дням недели:")
    df_load = booking_load_by_weekday(engine)
    print(df_load[["day", "avg_hours"]].to_string(index=False))
    plot_booking_load(df_load)

    print("\nГотово. Отчёты сохранены в папку /reports")


if __name__ == "__main__":
    main()
