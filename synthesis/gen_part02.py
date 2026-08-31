#!/usr/bin/env python3
"""
Generate synthetic industrial oilfield equipment part records.
- 10,000 total records across 15 product families (~667 each)
- Hierarchically consistent taxonomy labels (PF → TECH → BRAND → TOOLNAME)
- Realistic oilfield terminology in part descriptions
"""

import json
import csv
import random
from collections import defaultdict

# Seed for reproducibility
random.seed(200)

# Load taxonomy
with open('/Users/yemane/Code/asset-taxonomy-classifier/ml_pipeline/constraints/taxonomy_tree.json') as f:
    taxonomy = json.load(f)

pf_to_tech = taxonomy['pf_to_tech']
tech_to_brand = taxonomy['tech_to_brand']
brand_to_tool = taxonomy['brand_to_tool']

# The 15 assigned product families
ASSIGNED_PFS = [
    "[155] PACKERS",
    "[160] RESERVOIR MONITORING AND CONTROL",
    "[165] SAFETY VALVES",
    "[170] SAND CONTROL TOOLS",
    "[350] PCP DOWNHOLE EQUIP",
    "[351] PCP SURFACE EQUIP",
    "[352] MOTOR LEAD EXTENSION",
    "[366] TREES - CSUR",
    "[367] TUBING COMPLETIONS - CSUR",
    "[368] VALVES - CSUR",
    "[369] WELLHEADS - CSUR",
    "[370] FRAC AND FLOWBACK EQUIPMENT",
    "[375] TOOLS - CSUR",
    "[379] ANALYZERS",
    "[400] CHART RECORDERS"
]

