"""
Solar Permit Rule Engine
Checks extracted fields against NEC 690/705 and common solar code requirements.
Each rule returns a dict with: rule, status (pass/fail/warning/missing_data), message, reference
"""

def run_all_checks(extracted: dict) -> list:
    fields = extracted.get("fields", {})
    raw_text = extracted.get("raw_text", "")
    results = []

    results.append(check_system_size_consistency(fields))
    results.append(check_wire_gauge(fields))
    results.append(check_rapid_shutdown(fields))
    results.append(check_dc_disconnect(fields))
    results.append(check_pv_warning_label(fields))
    results.append(check_breaker_sizing(fields))
    results.append(check_voltage_limit(fields))
    results.append(check_nec_version_stated(fields))

    return results


def check_system_size_consistency(fields: dict) -> dict:
    """Check if module count × wattage ≈ stated system size."""
    rule = "System Size Consistency"
    ref = "General plan consistency check"

    count = fields.get("module_count")
    wattage = fields.get("module_wattage")
    stated_kw = fields.get("system_size_kw")

    if count and wattage and stated_kw:
        calculated_kw = (count * wattage) / 1000
        diff_pct = abs(calculated_kw - stated_kw) / stated_kw * 100
        if diff_pct <= 10:
            return {"rule": rule, "status": "pass",
                    "message": f"Calculated {calculated_kw:.2f} kW matches stated {stated_kw} kW (within 10%).",
                    "reference": ref}
        else:
            return {"rule": rule, "status": "fail",
                    "message": f"Mismatch: {count} modules × {wattage}W = {calculated_kw:.2f} kW, but plan states {stated_kw} kW.",
                    "reference": ref}
    return {"rule": rule, "status": "missing_data",
            "message": "Could not find module count, wattage, or system size to verify.",
            "reference": ref}


def check_wire_gauge(fields: dict) -> dict:
    """Basic check: warn if wire gauge seems too small for solar strings (rule of thumb: ≤10 AWG for strings)."""
    rule = "Conductor Sizing (NEC 690.8)"
    ref = "NEC Article 690.8"

    gauge = fields.get("wire_gauge_awg")
    if gauge is None:
        return {"rule": rule, "status": "missing_data",
                "message": "Wire gauge (AWG) not found in plan.",
                "reference": ref}
    if gauge <= 10:
        return {"rule": rule, "status": "pass",
                "message": f"{gauge} AWG conductor found — acceptable for PV string wiring.",
                "reference": ref}
    else:
        return {"rule": rule, "status": "warning",
                "message": f"{gauge} AWG may be undersized for PV string circuits. Verify ampacity per NEC 690.8.",
                "reference": ref}


def check_rapid_shutdown(fields: dict) -> dict:
    """Check if rapid shutdown is mentioned in the plan (required by NEC 690.12)."""
    rule = "Rapid Shutdown (NEC 690.12)"
    ref = "NEC Article 690.12"

    if fields.get("has_rapid_shutdown"):
        return {"rule": rule, "status": "pass",
                "message": "Rapid shutdown system referenced in plan.",
                "reference": ref}
    return {"rule": rule, "status": "fail",
            "message": "No rapid shutdown reference found. Required for rooftop PV per NEC 690.12.",
            "reference": ref}


def check_dc_disconnect(fields: dict) -> dict:
    """Check if DC disconnect is mentioned (required by NEC 690.13)."""
    rule = "DC Disconnect (NEC 690.13)"
    ref = "NEC Article 690.13"

    if fields.get("has_dc_disconnect"):
        return {"rule": rule, "status": "pass",
                "message": "DC disconnect referenced in plan.",
                "reference": ref}
    return {"rule": rule, "status": "fail",
            "message": "DC disconnect not found in plan. Required near array per NEC 690.13.",
            "reference": ref}


def check_pv_warning_label(fields: dict) -> dict:
    """Check if PV warning/caution labels are mentioned."""
    rule = "PV Warning Labels (NEC 690.31)"
    ref = "NEC Article 690.31 / NFPA 70E"

    if fields.get("has_pv_warning_label"):
        return {"rule": rule, "status": "pass",
                "message": "Photovoltaic warning label referenced in plan.",
                "reference": ref}
    return {"rule": rule, "status": "warning",
            "message": "No PV warning label found. Ensure 'Warning: Photovoltaic Power Source' labels are on plan.",
            "reference": ref}


def check_breaker_sizing(fields: dict) -> dict:
    """Check breaker is not obviously oversized relative to voltage (basic heuristic)."""
    rule = "Breaker Sizing (NEC 705.12)"
    ref = "NEC Article 705.12(D)(2) — 120% rule"

    breaker = fields.get("breaker_amps")
    if breaker is None:
        return {"rule": rule, "status": "missing_data",
                "message": "Breaker size not detected in plan.",
                "reference": ref}
    if breaker <= 200:
        return {"rule": rule, "status": "pass",
                "message": f"{breaker}A breaker found — within typical residential range. Verify 120% rule manually.",
                "reference": ref}
    return {"rule": rule, "status": "warning",
            "message": f"{breaker}A breaker detected — verify compliance with NEC 705.12 120% rule.",
            "reference": ref}


def check_voltage_limit(fields: dict) -> dict:
    """Check DC voltage does not exceed 600V for residential (NEC 690.7)."""
    rule = "Max DC Voltage (NEC 690.7)"
    ref = "NEC Article 690.7"

    voltage = fields.get("voltage")
    if voltage is None:
        return {"rule": rule, "status": "missing_data",
                "message": "Voltage not detected in plan.",
                "reference": ref}
    if voltage <= 600:
        return {"rule": rule, "status": "pass",
                "message": f"{voltage}V detected — within 600V residential limit.",
                "reference": ref}
    return {"rule": rule, "status": "warning",
            "message": f"{voltage}V detected — exceeds 600V residential limit. Verify if commercial/utility rules apply (NEC 690.7).",
            "reference": ref}


def check_nec_version_stated(fields: dict) -> dict:
    """Check that a NEC code version is referenced on the plan."""
    rule = "Code Version Referenced"
    ref = "General plan completeness"

    version = fields.get("nec_version")
    if version:
        return {"rule": rule, "status": "pass",
                "message": f"NEC {version} referenced on plan.",
                "reference": ref}
    return {"rule": rule, "status": "warning",
            "message": "No NEC version found on plan. Plans should state the applicable code edition.",
            "reference": ref}
