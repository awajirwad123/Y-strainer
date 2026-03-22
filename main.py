"""
main.py — FastAPI application for the Y-Strainer Pressure Drop Calculator.

Web routes
──────────
GET  /           → calculator UI (requires login)
GET  /login      → login page
POST /login      → authenticate
GET  /signup     → registration page
POST /signup     → create account
GET  /logout     → clear session

API endpoints
─────────────
POST /calculate
POST /calculate/from-selection
GET  /lookup/meshes
GET  /lookup/perforations
GET  /lookup/strainer-models

Run with:
    uvicorn main:app --reload
"""

import secrets
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from schemas import (
    CalculationRequest,
    LookupRequest,
    CalculationResponse,
    MeshOption,
    PerfOption,
    StrainerSizeOption,
)
from calculator import calculate
from config import MESH_DATA, PERF_SHEET_DATA, STRAINER_DATA
from database import init_db, create_user, get_user_by_username, verify_password

# ── Session secret (persisted between restarts) ────────────────────────────────
_SECRET_FILE = Path(__file__).parent / ".session_secret"


def _get_session_secret() -> str:
    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_text().strip()
    key = secrets.token_hex(32)
    _SECRET_FILE.write_text(key)
    return key


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def _lifespan(application: FastAPI):
    init_db()
    yield


# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Y-Strainer Pressure Drop Calculator",
    description=(
        "Calculates pressure drop across Y-strainers for two conditions: "
        "100 % clean screen and 50 % clogged screen. "
        "Implements the Forbes Marshall formula chain validated against 14 software screenshots."
    ),
    version="1.0.0",
    lifespan=_lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=_get_session_secret())

_BASE = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(_BASE / "static")), name="static")
templates = Jinja2Templates(directory=str(_BASE / "templates"))


# ── Auth helpers ───────────────────────────────────────────────────────────────
def _current_user(request: Request) -> str | None:
    return request.session.get("username")


# ── Web routes ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request):
    if not _current_user(request):
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(
        "calculator.html", {"request": request, "username": _current_user(request)}
    )


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request):
    if _current_user(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse, include_in_schema=False)
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user = get_user_by_username(username)
    if user and verify_password(password, user["password_hash"]):
        request.session["username"] = user["username"]
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid username or password."},
    )


@app.get("/signup", include_in_schema=False)
@app.post("/signup", include_in_schema=False)
def signup_disabled(request: Request):
    """Registration is closed — accounts are created by the administrator only."""
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Page not found")


@app.get("/logout", include_in_schema=False)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ── Primary calculation endpoint ───────────────────────────────────────────────

@app.post(
    "/calculate",
    response_model=CalculationResponse,
    summary="Calculate pressure drop — direct inputs",
    tags=["calculation"],
)
def calculate_direct(req: CalculationRequest) -> CalculationResponse:
    """All geometry and fluid properties are provided directly by the caller."""
    result = calculate(
        rho=req.rho,
        mu_cP=req.mu_cP,
        W=req.W,
        flow_unit=req.flow_unit,
        D_pipe_cm=req.D_pipe_cm,
        D_screen_cm=req.D_screen_cm,
        L_cm=req.L_cm,
        D_open_cm=req.D_open_cm,
        Q_pct=req.Q_pct,
        P_pct=req.P_pct,
    )
    return CalculationResponse(tag_no=req.tag_no, fluid_name=req.fluid_name, **result)


# ── Lookup-based calculation endpoint ─────────────────────────────────────────

