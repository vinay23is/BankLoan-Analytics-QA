from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ReconciliationResult:
    kpi_name: str
    pandas_value: float
    sql_value: float
    difference: float
    tolerance: float
    status: str   # PASS / FAIL


def reconcile(pandas_kpis: Dict[str, float],
              sql_kpis: Dict[str, float],
              tolerance: float = 0.01) -> List[ReconciliationResult]:
    """Compare KPI values from two computation methods.

    A FAIL means the two methods disagree beyond the tolerance threshold,
    which in a real environment would indicate a calculation error in the
    BI layer (e.g. a wrong DAX filter or stale report refresh).
    """
    results = []
    for name in pandas_kpis:
        pv   = float(pandas_kpis[name])
        sv   = float(sql_kpis.get(name, 0.0))
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
