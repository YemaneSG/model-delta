#!/usr/bin/env python3
"""
Synthetic part record generator for flow measurement and instrumentation equipment.
Generates 10,000 hierarchically consistent part records across 15 product families.
"""

import json
import csv
import random
from pathlib import Path
from collections import Counter

# Configuration
RECORDS_PER_PF = 667  # ~667 per PF × 15 = ~10,000
TARGET_RECORDS = 10000
SEED_BASE = 400

TARGET_PFS = [
    "[402] DIFFERENTIAL PRESSURE INSTRUMENTS",
    "[403] FLOW COMPUTERS",
    "[404] FLOW METERS",
    "[405] FLOW SWITCHES",
    "[406] FLOW TRANSMITTERS",
    "[407] FLUID QUALITY",
    "[408] HEAT TRACE",
    "[409] LEVEL INSTRUMENTS",
    "[410] LOADING",
    "[411] METERING",
    "[412] PRESSURE INSTRUMENTS",
    "[413] PROVERS",
    "[414] PULSE INSTRUMENTS",
    "[415] TEMPERATURE INSTRUMENTS",
    "[416] VALVES - CFLO",
]

# Vocabulary banks for realistic part descriptions by PF
DESCRIPTIONS = {
    "[402] DIFFERENTIAL PRESSURE INSTRUMENTS": [
        "DIFFERENTIAL PRESSURE TRANSMITTER ORIFICE",
        "DIFFERENTIAL PRESSURE SWITCH PILOT OPERATED",
        "DIFFERENTIAL PRESSURE GAUGE LIQUID FILLED",
        "DIFFERENTIAL PRESSURE CELL FLUSH DIAPHRAGM",
        "DIFFERENTIAL PRESSURE TRANSDUCER ELECTRONIC",
        "DIFFERENTIAL PRESSURE INDICATOR MECHANICAL",
        "DIFFERENTIAL PRESSURE SENSOR ANALOG OUTPUT",
        "DIFFERENTIAL PRESSURE SWITCH ADJUSTABLE SETPOINT",
        "DIFFERENTIAL PRESSURE RECORDER STRIP CHART",
        "DIFFERENTIAL PRESSURE TRANSMITTER REMOTE SEAL",
    ],
    "[403] FLOW COMPUTERS": [
        "FLOW COMPUTER MODULAR RTU DISPLAY",
        "FLOW COMPUTER EMBEDDED FIRMWARE UPDATE",
        "FLOW COMPUTER MULTI INPUT CHANNEL",
        "FLOW COMPUTER DIGITAL COMMUNICATION GATEWAY",
        "FLOW COMPUTER ORIFICE PLATE INTEGRATED",
        "FLOW COMPUTER CORIOLIS COMPATIBLE",
        "FLOW COMPUTER TURBINE CORRECTOR",
        "FLOW COMPUTER ULTRASONIC VOLUME TEMPERATURE",
        "FLOW COMPUTER DATA LOGGER STORAGE",
        "FLOW COMPUTER NETWORK INTERFACE MODBUS",
    ],
    "[404] FLOW METERS": [
        "ULTRASONIC FLOW METER CLAMP ON",
        "CORIOLIS FLOW METER INLINE CARBON STEEL",
        "TURBINE FLOW METER PRECISION BEARING",
        "ORIFICE FLOW METER FLANGE MOUNTED",
        "MAGNETIC FLOW METER CERAMIC LINED",
        "POSITIVE DISPLACEMENT METER PISTON",
        "VORTEX FLOW METER STEAM SERVICE",
        "ROTAMETER VARIABLE AREA GLASS TUBE",
        "WEDGE FLOW METER RESTRICTION ORIFICE",
        "THERMAL MASS FLOW METER BYPASS",
    ],
    "[405] FLOW SWITCHES": [
        "FLOW SWITCH PADDLE TYPE INSERTION",
        "FLOW SWITCH TURBINE WHEEL ROTOR",
        "FLOW SWITCH MAGNET FLANGE BODY",
        "FLOW SWITCH PISTON ADJUSTABLE SETPOINT",
        "FLOW SWITCH PILOT OPERATED PRESSURE",
        "FLOW SWITCH SPRING LOADED RELAY",
        "FLOW SWITCH ELECTRONIC THRESHOLD SENSOR",
        "FLOW SWITCH MECHANICAL ACTUATOR SNAP",
        "FLOW SWITCH THREADED ADAPTER BODY",
        "FLOW SWITCH VISUAL INDICATOR POSITION",
    ],
    "[406] FLOW TRANSMITTERS": [
        "FLOW TRANSMITTER ELECTRONIC OUTPUT SIGNAL",
        "FLOW TRANSMITTER ULTRASONIC CLAMP ATTACHMENT",
        "FLOW TRANSMITTER MAGNETIC PICKUP SENSOR",
        "FLOW TRANSMITTER PRESSURE DIFFERENTIAL",
        "FLOW TRANSMITTER REMOTE SEAL ADAPTER",
        "FLOW TRANSMITTER INTEGRAL CONVERTER MODULE",
        "FLOW TRANSMITTER FREQUENCY OUTPUT PULSE",
        "FLOW TRANSMITTER TEMPERATURE COMPENSATED",
        "FLOW TRANSMITTER DIGITAL COMMUNICATION INTERFACE",
        "FLOW TRANSMITTER CORIOLIS DUAL PARAMETER",
    ],
    "[407] FLUID QUALITY": [
        "FLUID ANALYZER INLINE NIR SENSOR",
        "FLUID ANALYZER DIELECTRIC CONSTANT PROBE",
        "WATER IN OIL SENSOR CAPACITIVE",
        "WATER IN OIL METER KARL FISCHER",
        "PARTICLE COUNTER OPTICAL LASER SENSOR",
        "VISCOSITY ANALYZER TEMPERATURE CORRECTED",
        "ACID NUMBER ANALYZER POTENTIOMETRIC",
        "MOISTURE ANALYZER COULOMETRIC TITRATION",
        "DENSITY ANALYZER OSCILLATING TUBE",
        "CONDUCTIVITY METER INLINE ELECTRODE",
    ],
    "[408] HEAT TRACE": [
        "HEAT TRACE SELF REGULATING CABLE",
        "HEAT TRACE CONSTANT WATTAGE POWER",
        "HEAT TRACE MINERAL INSULATED SHEATH",
        "HEAT TRACE CONTROL THERMOSTAT DIGITAL",
        "HEAT TRACE JUNCTION BOX TERMINAL",
        "HEAT TRACE POWER SUPPLY TRANSFORMER",
        "HEAT TRACE WEATHERPROOF OUTER JACKET",
        "HEAT TRACE BRANCH CABLE ASSEMBLY",
        "HEAT TRACE EXTENSION CORD INDUSTRIAL",
        "HEAT TRACE INSTALLATION KIT FASTENERS",
    ],
    "[409] LEVEL INSTRUMENTS": [
        "LEVEL TRANSMITTER GUIDED WAVE RADAR",
        "LEVEL GAUGE GLASS TUBE REFLEX",
        "LEVEL SWITCH FLOAT MECHANICAL",
        "LEVEL SWITCH CAPACITIVE ELECTRODE",
        "LEVEL TRANSMITTER ULTRASONIC ECHO",
        "LEVEL TRANSMITTER DISPLACER BUOYANCY",
        "LEVEL SWITCH PADDLE ARM ROTATING",
        "LEVEL TRANSMITTER MAGNETIC FLOAT TAPE",
        "LEVEL INDICATOR SIGHT GLASS VALVE",
        "LEVEL TRANSMITTER PRESSURE HYDROSTATIC",
    ],
    "[410] LOADING": [
        "LOADING SYSTEM FLOW METER REFERENCE",
        "LOADING ARM SWIVEL JOINT BEARING",
        "LOADING PLATFORM SCALE LOAD CELL",
        "LOADING COUNTER DIGITAL DISPLAY",
        "LOADING VALVE PROPORTIONAL CONTROL",
        "LOADING HOSE BREAKAWAY COUPLING",
        "LOADING SKID SEPARATOR VESSEL",
        "LOADING MANIFEST PRINTER PRINTER",
        "LOADING OVERFILL PROTECTION DEVICE",
        "LOADING PUMP GEAR REDUCTION MOTOR",
    ],
    "[411] METERING": [
        "METERING PUMP RECIPROCATING PISTON",
        "METERING PUMP GEAR DRIVEN CONSTANT",
        "METERING VALVE PROPORTIONAL SPOOL",
        "METERING FLOW CONTROL RESTRICTOR",
        "METERING ORIFICE PLATE CALIBRATED",
        "METERING TURBINE WHEEL ROTOR",
        "METERING POSITIVE DISPLACEMENT SCREW",
        "METERING ROLLER ROTOR PUMP UNIT",
        "METERING PROOF METER REFERENCE",
        "METERING MASTER METER INTERCHANGE",
    ],
    "[412] PRESSURE INSTRUMENTS": [
        "PRESSURE GAUGE BOURDON TUBE 0-5000PSI",
        "PRESSURE TRANSMITTER ELECTRONIC SIGNAL",
        "PRESSURE SWITCH ADJUSTABLE SETPOINT",
        "PRESSURE RELIEF VALVE PILOT OPERATED",
        "PRESSURE REGULATOR BALANCED SPRING",
        "PRESSURE INDICATOR GLYCERIN DAMPED",
        "PRESSURE SENSOR CERAMIC CAPACITIVE",
        "PRESSURE TRANSDUCER STRAIN GAUGE",
        "PRESSURE FILTER BYPASS SPRING",
        "PRESSURE SNUBBER SINTERED BRONZE",
    ],
    "[413] PROVERS": [
        "PROVER BALL PIPE SMALL VOLUME",
        "PROVER DISPLACEMENT SERVO CONTROLLED",
        "PROVER RUNNING CHAMBER SPHERE",
        "PROVER SPHERE LARGE CAPACITY METER",
        "PROVER BELT DRIVE MECHANICAL COUNTER",
        "PROVER COMPACT PORTABLE FIELD UNIT",
        "PROVER CALIBRATION CERTIFICATE TRACEABLE",
        "PROVER MANUAL VALVE ISOLATION BLOCK",
        "PROVER SCOPE FINDER ALIGNMENT TOOL",
        "PROVER DISPLACEMENT BUCKET TRAP",
    ],
    "[414] PULSE INSTRUMENTS": [
        "PULSE CONVERTER FREQUENCY DIGITAL",
        "PULSE COUNTER TOTALIZER MECHANICAL",
        "PULSE COUNTER ELECTRONIC RESET",
        "PULSE DIVIDER GEAR REDUCTION",
        "PULSE TESTER INDICATOR LIGHT",
        "PULSE ADAPTER MAGNETIC PICKUP SWITCH",
        "PULSE OUTPUT METER TRANSMISSION SIGNAL",
        "PULSE CONDITIONER SIGNAL FILTER",
        "PULSE DETECTOR PROXIMITY SENSOR",
        "PULSE INTEGRATOR FLOW INTEGRATION",
    ],
    "[415] TEMPERATURE INSTRUMENTS": [
        "TEMPERATURE SENSOR RTD THERMOWELL",
        "TEMPERATURE TRANSMITTER ELECTRONIC OUTPUT",
        "TEMPERATURE INDICATOR DIAL BIMETALLIC",
        "TEMPERATURE SWITCH FIXED SETPOINT",
        "TEMPERATURE RECORDER STRIP CHART",
        "TEMPERATURE PROBE IMMERSION SHEATH",
        "TEMPERATURE CONTROLLER PROPORTIONAL BAND",
        "TEMPERATURE COMPENSATOR AUTOMATIC FLUID",
        "TEMPERATURE SENSOR THERMISTOR PROBE",
        "TEMPERATURE GAUGE LIQUID BULB",
    ],
    "[416] VALVES - CFLO": [
        "CONTROL VALVE GLOBE CAGE TRIM",
        "CONTROL VALVE BALL FLOATING SEAT",
        "CONTROL VALVE BUTTERFLY OFFSET DISC",
        "CONTROL VALVE ROTARY PLUG SLEEVE",
        "CONTROL VALVE THREE WAY DIVERTER",
        "CONTROL VALVE POPPET PILOT ASSISTED",
        "CONTROL VALVE SEGMENTED BALL TRIM",
        "CONTROL VALVE GATE WEDGE GUIDING",
        "CONTROL VALVE CHECK POPPET SPRING",
        "CONTROL VALVE SOLENOID PILOT ASSIST",
    ],
}


