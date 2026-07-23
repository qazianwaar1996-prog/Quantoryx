# backend/schemas/api_schemas.py
"""
Quantoryx — API Schemas Module.

This module defines all the Pydantic schemas for request validation and
response serialization across the Quantoryx FastAPI enterprise backend.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# =====================================================================
# GENERAL SYSTEM SCHEMAS
# =====================================================================

class HealthResponse(BaseModel):
    """Schema for the GET /health endpoint."""
    status: str = Field(..., description="The operating status of the backend API (e.g., 'OK')")
    timestamp: datetime = Field(..., description="The current server UTC timestamp")
    uptime_seconds: float = Field(..., description="The elapsed system uptime in seconds")


class VersionResponse(BaseModel):
    """Schema for the GET /version endpoint."""
    system_name: str = Field(..., description="The framework branding name")
    version: str = Field(..., description="The semantic version number of the system")


class StatusResponse(BaseModel):
    """Schema for the GET /status endpoint."""
    active: bool = Field(..., description="Flag indicating if the system is ready to process requests")
    workspace_initialized: bool = Field(..., description="Flag indicating if directories are mapped")
    supported_pairs: List[str] = Field(..., description="List of recognized instruments")
    supported_timeframes: List[str] = Field(..., description="List of supported chart intervals")


# =====================================================================
# BACKTESTING SCHEMAS
# =====================================================================

class BacktestRequest(BaseModel):
    """Schema for the POST /backtest endpoint request."""
    strategy: str = Field(..., description="Target strategy key, e.g., 'EMA', 'RSI', 'MACD'")
    symbol: str = Field("EURUSD", description="Target currency pair or instrument symbol")
    timeframe: str = Field("1H", description="Data chart timeframe (e.g., '1H', '1D')")
    fast_period: Optional[int] = Field(None, description="Optional fast window override parameter")
    slow_period: Optional[int] = Field(None, description="Optional slow window override parameter")
    custom_params: Optional[Dict[str, Any]] = Field(None, description="Arbitrary custom strategy parameter overrides")


class BacktestMetrics(BaseModel):
    """Portfolio metrics calculated during a simulation run."""
    net_profit: float = Field(..., description="Total accumulated net profit or loss")
    profit_factor: float = Field(..., description="Gross profit divided by absolute gross loss")
    max_drawdown: float = Field(..., description="Peak-to-trough maximum drawdown amount")
    win_rate: float = Field(..., description="The percentage of winning trade setups")
    sharpe_ratio: float = Field(..., description="The estimated annualized risk-adjusted return ratio")


class BacktestResponse(BaseModel):
    """Schema for the POST /backtest endpoint response."""
    strategy: str = Field(..., description="Executed strategy name")
    symbol: str = Field(..., description="Target instrument ticker")
    timeframe: str = Field(..., description="Selected timeframe interval")
    parameters: Dict[str, Any] = Field(..., description="Final parameters utilized during run")
    metrics: BacktestMetrics = Field(..., description="Calculated performance metrics")
    trade_count: int = Field(..., description="Total count of simulated trade setups executed")


# =====================================================================
# OPTIMIZATION SCHEMAS
# =====================================================================

class OptimizeRequest(BaseModel):
    """Schema for the POST /optimize endpoint request."""
    strategy: str = Field(..., description="Target strategy key, e.g., 'EMA', 'RSI', 'MACD'")
    symbol: str = Field("EURUSD", description="Target instrument ticker")
    timeframe: str = Field("1H", description="Target chart timeframe")
    metric: str = Field("sharpe_ratio", description="Primary ranking metric (e.g., 'sharpe_ratio', 'net_profit')")


class OptimizationResultRow(BaseModel):
    """Schema representing an individual parameter set result row."""
    rank: int = Field(..., description="Relative score placement ranking")
    strategy: str = Field(..., description="Evaluated strategy name")
    symbol: str = Field(..., description="Instrument symbol")
    timeframe: str = Field(..., description="Chart timeframe")
    parameters: Dict[str, Any] = Field(..., description="The parameter combination tested")
    net_profit: float = Field(..., description="The achieved net profit")
    profit_factor: float = Field(..., description="The achieved profit factor")
    max_drawdown: float = Field(..., description="The maximum drawdown")
    win_rate: float = Field(..., description="The ratio of winning executions")
    sharpe_ratio: float = Field(..., description="The annualized Sharpe ratio")


class OptimizeResponse(BaseModel):
    """Schema for the POST /optimize endpoint response."""
    strategy: str = Field(..., description="Optimized strategy name")
    symbol: str = Field(..., description="Target symbol ticker")
    timeframe: str = Field(..., description="Selected timeframe")
    ranking_metric: str = Field(..., description="Metric used to rank combinations")
    best_parameters: Dict[str, Any] = Field(..., description="The highest ranked parameter values")
    total_combinations_tested: int = Field(..., description="Total parameter permutations evaluated")
    top_results: List[OptimizationResultRow] = Field(..., description="Top ranked parameter configuration listings")


# =====================================================================
# WALK-FORWARD SCHEMAS
# =====================================================================

class WalkForwardRequest(BaseModel):
    """Schema for the POST /walk-forward endpoint request."""
    strategy: str = Field(..., description="Target strategy name")
    symbol: str = Field("EURUSD", description="Target trading pair")
    timeframe: str = Field("1H", description="Target timeframe mapping")
    train_days: int = Field(180, description="In-sample historical training window size in calendar days")
    test_days: int = Field(60, description="Out-of-sample unseen test window size in calendar days")
    metric: str = Field("sharpe_ratio", description="Optimization metric used to evaluate training periods")


class FoldResult(BaseModel):
    """Schema representing results for an individual walk-forward validation fold."""
    fold: int = Field(..., description="Chronological fold slice index")
    train_start: str = Field(..., description="Start of In-Sample calendar date")
    train_end: str = Field(..., description="End of In-Sample calendar date")
    test_start: str = Field(..., description="Start of Out-of-Sample calendar date")
    test_end: str = Field(..., description="End of Out-of-Sample calendar date")
    parameters: Dict[str, Any] = Field(..., description="Best parameters determined during training phase")
    is_sharpe_ratio: float = Field(..., description="In-Sample Sharpe ratio metric")
    oos_sharpe_ratio: float = Field(..., description="Out-of-Sample Sharpe ratio metric")
    is_net_profit: float = Field(..., description="In-Sample cumulative net profit")
    oos_net_profit: float = Field(..., description="Out-of-Sample cumulative net profit")


class WalkForwardResponse(BaseModel):
    """Schema for the POST /walk-forward endpoint response."""
    strategy: str = Field(..., description="Target strategy name validated")
    symbol: str = Field(..., description="Trading pair instrument symbol")
    timeframe: str = Field(..., description="Target data timeframe interval")
    train_days: int = Field(..., description="Train window size in days")
    test_days: int = Field(..., description="Test window size in days")
    mean_is_sharpe: float = Field(..., description="Average In-Sample Sharpe ratio across all folds")
    mean_oos_sharpe: float = Field(..., description="Average Out-of-Sample Sharpe ratio across all folds")
    total_oos_profit: float = Field(..., description="Aggregated Out-of-Sample net profit across all folds")
    folds: List[FoldResult] = Field(..., description="Detailed records per evaluated fold slice")


# =====================================================================
# PAPER TRADING SCHEMAS
# =====================================================================

class PaperTradingRequest(BaseModel):
    """Schema for the POST /paper-trading endpoint request."""
    symbol: str = Field("EURUSD", description="Instrument symbol to trade paper capital against")
    capital: float = Field(100000.0, description="Starting virtual account balance")
    leverage: float = Field(30.0, description="Account leverage mapping multiplier")
    spread: float = Field(0.0002, description="Target transaction spread mapped as a decimal multiplier")


class TradeLogEntry(BaseModel):
    """Schema representing an individual completed trade record entry."""
    symbol: str = Field(..., description="Traded asset symbol")
    direction: str = Field(..., description="Order direction ('LONG' or 'SHORT')")
    entry_time: str = Field(..., description="Calendar time of order opening")
    exit_time: str = Field(..., description="Calendar time of order closing")
    entry_price: float = Field(..., description="Open fill price level")
    exit_price: float = Field(..., description="Close fill price level")
    size: float = Field(..., description="Traded order volume size in units")
    pnl: float = Field(..., description="Realized transaction profit or loss")
    reason: str = Field(..., description="Closed trigger reasoning description")
    entry_regime: str = Field(..., description="Classified market regime at entry time")


class PaperTradingResponse(BaseModel):
    """Schema for the POST /paper-trading endpoint response."""
    symbol: str = Field(..., description="Paper traded instrument ticker")
    starting_balance: float = Field(..., description="Starting capital allocation balance")
    terminal_balance: float = Field(..., description="End state cash ledger balance")
    terminal_equity: float = Field(..., description="End state net equity (including unrealized pnl)")
    total_trades_executed: int = Field(..., description="Total trades finalized during run")
    recent_trades: List[TradeLogEntry] = Field(..., description="Sample listings of recently executed trade logs")


# =====================================================================
# AI ANALYSIS SCHEMAS
# =====================================================================

class AIAnalysisRequest(BaseModel):
    """Schema for the POST /ai-analysis endpoint request."""
    symbol: str = Field("EURUSD", description="Target trading asset")
    timeframe: str = Field("1H", description="Target timeframe interval")
    threshold: float = Field(65.0, description="Confidence score requirement limit to permit execution")


class StrategySummary(BaseModel):
    """Summary of historical strategy performance metrics supplied to the AI engine."""
    strategy: str = Field(..., description="Name of strategy evaluated")
    avg_oos_sharpe: float = Field(..., description="Estimated Sharpe ratio performance")
    avg_oos_win_rate: float = Field(..., description="Estimated Win Rate ratio")
    avg_oos_profit_factor: float = Field(..., description="Estimated Profit Factor ratio")
    active_params: Dict[str, Any] = Field(..., description="Optimized operational parameters")


class AIAnalysisResponse(BaseModel):
    """Schema for the POST /ai-analysis endpoint response."""
    timestamp: str = Field(..., description="Evaluation runtime timestamp mapping")
    symbol: str = Field(..., description="Target instrument evaluated")
    timeframe: str = Field(..., description="Chart timeframe context")
    market_regime: str = Field(..., description="Classified active market regime context")
    selected_strategy: str = Field(..., description="Champion strategy nominated for operation")
    confidence_score: float = Field(..., description="Synthesized confidence rating (0 - 100)")
    decision_action: str = Field(..., description="Determined operational status ('EXECUTE' or 'SKIP')")
    explanation: str = Field(..., description="Cognitive narrative explication reasoning")
    parameters: Dict[str, Any] = Field(..., description="The nominated champion model parameters")


# =====================================================================
# PORTFOLIO AND REPORT SCHEMAS
# =====================================================================

class EquityCurvePoint(BaseModel):
    """Schema representing an individual equity curve data point."""
    date: str = Field(..., description="Date or snapshot timestamp mapping")
    balance: float = Field(..., description="Ledger account cash balance")
    equity: float = Field(..., description="Ledger account net equity valuation")
    drawdown_pct: float = Field(..., description="Accumulated peak drawdown percent ratio")


class PortfolioResponse(BaseModel):
    """Schema for the GET /portfolio endpoint response."""
    starting_balance: float = Field(..., description="Initial cash allocation")
    ending_equity: float = Field(..., description="End cash valuation")
    total_return_pct: float = Field(..., description="Cumulative performance yield ratio")
    max_drawdown_pct: float = Field(..., description="Absolute peak-to-trough account drawdown percent")
    sharpe_ratio: float = Field(..., description="Portfolio annualized Sharpe ratio score")
    total_trades: int = Field(..., description="Total completed portfolio trades recorded")
    win_rate: float = Field(..., description="Combined win rate coefficient percentage")
    profit_factor: float = Field(..., description="Combined profit factor multiplier")
    equity_curve: List[EquityCurvePoint] = Field(..., description="Daily portfolio equity track histories")


class ReportItem(BaseModel):
    """Schema representing a compiled system output report file meta."""
    filename: str = Field(..., description="Raw output filename mapping")
    category: str = Field(..., description="Folder categorizing destination")
    size_kb: float = Field(..., description="File storage footprint size in Kilobytes")
    last_modified: str = Field(..., description="Timestamp of last modification")


class ReportsListResponse(BaseModel):
    """Schema for the GET /reports endpoint response."""
    reports_count: int = Field(..., description="Total counts of compiled report logs mapped")
    reports: List[ReportItem] = Field(..., description="Details of verified output reports")


# =====================================================================
# STRATEGIES AND REGIME SCHEMAS
# =====================================================================

class StrategySchemaDetail(BaseModel):
    """Schema detailed parameters of an individual strategy."""
    name: str = Field(..., description="Target class registry identifier")
    config_key: str = Field(..., description="Configuration lookup dictionary default key")
    default_parameters: Dict[str, Any] = Field(..., description="Default operational strategy parameters")


class StrategiesResponse(BaseModel):
    """Schema for the GET /strategies endpoint response."""
    strategies: List[StrategySchemaDetail] = Field(..., description="Metadata list of registered strategy models")


class MarketRegimeResponse(BaseModel):
    """Schema for the GET /market-regime endpoint response."""
    symbol: str = Field(..., description="Evaluated instrument context")
    timeframe: str = Field(..., description="Selected timeframe context")
    total_bars_analyzed: int = Field(..., description="Total chart bar indices verified")
    distribution: Dict[str, int] = Field(..., description="Raw index counts per classified market regime")
    percentage_distribution: Dict[str, float] = Field(..., description="Ratio density mapping per market regime")


# =====================================================================
# SYSTEM HEALTH SCHEMAS
# =====================================================================

class ModuleValidationStatus(BaseModel):
    """Module status mapping payload."""
    engine_backtest_engine: str = Field(..., alias="engine.backtest_engine")
    optimizer_param_ranges: str = Field(..., alias="optimizer.param_ranges")
    optimizer_optimizer_engine: str = Field(..., alias="optimizer.optimizer_engine")
    market_regime_detector: str = Field(..., alias="market_regime.detector")
    market_regime_analyzer: str = Field(..., alias="market_regime.analyzer")
    walk_forward_validation_engine: str = Field(..., alias="walk_forward.validation_engine")
    risk_risk_manager: str = Field(..., alias="risk.risk_manager")
    portfolio_portfolio_manager: str = Field(..., alias="portfolio.portfolio_manager")
    paper_trading_paper_engine: str = Field(..., alias="paper_trading.paper_engine")
    ai_engine_decision_engine: str = Field(..., alias="ai_engine.decision_engine")

    class Config:
        allow_population_by_field_name = True


class BenchmarkPerformance(BaseModel):
    """Benchmark monitoring statistics."""
    execution_status: str = Field(..., description="Run status of the validator loop")
    execution_time_seconds: float = Field(..., description="Time taken to run benchmark in seconds")
    peak_memory_usage_mb: float = Field(..., description="Memory footprint monitored during run in MB")


class SystemHealthResponse(BaseModel):
    """Schema for the GET /system-health endpoint response, matching pipeline_validator structure."""
    timestamp: str = Field(..., description="Datetime metadata mapping")
    status: str = Field(..., description="Global system operational code (e.g., 'PASS', 'WARNING')")
    modules_validation: Dict[str, str] = Field(..., description="Status mappings per validated core import module")
    report_audit: Dict[str, str] = Field(..., description="Audit status per expected CSV ledger output")
    benchmarks: BenchmarkPerformance = Field(..., description="Profile runtime metrics")
    warnings: List[str] = Field(..., description="Identified warning event strings")
    recommendations: List[str] = Field(..., description="Recommended tuning or optimization steps")


# =====================================================================
# DASHBOARD SCHEMAS
# =====================================================================

class DashboardResponse(BaseModel):
    """Schema for the GET /dashboard endpoint response, yielding dashboard analytics overview."""
    active_symbol: str = Field(..., description="Instrument symbol running active")
    active_timeframe: str = Field(..., description="Timeframe running active")
    champion_strategy: str = Field(..., description="Champion strategy nominated by the AI module")
    ai_confidence_score: float = Field(..., description="Confidence score coefficient")
    market_regime: str = Field(..., description="Active market context")
    ai_status: str = Field(..., description="The operating decision execution verdict")
    portfolio_summary: Dict[str, Any] = Field(..., description="Core portfolio metrics overview")
    recent_executed_trades: List[TradeLogEntry] = Field(..., description="Recent transaction ledger listings")


# =====================================================================
# v4.5 USER SETTINGS SCHEMAS
# =====================================================================

class UserSettingsResponse(BaseModel):
    """Response model for user settings configuration."""
    id: int = Field(..., description="The unique row ID of the settings record")
    user_id: str = Field(..., description="The matching user UUID index")
    default_symbol: str = Field(..., description="Pre-selected trading instrument ticker")
    default_timeframe: str = Field(..., description="Pre-selected default chart timeframe")
    risk_per_trade_pct: float = Field(..., description="Calculated trade-level risk percentage")
    leverage: float = Field(..., description="Default margin leverage mapping value")
    spread: float = Field(..., description="Assumed spread multiplier used for backtests")
    confidence_threshold: float = Field(..., description="Pre-selected confidence limit for execution approval")
    updated_at: datetime = Field(..., description="The timestamp of the last configuration save")

    class Config:
        orm_mode = True


class UserSettingsUpdateRequest(BaseModel):
    """Validation structure when updating user operational settings."""
    default_symbol: Optional[str] = Field(None, max_length=20, description="New default asset symbol")
    default_timeframe: Optional[str] = Field(None, max_length=10, description="New default timeframe interval")
    risk_per_trade_pct: Optional[float] = Field(None, ge=0.1, le=10.0, description="Adjusted default risk percentage")
    leverage: Optional[float] = Field(None, ge=1.0, le=500.0, description="Adjusted operational leverage")
    spread: Optional[float] = Field(None, ge=0.0, description="Adjusted standard spread cost ratio")
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=100.0, description="Adjusted validation threshold")


# =====================================================================
# v4.5 PORTFOLIO HOLDINGS & ALLOCATION SCHEMAS
# =====================================================================

class ActivePositionResponse(BaseModel):
    """Response model representing a live, open trading position (Holdings)."""
    id: int = Field(..., description="Position unique record row ID")
    user_id: str = Field(..., description="Asset holder user ID")
    symbol: str = Field(..., description="Traded asset ticker symbol")
    direction: str = Field(..., description="Current position trend direction (LONG or SHORT)")
    entry_time: datetime = Field(..., description="Live entry timestamp execution value")
    entry_price: float = Field(..., description="Base fill execution entry price")
    size: float = Field(..., description="Total holdings unit volumes")
    stop_loss: float = Field(..., description="Configured dynamic stop loss trigger level")
    take_profit: float = Field(..., description="Configured dynamic target profit trigger level")
    required_margin: float = Field(..., description="Allocated capital leverage margin utilized")
    entry_regime: Optional[str] = Field(None, description="The identified market context at the time of entry")

    class Config:
        orm_mode = True


# =====================================================================
# v4.5 WATCHLIST SCHEMAS
# =====================================================================

class WatchlistItemResponse(BaseModel):
    """Serialized item nested inside a Watchlist."""
    id: int = Field(..., description="The unique watchlist item index ID")
    watchlist_id: int = Field(..., description="The watchlist parent record ID")
    symbol: str = Field(..., description="The asset symbol")
    created_at: datetime = Field(..., description="Creation date timestamp")

    class Config:
        orm_mode = True


class WatchlistResponse(BaseModel):
    """Serialized watchlist containing grouping names and nested item listings."""
    id: int = Field(..., description="The watchlist unique index ID")
    user_id: str = Field(..., description="The associated owner user UUID")
    name: str = Field(..., description="The designated watchlist classification name")
    created_at: datetime = Field(..., description="The creation timestamp")
    items: List[WatchlistItemResponse] = Field([], description="The list of nested tracking ticker symbols")

    class Config:
        orm_mode = True


class WatchlistCreateRequest(BaseModel):
    """Validation structure when instantiating a new Watchlist."""
    name: str = Field(..., min_length=1, max_length=50, description="Watchlist classification name")


class WatchlistItemCreateRequest(BaseModel):
    """Validation structure when appending a ticker symbol into a Watchlist."""
    symbol: str = Field(..., min_length=2, max_length=20, description="Ticker symbol to track")


# =====================================================================
# v4.5 NOTIFICATION SCHEMAS
# =====================================================================

class NotificationResponse(BaseModel):
    """Response model representing a single warning alert or notice message."""
    id: int = Field(..., description="The notification unique record index ID")
    user_id: str = Field(..., description="Target recipient user UUID")
    title: str = Field(..., description="Short heading summary")
    message: str = Field(..., description="Detailed message notification string")
    is_read: bool = Field(..., description="Flag indicating if the user has dismissed the notification")
    created_at: datetime = Field(..., description="The generation timestamp")

    class Config:
        orm_mode = True
