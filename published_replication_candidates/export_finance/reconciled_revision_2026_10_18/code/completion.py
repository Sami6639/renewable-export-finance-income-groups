"""Section 13: unrestricted-income outer envelopes for the regional operation.

Importing this module is inert. ``run`` requires the approved protocol and a
cleared arithmetic screen. Each source case has its own four-vertex hull;
cross-case summaries take scalar extrema over a union, never a pooled hull.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

import core


PROTOCOL_SHA256 = "7834022e03efc32a3b6b6bfdab74c8651c65b73d7b98ae177d98221ca3126382"
PROTOCOL_NAME = "ANALYSIS_PROTOCOL.md"
REGIONAL_IDS = (1907, 1908)
PANELS = ("all_locations", "international_reporting")
MODEL = "unrestricted-income outer envelope; targeted Standard Bank completion"
KEYS = ["target_type", "target", "income_class", "provider", "metric", "unit"]
DOLLAR_ATOL = 1e-5
SHARE_ATOL = 1e-10
PP_ATOL = 1e-8


def _execution_gate() -> dict:
    """Fail closed before loading outcome data, including when raw is supplied."""
    from run_revision import gate as shared_execution_gate

    approval = shared_execution_gate()
    protocol = core.ROOT / "protocol" / PROTOCOL_NAME
    digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
    if digest != PROTOCOL_SHA256 or approval.get("sha256") != digest:
        raise RuntimeError("The section-13 approved protocol hash does not match.")
    gate = json.loads((core.ROOT / "audit/arithmetic_gate.json").read_text())
    if gate.get("protocol_sha256") != digest:
        raise RuntimeError("The arithmetic screen references a different protocol.")
    return {"protocol_sha256": digest, "arithmetic_screen_status": gate["status"],
            "arithmetic_execution_gate": "cleared directly" if gate["status"] == "CLEAR" else "fixed flag membership verified against the public protocol"}


def complete_regional_income(q: pd.DataFrame, fractions: Mapping[str, float]) -> pd.DataFrame:
    """Construct a completion directly, preserving source IDs and portfolio scope.

    Fractional fragments exist only for the interior verification. At a vertex,
    each original instrument remains one analytical component. Country status
    stays regional/unallocated: assigning an income class never invents a country.
    """
    f = np.asarray([fractions.get(c, 0.0) for c in core.CLASSES], dtype=float)
    if not np.all(np.isfinite(f)) or np.any(f < 0) or not np.isclose(f.sum(), 1, atol=1e-14, rtol=0):
        raise ValueError("Completion fractions must lie on the four-class simplex.")
    mask = q.source_excel_row.isin(REGIONAL_IDS)
    regional = q.loc[mask].copy()
    assert set(regional.source_excel_row) == set(REGIONAL_IDS) and len(regional) == 2
    assert regional.included.all() and regional.income.isna().all()
    assert regional.provider_key.eq("Japan").all()
    assert regional.analytical_year.eq(2014).all()
    assert regional.recipient_status.eq("source_verified_cross_border_region").all()
    assert np.isfinite(regional.amount).all() and regional.amount.gt(0).all()
    parts = [q.loc[~mask].copy()]
    for c, fraction in zip(core.CLASSES, f):
        if fraction:
            z = regional.copy()
            z["amount"] = z.amount * fraction
            z["income"] = c
            z["completion_fraction"] = fraction
            z["completion_income"] = c
            z["component_id"] = z.component_id + "__completion_" + c
            parts.append(z)
    completed = pd.concat(parts, ignore_index=True)
    assert np.isclose(completed.amount.sum(), q.amount.sum(), atol=DOLLAR_ATOL, rtol=1e-13)
    assert completed.loc[completed.source_excel_row.isin(REGIONAL_IDS), "recipient"].isna().all()
    return completed


def _evaluate(q: pd.DataFrame) -> dict[str, pd.DataFrame]:
    allocation, _, _ = core.allocate(q)
    allocation = allocation.rename(columns={
        "amount": "numerator_amount",
        "classified_denominator": "targeted_completion_denominator",
        "unknown_amount": "other_unknown_income_amount",
        "share_classified": "targeted_completion_share",
    }).drop(columns=["lower_observed_bound", "upper_observed_bound"])
    allocation["income_classification"] = "fixed_FY2013"
    allocation["denominator_definition"] = "known-income amount plus completed Standard Bank support; excludes other unknown income"
    decomposition, cells = core.decomposition(q)
    decomposition = decomposition.rename(columns={
        "classified_denominator_early": "targeted_completion_denominator_early",
        "classified_denominator_late": "targeted_completion_denominator_late",
    })
    providers, matrices = core.matrices(q)
    provider_period_rows = []
    period_index = {}
    for period, matrix in matrices.items():
        totals = matrix.sum(axis=1)
        denominator = float(totals.sum())
        period_index[period] = (totals, denominator)
        for p, provider in enumerate(providers):
            for k, income_class in enumerate(core.CLASSES):
                provider_period_rows.append({
                    "period": period, "income_class": income_class, "provider": provider,
                    "provider_income_amount": matrix[p, k], "provider_total": totals[p],
                    "targeted_completion_denominator": denominator,
                    "provider_weight": totals[p] / denominator if denominator > 0 else np.nan,
                    "within_provider_share": matrix[p, k] / totals[p] if totals[p] > 0 else np.nan,
                    "portfolio_class_contribution": matrix[p, k] / denominator if denominator > 0 else np.nan,
                    "positive_provider_support": bool(totals[p] > 0),
                })
    provider_periods = pd.DataFrame(provider_period_rows)
    # Include exact provider/class numerators and full denominators even for
    # undefined pairs; support is defined by positive dollars, never row counts.
    supplements = []
    for early, late in core.PAIRS:
        pa, va = period_index[early]
        pb, vb = period_index[late]
        for p, provider in enumerate(providers):
            support = "common" if pa[p] > 0 and pb[p] > 0 else "entry" if pb[p] > 0 else "exit" if pa[p] > 0 else "absent"
            for k, income_class in enumerate(core.CLASSES):
                supplements.append({
                    "pair": f"{early}_to_{late}", "income_class": income_class, "provider": provider,
                    "provider_income_amount_early": matrices[early][p, k],
                    "provider_income_amount_late": matrices[late][p, k],
                    "provider_amount_early": pa[p], "provider_amount_late": pb[p],
                    "weight_early": pa[p] / va if va > 0 else np.nan,
                    "weight_late": pb[p] / vb if vb > 0 else np.nan,
                    "within_share_early": matrices[early][p, k] / pa[p] if pa[p] > 0 else np.nan,
                    "within_share_late": matrices[late][p, k] / pb[p] if pb[p] > 0 else np.nan,
                    "targeted_completion_denominator_early": va,
                    "targeted_completion_denominator_late": vb,
                    "support": support,
                    "provider_delta_pp": 100 * (matrices[late][p, k] / vb - matrices[early][p, k] / va) if va > 0 and vb > 0 else np.nan,
                })
    supplements = pd.DataFrame(supplements)
    overlap = [c for c in supplements if c in cells and c not in ["pair", "income_class", "provider"]]
    cells = cells.drop(columns=overlap).merge(supplements, on=["pair", "income_class", "provider"], validate="one_to_one")
    return {"allocations": allocation, "decompositions": decomposition,
            "provider_decompositions": cells, "provider_periods": provider_periods}


def _scalar_vector(results: dict[str, pd.DataFrame], include_provider_periods: bool = False) -> pd.DataFrame:
    """Only affine dollar/share/accounting targets, never integer record counts."""
    pieces = []
    specifications = [
        ("allocations", "period", "allocation", ["numerator_amount", "targeted_completion_share", "share_observed"]),
        ("decompositions", "pair", "decomposition", core.TERMS),
        ("provider_decompositions", "pair", "provider_decomposition", ["provider_delta_pp"] + core.TERMS[1:]),
    ]
    if include_provider_periods:
        specifications.append(("provider_periods", "period", "provider_allocation", ["provider_income_amount", "within_provider_share", "portfolio_class_contribution"]))
    for table, target, kind, metrics in specifications:
        z = results[table].copy()
        if "provider" not in z:
            z["provider"] = "__portfolio__"
        # Other unknown income is retained in the allocation output, but is not
        # one of the four completed income categories or a feasible fifth vertex.
        z = z.loc[z.income_class.isin(core.CLASSES)]
        z = z.melt(id_vars=[target, "income_class", "provider"], value_vars=metrics, var_name="metric", value_name="value")
        z = z.rename(columns={target: "target"})
        z["target_type"] = kind
        z["unit"] = np.where(z.metric.str.endswith("_pp"), "percentage_points", np.where(z.metric.str.endswith("_amount"), "nominal_USD", "fraction"))
        pieces.append(z[KEYS + ["value"]])
    return pd.concat(pieces, ignore_index=True)


def _tolerance(unit: str, scale: float = 0.0) -> float:
    return DOLLAR_ATOL + 1e-12 * scale if unit == "nominal_USD" else PP_ATOL if unit == "percentage_points" else SHARE_ATOL


def _assert_close(actual: np.ndarray, expected: np.ndarray, unit: str) -> float:
    actual, expected = np.asarray(actual, float), np.asarray(expected, float)
    if not np.array_equal(np.isnan(actual), np.isnan(expected)):
        raise AssertionError("Undefined status changed during affine validation.")
    keep = np.isfinite(actual) & np.isfinite(expected)
    if np.any(np.isinf(actual)) or np.any(np.isinf(expected)):
        raise AssertionError("Infinite completion result.")
    error = float(np.max(np.abs(actual[keep] - expected[keep]))) if keep.any() else 0.0
    scale = float(np.max(np.abs(expected[keep]))) if keep.any() else 0.0
    assert error <= _tolerance(unit, scale), (unit, error, scale)
    return error


def _validate_evaluation(results: dict[str, pd.DataFrame]) -> list[dict]:
    checks = []
    a = results["allocations"]
    for period, z in a.groupby("period", sort=False):
        known = z[z.income_class.isin(core.CLASSES)]
        denominator = float(z.targeted_completion_denominator.iloc[0])
        observed = float(z.observed_denominator.iloc[0])
        errors = [
            _assert_close([z.numerator_amount.sum()], [observed], "nominal_USD"),
            _assert_close([known.numerator_amount.sum()], [denominator], "nominal_USD"),
        ]
        if denominator > 0:
            errors.append(_assert_close([known.targeted_completion_share.sum()], [1.0], "fraction"))
        checks.append({"test": "allocation_and_simplex_closure", "target": period, "max_absolute_error": max(errors), "status": "passed"})
    for pair, z in results["decompositions"].groupby("pair", sort=False):
        if z.status.eq("defined").all():
            errors = [
                _assert_close(z[core.TERMS[1:]].sum(axis=1), z.delta_pp, "percentage_points"),
                _assert_close([z.delta_pp.sum()], [0.0], "percentage_points"),
                _assert_close([z.within_pp.sum()], [0.0], "percentage_points"),
                _assert_close([z[["composition_pp", "entry_pp", "exit_pp"]].to_numpy().sum()], [0.0], "percentage_points"),
            ]
            checks.append({"test": "decomposition_and_four_class_closure", "target": pair, "max_absolute_error": max(errors), "status": "passed"})
        else:
            checks.append({"test": "decomposition_and_four_class_closure", "target": pair, "max_absolute_error": np.nan, "status": "undefined_pair_preserved"})
    cells = results["provider_decompositions"]
    expected = cells.provider_delta_pp.to_numpy()
    actual = cells[core.TERMS[1:]].sum(axis=1, min_count=4).to_numpy()
    error = _assert_close(actual, expected, "percentage_points")
    checks.append({"test": "provider_cell_closure", "target": "all_pairs_and_classes", "max_absolute_error": error, "status": "passed"})
    return checks


def _constant_vertex_checks(evaluations: Mapping[str, dict[str, pd.DataFrame]]) -> list[dict]:
    baseline = evaluations[core.CLASSES[0]]
    checks = []
    specs = [
        ("allocations", ["period", "income_class"], ["targeted_completion_denominator", "observed_denominator", "other_unknown_income_amount"], []),
        ("provider_periods", ["period", "income_class", "provider"], ["provider_total", "targeted_completion_denominator", "provider_weight"], ["positive_provider_support"]),
        ("provider_decompositions", ["pair", "income_class", "provider"], ["provider_amount_early", "provider_amount_late", "weight_early", "weight_late", "targeted_completion_denominator_early", "targeted_completion_denominator_late"], ["support"]),
    ]
    for table, keys, numeric, categorical in specs:
        b = baseline[table].set_index(keys).sort_index()
        errors = []
        for vertex, result in evaluations.items():
            z = result[table].set_index(keys).sort_index()
            assert z.index.equals(b.index)
            for c in categorical:
                assert z[c].equals(b[c]), (table, vertex, c)
            for c in numeric:
                unit = "fraction" if "weight" in c else "nominal_USD"
                errors.append(_assert_close(z[c], b[c], unit))
        checks.append({"test": "constant_denominators_and_support", "target": table, "max_absolute_error": max(errors, default=0.0), "status": "passed"})
    return checks


def _interior_checks(evaluations: Mapping[str, dict[str, pd.DataFrame]], interior: dict[str, pd.DataFrame]) -> pd.DataFrame:
    vertices = []
    for vertex, results in evaluations.items():
        v = _scalar_vector(results, include_provider_periods=True)
        v["vertex"] = vertex
        vertices.append(v)
    vertices = pd.concat(vertices, ignore_index=True)
    average = vertices.groupby(KEYS, sort=False, dropna=False).value.agg(lambda x: float(np.mean(x.to_numpy()))).rename("vertex_mean")
    observed = _scalar_vector(interior, include_provider_periods=True).set_index(KEYS).value.rename("interior_value")
    check = observed.to_frame().join(average, how="outer", validate="one_to_one").reset_index()
    assert len(check) == len(observed) == len(average)
    check["absolute_error"] = (check.interior_value - check.vertex_mean).abs()
    check["status"] = np.where(check.interior_value.isna(), "undefined_preserved", "passed")
    for unit, z in check.groupby("unit", sort=False):
        _assert_close(z.interior_value, z.vertex_mean, unit)
    return check


def _derivative_checks(evaluations: Mapping[str, dict[str, pd.DataFrame]], regional_amount: float) -> pd.DataFrame:
    """Verify symbolic derivatives and vertex differences on simplex directions.

    Increasing x_k is compensated in another class so that U and all weights
    stay fixed. Slopes are fractions per USD; residuals are scaled to a full-U
    percentage-point contrast to avoid a vacuous near-zero absolute tolerance.
    """
    representative = evaluations[core.CLASSES[0]]["provider_periods"]
    japan = representative.loc[representative.provider.eq("Japan")].drop_duplicates("period").set_index("period")
    rows = []
    for early, late in core.PAIRS:
        ea, la = japan.loc[early], japan.loc[late]
        pa, pb = float(ea.provider_total), float(la.provider_total)
        va, vb = float(ea.targeted_completion_denominator), float(la.targeted_completion_denominator)
        ie, il = int(2014 in core.PERIODS[early]), int(2014 in core.PERIODS[late])
        if va <= 0 or vb <= 0:
            rows.append({"pair": f"{early}_to_{late}", "status": "undefined_pair_preserved"})
            continue
        wa, wb = pa / va, pb / vb
        co, en, ex = pa > 0 and pb > 0, pa == 0 and pb > 0, pa > 0 and pb == 0
        composition = (wb - wa) * (ie / pa + il / pb) / 2 if co else 0.0
        within = (wa + wb) * (il / pb - ie / pa) / 2 if co else 0.0
        entry = il / vb if en else 0.0
        exit_term = -ie / va if ex else 0.0
        delta = il / vb - ie / va
        expected = dict(zip(core.TERMS, [delta, composition, within, entry, exit_term]))
        identity_error = abs((composition + within + entry + exit_term - delta) * regional_amount * 100)
        assert identity_error <= PP_ATOL
        for c in core.CLASSES:
            other = next(k for k in core.CLASSES if k != c)
            pair = f"{early}_to_{late}"
            own_rows = evaluations[c]["decompositions"]
            other_rows = evaluations[other]["decompositions"]
            own = own_rows.loc[own_rows.pair.eq(pair) & own_rows.income_class.eq(c)].iloc[0]
            alt = other_rows.loc[other_rows.pair.eq(pair) & other_rows.income_class.eq(c)].iloc[0]
            for term, slope in expected.items():
                observed = (float(own[term]) - float(alt[term])) / (100 * regional_amount)
                error = abs((observed - slope) * regional_amount * 100)
                assert error <= PP_ATOL, (pair, c, term, error)
                rows.append({"pair": pair, "income_class": c, "metric": term,
                             "compensating_class": other, "Japan_support": "common" if co else "entry" if en else "exit" if ex else "absent",
                             "affected_early": ie, "affected_late": il,
                             "provider_amount_early": pa, "provider_amount_late": pb,
                             "completed_denominator_early": va, "completed_denominator_late": vb,
                             "symbolic_derivative_fraction_per_USD": slope,
                             "vertex_derivative_fraction_per_USD": observed,
                             "full_U_contrast_error_pp": error,
                             "symbolic_identity_full_U_error_pp": identity_error,
                             "status": "passed"})
    return pd.DataFrame(rows)


def _envelopes(vectors: pd.DataFrame, grouping: list[str], union: bool) -> pd.DataFrame:
    keys = grouping + KEYS
    z = vectors[keys + [c for c in ["case_id", "vertex", "value"] if c not in keys]].copy()
    z["value"] = z.value.where(np.isfinite(z.value))
    z["attainer"] = z.case_id + "::" + z.vertex if union else z.vertex
    summary = z.groupby(keys, sort=False, dropna=False).agg(
        lower=("value", "min"), upper=("value", "max"),
        defined_vertex_count=("value", "count"), total_vertex_count=("value", "size"),
        source_case_count=("case_id", "nunique"))
    joined = z.join(summary[["lower", "upper"]], on=keys, validate="many_to_one")
    for bound in ["lower", "upper"]:
        matching = joined.loc[joined.value.eq(joined[bound])]
        attaining = matching.groupby(keys, sort=False, dropna=False).attainer.agg(
            lambda ids: json.dumps(sorted(set(ids)), separators=(",", ":")))
        summary[bound + "_attaining_case_vertices"] = attaining.reindex(summary.index).fillna("[]")
    summary["undefined_vertex_count"] = summary.total_vertex_count - summary.defined_vertex_count
    summary = summary.drop(columns="total_vertex_count").reset_index()
    summary["set_description"] = "union_of_case_specific_four_vertex_hulls" if union else "one_case_four_vertex_convex_hull"
    summary["extremum_attainment"] = "exact equality among computed vertices; no tolerance-based ties"
    return summary


def run(raw: pd.DataFrame | None = None, output_dir: str | Path | None = None) -> dict:
    """Compute all 12 core G1 and six agreement G1 cases after both gates clear."""
    gate = _execution_gate()
    raw = core.load() if raw is None else raw.copy(deep=True)
    raw = raw.loc[raw.technology_group.eq("Renewable")].copy()
    assert set(REGIONAL_IDS).issubset(set(raw.source_excel_row))
    output_dir = Path(output_dir) if output_dir is not None else core.ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    tables = {name: [] for name in ["allocations", "decompositions", "provider_decompositions", "provider_periods"]}
    manifest, validations, interiors, derivatives, scalar_vectors = [], [], [], [], []
    scenarios = [s for s in core.SCENARIOS if s["G"] == 1]
    cases = [(s, False) for s in scenarios] + [(s, True) for s in scenarios if s["O"] == 1]
    assert len(scenarios) == 12 and len(cases) == 18
    for scenario, overlay in cases:
        transformed = core.transform(raw, scenario, overlay=overlay, income_year=2013)
        case_id = scenario["scenario"] + ("_agreement" if overlay else "")
        family = "agreement_G1" if overlay else "core_G1"
        meta = {"case_id": case_id, "base_scenario": scenario["scenario"],
                "case_family": family, **{k: scenario[k] for k in "AOGD"}}
        regional = transformed.loc[transformed.source_excel_row.isin(REGIONAL_IDS)]
        regional_amount = float(regional.amount.sum())
        manifest.append(meta | {"regional_amount": regional_amount, "provider": "Japan", "analytical_year": 2014,
                                "income_classification": "fixed_FY2013", "vertices": json.dumps(core.CLASSES),
                                "joint_set": "convex hull of this case's four complete vertex vectors", "model": MODEL})
        for panel in PANELS:
            q = core.panel(transformed, panel)
            panel_meta = meta | {"panel": panel, "completion_model": MODEL}
            evaluations = {}
            for vertex in core.CLASSES:
                completed = complete_regional_income(q, {vertex: 1.0})
                result = _evaluate(completed)
                evaluations[vertex] = result
                vmeta = panel_meta | {"vertex": vertex, "vertex_id": case_id + "::" + vertex,
                                      "regional_completion_amount": regional_amount}
                for name, frame in result.items():
                    tables[name].append(frame.assign(**vmeta))
                scalar_vectors.append(_scalar_vector(result).assign(**vmeta))
                for check in _validate_evaluation(result):
                    validations.append(panel_meta | {"vertex": vertex} | check)
            for check in _constant_vertex_checks(evaluations):
                validations.append(panel_meta | {"vertex": "all_four"} | check)
            # Reconstruct U/4 independently from retained rows. It is a check,
            # never a fifth feasible-source scenario or envelope candidate.
            interior_q = complete_regional_income(q, {c: 0.25 for c in core.CLASSES})
            interior = _evaluate(interior_q)
            for check in _validate_evaluation(interior):
                validations.append(panel_meta | {"vertex": "equal_quarter_verification_only"} | check)
            interiors.append(_interior_checks(evaluations, interior).assign(**panel_meta))
            derivatives.append(_derivative_checks(evaluations, regional_amount).assign(**panel_meta))
            # Explicitly reconcile completed and uncompleted denominators and
            # retain the remaining unknown-income amount for every period.
            uncompleted, _, _ = core.allocate(q)
            completed_a = evaluations[core.CLASSES[0]]["allocations"]
            for period, years in core.PERIODS.items():
                old = uncompleted.loc[uncompleted.period.eq(period)].iloc[0]
                new = completed_a.loc[completed_a.period.eq(period)].iloc[0]
                addition = regional_amount if 2014 in years else 0.0
                errors = [
                    _assert_close([new.targeted_completion_denominator], [old.classified_denominator + addition], "nominal_USD"),
                    _assert_close([new.observed_denominator], [old.observed_denominator], "nominal_USD"),
                    _assert_close([new.other_unknown_income_amount], [old.unknown_amount - addition], "nominal_USD"),
                ]
                validations.append(panel_meta | {"vertex": "all_four", "test": "completed_versus_uncompleted_denominator",
                    "target": period, "uncompleted_classified_denominator": old.classified_denominator,
                    "targeted_completion_denominator": new.targeted_completion_denominator,
                    "regional_amount_in_period": addition, "other_unknown_income_amount": new.other_unknown_income_amount,
                    "observed_denominator": new.observed_denominator, "max_absolute_error": max(errors), "status": "passed"})
    frames = {name: pd.concat(parts, ignore_index=True) for name, parts in tables.items()}
    # Persist complete vectors first so independent review can begin while the
    # scalar summaries are prepared. The final summary is written only on success.
    for name, frame in frames.items():
        frame.to_csv(output_dir / ("completion_vertex_" + name + ".csv"), index=False)
    print("Completion: all 18 cases' four vertex vectors and support tables saved; preparing scalar envelopes.", flush=True)
    vectors = pd.concat(scalar_vectors, ignore_index=True)
    case_envelopes = _envelopes(vectors, ["case_family", "case_id", "panel"], union=False)
    union_envelopes = []
    for label, family in [("core_G1_12_case_union", "core_G1"), ("agreement_G1_6_case_union", "agreement_G1"), ("combined_G1_18_case_union", None)]:
        selected = vectors if family is None else vectors.loc[vectors.case_family.eq(family)]
        union_envelopes.append(_envelopes(selected, ["panel"], union=True).assign(union_set=label))
    outputs = {"completion_vertex_" + name: frame for name, frame in frames.items()}
    outputs.update({"completion_case_manifest": pd.DataFrame(manifest),
                    "completion_case_scalar_envelopes": case_envelopes,
                    "completion_union_scalar_envelopes": pd.concat(union_envelopes, ignore_index=True),
                    "completion_validation": pd.DataFrame(validations),
                    "completion_interior_verification": pd.concat(interiors, ignore_index=True),
                    "completion_derivative_verification": pd.concat(derivatives, ignore_index=True)})
    outputs["completion_denominator_reconciliation"] = outputs["completion_validation"].loc[
        outputs["completion_validation"].test.eq("completed_versus_uncompleted_denominator")
    ].copy()
    union_table = outputs["completion_union_scalar_envelopes"]
    outputs["completion_union_endpoint_reporting"] = union_table.loc[
        union_table.panel.eq("international_reporting")
        & union_table.target_type.eq("decomposition")
        & union_table.target.eq("early_to_late")
    ].copy()
    for name, frame in outputs.items():
        frame.to_csv(output_dir / (name + ".csv"), index=False)
    summary = gate | {"status": "passed", "core_G1_cases": 12, "agreement_G1_cases": 6,
                       "arithmetic_block_scope": "Q0 only; the arithmetic-screen amendment does not authorize Q1 completion vertices",
                       "vertices_per_case": 4, "panels": list(PANELS), "income_classification": "fixed_FY2013",
                       "interior_point": "U/4 in each class; verification only",
                       "output_rows": {name: len(frame) for name, frame in outputs.items()},
                       "interpretation": MODEL,
                       "joint_set_warning": "Marginal scalar extremes generally cannot be jointly attained. Each case is a separate four-vertex hull; summaries across source cases are unions, not convex mixtures.",
                       "scope_limits": "Conditional on observed amounts, fixed provider/FY, retained source case, and unrestricted four-class completion of Standard Bank only. Excludes missing amounts, other unresolved income, unknown geography, unreviewed amount errors, finance principal, and worldwide exposure.",
                       "count_warning": "Record/component counts are saved at vertices, but are not affine outcomes and receive no scalar completion bounds."}
    (output_dir / "completion_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