# Rich vocabulary for part descriptions, organized by PF
DESCRIPTION_VOCAB = {
    "[155] PACKERS": [
        "PACKER ELEMENT RUBBER SEAL",
        "PACKER ANCHOR SLIPS ASSEMBLY",
        "PACKER MANDREL EXPANSION CONE",
        "PACKER COMPRESSION RING ELASTOMER",
        "PACKER TOP SEAL ASSEMBLY",
        "PACKER STRIPPER ELEMENT",
        "PACKER SETTING TOOL PROFILE",
        "PACKER LATCH RETENTION DEVICE",
        "PACKER BACKUP RING PLASTIC",
        "PACKER STRIPPER SPRING",
    ],
    "[160] RESERVOIR MONITORING AND CONTROL": [
        "RESERVOIR SENSOR FIBER OPTIC GAUGE",
        "PRESSURE MONITORING TOOL SUBSURFACE",
        "TEMPERATURE TELEMETRY RECEIVER MODULE",
        "FLOW RATE MEASUREMENT PROBE",
        "WELLBORE SAMPLE COLLECTOR APPARATUS",
        "CONTROL VALVE PILOT OPERATED",
        "WIRELESS TRANSMISSION UNIT SEALED",
        "PRESSURE DIFFERENTIAL SENSOR ASSEMBLY",
        "REAL TIME MONITORING SYSTEM NODE",
        "FLUID PROPERTY ANALYZER PROBE",
    ],
    "[165] SAFETY VALVES": [
        "SAFETY VALVE SUBSURFACE FLAPPER",
        "SAFETY VALVE PILOT OPERATED POPPET",
        "SAFETY RELIEF CARTRIDGE ASSEMBLY",
        "PRESSURE RELIEF BALL SEAT",
        "SAFETY VALVE SPRING ADJUSTABLE",
        "SAFETY VALVE CAGE GUIDANCE RING",
        "SAFETY VALVE VENT LINE RESTRICTION",
        "SAFETY VALVE PILOT DRAIN PASSAGE",
        "SAFETY VALVE CRACKING PRESSURE SET",
        "SAFETY VALVE BONNET RETAINING RING",
    ],
    "[170] SAND CONTROL TOOLS": [
        "SAND SCREEN WIRE WRAPPED BASE PIPE",
        "SAND FILTER MESH RETENTION DEVICE",
        "SAND PRODUCTION CONTROL COMPLETION",
        "SCREEN HOUSING PERFORATED JACKET",
        "SAND RETENTION FILTER PACK ASSEMBLY",
        "SCREEN BRIDGE PLUG SETTING TOOL",
        "SAND CONSOLIDATION RESIN COATED",
        "SCREEN EXTENSION TUBING JOINT",
        "SAND MANAGEMENT CYCLIC FLOW TOOL",
        "SCREEN SEATING NIPPLE PROFILE",
    ],
    "[350] PCP DOWNHOLE EQUIP": [
        "PCP ROTOR ELASTOMER COATED",
        "PCP PUMP STATOR SLEEVE ASSEMBLY",
        "PCP CHECK VALVE BALL RETAINER",
        "PCP INTAKE FOOT PIECE",
        "PCP DISCHARGE HEAD CONNECTION",
        "PCP MOTOR DRIVE COUPLING SHAFT",
        "PCP BEARING BUSHING BRONZE LINED",
        "PCP ELASTOMER STRIP REPLACEMENT KIT",
        "PCP PUMP TUBING ANCHOR COLLAR",
        "PCP BYPASS CHECK CARTRIDGE VALVE",
    ],
    "[351] PCP SURFACE EQUIP": [
        "PCP SURFACE DRIVE MOTOR ELECTRIC",
        "PCP GEARBOX SPEED REDUCER UNIT",
        "PCP BRAKE CLUTCH ENGAGEMENT",
        "PCP MOTOR BASE FRAME WELDED",
        "PCP CONTROL PANEL VARIABLE FREQUENCY",
        "PCP LUBRICATION SYSTEM PUMP",
        "PCP COUPLING TORQUE TRANSMISSION SHAFT",
        "PCP SAFETY SHUTDOWN PRESSURE RELIEF",
        "PCP SEAL INTEGRITY MONITORING UNIT",
        "PCP SURFACE TERMINATION HEAD ASSEMBLY",
    ],
    "[352] MOTOR LEAD EXTENSION": [
        "MOTOR LEAD EXTENSION FLAT CABLE",
        "MOTOR LEAD ARMOR PROTECTING SLEEVE",
        "MOTOR LEAD TERMINATION CONNECTOR PLUG",
        "MOTOR LEAD INSULATION POLYETHYLENE",
        "MOTOR LEAD FLAT CONDUCTOR PAIR",
        "MOTOR LEAD INSULATED JUNCTION BOX",
        "MOTOR LEAD ARMOR SPLICE COUPLING",
        "MOTOR LEAD CABLE STRAIN RELIEF",
        "MOTOR LEAD TRANSITION SLEEVE COUPLING",
        "MOTOR LEAD CONNECTOR PRESSURE HOUSING",
    ],
    "[366] TREES - CSUR": [
        "TREE CHRISTMAS DUAL MASTER VALVE",
        "TREE WELLHEAD SPOOL ASSEMBLY",
        "TREE MASTER VALVE BODY DUCTILE",
        "TREE FLOWLINE SWABLINE COUPLING",
        "TREE BALL VALVE FULL BORE GATE",
        "TREE CHOKE VALVE POSITIONING UNIT",
        "TREE XMAS SECONDARY SAFETY DEVICE",
        "TREE WING VALVE ISOLATION BLOCK",
        "TREE CASINGHEAD ADAPTER FLANGE PLATE",
        "TREE TUBING HEAD UNION COUPLING",
    ],
    "[367] TUBING COMPLETIONS - CSUR": [
        "TUBING COMPLETION PACKER MANDREL JOINT",
        "TUBING LATCH MECHANICAL PROFILE SETTER",
        "TUBING HANGER SLIP ASSEMBLY DOGS",
        "TUBING CROSS OVER COUPLING SPOOL",
        "TUBING SWAGE STUD ADAPTER SEAT",
        "TUBING SEATING NIPPLE BALL CATCHUP",
        "TUBING SCREEN LINER SLOTTED JOINT",
        "TUBING HANGER LOCK RING RETENTION",
        "TUBING EXPANSION COUPLING FLEXIBLE",
        "TUBING CONNECTOR PROFILED POLISHED BORE",
    ],
    "[368] VALVES - CSUR": [
        "VALVE CHECK CARTRIDGE POPPET ASSEMBLY",
        "VALVE GATE SLIDING DISC MECHANISM",
        "VALVE BALL FLOATING SPHERE DESIGN",
        "VALVE BUTTERFLY DISC SWINGING WING",
        "VALVE GLOBE PLUG POINTED STEM",
        "VALVE STOP CHECK FLOW DIRECTION",
        "VALVE NEEDLE RESTRICTED ORIFICE OUTLET",
        "VALVE THREE WAY MANIFOLD BLOCK",
        "VALVE PILOT OPERATED PRESSURE RELIEF",
        "VALVE SOLENOID CONTROLLED CARTRIDGE",
    ],
    "[369] WELLHEADS - CSUR": [
        "WELLHEAD CASING HEAD SPOOL CONNECTION",
        "WELLHEAD TUBING HEAD UNION ADAPTER",
        "WELLHEAD HANGAR LANDING RING ASSEMBLY",
        "WELLHEAD MASTER VALVE BODY CASTING",
        "WELLHEAD SEAL BORE BUSHING INSERT",
        "WELLHEAD PRESSURE HOUSING STACK FLANGE",
        "WELLHEAD GUIDE BUSHING CENTERING GUIDE",
        "WELLHEAD CONNECTOR PROFILED BORE RING",
        "WELLHEAD CASINGHEAD DRIVE BUSHING WEAR",
        "WELLHEAD TUBING HANGER LATCH RETAINER",
    ],
    "[370] FRAC AND FLOWBACK EQUIPMENT": [
        "FRAC PLUG COMPOSITE DISSOLVABLE",
        "FRAC SLEEVE BALL DROP ACTIVATED",
        "FRAC BALL SEALING SPHERE PROFILE",
        "FRAC PACKER ISOLATION SETTING TOOL",
        "FRAC VALVE MECHANICAL ACTIVATION DEVICE",
        "FRAC DIVERTER FLOW PATH CONTROLLER",
        "FRAC SPACER FLUID SEPARATION LAYER",
        "FRAC BRIDGE PLUG REMOVABLE SETTING DEPTH",
        "FRAC EQUALIZER PORT TIMING RESTRICTION",
        "FRAC SYSTEM COMPLETION ISOLATION ASSEMBLY",
    ],
    "[375] TOOLS - CSUR": [
        "TOOL SETTING SLIPS CONICAL WEDGE",
        "TOOL RUNNING COUPLING PULL CONNECTOR",
        "TOOL LATCHING DOOR MECHANICAL PROFILE",
        "TOOL PULLING FISH EAR GRAPPLE",
        "TOOL CIRCULATION SIDE POCKET MANDREL",
        "TOOL ORIENTING GUIDE LANDING NIPPLE",
        "TOOL WASH PIPE BYPASS CHAMBER",
        "TOOL LOCK RING RETENTION PAWL",
        "TOOL DISCONNECT MECHANICAL RELEASE SLEEVE",
        "TOOL PRESSURE TEST GAUGE ADAPTER",
    ],
    "[379] ANALYZERS": [
        "ANALYZER FLUID PROPERTY MEASUREMENT",
        "ANALYZER GAS CHROMATOGRAPH SEPARATOR",
        "ANALYZER WATER CONTENT MOISTURE METER",
        "ANALYZER OIL QUALITY VISCOSITY TEST",
        "ANALYZER PRESSURE TRANSDUCER SENSOR",
        "ANALYZER TEMPERATURE RESISTANCE THERMAL",
        "ANALYZER DENSITY HYDROCARBON FLUID",
        "ANALYZER CORROSION RATE MONITORING",
        "ANALYZER SAMPLE COLLECTION CARTRIDGE",
        "ANALYZER WIRELESS TRANSMISSION DEVICE",
    ],
    "[400] CHART RECORDERS": [
        "CHART RECORDER PRESSURE MECHANICAL",
        "CHART RECORDER TEMPERATURE THERMAL PEN",
        "CHART RECORDER FLOW RATE MECHANICAL",
        "CHART RECORDER DUAL TRACE PEN ARM",
        "CHART RECORDER CIRCULAR DRUM MECHANISM",
        "CHART RECORDER STRIP PAPER MOTOR DRIVE",
        "CHART RECORDER ANALOG DIAL GAUGE",
        "CHART RECORDER PNEUMATIC TRANSMISSION",
        "CHART RECORDER INK PEN CARTRIDGE",
        "CHART RECORDER CALIBRATION ADJUSTMENT SCREW",
    ],
}

