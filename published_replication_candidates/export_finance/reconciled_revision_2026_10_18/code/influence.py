"""Complete deterministic influence diagnostics for frozen protocol section 9.

Importing this module performs no archive calculations. ``run`` deliberately
requires an explicit arithmetic-screen clearance from the execution owner.
All dollar changes are implemented by subtracting small NumPy accounting
arrays; pandas decompositions are not repeated for each deleted entity.
"""
from __future__ import annotations

import csv
import gzip
import json
from contextlib import ExitStack
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from core import CLASSES, PANELS, ROOT, SCENARIOS, TERMS, decompose_arrays, load, panel, transform


INFLUENCE_PANELS = (
    "international_reporting", "country_assigned_international", "all_locations"
)
YEARS = np.arange(2013, 2023)
EARLY = np.array([0, 1, 2])
LATE = np.array([7, 8, 9])
PACKAGES = {
    "Standard Bank 1907/1908": (1907, 1908),
    "Karuma 109/2253": (109, 2253),
    "Dogger 7410/8034/8413": (7410, 8034, 8413),
}
METRICS = TERMS + ["annual_share_classified_pp", "annual_share_observed_pp"]
ID_FIELDS = ["scenario", "panel", "unit_type", "unit_id"]
SUPPORT_FIELDS = [
    "common_provider_count", "entry_provider_count", "exit_provider_count",
    "common_volume_share_early", "common_volume_share_late",
    "classified_denominator_early", "classified_denominator_late",
]


def _ratio(numerator, denominator):
    """Return undefined, rather than zero, when an observed total is zero."""
    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)
    return np.divide(
        numerator, denominator, out=np.full(numerator.shape, np.nan),
        where=denominator > 0,
    )


def _endpoint(cube):
    a, b = cube[EARLY].sum(axis=0), cube[LATE].sum(axis=0)
    terms, delta, aux = decompose_arrays(a, b)
    if aux is None:
        values = np.full((4, 5), np.nan)
        support = {name: np.nan for name in SUPPORT_FIELDS}
        support.update(classified_denominator_early=float(a.sum()),
                       classified_denominator_late=float(b.sum()))
    else:
        values = np.column_stack([delta, terms.sum(axis=0)])
        support = aux[0]
        assert np.max(np.abs(values[:, 0] - values[:, 1:].sum(axis=1))) < 1e-8
    return values, support


def _annual(cube, observed):
    amount = cube.sum(axis=1)
    classified = amount.sum(axis=1)
    return {
        "amount": amount,
        "classified": classified,
        "observed": observed,
        "share_classified": 100 * _ratio(amount, classified[:, None]),
        "share_observed": 100 * _ratio(amount, observed[:, None]),
    }