def load_taxonomy(path):
    """Load the taxonomy tree from JSON."""
    with open(path) as f:
        return json.load(f)


def generate_part_number(used_set, seed):
    """Generate unique 8-digit part number."""
    while True:
        part_num = f"{random.randint(10000000, 99999999)}"
        if part_num not in used_set:
            used_set.add(part_num)
            return part_num


def generate_description(pf):
    """Generate realistic part description for given PF."""
    desc_bank = DESCRIPTIONS.get(pf, ["FLOW MEASUREMENT EQUIPMENT"])
    return random.choice(desc_bank)


def generate_records(taxonomy):
    """Generate all synthetic part records."""
    pf_to_tech = taxonomy["pf_to_tech"]
    tech_to_brand = taxonomy["tech_to_brand"]
    brand_to_tool = taxonomy["brand_to_tool"]

    records = []
    used_part_numbers = set()

    # Calculate records per PF to hit target
    total_pfs = len(TARGET_PFS)
    records_per_pf = TARGET_RECORDS // total_pfs

    for pf_idx, pf in enumerate(TARGET_PFS):
        random.seed(SEED_BASE + pf_idx)

        # Get valid techs for this PF
        if pf not in pf_to_tech:
            print(f"WARNING: {pf} not in taxonomy")
            continue

        valid_techs = pf_to_tech[pf]
        if not valid_techs:
            print(f"WARNING: {pf} has no techs")
            continue

        # Generate records for this PF
        for _ in range(records_per_pf):
            # Sample tech
            tech = random.choice(valid_techs)

            # Sample brand
            if tech not in tech_to_brand:
                print(f"WARNING: tech {tech} not in tech_to_brand")
                continue
            valid_brands = tech_to_brand[tech]
            if not valid_brands:
                continue
            brand = random.choice(valid_brands)

            # Sample tool
            toolname = ""
            if brand in brand_to_tool:
                valid_tools = brand_to_tool[brand]
                if valid_tools:
                    toolname = random.choice(valid_tools)

            # Generate part number and description
            part_num = generate_part_number(used_part_numbers, SEED_BASE + pf_idx)
            description = generate_description(pf)

            record = {
                "Part Number": part_num,
                "Part Description": description,
                "PRODUCT_FAMILY_NAME": pf,
                "TECHNOLOGY_NAME": tech,
                "BRAND_NAME": brand,
                "TOOLNAME": toolname,
                "BUSINESS_LINE_NAME": "SYNTHETIC",
            }
            records.append(record)

    return records


