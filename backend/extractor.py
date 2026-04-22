import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path: str) -> dict:
    """Extract text and key fields from a solar permit PDF."""
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    doc.close()

    fields = parse_fields(full_text)

    return {
        "page_count": len(doc),
        "raw_text": full_text,
        "fields": fields
    }

def parse_fields(text: str) -> dict:
    """Extract key solar permit fields from raw text using regex patterns."""
    fields = {}

    # Module / Panel info
    module_match = re.search(r'(\d+)\s*(pv\s*modules?|solar\s*panels?|modules?)', text, re.IGNORECASE)
    fields["module_count"] = int(module_match.group(1)) if module_match else None

    pmax_match = re.search(r'(\d{2,4})\s*[wW](?:att)?[- ]*(?:module|panel|pmax|p_max)?', text, re.IGNORECASE)
    fields["module_wattage"] = int(pmax_match.group(1)) if pmax_match else None

    # System size (kW)
    kw_match = re.search(r'(\d+(?:\.\d+)?)\s*k[wW](?:\s*DC|\s*AC|\s*STC)?', text, re.IGNORECASE)
    fields["system_size_kw"] = float(kw_match.group(1)) if kw_match else None

    # Wire / conductor gauge
    wire_match = re.search(r'(\d+)\s*(?:AWG|awg)', text, re.IGNORECASE)
    fields["wire_gauge_awg"] = int(wire_match.group(1)) if wire_match else None

    # Inverter
    inverter_match = re.search(r'inverter[:\s]+([A-Za-z0-9\-\s]+?)(?:\n|,|;)', text, re.IGNORECASE)
    fields["inverter"] = inverter_match.group(1).strip() if inverter_match else None

    # Breaker size
    breaker_match = re.search(r'(\d+)\s*[aA](?:mp)?[- ]*(?:breaker|ocpd|overcurrent)?', text, re.IGNORECASE)
    fields["breaker_amps"] = int(breaker_match.group(1)) if breaker_match else None

    # Voltage
    voltage_match = re.search(r'(\d{2,4})\s*[vV](?:olt)?(?:AC|DC)?', text, re.IGNORECASE)
    fields["voltage"] = int(voltage_match.group(1)) if voltage_match else None

    # Rapid shutdown mentioned?
    fields["has_rapid_shutdown"] = bool(re.search(r'rapid\s*shutdown', text, re.IGNORECASE))

    # DC disconnect mentioned?
    fields["has_dc_disconnect"] = bool(re.search(r'dc\s*disconnect', text, re.IGNORECASE))

    # Labels/warnings mentioned?
    fields["has_pv_warning_label"] = bool(re.search(r'warning.*photovoltaic|pv.*warning|caution.*solar', text, re.IGNORECASE))

    # NEC code version mentioned?
    nec_match = re.search(r'NEC\s*(\d{4})', text, re.IGNORECASE)
    fields["nec_version"] = nec_match.group(1) if nec_match else None

    return fields