class _PanelArrays:
    """A panel's fixed provider-year-class arrays and row deletion indexes."""

    def __init__(self, q):
        self.q = q.reset_index(drop=True)
        self.providers = sorted(self.q.provider_key.unique().tolist())
        self.source_rows = self.q.source_excel_row.to_numpy(dtype=int)
        self.year = self.q.analytical_year.to_numpy(dtype=int) - 2013
        if not np.all((self.year >= 0) & (self.year < 10)):
            raise ValueError("Influence inputs must retain the frozen 2013–2022 axis")
        self.provider = pd.Categorical(self.q.provider_key, self.providers).codes
        self.income = pd.Categorical(self.q.income, CLASSES).codes
        original = self.q.amount.to_numpy(dtype=float)
        if np.isinf(original).any() or (original[np.isfinite(original)] < 0).any():
            raise ValueError("Nonfinite or negative amounts require protocol review")
        # NaN contributes no observed dollars; its missingness remains in ledgers.
        self.amount = np.where(np.isnan(original), 0.0, original)
        self.known = self.income >= 0
        self.cube = np.zeros((10, len(self.providers), 4), dtype=float)
        self.positive_count = np.zeros(self.cube.shape, dtype=np.int64)
        idx = (self.year[self.known], self.provider[self.known], self.income[self.known])
        np.add.at(self.cube, idx, self.amount[self.known])
        np.add.at(self.positive_count, idx, (self.amount[self.known] > 0).astype(int))
        self.observed = np.bincount(self.year, weights=self.amount, minlength=10)
        self.observed_positive_count = np.bincount(
            self.year, weights=(self.amount > 0).astype(int), minlength=10
        ).astype(int)
        self.endpoint, self.support = _endpoint(self.cube)
        self.annual = _annual(self.cube, self.observed)
        self.by_source = {int(r): np.flatnonzero(self.source_rows == r)
                          for r in self.source_rows}

    def positions(self, source_ids):
        pieces = [self.by_source[int(r)] for r in source_ids if int(r) in self.by_source]
        return np.concatenate(pieces) if pieces else np.array([], dtype=int)

    def delete(self, positions):
        removed = np.zeros_like(self.cube)
        removed_count = np.zeros_like(self.positive_count)
        known_positions = positions[self.known[positions]]
        idx = (self.year[known_positions], self.provider[known_positions],
               self.income[known_positions])
        np.add.at(removed, idx, self.amount[known_positions])
        np.add.at(removed_count, idx, (self.amount[known_positions] > 0).astype(int))
        after = self.cube - removed
        counts_after = self.positive_count - removed_count
        assert (counts_after >= 0).all()
        # When every positive row in a cell is deleted, prevent cancellation
        # residue from inventing a tiny positive provider and changing support.
        after[counts_after == 0] = 0.0
        tolerance = 32 * np.finfo(float).eps * np.maximum(1, self.cube)
        if (after < -tolerance).any():
            raise AssertionError("Deletion produced negative classified dollars")
        after = np.maximum(after, 0)
        removed_observed = np.bincount(
            self.year[positions], weights=self.amount[positions], minlength=10
        )
        observed = self.observed - removed_observed
        remaining_count = self.observed_positive_count - np.bincount(
            self.year[positions], weights=(self.amount[positions] > 0).astype(int),
            minlength=10,
        ).astype(int)
        observed[remaining_count == 0] = 0.0
        if (observed < -32 * np.finfo(float).eps * np.maximum(1, self.observed)).any():
            raise AssertionError("Deletion produced negative observed dollars")
        observed = np.maximum(observed, 0)
        if np.any(removed[np.concatenate([EARLY, LATE])]):
            endpoint, support = _endpoint(after)
        else:
            endpoint, support = self.endpoint.copy(), self.support.copy()
        annual = _annual(after, observed)
        influence = endpoint - self.endpoint
        annual_influence = {
            "classified": annual["share_classified"] - self.annual["share_classified"],
            "observed": annual["share_observed"] - self.annual["share_observed"],
        }
        unaffected_years = np.ones(10, dtype=bool)
        unaffected_years[self.year[positions]] = False
        for values in annual_influence.values():
            assert np.all((values[unaffected_years] == 0) | np.isnan(values[unaffected_years]))
        if not np.any(removed[np.concatenate([EARLY, LATE])]):
            assert np.all((influence == 0) | np.isnan(influence))
        if not self.amount[positions].any():
            assert np.all((influence == 0) | np.isnan(influence))
            for values in annual_influence.values():
                assert np.all((values == 0) | np.isnan(values))
        return endpoint, support, annual, influence, annual_influence


def _json(values):
    return json.dumps(list(values), separators=(",", ":"), ensure_ascii=False)


def _writer(stack, path, fields):
    opener = gzip.open if str(path).endswith(".gz") else open
    handle = stack.enter_context(opener(path, "wt", encoding="utf-8", newline=""))
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
    writer.writeheader()
    return writer


def _csv_row(writer, values):
    # CSV has explicit empty cells for undefined numeric outcomes, never zero.
    clean = {key: ("" if isinstance(value, (float, np.floating)) and not np.isfinite(value)
                   else value) for key, value in values.items()}
    writer.writerow(clean)


def _entities(d):
    records = [("record", str(int(row)), (int(row),))
               for row in sorted(d.source_excel_row)]
    providers = [("provider", str(provider), tuple(sorted(g.source_excel_row.astype(int))))
                 for provider, g in d.groupby("provider_key", sort=True)]
    packages = [("package", name, ids) for name, ids in PACKAGES.items()]
    return records + providers + packages


