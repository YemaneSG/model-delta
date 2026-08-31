#!/usr/bin/env python3
"""
Synthetic part record generator for oilfield equipment taxonomy classifier.
Generates 10,000 records across 15 product families with hierarchically consistent labels.
"""

import json
import random
import csv
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

TAXONOMY_PATH = "/Users/yemane/Code/asset-taxonomy-classifier/ml_pipeline/constraints/taxonomy_tree.json"
OUTPUT_PATH = "/Users/yemane/Code/model-delta/synthesis/synthesized_part_04.csv"
TOTAL_RECORDS = 10000
SEED = 600

ASSIGNED_PFS = [
    "[417] VALVES - CDIST",
    "[863] CHOKES - CSUB",
    "[864] COMMON WELLHEAD EQUIPMENT",
    "[865] XL BORE SPECIFIC EQUIPMENT",
    "[867] CONTROLS - SPS",
    "[868] MANIFOLDS - SPS",
    "[869] CONTROLS WELL ACCESS SERVICES",
    "[912] ZEITECS",
    "[931] PROCESS TECHNOLOGIES - MPS",
    "[933] PROCESSING SYSTEMS",
    "[965] SUBSEA WELLHEADS",
    "[966] TOOLS - CSUB",
    "[967] WELLHEAD DRILL THRU EQUIPMENT",
    "[968] TREES - CSUB",
    "[969] VALVES - CSUB",
]