def write_csv(records, output_path):
    """Write records to CSV file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "Part Number",
        "Part Description",
        "PRODUCT_FAMILY_NAME",
        "TECHNOLOGY_NAME",
        "BRAND_NAME",
        "TOOLNAME",
        "BUSINESS_LINE_NAME",
    ]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)

    return len(records)


def main():
    """Main entry point."""
    taxonomy_path = "/Users/yemane/Code/asset-taxonomy-classifier/ml_pipeline/constraints/taxonomy_tree.json"
    output_path = "/Users/yemane/Code/model-delta/synthesis/synthesized_part_03.csv"

    print(f"Loading taxonomy from {taxonomy_path}...")
    taxonomy = load_taxonomy(taxonomy_path)

    print(f"Generating {TARGET_RECORDS} synthetic part records...")
    records = generate_records(taxonomy)

    print(f"Writing {len(records)} records to {output_path}...")
    row_count = write_csv(records, output_path)

    # Verify output
    pf_counts = Counter(r["PRODUCT_FAMILY_NAME"] for r in records)

    print("\n=== SYNTHESIS COMPLETE ===")
    print(f"Total rows written: {row_count}")
    print(f"Unique Product Families: {len(pf_counts)}")
    print(f"Records per PF:")
    for pf in sorted(TARGET_PFS):
        count = pf_counts.get(pf, 0)
        status = "✓" if count > 0 else "✗ MISSING"
        print(f"  {pf}: {count} {status}")

    empty_pfs = [pf for pf in TARGET_PFS if pf_counts.get(pf, 0) == 0]
    if empty_pfs:
        print(f"\nWARNING: {len(empty_pfs)} PFs with 0 records")
    else:
        print("\n✓ All PFs have records")


if __name__ == "__main__":
    main()