def _score(values):
    finite = np.isfinite(values)
    return {
        "max_absolute_influence_pp": float(np.abs(values[finite]).max()) if finite.any() else np.nan,
        "summed_absolute_influence_pp": float(np.abs(values[finite]).sum()) if finite.any() else np.nan,
        "defined_vector_cell_count": int(finite.sum()),
        "undefined_vector_cell_count": int((~finite).sum()),
    }


def _rank_and_concentrate(rows):
    """Rank Linf; report both L1-mass and Linf-score concentration explicitly."""
    rankings, concentration = [], []
    groups = {}
    for row in rows:
        key = tuple(row[name] for name in ("scenario", "panel", "unit_type", "metric"))
        groups.setdefault(key, []).append(row)
    for key, group in groups.items():
        kind = key[2]
        identity = dict(zip(("scenario", "panel", "unit_type", "metric"), key))
        eligible = [r for r in group if r["deletion_status"] == "deleted"
                    and np.isfinite(r["max_absolute_influence_pp"])]
        tie_key = lambda r: int(r["unit_id"]) if kind == "record" else r["unit_id"]
        eligible.sort(key=lambda r: (-r["max_absolute_influence_pp"], tie_key(r)))
        scores = [r["max_absolute_influence_pp"] for r in eligible]
        score_counts = {}
        for score in scores:
            score_counts[score] = score_counts.get(score, 0) + 1
        first_rank = {}
        for rank, row in enumerate(eligible, 1):
            score = row["max_absolute_influence_pp"]
            first_rank.setdefault(score, rank)
            row.update(rank=rank, weak_order_rank=first_rank[score],
                       equal_score_count=score_counts[score], ranking_status="ranked")
        for row in group:
            if "rank" not in row:
                row.update(rank="", weak_order_rank="", equal_score_count="",
                           ranking_status="not_in_panel" if row["deletion_status"] != "deleted"
                           else "all_vector_cells_undefined")
        # Keep output in the precise deterministic order actually used to rank.
        rankings.extend(eligible)
        rankings.extend(sorted([r for r in group if not r["rank"]], key=tie_key))
        l1_total = float(sum(r["summed_absolute_influence_pp"] for r in eligible))
        score_total = float(sum(scores))
        result = identity | {
            "ranked_unit_count": len(eligible),
            "already_absent_or_outside_panel_count": sum(r["deletion_status"] != "deleted" for r in group),
            "all_undefined_unit_count": sum(r["deletion_status"] == "deleted" and
                                             not np.isfinite(r["max_absolute_influence_pp"]) for r in group),
            "partially_undefined_ranked_unit_count": sum(r["undefined_vector_cell_count"] > 0 for r in eligible),
            "total_summed_absolute_influence_pp": l1_total,
            "total_max_absolute_ranking_score_pp": score_total,
        }
        for n in (1, 5):
            top = eligible[:n]
            mass = float(sum(r["summed_absolute_influence_pp"] for r in top))
            score_mass = float(sum(r["max_absolute_influence_pp"] for r in top))
            result.update({
                f"top_{n}_unit_ids": _json(r["unit_id"] for r in top),
                f"top_{n}_actual_unit_count": len(top),
                f"top_{n}_summed_absolute_influence_pp": mass,
                f"top_{n}_share_summed_absolute_influence": mass / l1_total if l1_total else np.nan,
                f"top_{n}_max_absolute_ranking_score_pp": score_mass,
                f"top_{n}_share_max_absolute_ranking_score": score_mass / score_total if score_total else np.nan,
            })
        concentration.append(result)
    return rankings, concentration


