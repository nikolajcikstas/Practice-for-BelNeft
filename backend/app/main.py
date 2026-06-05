from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import bookings, employees, skills

app = FastAPI(
    title="Портал управления компетенциями и расписанием",
    version="1.0.0",
    description="Внутренний портал отдела цифровизации строительства",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(skills.router)
app.include_router(bookings.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
