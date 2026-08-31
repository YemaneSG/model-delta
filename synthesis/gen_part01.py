#!/usr/bin/env python3
"""
Synthetic oilfield part record generator for ML taxonomy classifier.
Generates 10,000 records across 15 product families with hierarchically consistent labels.
"""

import json
import random
import csv
from collections import defaultdict
import sys

# Configuration
TOTAL_RECORDS = 10000
NUM_PFS = 15
RECORDS_PER_PF = TOTAL_RECORDS // NUM_PFS  # ~667 per PF
REMAINDER = TOTAL_RECORDS % NUM_PFS  # 10 records distributed across first PFs
SEED = 42

# Assigned product families
ASSIGNED_PFS = [
    "[105] AL CABLES",
    "[110] AL DOWNHOLE EQUIPMENT",
    "[115] AL SURFACE EQUIPMENT",
    "[120] DOWNHOLE MONITORING",
    "[125] GAS LIFT",
    "[130] HORIZONTAL PUMPING SYSTEM",
    "[135] CONNECTORS",
    "[140] COMPLETION ACCESSORIES",
    "[141] TLM",
    "[143] DIAGNOSTICS & ACQUISITION",
    "[144] INSTALLATION EQUIPMENT",
    "[145] FORMATION ISOLATION VALVES",
    "[146] LINER HANGERS",
    "[147] MULTI-STAGE STIMULATION",
    "[150] MULTILATERALS",
]