def _recorded_value_tables(q, scenario, panel_name):
    rows, summaries = [], []
    for period, years in (("early", (2013, 2014, 2015)), ("late", (2020, 2021, 2022))):
        z = q[q.analytical_year.isin(years)]
        for measure, column in (("original_recorded_nominal_usd", "nominal_usd"),
                                ("scenario_analytical_nominal_usd", "amount")):
            # Financial concentration uses all observed panel dollars, including
            # unclassified-income amounts, and never influence magnitudes.
            finite = z[np.isfinite(z[column])].copy()
            finite = finite.sort_values([column, "source_excel_row"], ascending=[False, True])
            total = float(finite[column].sum())
            base = dict(scenario=scenario, panel=panel_name, period=period,
                        value_measure=measure, observed_total_usd=total)
            for rank, (_, r) in enumerate(finite.iterrows(), 1):
                rows.append(base | dict(rank=rank, source_excel_row=int(r.source_excel_row),
                                        value_usd=float(r[column]), value_share=float(r[column]) / total if total else np.nan))
            summary = base | dict(included_source_row_count=len(z),
                                  observed_amount_row_count=len(finite),
                                  missing_amount_row_count=int(z[column].isna().sum()))
            for n in (1, 5):
                top = finite.head(n)
                amount = float(top[column].sum())
                summary.update({f"top_{n}_source_excel_rows": _json(top.source_excel_row.astype(int)),
                                f"top_{n}_actual_row_count": len(top),
                                f"top_{n}_value_usd": amount,
                                f"top_{n}_recorded_value_share": amount / total if total else np.nan})
            summaries.append(summary)
    return rows, summaries