@app.post(
    "/calculate/from-selection",
    response_model=CalculationResponse,
    summary="Calculate pressure drop — model / mesh / perf selection",
    tags=["calculation"],
)
def calculate_from_selection(req: LookupRequest) -> CalculationResponse:
    """Resolve geometry from the reference tables, then run the calculation.

    - model + nps  →  D_pipe_cm, D_screen_cm, L_cm   (Strainer data sheet)
    - mesh + swg   →  D_open_cm, Q_pct               (Mesh Data sheet)
    - perforation  →  P_pct                           (Perf Sheet sheet)

    No-Mesh case: set mesh=0 and provide D_open_cm_override.
    """
    # ── Strainer geometry ──────────────────────────────────────────────────────
    strainer_key = (req.model.strip().upper(), req.nps.strip())
    if strainer_key not in STRAINER_DATA:
        raise HTTPException(
            status_code=404,
            detail=f"Strainer model '{req.model}' NPS '{req.nps}' not found in catalogue."
                   " Use GET /lookup/strainer-models to see available options.",
        )
    pipe_OD_mm, screen_D_mm, screen_L_mm = STRAINER_DATA[strainer_key]
    D_pipe_cm = pipe_OD_mm / 10.0
    D_screen_cm = screen_D_mm / 10.0
    L_cm = screen_L_mm / 10.0

    # ── Mesh / opening data ────────────────────────────────────────────────────
    if req.mesh == 0:
        # No-Mesh case: full open area, caller must supply effective opening width
        Q_pct = 100.0
        if req.D_open_cm_override is None:
            raise HTTPException(
                status_code=422,
                detail="D_open_cm_override is required when mesh=0 (No Mesh).",
            )
        D_open_cm = req.D_open_cm_override
    else:
        mesh_key = (req.mesh, req.swg)
        if mesh_key not in MESH_DATA:
            raise HTTPException(
                status_code=404,
                detail=f"Mesh {req.mesh} × SWG {req.swg} not found."
                       " Use GET /lookup/meshes to see available options.",
            )
        opening_mm, Q_pct = MESH_DATA[mesh_key]
        D_open_cm = opening_mm / 10.0

    # ── Perforation data ───────────────────────────────────────────────────────
    perf_key = req.perforation.strip().upper()
    if perf_key not in PERF_SHEET_DATA:
        raise HTTPException(
            status_code=404,
            detail=f"Perforation '{req.perforation}' not found."
                   " Use GET /lookup/perforations to see available options.",
        )
    P_pct = PERF_SHEET_DATA[perf_key]

    # ── Run calculation ────────────────────────────────────────────────────────
    result = calculate(
        rho=req.rho,
        mu_cP=req.mu_cP,
        W=req.W,
        flow_unit=req.flow_unit,
        D_pipe_cm=D_pipe_cm,
        D_screen_cm=D_screen_cm,
        L_cm=L_cm,
        D_open_cm=D_open_cm,
        Q_pct=Q_pct,
        P_pct=P_pct,
    )
    return CalculationResponse(tag_no=req.tag_no, fluid_name=req.fluid_name, **result)


# ── Lookup list endpoints ──────────────────────────────────────────────────────

@app.get(
    "/lookup/meshes",
    response_model=list[MeshOption],
    summary="List available mesh options",
    tags=["lookup"],
)
def list_meshes() -> list[MeshOption]:
    """Returns all (mesh, SWG) combinations with opening size and open-area %."""
    return [
        MeshOption(mesh=m, swg=s, opening_mm=v[0], open_area_pct=v[1])
        for (m, s), v in sorted(MESH_DATA.items())
    ]


@app.get(
    "/lookup/perforations",
    response_model=list[PerfOption],
    summary="List available perforation options",
    tags=["lookup"],
)
def list_perforations() -> list[PerfOption]:
    """Returns all perforation descriptions with their open-area %."""
    return [
        PerfOption(description=desc, open_area_pct=pct)
        for desc, pct in PERF_SHEET_DATA.items()
    ]


@app.get(
    "/lookup/strainer-models",
    response_model=list[StrainerSizeOption],
    summary="List available strainer models and sizes",
    tags=["lookup"],
)
def list_strainer_models() -> list[StrainerSizeOption]:
    """Returns all (model, NPS) combinations with screen and pipe dimensions."""
    return [
        StrainerSizeOption(
            model=k[0], nps=k[1],
            pipe_OD_mm=v[0], screen_D_mm=v[1], screen_L_mm=v[2],
        )
        for k, v in sorted(STRAINER_DATA.items())
    ]