# Description term banks by product family type (subsea/wellhead terminology)
DESCRIPTION_BANKS = {
    "VALVES": [
        "GATE VALVE SUBSEA ACTUATED",
        "CHECK VALVE CARTRIDGE BONNET",
        "BALL VALVE PILOT OPERATED",
        "NEEDLE VALVE REGULATED FLOW",
        "RELIEF VALVE PILOT ACTUATED",
        "ISOLATION VALVE FLANGED CONNECTION",
        "DIRECTIONAL CONTROL VALVE SPOOL",
        "PROPORTIONAL VALVE SERVO CONTROLLED",
        "SOLENOID VALVE POPPET TYPE",
        "SHUTTLE VALVE INTEGRATED BODY",
    ],
    "CHOKES": [
        "CHOKE SUBSEA ELECTRO-HYDRAULIC ACTUATED",
        "FIXED CHOKE FLOW RESTRICTION",
        "ADJUSTABLE CHOKE MANUAL CALIBRATED",
        "BEAN CHOKE SURFACE MOUNTED",
        "EROSION RESISTANT CHOKE INSERT",
        "CAVITATION CONTROL CHOKE DESIGN",
        "PRESSURE BALANCED CHOKE ASSEMBLY",
        "DUAL STAGE CHOKE CONFIGURATION",
        "FLOW CONTROL CHOKE MANDREL",
        "SUBSEA PROCESS CHOKE SUBSURFACE",
    ],
    "WELLHEAD": [
        "WELLHEAD CASING SPOOL DUAL STUDDED",
        "WELLHEAD TUBING SPOOL COMPACT",
        "WELLHEAD ADAPTER FLANGE THREADED",
        "WELLHEAD CONNECTOR FACE SEAL",
        "WELLHEAD HOUSING STRESS RELIEVED",
        "WELLHEAD HANGER LOAD BOWL",
        "WELLHEAD SEAL ASSEMBLY ELASTOMER",
        "WELLHEAD BUSHING WEAR RESISTANT",
        "WELLHEAD MANDREL BORE PROTECTION",
        "WELLHEAD RING LOAD BEARING",
    ],
    "SUBSEA": [
        "SUBSEA TREE HORIZONTAL DUAL BORE",
        "SUBSEA TEMPLATE MANIFOLD INTEGRATED",
        "SUBSEA MUDMAT FOUNDATION PILES",
        "SUBSEA ADAPTER SLED MOUNTED",
        "SUBSEA HOUSING COMPACT MODULAR",
        "SUBSEA BODY FABRICATED STEEL",
        "SUBSEA STACK VERTICAL CONFIGURATION",
        "SUBSEA PLATEN LOAD RATED",
        "SUBSEA STRUCTURE FLEXIBLE JUMPER",
        "SUBSEA ASSEMBLY PRE-TESTED FACTORY",
    ],
    "CONTROLS": [
        "CONTROL MODULE SUBSEA RETRIEVABLE",
        "CONTROL SYSTEM PILOT OPERATED",
        "CONTROL VALVE SHUTTLE LOGIC",
        "PILOT SUPPLY CONTROL BLOCK",
        "PRESSURE REDUCING CONTROL STATION",
        "FLOW CONTROL PROPORTIONAL LIMITER",
        "SEQUENCE CONTROL MANIFOLD STACK",
        "SOLENOID PILOT CONTROL SYSTEM",
        "REDUNDANT CONTROL DUAL CHANNEL",
        "INTEGRATED CONTROL SUBSEA PACKAGE",
    ],
    "MANIFOLD": [
        "MANIFOLD TEMPLATE SUBSEA 4 SLOT",
        "MANIFOLD BLOCK ALUMINUM PORTED",
        "MANIFOLD PLATE SANDWICH STACKED",
        "MANIFOLD BODY DUCTILE IRON CAST",
        "MANIFOLD CAVITY CROSS-DRILLED PORTED",
        "MANIFOLD INTERFACE SUBPLATE MOUNTED",
        "MANIFOLD SPOOL DIRECTIONAL CONTROL",
        "MANIFOLD VALVE CAVITY INTEGRATED",
        "MANIFOLD CONNECTOR PORT INTERFACE",
        "MANIFOLD ASSEMBLY PRESSURE TESTED",
    ],
    "TOOLS": [
        "WELLHEAD TOOLS DRILL THRU CORE",
        "EXTRACTION TOOL JAW TYPE OVERSHOT",
        "RUNNING TOOL GUIDE ASSEMBLY",
        "SETTING TOOL POPPET ACTIVATED",
        "SERVICE TOOL RETRIEVABLE SUBSEA",
        "SKID ASSEMBLY LANDING FRAME",
        "BASKET GUIDE ALIGNMENT SPINDLE",
        "CAGE LOCK RETENTION MECHANISM",
        "TRIGGER LATCH SHEAR PIN RELEASE",
        "ADAPTER CARTRIDGE QUICK CHANGE",
    ],
    "TREES": [
        "SUBSEA TREE HORIZONTAL DUAL BORE",
        "MUDLINE TREE SURFACE WELLHEAD",
        "CHRISTMAS TREE MASTER SLAVE",
        "PRODUCTION TREE SINGLE STEM",
        "INJECTION TREE PRESSURE RATED",
        "TIEBACK TREE REMOTE INTERFACE",
        "TEMPLATE SUBSEA MANIFOLD TREE",
        "RISER BASE TREE FLEX JOINT",
        "TRUNKLINE TREE TEE CONFIGURATION",
        "DISCONNECT TREE QUICK COUPLING",
    ],
    "PROCESSING": [
        "PROCESS SEPARATOR HORIZONTAL 3 PHASE",
        "COMPRESSOR STAGE CENTRIFUGAL IMPELLER",
        "PUMP STAGE MULTISTAGE CENTRIFUGAL",
        "METER TURBINE TYPE FLOW MEASUREMENT",
        "MEASUREMENT DEVICE ORIFICE PLATE",
        "TREATMENT SKID PRODUCED WATER",
        "WATER INJECTION TREATMENT SYSTEM",
        "OIL CONDITIONING FILTER CARTRIDGE",
        "GAS DEHYDRATION GLYCOL CONTACTOR",
        "POWER GENERATION TURBINE DRIVEN",
    ],
    "EQUIPMENT": [
        "DRILL THRU WELLHEAD COMPACT 20IN",
        "BORE PROTECTION SLEEVE HARDENED",
        "SEAL ASSEMBLY ELASTOMER BONDED",
        "CASING HANGER DUAL CONE SEAL",
        "TUBING HANGER MANDREL ORIENTATION SLEEVE",
        "ADAPTER BLOCK SUBSEA MOUNTED",
        "INTERFACE PLATE BOLTED ASSEMBLY",
        "SUPPORT FRAME INTEGRAL GUIDEWIRES",
        "SPACER RING PRECISION MACHINED",
        "BACKUP RING POLYMER REINFORCED",
    ],
    "ZEITECS": [
        "ZEITEC PUMP ELECTRIC SUBMERSIBLE",
        "ZEITEC SHUTTLE VALVE MANIFOLD",
        "ZEITEC FLOW DIVIDER PRIORITY",
        "ZEITEC ACCUMULATOR BLADDER TYPE",
        "ZEITEC COOLER PLATE FIN ALUMINUM",
        "ZEITEC FILTER ELEMENT MICRON",
        "ZEITEC MOTOR ELECTRIC AC INDUCTION",
        "ZEITEC DAMPER PULSATION CONTROL",
        "ZEITEC INTENSIFIER PRESSURE BOOST",
        "ZEITEC REGULATOR PRESSURE REDUCING",
    ],
}

# ============================================================================
# Utility Functions
# ============================================================================

def load_taxonomy(path):
    """Load taxonomy from JSON file."""
    with open(path) as f:
        return json.load(f)


def get_description_bank(pf_name):
    """Map PF to appropriate description term bank."""
    pf_lower = pf_name.lower()

    if "valve" in pf_lower:
        return DESCRIPTION_BANKS["VALVES"]
    elif "choke" in pf_lower:
        return DESCRIPTION_BANKS["CHOKES"]
    elif "wellhead" in pf_lower:
        return DESCRIPTION_BANKS["WELLHEAD"]
    elif "subsea" in pf_lower:
        return DESCRIPTION_BANKS["SUBSEA"]
    elif "tree" in pf_lower:
        return DESCRIPTION_BANKS["TREES"]
    elif "control" in pf_lower:
        return DESCRIPTION_BANKS["CONTROLS"]
    elif "manifold" in pf_lower:
        return DESCRIPTION_BANKS["MANIFOLD"]
    elif "tool" in pf_lower:
        return DESCRIPTION_BANKS["TOOLS"]
    elif "processing" in pf_lower or "process" in pf_lower:
        return DESCRIPTION_BANKS["PROCESSING"]
    elif "zeitec" in pf_lower:
        return DESCRIPTION_BANKS["ZEITECS"]
    else:
        return DESCRIPTION_BANKS["EQUIPMENT"]