# Rich vocabulary for part descriptions by PF type
DESCRIPTION_VOCAB = {
    "[105] AL CABLES": [
        "POWER CABLE 3/0 AWG FLAT", "CABLE ARMOR BRAID COMPOSITE",
        "ELECTRICAL WIRE INSULATION JACKET", "CABLE TERMINATOR SEALED",
        "COPPER CONDUCTOR STRANDED", "CABLE REEL ASSEMBLY",
        "POWER CABLE 4/0 AWG ROUND", "CABLE SPLICE KIT POTHEAD",
        "SHIELDED CABLE ASSEMBLY", "CABLE GLAND STAINLESS STEEL",
        "ARMORED FIBER OPTIC CABLE", "CABLE JACKET POLYURETHANE",
        "POWER CONNECTOR CABLE HEAD", "SIGNAL CABLE TWISTED PAIR",
    ],
    "[110] AL DOWNHOLE EQUIPMENT": [
        "DOWNHOLE PUMP CENTRIFUGAL STAGE", "ELECTRIC SUBMERSIBLE MOTOR",
        "DOWNHOLE SENSOR TEMPERATURE GAUGE", "PUMP INTAKE SCREEN FILTER",
        "MOTOR COUPLING FLEXIBLE SHAFT", "PUMP BEARING RADIAL COMPOSITE",
        "DOWNHOLE CABLE LUBRICATOR", "PUMP PROTECTOR THERMAL",
        "MOTOR FLAT CABLE SPLICE", "DOWNHOLE ACCESSORY SUB",
        "PUMP STAGE 513 SERIES", "DOWNHOLE ACCELERATOR VALVE",
    ],
    "[115] AL SURFACE EQUIPMENT": [
        "SURFACE MOTOR ELECTRIC DRIVE", "PUMP FOUNDATION BASEPLATE",
        "TRANSFORMER THREE PHASE", "SWITCHBOX CONTROL PANEL",
        "CABLE ENTRY CONDUIT SEALED", "VENTILATION COOLING FAN",
        "MOTOR HEAT SINK RADIATOR", "DISCONNECT SWITCH RATED",
        "JUNCTION BOX SEALED", "POWER DISTRIBUTION PANEL",
    ],
    "[120] DOWNHOLE MONITORING": [
        "PRESSURE GAUGE DOWNHOLE SENSOR", "TEMPERATURE TRANSMITTER DIGITAL",
        "DOWNHOLE INCLINOMETER GYRO", "DOWNHOLE ACCELEROMETER SENSOR",
        "PRESSURE TRANSDUCER DIAPHRAGM", "TEMPERATURE PROBE THERMOCOUPLE",
        "DOWNHOLE STRAIN GAUGE LOAD", "VIBRATION SENSOR ACCELEROMETER",
        "DOWNHOLE CLOCK BATTERY POWERED", "SIGNAL CONDITIONER MODULE",
    ],
    "[125] GAS LIFT": [
        "GAS LIFT VALVE POPPET", "GAS LIFT MANDREL SIDE POCKET",
        "INJECTION VALVE CHECK SPRING", "GAS INJECTION TUBING CONNECTION",
        "UNLOADING VALVE ORIFICE", "PILOT OPERATED VALVE ASSEMBLY",
        "GAS LIFT SUPPLY LINE", "VALVE CAGE RETENTION RING",
        "INJECTION PORT TUBING INSERT", "PRESSURE EQUALIZING SEAT",
    ],
    "[130] HORIZONTAL PUMPING SYSTEM": [
        "CENTRIFUGAL PUMP BOWL ASSEMBLY", "INTAKE SECTION FILTER SCREEN",
        "PUMP DIFFUSER IMPELLER STAGE", "THRUST BEARING BLOCK ASSEMBLY",
        "PUMP BEARING BUSHING COMPOSITE", "MOTOR SHAFT COUPLING CONNECTOR",
        "PUMP HOUSING PRESSURE CONTAINING", "COLUMN PIPE HEAVY WALL",
        "INTAKE STRAINER MESH FINE", "DISCHARGE HEAD MOUNTING FLANGE",
    ],
    "[135] CONNECTORS": [
        "CONNECTOR SUB THREADED 3.5IN", "MANDREL CONNECTOR PROFILE",
        "PROFILE COUPLING HALF LOCK", "CONNECTION SHOULDER ALIGNMENT",
        "THREADED CONNECTION LOCK RING", "CONNECTOR NOSE PIECE GUIDE",
        "LOCKING RING RETENTION GROOVE", "CONNECTOR BODY PROFILE",
        "COUPLING NUT TORQUE LIMIT", "CONNECTION SEAL ELASTOMER",
    ],
    "[140] COMPLETION ACCESSORIES": [
        "PACKER ELEMENT RUBBER MOLDED", "SHEAR PIN SHEAR LOAD",
        "EQUALIZING HOLE PERFORATED", "DRAG RING FRICTION REDUCER",
        "BACKUP RING ELASTOMER", "PACKING ELEMENT CORE WIRE",
        "LOAD SHOULDER MANDREL", "SEATING SHOULDER SEAL BLOCK",
        "SLIP ELEMENT WEDGE ANGLE", "CAGE SPRING ASSEMBLY",
    ],
    "[141] TLM": [
        "TELEMETRY TOOL MANDREL BORE", "SIGNAL TRANSMITTER MODULATED",
        "BATTERY PACK POWER SUPPLY", "DOWNHOLE PRESSURE GAUGE ELECTRONIC",
        "TEMPERATURE SENSOR THERMISTOR", "TELEMETRY COLLAR HOUSING",
        "POWER MANAGEMENT MODULE", "SIGNAL PROCESSING BOARD",
        "DOWNHOLE MEMORY DEVICE", "TRANSMISSION ANTENNA COIL",
    ],
    "[143] DIAGNOSTICS & ACQUISITION": [
        "DATA LOGGER MEMORY UNIT", "PRESSURE RECORDING SENSOR",
        "TEMPERATURE ACQUISITION PROBE", "WELL TEST PLUG VALVE",
        "FLOW MEASUREMENT ORIFICE PLATE", "DATA STORAGE CARTRIDGE",
        "SAMPLING PORT VALVE CHECK", "PRESSURE HISTORY GAUGE",
        "TIME CLOCK RECORDING DEVICE", "DIGITAL DISPLAY READOUT",
    ],
    "[144] INSTALLATION EQUIPMENT": [
        "RUNNING TOOL MANDREL ADAPTER", "PULLING NECK SHEAR PIN",
        "SETTING JAR HYDRAULIC IMPACT", "GUIDE SHOE ALIGNMENT RING",
        "LAUNCHING DEVICE PRESSURE", "INSTALLATION LUBRICANT FLUID",
        "SETTING CHARGE EXPLOSIVE", "SPOTTER PLUG IDENTIFICATION",
        "LANDING NIPPLE PROFILE MATCH", "SETTING PISTON BORE",
    ],
    "[145] FORMATION ISOLATION VALVES": [
        "FORMATION ISOLATION VALVE FLAPPER", "VALVE SEAT PROFILE CONTACT",
        "FLAPPER HINGE PIN RETENTION", "SPRING RETURN HELICAL COIL",
        "CRACKING PRESSURE SETTING SCREW", "SEALING ELEMENT ELASTOMER",
        "FLAPPER STOP MECHANICAL BLOCK", "PRESSURE RELIEF VENT PORT",
        "VALVE BODY HOUSING STEEL", "POPPET MECHANISM ASSEMBLY",
    ],
    "[146] LINER HANGERS": [
        "LINER HANGER HYDRAULIC SET", "SLIPS CONICAL WEDGE ANGLE",
        "HANGER LOCK RING LOAD",
        "BYPASS VALVE RELIEF PORT", "SETTING PISTON BORE SEAL",
        "HANGER SEAL ASSEMBLY", "SLIP ELEMENT GEOMETRY CONTACT",
        "LOAD SHOULDER MANDREL PROFILE", "PACKING ELEMENT SEAL CONE",
        "LOCK RING LATCH MECHANISM",
    ],
    "[147] MULTI-STAGE STIMULATION": [
        "MULTI STAGE PLUG REMOVABLE", "STAGE ISOLATION BALL SEATING",
        "DROP BALL SEATING DEVICE", "PORT CONNECTOR FLOW PATH",
        "STAGE PLUG LANDING COLLAR", "ISOLATION BALL PLASTIC COMPOSITE",
        "BALL DROP TUBE GUIDE", "SEATING NIPPLE PROFILE SEAT",
        "STAGE BALL CATCHER ASSEMBLY", "PORT OPENING SLEEVE SHIFT",
    ],
    "[150] MULTILATERALS": [
        "LATERAL JUNCTION TEE STEEL", "LATERAL BRANCH CONNECTION",
        "LATERAL SEAL ASSEMBLY HOUSING", "LATERAL WINDOW OPENING CASING",
        "LATERAL TIEBACK CONNECTOR", "JUNCTION CONNECTOR HYBRID",
        "LATERAL JUNCTION PRESSURE RATED", "LATERAL GUIDE MILL OPENING",
        "LATERAL BRANCH SEAL ELEMENT", "LATERAL TIEBACK LOAD SHOULDER",
    ],
}


