# backend/api/endpoints.py
"""
Quantoryx — API Endpoints Router Module.

This module maps HTTP paths to backend operations, validating inputs through 
Pydantic model structures and delegating system computations to the QuantoryxService.
"""

from fastapi import APIRouter, HTTPException, Query, status

# Import schemas and services
from backend.schemas.api_schemas import (
    HealthResponse,
    VersionResponse,
    StatusResponse,
    BacktestRequest,
    BacktestResponse,
    OptimizeRequest,
    OptimizeResponse,
    WalkForwardRequest,
    WalkForwardResponse,
    PaperTradingRequest,
    PaperTradingResponse,
    AIAnalysisRequest,
    AIAnalysisResponse,
    DashboardResponse,
    PortfolioResponse,
    ReportsListResponse,
    StrategiesResponse,
    MarketRegimeResponse,
    SystemHealthResponse
)
from backend.services.quantoryx_service import QuantoryxService

# Initialize Router
router = APIRouter(tags=["Quantoryx Core Engine API"])


# =====================================================================
# SYSTEM DIAGNOSTIC ENDPOINTS
# =====================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get API Operational Health",
    description="Returns operating uptime and UTC system times to monitor service integrity."
)
async def get_health():
    try:
        return QuantoryxService.get_health_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve system operational health: {str(e)}"
        )


@router.get(
    "/version",
    response_model=VersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get System Version Metadata",
    description="Returns system branding details and semantic version codes."
)
async def get_version():
    try:
        return QuantoryxService.get_version_info()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve version specifications: {str(e)}"
        )


@router.get(
    "/status",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Framework Status Overview",
    description="Returns recognized instruments, chart timeframes, and folder initialization flags."
)
async def get_status():
    try:
        return QuantoryxService.get_system_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve framework statuses: {str(e)}"
        )


# =====================================================================
# SIMULATION & ANALYSIS ENDPOINTS (POST)
# =====================================================================

@router.post(
    "/backtest",
    response_model=BacktestResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Strategy Backtest",
    description="Runs a single-strategy backtest sweep over pricing history and compiles KPIs."
)
async def post_backtest(payload: BacktestRequest):
    try:
        result = QuantoryxService.run_backtest_simulation(
            strategy=payload.strategy,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            fast_period=payload.fast_period,
            slow_period=payload.slow_period,
            custom_params=payload.custom_params
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parameter verification failed: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backtest simulation sweep failed: {str(e)}"
        )


@router.post(
    "/optimize",
    response_model=OptimizeResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Parameter Grid Optimization",
    description="Sweeps strategy parameters over prices, ranking sets by a target performance metric."
)
async def post_optimize(payload: OptimizeRequest):
    try:
        result = QuantoryxService.run_optimization_sweep(
            strategy=payload.strategy,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            metric=payload.metric
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verification failed: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization sweep failed: {str(e)}"
        )


@router.post(
    "/walk-forward",
    response_model=WalkForwardResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Walk-Forward Validation",
    description="Executes rolling training (In-Sample) and testing (Out-of-Sample) validation folds."
)
async def post_walk_forward(payload: WalkForwardRequest):
    try:
        result = QuantoryxService.run_walk_forward_validation(
            strategy=payload.strategy,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            train_days=payload.train_days,
            test_days=payload.test_days,
            metric=payload.metric
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payload processing error: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Walk-forward pipeline failed: {str(e)}"
        )


@router.post(
    "/paper-trading",
    response_model=PaperTradingResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Paper Trading Simulator",
    description="Executes virtual chronological orders on leveraged accounts, logging transactions and stops."
)
async def post_paper_trading(payload: PaperTradingRequest):
    try:
        result = QuantoryxService.run_paper_trading_simulator(
            symbol=payload.symbol,
            capital=payload.capital,
            leverage=payload.leverage,
            spread=payload.spread
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Execution error: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Paper trading simulation run failed: {str(e)}"
        )


@router.post(
    "/ai-analysis",
    response_model=AIAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Run AI Decision Analysis",
    description="Evaluates indicator configurations, detects active regimes, and nominates champion models."
)
async def post_ai_analysis(payload: AIAnalysisRequest):
    try:
        result = QuantoryxService.run_ai_strategy_selection(
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            threshold=payload.threshold
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AI context mapping failed: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI selection calculations failed: {str(e)}"
        )


# =====================================================================
# DATA RETRIEVAL ENDPOINTS (GET)
# =====================================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Dashboard Summary Overview",
    description="Consolidates system states, active session indicators, and transaction summaries."
)
async def get_dashboard():
    try:
        return QuantoryxService.get_dashboard_summary_overview()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to consolidate dashboard information: {str(e)}"
        )


@router.get(
    "/portfolio",
    response_model=PortfolioResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Portfolio Equity Performance",
    description="Assembles floating balance curve datasets, peak drawdowns, and annualized Sharpe ratios."
)
async def get_portfolio():
    try:
        return QuantoryxService.get_portfolio_snapshot()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile portfolio track snapshots: {str(e)}"
        )


@router.get(
    "/reports",
    response_model=ReportsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Compiled System Reports",
    description="Scans standard output directories and lists registered CSV output documents."
)
async def get_reports():
    try:
        return QuantoryxService.get_reports_registry()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query system directories: {str(e)}"
        )


@router.get(
    "/strategies",
    response_model=StrategiesResponse,
    status_code=status.HTTP_200_OK,
    summary="List Registered Trading Strategies",
    description="Returns metadata specifications and default parameter definitions of strategies."
)
async def get_strategies():
    try:
        return QuantoryxService.get_strategies_metadata()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to inspect strategy registry: {str(e)}"
        )


@router.get(
    "/market-regime",
    response_model=MarketRegimeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Market Regime Distribution Statistics",
    description="Runs regime classification and aggregates indicators to yield distribution parameters."
)
async def get_market_regime(
    symbol: str = Query("EURUSD", description="Instrument symbol to query"),
    timeframe: str = Query("1H", description="Target timeframe interval")
):
    try:
        return QuantoryxService.get_market_regime_distribution(symbol, timeframe)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile market regime distributions: {str(e)}"
        )


@router.get(
    "/system-health",
    response_model=SystemHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Live System Health Diagnostics",
    description="Executes a system diagnostic pass checking imports, scanning AST codes, and validating output schemas."
)
async def get_system_health():
    try:
        return QuantoryxService.run_system_health_validator()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run health validator suite: {str(e)}"
)