# Generate part numbers with uniqueness check
used_part_numbers = set()

def generate_unique_part_number():
    """Generate an 8-digit numeric part number, ensuring uniqueness."""
    while True:
        part_num = str(random.randint(10000000, 99999999))
        if part_num not in used_part_numbers:
            used_part_numbers.add(part_num)
            return part_num

def generate_description(pf):
    """Generate a realistic part description for the given PF."""
    vocab = DESCRIPTION_VOCAB.get(pf, ["EQUIPMENT COMPONENT ASSEMBLY"])
    base_desc = random.choice(vocab)

    # Occasionally add variations
    variations = [
        base_desc,
        base_desc + " STANDARD",
        base_desc + " PREMIUM",
        base_desc + " OIL GRADE",
        base_desc + " ALLOY STEEL",
        base_desc + " STAINLESS FINISH",
    ]
    return random.choice(variations)

def generate_records():
    """Generate all 10,000 records across the 15 PFs."""
    records = []
    pf_counts = defaultdict(int)

    total_records = 10000
    records_per_pf = total_records // len(ASSIGNED_PFS)

    for pf_idx, pf in enumerate(ASSIGNED_PFS):
        # Distribute records, handling remainder
        if pf_idx < total_records % len(ASSIGNED_PFS):
            num_records = records_per_pf + 1
        else:
            num_records = records_per_pf

        # Seed for this PF for reproducibility
        random.seed(200 + pf_idx)

        # Get available technologies for this PF
        techs = pf_to_tech.get(pf, [])
        if not techs:
            print(f"WARNING: No technologies for {pf}")
            continue

        for _ in range(num_records):
            # Sample technology
            tech = random.choice(techs)

            # Sample brand from technology
            brands = tech_to_brand.get(tech, [])
            if not brands:
                print(f"WARNING: No brands for technology {tech}")
                continue
            brand = random.choice(brands)

            # Sample toolname from brand
            tools = brand_to_tool.get(brand, [])
            toolname = random.choice(tools) if tools else ""

            # Generate part number and description
            part_number = generate_unique_part_number()
            description = generate_description(pf)

            records.append({
                'Part Number': part_number,
                'Part Description': description,
                'PRODUCT_FAMILY_NAME': pf,
                'TECHNOLOGY_NAME': tech,
                'BRAND_NAME': brand,
                'TOOLNAME': toolname,
                'BUSINESS_LINE_NAME': 'SYNTHETIC'
            })

            pf_counts[pf] += 1

    return records, pf_counts

