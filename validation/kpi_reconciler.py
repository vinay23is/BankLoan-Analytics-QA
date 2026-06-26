from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ReconciliationResult:
    kpi_name: str
    pandas_value: float
    sql_value: Optional[float]
    difference: Optional[float]
    tolerance: float
    status: str   # PASS / FAIL


def reconcile(pandas_kpis: Dict[str, float],
              sql_kpis: Dict[str, float],
              tolerance: float = 0.01) -> List[ReconciliationResult]:
    """Compare KPI values from two computation methods.

    A FAIL means the two methods disagree beyond the tolerance threshold,
    or the SQL side did not return the KPI at all — which in a real
    environment would indicate a calculation error or missing measure
    in the BI layer.
    """
    results = []
    for name in pandas_kpis:
        pv = float(pandas_kpis[name])
        if name not in sql_kpis:
            results.append(ReconciliationResult(
                kpi_name=name,
                pandas_value=pv,
                sql_value=None,
                difference=None,
                tolerance=tolerance,
                status="FAIL",
            ))
            continue
        sv   = float(sql_kpis[name])
        diff = abs(pv - sv)
        results.append(ReconciliationResult(
            kpi_name=name,
            pandas_value=pv,
            sql_value=sv,
            difference=round(diff, 6),
            tolerance=tolerance,
            status="PASS" if diff <= tolerance else "FAIL",
        ))
    return results
