"""Генерация аналитических отчётов (Pandas + Matplotlib + Seaborn)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from sqlalchemy import create_engine, text

from app.db_url import get_database_url

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["font.family"] = ["DejaVu Sans", "sans-serif"]

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "/app/reports"))

REPORT_CATALOG = [
    {"id": "top_skills",       "title": "Топ-5 наиболее востребованных навыков"},
    {"id": "booking_weekday",  "title": "Бронирования по дням недели"},
    {"id": "booking_hours",    "title": "Активность переговорной по часам"},
    {"id": "skill_levels",     "title": "Распределение уровней владения навыками"},
    {"id": "skills_category",  "title": "Навыки по категориям"},
    {"id": "top_employees",    "title": "Топ сотрудников по числу навыков"},
]

_WEEKDAY_ORDER = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
_DOW_MAP = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 0: "Вс"}


def get_engine():
    return create_engine(get_database_url())


# ── запросы ──────────────────────────────────────────────────────────────────

def _q_top_skills(engine) -> pd.DataFrame:
    q = text("""
        SELECT s.name AS skill, s.category, COUNT(es.id) AS total
        FROM employee_skills es
        JOIN skills s ON s.id = es.skill_id
        GROUP BY s.id, s.name, s.category
        ORDER BY total DESC
        LIMIT 5
    """)
    with engine.connect() as conn:
        return pd.read_sql(q, conn)


def _q_booking_weekday(engine) -> pd.DataFrame:
    q = text("""
        SELECT EXTRACT(DOW FROM start_time)::int AS dow, COUNT(*) AS bookings
        FROM bookings
        GROUP BY dow
    """)
    with engine.connect() as conn:
        raw = pd.read_sql(q, conn)

    all_days = pd.DataFrame({"dow": list(_DOW_MAP.keys())})
    df = all_days.merge(raw, on="dow", how="left").fillna(0)
    df["day"] = df["dow"].map(_DOW_MAP)
    df["day"] = pd.Categorical(df["day"], categories=_WEEKDAY_ORDER, ordered=True)
    return df.sort_values("day")


def _q_booking_hours(engine) -> pd.DataFrame:
    q = text("""
        SELECT EXTRACT(HOUR FROM start_time)::int AS hour, COUNT(*) AS bookings
        FROM bookings
        GROUP BY hour
        ORDER BY hour
    """)
    with engine.connect() as conn:
        raw = pd.read_sql(q, conn)

    all_hours = pd.DataFrame({"hour": range(8, 21)})
    df = all_hours.merge(raw, on="hour", how="left").fillna(0)
    df["label"] = df["hour"].apply(lambda h: f"{h:02d}:00")
    return df


def _q_skill_levels(engine) -> pd.DataFrame:
    q = text("""
        SELECT s.category, es.proficiency_level AS level, COUNT(*) AS cnt
        FROM employee_skills es
        JOIN skills s ON s.id = es.skill_id
        GROUP BY s.category, es.proficiency_level
        ORDER BY s.category, es.proficiency_level
    """)
    with engine.connect() as conn:
        return pd.read_sql(q, conn)


def _q_skills_category(engine) -> pd.DataFrame:
    q = text("""
        SELECT category, COUNT(*) AS total
        FROM skills
        GROUP BY category
        ORDER BY total DESC
    """)
    with engine.connect() as conn:
        return pd.read_sql(q, conn)


def _q_top_employees(engine) -> pd.DataFrame:
    q = text("""
        SELECT
            e.last_name || ' ' || LEFT(e.first_name, 1) || '.' AS name,
            COUNT(es.id) AS skills,
            ROUND(AVG(es.proficiency_level), 1) AS avg_level
        FROM employees e
        LEFT JOIN employee_skills es ON es.employee_id = e.id
        GROUP BY e.id, e.last_name, e.first_name
        ORDER BY skills DESC, avg_level DESC
        LIMIT 8
    """)
    with engine.connect() as conn:
        return pd.read_sql(q, conn)


# ── отрисовка ─────────────────────────────────────────────────────────────────

def _save(fig: plt.Figure, name: str, fmt: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{name}.{fmt}"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _plot_top_skills(df: pd.DataFrame, fmt: str) -> Path | None:
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.9)))
    palette = sns.color_palette("Blues_d", len(df))
    bars = ax.barh(df["skill"], df["total"], color=palette, height=0.55, edgecolor="white")
    ax.bar_label(bars, labels=[f" {int(v)}" for v in df["total"]], padding=2, fontsize=11)
    ax.set_xlabel("Количество назначений")
    ax.set_title("Топ-5 наиболее востребованных навыков", fontsize=14, fontweight="bold", pad=12)
    ax.invert_yaxis()
    ax.set_xlim(0, df["total"].max() * 1.2 + 0.5)
    sns.despine(left=True, bottom=False)
    return _save(fig, "top_skills", fmt)


def _plot_booking_weekday(df: pd.DataFrame, fmt: str) -> Path | None:
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(df))
    colors = [
        sns.color_palette("Blues", 9)[5] if v > 0 else sns.color_palette("Blues", 9)[1]
        for v in df["bookings"]
    ]
    bars = ax.bar(x, df["bookings"].astype(float), width=0.55, color=colors, edgecolor="white")
    for rect, val in zip(bars, df["bookings"]):
        if val > 0:
            ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.05,
                    str(int(val)), ha="center", va="bottom", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(df["day"].astype(str), fontsize=11)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.set_ylabel("Количество бронирований")
    ax.set_title("Бронирования переговорной по дням недели", fontsize=14, fontweight="bold", pad=12)
    sns.despine()
    return _save(fig, "booking_weekday", fmt)


def _plot_booking_hours(df: pd.DataFrame, fmt: str) -> Path | None:
    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(df))
    colors = sns.color_palette("Greens", len(df) + 3)[2:]
    bars = ax.bar(x, df["bookings"].astype(float), width=0.6, color=colors, edgecolor="white")
    for rect, val in zip(bars, df["bookings"]):
        if val > 0:
            ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.05,
                    str(int(val)), ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(df["label"], rotation=45, ha="right", fontsize=10)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.set_ylabel("Количество бронирований")
    ax.set_title("Активность переговорной по часам", fontsize=14, fontweight="bold", pad=12)
    sns.despine()
    fig.tight_layout()
    return _save(fig, "booking_hours", fmt)


def _plot_skill_levels(df: pd.DataFrame, fmt: str) -> Path | None:
    if df.empty:
        return None

    pivot = df.pivot_table(index="level", columns="category", values="cnt", aggfunc="sum").fillna(0)
    pivot = pivot.reindex(range(1, 6), fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 5))
    palette = sns.color_palette("tab10", len(pivot.columns))
    x = np.arange(len(pivot))
    n = len(pivot.columns)
    width = 0.7 / max(n, 1)

    for i, (col, color) in enumerate(zip(pivot.columns, palette)):
        offset = (i - n / 2 + 0.5) * width
        bars = ax.bar(x + offset, pivot[col], width=width * 0.9,
                      label=col, color=color, edgecolor="white")

    level_labels = ["1 — Знаком", "2 — Базовый", "3 — Средний", "4 — Хороший", "5 — Эксперт"]
    ax.set_xticks(x)
    ax.set_xticklabels(level_labels, fontsize=10)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.set_ylabel("Количество назначений")
    ax.set_title("Распределение уровней владения навыками по категориям",
                 fontsize=13, fontweight="bold", pad=12)
    if n > 0:
        ax.legend(title="Категория", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    sns.despine()
    fig.tight_layout()
    return _save(fig, "skill_levels", fmt)


def _plot_skills_category(df: pd.DataFrame, fmt: str) -> Path | None:
    if df.empty:
        return None
    fig, (ax_pie, ax_bar) = plt.subplots(1, 2, figsize=(13, 5))

    palette = sns.color_palette("tab10", len(df))
    wedges, texts, autotexts = ax_pie.pie(
        df["total"], labels=None, autopct="%1.0f%%",
        colors=palette, startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for at in autotexts:
        at.set_fontsize(10)
    ax_pie.legend(wedges, df["category"], title="Категория",
                  loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
    ax_pie.set_title("Доли категорий навыков", fontsize=12, fontweight="bold")

    bars = ax_bar.barh(df["category"], df["total"],
                       color=palette, height=0.55, edgecolor="white")
    ax_bar.bar_label(bars, labels=[f" {int(v)}" for v in df["total"]], padding=2, fontsize=10)
    ax_bar.set_xlabel("Навыков")
    ax_bar.invert_yaxis()
    ax_bar.set_xlim(0, df["total"].max() * 1.3 + 0.5)
    ax_bar.set_title("Количество навыков по категориям", fontsize=12, fontweight="bold")
    sns.despine(ax=ax_bar, left=True)

    fig.suptitle("Навыки по категориям", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save(fig, "skills_category", fmt)


def _plot_top_employees(df: pd.DataFrame, fmt: str) -> Path | None:
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.8)))

    cmap = sns.color_palette("RdYlGn", 6)
    colors = [cmap[min(int(v), 5)] for v in df["avg_level"]]
    bars = ax.barh(df["name"], df["skills"], color=colors, height=0.55, edgecolor="white")

    for rect, avg in zip(bars, df["avg_level"]):
        label = f"  ср. уровень {avg:.1f}" if avg > 0 else "  нет навыков"
        ax.text(rect.get_width() + 0.1, rect.get_y() + rect.get_height() / 2,
                label, va="center", fontsize=9, color="#555")

    ax.set_xlabel("Количество навыков")
    ax.set_title("Топ сотрудников по числу навыков", fontsize=14, fontweight="bold", pad=12)
    ax.invert_yaxis()
    ax.set_xlim(0, df["skills"].max() * 1.45 + 0.5)
    sns.despine(left=True, bottom=False)
    fig.tight_layout()
    return _save(fig, "top_employees", fmt)


# ── публичный API ─────────────────────────────────────────────────────────────

def generate_reports(fmt: str = "png") -> list[dict]:
    if fmt not in {"png", "pdf"}:
        raise ValueError("format must be png or pdf")

    engine = get_engine()
    generated: list[dict] = []

    tasks = [
        (_plot_top_skills,      _q_top_skills,      "top_skills"),
        (_plot_booking_weekday, _q_booking_weekday,  "booking_weekday"),
        (_plot_booking_hours,   _q_booking_hours,    "booking_hours"),
        (_plot_skill_levels,    _q_skill_levels,     "skill_levels"),
        (_plot_skills_category, _q_skills_category,  "skills_category"),
        (_plot_top_employees,   _q_top_employees,    "top_employees"),
    ]

    for plot_fn, query_fn, report_id in tasks:
        try:
            path = plot_fn(query_fn(engine), fmt)
            if path:
                generated.append(_file_meta(path, report_id, fmt))
        except Exception as exc:
            print(f"WARN: {report_id} failed: {exc}")

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
            if path.exists():
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