def run(output_dir=None, raw=None, *, arithmetic_screen_cleared=False,
        progress: Callable[[str, str], None] | None = None):
    """Export every section-9 influence, plus auditable ranks and denominators.

    The owner must verify the complete arithmetic screen and any required dated
    amendment before setting ``arithmetic_screen_cleared=True``. This argument is
    an execution gate, not a claim that the code can grant scientific approval.
    Only the 24 core scenarios and the three frozen influence panels are run.
    """
    if not arithmetic_screen_cleared:
        raise RuntimeError("STOP: complete arithmetic-screen clearance is required before archive outcomes")
    # The explicit argument is not a substitute for the shared documentary gate.
    # Import lazily so syntax checks and synthetic arithmetic tests remain inert.
    from run_revision import gate
    approval = gate()
    output_dir = Path(output_dir) if output_dir is not None else ROOT / "outputs" / "influence"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = load() if raw is None else raw.copy(deep=True)
    raw_renewable = raw[raw.technology_group.eq("Renewable")].copy()
    assert raw_renewable.source_excel_row.is_unique
    source_ids = set(raw_renewable.source_excel_row.astype(int))
    assert set(INFLUENCE_PANELS).issubset(PANELS)
    assert len(SCENARIOS) == 24 and len({s["scenario"] for s in SCENARIOS}) == 24
    missing_members = {k: sorted(set(v) - source_ids) for k, v in PACKAGES.items()
                       if set(v) - source_ids}
    if missing_members:
        raise ValueError(f"Frozen package members missing from locked Renewable input: {missing_members}")

    endpoint_fields = ID_FIELDS + ["deletion_status", "income_class", "outcome_status"]
    endpoint_fields += [f"{phase}_{term}" for phase in ("baseline", "deleted", "influence") for term in TERMS]
    endpoint_fields += [f"{phase}_{field}" for phase in ("baseline", "deleted") for field in SUPPORT_FIELDS]
    annual_fields = ID_FIELDS + ["deletion_status", "year", "income_class"]
    annual_fields += [f"{phase}_{field}" for phase in ("baseline", "deleted") for field in
                      ("class_amount_usd", "classified_denominator_usd", "observed_denominator_usd", "share_classified_pp", "share_observed_pp")]
    annual_fields += ["influence_share_classified_pp", "influence_share_observed_pp",
                      "classified_influence_status", "observed_influence_status"]
    entity_fields = ID_FIELDS + [
        "deletion_status", "fixed_source_excel_rows", "fixed_source_row_count",
        "scenario_included_source_row_count", "panel_included_source_row_count",
        "removed_component_count", "removed_observed_amount_usd", "removed_classified_amount_usd",
        "removed_missing_amount_count", "removed_zero_amount_count", "removed_endpoint_component_count",
        "record_provider", "original_year", "analytical_year", "original_recorded_amount_usd",
        "analytical_amount_usd", "scenario_included", "panel_included", "record_income_class",
        "recipient_status", "scenario_exclusion_reason",
    ]
    ranking_fields = ID_FIELDS + ["deletion_status", "metric", "max_absolute_influence_pp",
                                  "summed_absolute_influence_pp", "defined_vector_cell_count",
                                  "undefined_vector_cell_count", "rank", "weak_order_rank",
                                  "equal_score_count", "ranking_status"]
    rank_rows, value_summaries = [], []
    counts = {"scenario_panel_pairs": 0, "entities": 0, "endpoint_rows": 0, "annual_rows": 0}
    files = {}
    with ExitStack() as stack:
        endpoint_writers, annual_writers = {}, {}
        for kind in ("record", "provider", "package"):
            for suffix, fields, writers in (("endpoint", endpoint_fields, endpoint_writers),
                                            ("annual", annual_fields, annual_writers)):
                filename = f"{kind}_influence_{suffix}.csv.gz"
                files[f"{kind}_{suffix}"] = str(output_dir / filename)
                writers[kind] = _writer(stack, output_dir / filename, fields)
        files["ledger"] = str(output_dir / "influence_entity_ledger.csv.gz")
        ledger_writer = _writer(stack, files["ledger"], entity_fields)
        value_fields = ["scenario", "panel", "period", "value_measure", "observed_total_usd",
                        "rank", "source_excel_row", "value_usd", "value_share"]
        files["recorded_value_rankings"] = str(output_dir / "endpoint_recorded_value_rankings.csv.gz")
        value_writer = _writer(stack, files["recorded_value_rankings"], value_fields)

        for scenario in SCENARIOS:
            d = transform(raw_renewable, scenario)
            assert len(d) == len(raw_renewable) and d.source_excel_row.is_unique
            all_by_id = d.set_index("source_excel_row", drop=False)
            entities = _entities(d)
            for panel_name in INFLUENCE_PANELS:
                q = panel(d, panel_name)
                arrays = _PanelArrays(q)
                common = dict(scenario=scenario["scenario"], panel=panel_name)
                value_rows, summaries = _recorded_value_tables(q, scenario["scenario"], panel_name)
                for row in value_rows:
                    _csv_row(value_writer, row)
                value_summaries.extend(summaries)
                for kind, unit_id, fixed_ids in entities:
                    source = all_by_id.loc[list(fixed_ids)]
                    positions = arrays.positions(fixed_ids)
                    deleted_rows = arrays.q.iloc[positions]
                    included_count = int(source.included.sum())
                    status = ("deleted" if len(positions) else "already absent" if not included_count
                              else "outside geography panel")
                    ident = common | dict(unit_type=kind, unit_id=unit_id)
                    metadata = ident | dict(deletion_status=status)
                    ep, support, annual, diff, annual_diff = arrays.delete(positions)
                    known_deleted = deleted_rows.income.isin(CLASSES)
                    ledger = metadata | dict(
                        fixed_source_excel_rows=_json(fixed_ids), fixed_source_row_count=len(fixed_ids),
                        scenario_included_source_row_count=included_count,
                        panel_included_source_row_count=deleted_rows.source_excel_row.nunique(),
                        removed_component_count=len(deleted_rows),
                        removed_observed_amount_usd=float(deleted_rows.amount.sum()),
                        removed_classified_amount_usd=float(deleted_rows.loc[known_deleted, "amount"].sum()),
                        removed_missing_amount_count=int(deleted_rows.amount.isna().sum()),
                        removed_zero_amount_count=int(deleted_rows.amount.eq(0).sum()),
                        removed_endpoint_component_count=int(deleted_rows.analytical_year.isin((2013, 2014, 2015, 2020, 2021, 2022)).sum()),
                    )
                    if kind == "record":
                        r = source.iloc[0]
                        ledger.update(record_provider=r.provider_key, original_year=int(r.FY),
                                      analytical_year=int(r.analytical_year),
                                      original_recorded_amount_usd=r.nominal_usd, analytical_amount_usd=r.amount,
                                      scenario_included=bool(r.included), panel_included=bool(len(positions)),
                                      record_income_class=r.income if r.income in CLASSES else "Unknown",
                                      recipient_status=r.recipient_status,
                                      scenario_exclusion_reason=r.reason if not r.included else "")
                    _csv_row(ledger_writer, ledger)
                    counts["entities"] += 1
                    for k, income_class in enumerate(CLASSES):
                        row = metadata | dict(income_class=income_class,
                                              outcome_status="defined" if np.isfinite(diff[k]).all() else "undefined")
                        for phase, values in (("baseline", arrays.endpoint), ("deleted", ep), ("influence", diff)):
                            row.update({f"{phase}_{term}": float(values[k, j]) for j, term in enumerate(TERMS)})
                        for phase, values in (("baseline", arrays.support), ("deleted", support)):
                            row.update({f"{phase}_{field}": values[field] for field in SUPPORT_FIELDS})
                        _csv_row(endpoint_writers[kind], row)
                        counts["endpoint_rows"] += 1
                        for yi, year in enumerate(YEARS):
                            row = metadata | dict(year=int(year), income_class=income_class)
                            for phase, values in (("baseline", arrays.annual), ("deleted", annual)):
                                row.update({
                                    f"{phase}_class_amount_usd": float(values["amount"][yi, k]),
                                    f"{phase}_classified_denominator_usd": float(values["classified"][yi]),
                                    f"{phase}_observed_denominator_usd": float(values["observed"][yi]),
                                    f"{phase}_share_classified_pp": float(values["share_classified"][yi, k]),
                                    f"{phase}_share_observed_pp": float(values["share_observed"][yi, k]),
                                })
                            for scope in ("classified", "observed"):
                                value = float(annual_diff[scope][yi, k])
                                row[f"influence_share_{scope}_pp"] = value
                                row[f"{scope}_influence_status"] = "defined" if np.isfinite(value) else "undefined"
                            _csv_row(annual_writers[kind], row)
                            counts["annual_rows"] += 1
                    for j, metric in enumerate(TERMS):
                        rank_rows.append(metadata | dict(metric=metric) | _score(diff[:, j]))
                    for scope in ("classified", "observed"):
                        rank_rows.append(metadata | dict(metric=f"annual_share_{scope}_pp") | _score(annual_diff[scope]))
                counts["scenario_panel_pairs"] += 1
                if progress is not None:
                    progress(scenario["scenario"], panel_name)

        rankings, concentration = _rank_and_concentrate(rank_rows)
        files["rankings"] = str(output_dir / "influence_rankings.csv.gz")
        writer = _writer(stack, files["rankings"], ranking_fields)
        for row in rankings:
            _csv_row(writer, row)
        files["concentration"] = str(output_dir / "influence_concentration.csv")
        writer = _writer(stack, files["concentration"], list(concentration[0]))
        for row in concentration:
            _csv_row(writer, row)
        files["recorded_value_summary"] = str(output_dir / "endpoint_recorded_value_concentration.csv")
        writer = _writer(stack, files["recorded_value_summary"], list(value_summaries[0]))
        for row in value_summaries:
            _csv_row(writer, row)

    expected_entities = len(_entities(transform(raw_renewable, SCENARIOS[0]))) * 24 * 3
    assert counts["scenario_panel_pairs"] == 72
    assert counts["entities"] == expected_entities
    assert counts["endpoint_rows"] == 4 * expected_entities
    assert counts["annual_rows"] == 40 * expected_entities
    metadata = {
        "protocol_section": 9,
        "approved_protocol_sha256": approval.get("sha256"),
        "classification": "fixed FY2013",
        "scenarios": [s["scenario"] for s in SCENARIOS],
        "panels": list(INFLUENCE_PANELS),
        "years": YEARS.tolist(),
        "packages": PACKAGES,
        "counts": counts,
        "files": files,
        "influence_definition": "Outcome after deleting the named unit minus baseline outcome, in percentage points.",
        "population": "All original Renewable rows in the immutable retained-sample clean mapped input. No agreement-year overlays.",
        "excluded_rows": "Scenario-excluded source rows stay in every ledger with status 'already absent'; panel-excluded rows have status 'outside geography panel'. Their dollar influence is zero wherever baseline outcomes are defined.",
        "annual_estimands": "All ten classified-income and all-observed-dollar four-class annual share vectors are saved separately. Endpoint decomposition is classified-income accounting.",
        "ranking": "Each endpoint term ranks maximum absolute influence over four income classes. Annual metrics separately rank maximum absolute influence over four classes and all ten years. Exact score ties use source row ID numerically ascending, or provider/package label ascending. Weak-order tie ranks are also supplied.",
        "undefined": "Empty numeric CSV cells are undefined, never imputed zero. Annual ranks use defined vector cells, disclose their undefined cell counts, and exclude fully undefined deletions.",
        "concentration": "For top units selected by max-absolute rank, share_summed_absolute_influence divides their L1 influence-vector mass by total eligible L1 mass. share_max_absolute_ranking_score separately divides their ranking scores by all ranking scores. Both are undefined when their denominator is zero.",
        "recorded_value_concentration": "Separate financial-value measures use all observed endpoint-panel dollars among included records. Both original recorded nominal USD and scenario analytical nominal USD are shown; ties use source row ID. These are not influence concentration or exposure shares.",
        "interpretation": "Provider deletion changes reporting population. Fixed known-package deletion is secondary. Rows are archive records, not independent observations or certified projects. No preferred-result trimming, standard errors, or p-values.",
        "numerical_support": "Positive-row counts set emptied provider-year-class cells exactly to zero after subtraction, preventing floating-point residue from creating provider support.",
    }
    metadata_path = output_dir / "INFLUENCE_METADATA.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    files["metadata"] = str(metadata_path)
    return {"files": files, "counts": counts}