def generate_part_number(used_set, seed):
    """Generate unique 8-digit part number."""
    random.seed(seed)
    while True:
        pn = str(random.randint(10000000, 99999999))
        if pn not in used_set:
            used_set.add(pn)
            return pn


def generate_description(pf_name, seed):
    """Generate realistic part description from term bank."""
    bank = get_description_bank(pf_name)
    random.seed(seed)
    return random.choice(bank)


def dedup_list(lst):
    """Remove duplicates while preserving order."""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# ============================================================================
# Main Generation Loop
# ============================================================================

def main():
    print("Loading taxonomy...")
    tax = load_taxonomy(TAXONOMY_PATH)

    # Ensure output directory exists
    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)

    # Records per PF
    records_per_pf = TOTAL_RECORDS // len(ASSIGNED_PFS)
    remainder = TOTAL_RECORDS % len(ASSIGNED_PFS)

    print(f"Generating {TOTAL_RECORDS} records across {len(ASSIGNED_PFS)} PFs")
    print(f"Target: {records_per_pf} records per PF + {remainder} extra\n")

    records = []
    used_part_numbers = set()
    pf_counts = {}

    for pf_idx, pf in enumerate(ASSIGNED_PFS):
        pf_counts[pf] = 0
        tech_list = tax['pf_to_tech'].get(pf, [])

        if not tech_list:
            print(f"WARNING: {pf} has no TECHs in taxonomy")
            continue

        # Deduplicate and sample from TECH options for this PF
        unique_techs = dedup_list(tech_list)

        print(f"[{pf_idx+1}/{len(ASSIGNED_PFS)}] {pf}")
        print(f"  Unique TECHs: {len(unique_techs)}")

        # Add extra records to first PF to reach exactly TOTAL_RECORDS
        pf_records = records_per_pf
        if pf_idx == 0:
            pf_records += remainder

        # Generate records for this PF
        for record_idx in range(pf_records):
            # Random TECH from this PF's TECH options
            record_seed = SEED + (pf_idx * 1000) + record_idx
            random.seed(record_seed)
            tech = random.choice(unique_techs)

            # Random BRAND from this TECH's BRAND options
            brand_list = tax['tech_to_brand'].get(tech, [])
            if not brand_list:
                print(f"    WARNING: {tech} has no BRANDs")
                continue

            brand = random.choice(brand_list)

            # TOOLNAME from this BRAND's TOOLNAME options (may be empty)
            tool_list = tax['brand_to_tool'].get(brand, [])
            toolname = random.choice(tool_list) if tool_list else ""

            # Part Number (8-digit unique)
            part_num = generate_part_number(used_part_numbers, record_seed + 500000)

            # Part Description
            description = generate_description(pf, record_seed + 600000)

            records.append({
                "Part Number": part_num,
                "Part Description": description,
                "PRODUCT_FAMILY_NAME": pf,
                "TECHNOLOGY_NAME": tech,
                "BRAND_NAME": brand,
                "TOOLNAME": toolname,
                "BUSINESS_LINE_NAME": "SYNTHETIC",
            })

            pf_counts[pf] += 1

        print(f"  Generated: {pf_counts[pf]} records\n")

    # Write CSV
    print(f"Writing {len(records)} records to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Part Number",
            "Part Description",
            "PRODUCT_FAMILY_NAME",
            "TECHNOLOGY_NAME",
            "BRAND_NAME",
            "TOOLNAME",
            "BUSINESS_LINE_NAME",
        ])
        writer.writeheader()
        writer.writerows(records)

    # Summary
    print("\n" + "="*70)
    print("SYNTHESIS SUMMARY")
    print("="*70)
    print(f"Total records written: {len(records)}")
    print(f"Unique part numbers: {len(used_part_numbers)}")
    print(f"Unique PFs: {len([pf for pf, cnt in pf_counts.items() if cnt > 0])}")
    print(f"Output file: {OUTPUT_PATH}")

    print("\nRecords per PF:")
    for pf in ASSIGNED_PFS:
        count = pf_counts[pf]
        status = "OK" if count > 0 else "MISSING"
        print(f"  {pf}: {count:4d} [{status}]")

    # Check for zero-count PFs
    zero_count_pfs = [pf for pf, cnt in pf_counts.items() if cnt == 0]
    if zero_count_pfs:
        print(f"\nERROR: {len(zero_count_pfs)} PF(s) with 0 records:")
        for pf in zero_count_pfs:
            print(f"  - {pf}")
        return 1

    print("\nSynthesis complete!")
    return 0


if __name__ == "__main__":
    exit(main())