def load_taxonomy(taxonomy_path):
    """Load the taxonomy tree from JSON."""
    with open(taxonomy_path, 'r') as f:
        return json.load(f)


def generate_part_number(used_set, seed_val):
    """Generate a unique 8-digit part number."""
    random.seed(seed_val)
    while True:
        part_num = str(random.randint(10000000, 99999999))
        if part_num not in used_set:
            used_set.add(part_num)
            return part_num


def generate_description(pf, seed_val):
    """Generate a realistic part description for the PF type."""
    random.seed(seed_val)
    vocab = DESCRIPTION_VOCAB.get(pf, ["EQUIPMENT PART ASSEMBLY"])
    return random.choice(vocab)


def generate_synthetic_data(taxonomy_path, output_path):
    """Generate 10,000 synthetic part records."""

    print(f"Loading taxonomy from {taxonomy_path}...")
    taxonomy = load_taxonomy(taxonomy_path)

    # Build lookup dictionaries
    pf_to_tech = taxonomy.get("pf_to_tech", {})
    tech_to_brand = taxonomy.get("tech_to_brand", {})
    brand_to_tool = taxonomy.get("brand_to_tool", {})

    # Filter to assigned PFs only
    assigned_pf_to_tech = {pf: pf_to_tech[pf] for pf in ASSIGNED_PFS if pf in pf_to_tech}

    print(f"Found {len(assigned_pf_to_tech)} assigned PFs in taxonomy")
    for pf, techs in assigned_pf_to_tech.items():
        if not techs:
            print(f"  WARNING: {pf} has no technologies!")
        else:
            print(f"  {pf}: {len(techs)} technologies")

    used_part_numbers = set()
    records = []
    pf_counts = defaultdict(int)

    # Generate records
    record_id = 0
    for pf_idx, pf in enumerate(ASSIGNED_PFS):
        if pf not in assigned_pf_to_tech:
            print(f"WARNING: PF '{pf}' not found in taxonomy, skipping")
            continue

        techs = assigned_pf_to_tech[pf]
        if not techs:
            print(f"WARNING: PF '{pf}' has no technologies, skipping")
            continue

        # Add 1 extra record to first REMAINDER PFs to reach exactly 10,000
        num_records = RECORDS_PER_PF + (1 if pf_idx < REMAINDER else 0)
        for i in range(num_records):
            # Sample tech randomly (with seed for reproducibility)
            seed_val = SEED + record_id
            random.seed(seed_val)
            tech = random.choice(techs)

            # Sample brand
            if tech in tech_to_brand:
                brands = tech_to_brand[tech]
                if brands:
                    brand = random.choice(brands)
                else:
                    brand = ""
            else:
                brand = ""

            # Sample toolname
            toolname = ""
            if brand and brand in brand_to_tool:
                tools = brand_to_tool[brand]
                if tools:
                    toolname = random.choice(tools)

            # Generate part number and description
            part_num = generate_part_number(used_part_numbers, seed_val)
            description = generate_description(pf, seed_val + 1)

            records.append({
                'Part Number': part_num,
                'Part Description': description,
                'PRODUCT_FAMILY_NAME': pf,
                'TECHNOLOGY_NAME': tech,
                'BRAND_NAME': brand,
                'TOOLNAME': toolname,
                'BUSINESS_LINE_NAME': 'SYNTHETIC',
            })

            pf_counts[pf] += 1
            record_id += 1

    # Write CSV
    print(f"\nWriting {len(records)} records to {output_path}...")
    fieldnames = [
        'Part Number',
        'Part Description',
        'PRODUCT_FAMILY_NAME',
        'TECHNOLOGY_NAME',
        'BRAND_NAME',
        'TOOLNAME',
        'BUSINESS_LINE_NAME',
    ]

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # Report
    print(f"\n✓ Generated {len(records)} total records")
    print(f"✓ Unique part numbers: {len(used_part_numbers)}")
    print(f"✓ Product family distribution:")
    for pf in ASSIGNED_PFS:
        count = pf_counts.get(pf, 0)
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {pf}: {count} records")

    empty_pfs = [pf for pf in ASSIGNED_PFS if pf_counts.get(pf, 0) == 0]
    if empty_pfs:
        print(f"\nWARNING: {len(empty_pfs)} PFs with 0 records")
        return False

    return True


if __name__ == "__main__":
    taxonomy_path = "/Users/yemane/Code/asset-taxonomy-classifier/ml_pipeline/constraints/taxonomy_tree.json"
    output_path = "/Users/yemane/Code/model-delta/synthesis/synthesized_part_01.csv"

    success = generate_synthetic_data(taxonomy_path, output_path)
    sys.exit(0 if success else 1)