def synthetic_self_test():
    """Exercise deletion/support/undefined/ranking logic without archive data."""
    rows = [
        (1, "Japan", 2013, "L", 10.0),
        (2, "Japan", 2020, "H", 20.0),
        (3, "China", 2013, "LM", 30.0),
        (4, "China", 2020, "UM", 40.0),
        (5, "Japan", 2017, "H", 50.0),
        (6, "Japan", 2017, "H", np.nan),
        (7, "China", 2017, "L", 0.0),
        (8, "Japan", 2013, np.nan, 7.0),
    ]
    q = pd.DataFrame(rows, columns=["source_excel_row", "provider_key", "analytical_year", "income", "amount"])
    arrays = _PanelArrays(q)
    for ids in ((1,), (2,), (1, 2), (3, 4), (5,), (6,), (7,), (8,), tuple(range(1, 9)), ()):
        ep, support, annual, diff, annual_diff = arrays.delete(arrays.positions(ids))
        kept = q[~q.source_excel_row.isin(ids)]
        direct = _PanelArrays(kept)
        np.testing.assert_allclose(ep, direct.endpoint, rtol=1e-12, atol=1e-10, equal_nan=True)
        for name in ("share_classified", "share_observed", "amount", "classified", "observed"):
            np.testing.assert_allclose(annual[name], direct.annual[name], rtol=1e-12, atol=1e-10, equal_nan=True)
        if ids in ((5,), (6,), (7,), (8,), ()):
            np.testing.assert_array_equal(diff, np.zeros((4, 5)))
    assert np.isnan(arrays.delete(arrays.positions((1, 3)))[0]).all()
    synthetic_scores = []
    for rowid, values in ((11, np.array([1., -1., 0., 0.])),
                          (2, np.array([1., 0., 0., 0.])),
                          (9, np.zeros(4))):
        synthetic_scores.append(dict(scenario="synthetic", panel="synthetic", unit_type="record",
                                     unit_id=str(rowid), deletion_status="deleted", metric="delta_pp") | _score(values))
    ranked, concentration = _rank_and_concentrate(synthetic_scores)
    assert [r["unit_id"] for r in ranked] == ["2", "11", "9"]
    assert ranked[0]["weak_order_rank"] == ranked[1]["weak_order_rank"] == 1
    assert concentration[0]["top_1_share_summed_absolute_influence"] == 1 / 3
    assert concentration[0]["top_1_share_max_absolute_ranking_score"] == 1 / 2
    try:
        run()
    except RuntimeError as error:
        assert "STOP" in str(error)
    else:
        raise AssertionError("Archive execution gate failed")
    return "Synthetic influence tests passed; no archive outcomes calculated."


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Use synthetic data only")
    parser.add_argument("--arithmetic-screen-cleared", action="store_true",
                        help="Execution owner has cleared the complete arithmetic screen and any required amendment")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(synthetic_self_test())
    else:
        print(json.dumps(run(args.output_dir, arithmetic_screen_cleared=args.arithmetic_screen_cleared), indent=2))