# Generate all records
print("Generating 10,000 synthetic part records...")
records, pf_counts = generate_records()

# Write to CSV
output_path = '/Users/yemane/Code/model-delta/synthesis/synthesized_part_02.csv'
fieldnames = [
    'Part Number',
    'Part Description',
    'PRODUCT_FAMILY_NAME',
    'TECHNOLOGY_NAME',
    'BRAND_NAME',
    'TOOLNAME',
    'BUSINESS_LINE_NAME'
]

with open(output_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)

# Print summary
print(f"\n✓ Generated {len(records)} total records")
print(f"✓ Saved to {output_path}")
print(f"\nRecords per PF:")
for pf in ASSIGNED_PFS:
    count = pf_counts.get(pf, 0)
    status = "✓" if count > 0 else "✗"
    print(f"  {status} {pf}: {count} records")

# Check for missing PFs
missing = [pf for pf in ASSIGNED_PFS if pf_counts.get(pf, 0) == 0]
if missing:
    print(f"\n⚠ {len(missing)} PFs with 0 records:")
    for pf in missing:
        print(f"    - {pf}")
else:
    print(f"\n✓ All {len(ASSIGNED_PFS)} PFs have records")

# Verify CSV integrity
print(f"\nVerifying output CSV...")
with open(output_path, 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print(f"  Rows in CSV: {len(rows)}")
    print(f"  Columns: {list(rows[0].keys()) if rows else 'N/A'}")

    # Spot check a few records
    if rows:
        print(f"\nSpot check (first 3 records):")
        for i, row in enumerate(rows[:3]):
            print(f"  {i+1}. PN={row['Part Number']}, PF={row['PRODUCT_FAMILY_NAME']}, TECH={row['TECHNOLOGY_NAME']}")
