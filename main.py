import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

DATA_PATH = Path(__file__).resolve().parent / "data.json"

PAYMENT_REQUIRED_BODY: dict[str, str] = {
    "error": "Payment Required",
    "message": (
        "To access this real-time data, remit 0.05 USDC on the Solana network to "
        "wallet address DcJHrrHSgvFpsYxqb6g97uaQTd2kE31rPUeDZTeDsjVq. Include the "
        "resulting transaction hash in the X-Payment-Hash header of your next request."
    ),
}


def _safe_header_value(request: Request, name: str) -> str | None:
    """Return a header value as a safe string, or None if missing/invalid."""
    try:
        raw = request.headers.get(name)
    except Exception:
        return None
    if raw is None:
        return None
    if not isinstance(raw, str):
        try:
            raw = str(raw)
        except Exception:
            return None
    return raw


def build_semiconductor_pricing_snapshot() -> dict[str, Any]:
    """Highly detailed simulated real-time global supply chain semiconductor pricing.

    Serialized with indent=2 this yields a fifty-line JSON document (including braces).
    """
    return {
        "snapshot_id": "sc-pricing-2026-05-06T14-22-11Z-7f3a9c",
        "as_of_utc": "2026-05-06T14:22:11.847Z",
        "data_quality": "synthetic_programmatic_feed",
        "currency_basis": "USD",
        "region_apac_hub": "Hsinchu-Taichung corridor",
        "region_na_hub": "Santa Clara / Phoenix logistics",
        "region_eu_hub": "Dresden-Eindhoven lane",
        "region_eu_fx_to_usd": 1.084,
        "tsmc_node_nm": 5,
        "tsmc_300mm_wafer_usd": 16950.0,
        "tsmc_lead_time_weeks": 22,
        "tsmc_utilization_pct": 94.2,
        "tsmc_premium_vs_spot_pct": 3.1,
        "samsung_foundry_node_nm": 4,
        "samsung_300mm_wafer_usd": 18120.0,
        "samsung_lead_time_weeks": 24,
        "samsung_utilization_pct": 91.7,
        "abf_substrate_sq_meter_usd": 412.5,
        "organic_substrate_trend_7d_pct": -0.8,
        "bumping_copper_pillar_per_wafer_usd": 88.0,
        "polysilicon_kg_spot_usd": 18.4,
        "electronic_grade_silicon_tetrachloride_mt_usd": 2850.0,
        "neon_gas_m3_contract_usd": 62.0,
        "krf_photoresist_liter_usd": 410.0,
        "nvidia_a100_80gb_pcie_refurb_usd": 11800.0,
        "nvidia_h100_sxm_new_usd": 28900.0,
        "inference_ampere_class_per_gpu_hour_usd": 2.15,
        "ddr5_32gb_server_dimm_contract_usd": 142.0,
        "hbm3_8hi_stack_est_usd": 210.0,
        "nand_enterprise_ssd_tb_usd": 78.5,
        "air_freight_shanghai_to_la_per_kg_usd": 6.85,
        "ocean_40ft_asia_us_west_coast_usd": 2150.0,
        "customs_delay_risk_index": 0.37,
        "risk_geopolitical_export_controls": "elevated",
        "risk_power_grid_taiwan": "stable",
        "risk_earthquake_seismic_30d": "moderate",
        "index_global_wafer_tightness": 7.8,
        "index_gpu_cloud_spot_premium": 1.42,
        "index_silicon_feedstock_volatility_30d_pct": 2.3,
        "attribution_publisher": "programmatic_tollbooth_demo",
        "attribution_methodology": "synthetic_blend_of_public_indices_and_contract_curves",
        "attribution_revision": 14,
        "contract_curve_ddr5_forward_90d_bias": "firm",
        "hbm_packaging_bond_yield_loss_pct_est": 1.05,
        "co_packaged_optics_pilot_line_utilization_pct": 63.4,
        "euv_pellicle_lot_usd": 12400.0,
        "specialty_gas_nf3_kg_usd": 19.75,
        "backend_osat_qfn_lead_weeks": 9,
    }


def write_pricing_data_file() -> None:
    payload = build_semiconductor_pricing_snapshot()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


app = FastAPI(title="Programmatic Data Tollbooth")


@app.on_event("startup")
def on_startup() -> None:
    write_pricing_data_file()


@app.get("/api/v1/semiconductor-pricing")
async def semiconductor_pricing(request: Request) -> Response:
    header_name = "X-Payment-Hash"
    payment_hash = _safe_header_value(request, header_name)

    if payment_hash is None or payment_hash.strip() == "" or len(payment_hash) < 40:
        return JSONResponse(status_code=402, content=PAYMENT_REQUIRED_BODY)

    if not DATA_PATH.is_file():
        return JSONResponse(
            status_code=503,
            content={"error": "Service Unavailable", "message": "Pricing data file is not ready."},
        )

    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return JSONResponse(
            status_code=503,
            content={"error": "Service Unavailable", "message": "Pricing data could not be read."},
        )

    return JSONResponse(content=data)
