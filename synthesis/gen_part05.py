#!/usr/bin/env python3
"""
Synthetic part record generator for 15 oilfield equipment product families.
Generates 10,000 hierarchically-consistent part records from taxonomy.
"""

import json
import csv
import random
from pathlib import Path
from collections import defaultdict

# Configuration
SEED = 800
NUM_RECORDS = 10000
OUTPUT_CSV = Path("/Users/yemane/Code/model-delta/synthesis/synthesized_part_05.csv")
TAXONOMY_PATH = Path("/Users/yemane/Code/asset-taxonomy-classifier/ml_pipeline/constraints/taxonomy_tree.json")

# Target PFs (exactly 15)
TARGET_PFS = [
    "[971] WELLHEAD STD BORE SPECIFIC EQUIPMENT",
    "[972] WELLHEAD SYSTEM SPECIFIC EQUIPMENT",
    "[973] SRP SYSTEMS",
    "[974] CASING SPOOLS",
    "[975] SEALS - CSUR",
    "[976] CONNECTORS-CSUR",
    "[977] MUDLINE EQUIPMENT",
    "[978] WELL INTERVENTION SOLUTIONS",
    "[979] ELECTRO-HYDRAULIC CONTROL SYSTEM",
    "[984] SENTREE 5",
    "[985] SENTREE 6",
    "[986] DIRECT-HYDRAULIC CONTROL SYSTEM",
    "[987] SENTREE 3",
    "[988] SENTREE 7",
    "[996] FLOWLINE CONNECTION SYSTEMS",
]

# Rich vocabulary for part descriptions by PF type
DESC_VOCAB = {
    "[971] WELLHEAD STD BORE SPECIFIC EQUIPMENT": [
        "CASING SPOOL DOUBLE STUDDED 13-3/8IN",
        "TUBING HEAD FLANGED CONNECTION 7IN",
        "ADAPTER SPOOL WELLHEAD INTERFACE",
        "CASING FLANGE EXPANSION RING SET",
        "MASTER VALVE FULL PORT OPENING",
        "CONTROL VALVE PILOT OPERATED SUBSEA",
        "SPACER RING CASING SPOOL BORE",
        "SEAL BOWL CASING HEAD ASSEMBLY",
        "GUIDE RING CASING SPOOL GUIDE",
        "BONNET FLANGE CASING HEAD COVER",
    ],
    "[972] WELLHEAD SYSTEM SPECIFIC EQUIPMENT": [
        "WELLHEAD SYSTEM COMPACT HORIZONTAL",
        "PRODUCTION TREE DUAL BORE OUTLET",
        "CHRISTMAS TREE SUBSEA MOUNTING PAD",
        "WELLHEAD CONNECTOR QUICK DISCONNECT",
        "SYSTEM INTEGRATION MANIFOLD BLOCK",
        "PRODUCTION SYSTEM DUCTILE IRON BASE",
        "WELLHEAD ASSEMBLY SURFACE INSTALL",
        "EXPANSION JOINT PRESSURE RELIEF",
        "FLOWLINE HEADER INTEGRAL CHOKE",
        "SYSTEM TRANSITION SPOOL ADAPTER",
    ],
    "[973] SRP SYSTEMS": [
        "SUCKER ROD PUMP UNIT BEAM BALANCED",
        "SRP SYSTEM DOWNHOLE PLUNGER LIFT",
        "PUMP ASSEMBLY TUBING ANCHOR SLIPS",
        "ROD STRING GUIDE TUBE SUPPORT",
        "SURFACE UNIT GEAR REDUCER HOUSING",
        "PUMP JACK MOTOR COUPLING ASSEMBLY",
        "POLISH ROD GUIDE BEARING CARRIER",
        "CRANK ARM THROW WEIGHT COUNTERBALANCE",
        "WALKING BEAM SUPPORT EQUALIZER BAR",
        "DRIVE SHAFT UNIVERSAL JOINT COUPLING",
    ],
    "[974] CASING SPOOLS": [
        "CASING SPOOL SINGLE STUDDED 9-5/8IN",
        "CASING SPOOL DOUBLE STUDDED 13-3/8IN",
        "CASING SPOOL TRIPLE STACK ASSEMBLY",
        "SPOOL ADAPTER FLANGE CONNECTION RING",
        "CASING SPOOL BORE INSERT SLEEVE",
        "SPOOL LANDING RING LOCATING FEATURE",
        "CASING HEAD SPOOL OUTLET CONNECTION",
        "SPOOL BUSHING SEAL BORE GUIDE",
        "CASING SPOOL EXPANSION RING SEAL",
        "SPOOL CLOSURE FLANGE NUT SET",
    ],
    "[975] SEALS - CSUR": [
        "SEAL ASSEMBLY METAL TO METAL ANNULAR",
        "SEAL KIT ELASTOMER BACKUP RING SET",
        "DYNAMIC SEAL PACKING SLIPS ASSEMBLY",
        "CASING SEAL BONDED ELASTOMER RING",
        "SEAL INSERT GUIDE BORE BACKUP",
        "ELASTOMER SEAL STACK COMPRESSION SET",
        "METAL SEAL RING LEAKAGE CONTROL",
        "PACKING ELEMENT CONFINED SPACE SEAL",
        "SEAL ASSEMBLY SPHERICAL SEATING RING",
        "BACKUP RING TENSIONING SPRING LOADED",
    ],
    "[976] CONNECTORS-CSUR": [
        "CONNECTOR COLLET HYDRAULIC RELEASE",
        "QUICK CONNECTOR FLAT FACE COUPLING",
        "UMBILICAL CONNECTOR BULKHEAD FITTING",
        "CONNECTOR BODY SPLIT SLEEVE COUPLING",
        "CONNECTOR INTERFACE POPPET VALVE",
        "QUICK DISCONNECT PILOT OPERATED SEAL",
        "CONNECTOR ADAPTER REDUCED PORT SIZE",
        "MATING FACE CONNECTOR ALIGNMENT RING",
        "CONNECTOR PLUG BALL CHECK SYSTEM",
        "COUPLING HOUSING PRESSURE BALANCED",
    ],
    "[977] MUDLINE EQUIPMENT": [
        "MUDLINE SUSPENSION HANGER TIEBACK",
        "MUDLINE STRUCTURE CONDUCTOR PILE",
        "MUDLINE WELLHEAD BASE INTERFACE",
        "MUDLINE TEMPLATE GUIDE POST SYSTEM",
        "MUDLINE RISER CLAMP SUPPORT FRAME",
        "MUDLINE JUMPER INSTALLATION PALLET",
        "MUDLINE MANIFOLD INTEGRATED SPOOL",
        "MUDLINE TREE SUPPORT PILE DRIVER",
        "MUDLINE FLEX JOINT BEND LIMITER",
        "MUDLINE TEMPLATE PILE SLEEVE BORE",
    ],
    "[978] WELL INTERVENTION SOLUTIONS": [
        "WELL INTERVENTION RISER ADAPTER",
        "INTERVENTION TOOL SETTING ASSEMBLY",
        "WIRELINE ADAPTER TUBING HEAD SPOOL",
        "COILED TUBING CATWALK GUIDE PULLEY",
        "INTERVENTION LUBRICATOR SIDE OUTLET",
        "SNUBBING ASSEMBLY STRIPPER PACKER",
        "INTERVENTION WORK OVER HEAD FLANGE",
        "WINCH CABLE GUIDE TENSIONER PULLEY",
        "INTERVENTION DIVERTER CONTROL VALVE",
        "RISER COUPLING QUICK MATE CONNECTOR",
    ],
    "[979] ELECTRO-HYDRAULIC CONTROL SYSTEM": [
        "ELECTRO-HYDRAULIC UMBILICAL FLYING LEAD",
        "POWER MODULE TRANSFORMER SWITCH GEAR",
        "HYDRAULIC PUMP UNIT PRESSURE CONTROL",
        "ELECTRICAL INTERFACE JUNCTION BOX",
        "SOLENOID VALVE CARTRIDGE SPOOL TYPE",
        "PILOT PRESSURE ACCUMULATOR BLADDER",
        "ELECTRICAL CONNECTOR SUBSEA RATED",
        "CONTROL MODULE LOGIC PROCESSING UNIT",
        "POWER SUPPLY REDUNDANT SWITCHOVER",
        "HYDRAULIC HOSE UMBILICAL TERMINATION",
    ],
    "[984] SENTREE 5": [
        "SENTREE 5 TREE COMPACT HORIZONTAL",
        "SENTREE 5 PRODUCTION MASTER OUTLET",
        "SENTREE 5 CHOKE MODULE INTEGRATED",
        "SENTREE 5 CONTROL SYSTEM SUBSEA",
        "SENTREE 5 FLOWLINE CONNECTOR CLAMP",
        "SENTREE 5 TREE BORE INSERT SLEEVE",
        "SENTREE 5 PRODUCTION TREE DUAL BORE",
        "SENTREE 5 EXPANSION SPOOL ADAPTER",
        "SENTREE 5 MANIFOLD BLOCK COMPACT",
        "SENTREE 5 CHRISTMAS TREE PACKAGE",
    ],
    "[985] SENTREE 6": [
        "SENTREE 6 TREE DUAL BORE OUTLET",
        "SENTREE 6 PRODUCTION SYSTEM DESIGN",
        "SENTREE 6 INTEGRATED CHOKE SECTION",
        "SENTREE 6 SUBSEA MANIFOLD PACKAGE",
        "SENTREE 6 HORIZONTAL TREE MOUNTING",
        "SENTREE 6 FLOWLINE INTERFACE SPOOL",
        "SENTREE 6 CONTROL UMBILICAL JUMPER",
        "SENTREE 6 PRODUCTION TREE ASSEMBLY",
        "SENTREE 6 EXPANSION JOINT ASSEMBLY",
        "SENTREE 6 TREE SUPPORT BASE FRAME",
    ],
    "[986] DIRECT-HYDRAULIC CONTROL SYSTEM": [
        "CONTROL SYSTEM DIRECT HYDRAULIC POD",
        "HYDRAULIC PUMP UNIT DIRECT DRIVE",
        "PILOT SUPPLY REGULATOR DIRECT FEED",
        "HYDRAULIC MANIFOLD INTEGRATED DESIGN",
        "PRESSURE VESSEL ACCUMULATOR CHARGE",
        "HYDRAULIC FLUID COOLER HEAT EXCHANGER",
        "DIRECT CONTROL VALVE SOLENOID PILOT",
        "HYDRAULIC LINE MAIN PRESSURE CONDUIT",
        "FILTER UNIT RETURN LINE BYPASS",
        "CONTROL POD INTEGRATED VALVE STACK",
    ],
    "[987] SENTREE 3": [
        "SENTREE 3 TREE COMPACT DESIGN",
        "SENTREE 3 PRODUCTION OUTLET MANIFOLD",
        "SENTREE 3 INTEGRATED CHOKE ASSEMBLY",
        "SENTREE 3 SUBSEA TREE PACKAGE",
        "SENTREE 3 HORIZONTAL WELLHEAD TREE",
        "SENTREE 3 FLOWLINE CONNECTION BLOCK",
        "SENTREE 3 CONTROL SYSTEM INTERFACE",
        "SENTREE 3 EXPANSION SPOOL ADAPTER",
        "SENTREE 3 CHRISTMAS TREE ASSEMBLY",
        "SENTREE 3 MANIFOLD INTEGRATED DESIGN",
    ],
    "[988] SENTREE 7": [
        "SENTREE 7 TREE ADVANCED DESIGN",
        "SENTREE 7 PRODUCTION SYSTEM LAYOUT",
        "SENTREE 7 DUAL BORE MANIFOLD BLOCK",
        "SENTREE 7 INTEGRATED SUBSEA CONTROLS",
        "SENTREE 7 FLOWLINE INTERFACE PACKAGE",
        "SENTREE 7 HORIZONTAL TREE MOUNTING",
        "SENTREE 7 EXPANSION JOINT ASSEMBLY",
        "SENTREE 7 PRODUCTION TREE ASSEMBLY",
        "SENTREE 7 CHOKE MODULE INTEGRATED",
        "SENTREE 7 TREE SUPPORT STRUCTURE",
    ],
    "[996] FLOWLINE CONNECTION SYSTEMS": [
        "FLOWLINE CONNECTOR CLAMP HUB END",
        "FLOWLINE COUPLING QUICK DISCONNECT",
        "FLOWLINE CONNECTOR HALF COUPLING",
        "FLOWLINE JUMPER CONNECTOR ASSEMBLY",
        "FLOWLINE INTERFACE PLATE BOLTING",
        "FLOWLINE RISER CLAMP SUSPENSION",
        "FLOWLINE PIPE CONNECTOR THREAD TYPE",
        "FLOWLINE HOSE FERRULE COMPRESSION",
        "FLOWLINE CONNECTION SPOOL ADAPTER",
        "FLOWLINE FLEX JOINT PROTECTION",
    ],
}

def load_taxonomy():
    """Load and parse taxonomy_tree.json"""
    with open(TAXONOMY_PATH, 'r') as f:
        taxonomy = json.load(f)
    return taxonomy

def build_hierarchy(taxonomy):
    """
    Build hierarchical mappings from pre-computed taxonomy dicts:
    - pf_to_tech: PF → list of TECHs
    - tech_to_brand: TECH → list of BRANDs
    - brand_to_tool: BRAND → list of TOOLNAMEs
    """
    pf_to_tech = taxonomy.get("pf_to_tech", {})
    tech_to_brand = taxonomy.get("tech_to_brand", {})
    brand_to_tool = taxonomy.get("brand_to_tool", {})

    # Deduplicate tech lists (taxonomy has repeats)
    for pf in pf_to_tech:
        pf_to_tech[pf] = list(set(pf_to_tech[pf]))

    for tech in tech_to_brand:
        tech_to_brand[tech] = list(set(tech_to_brand[tech]))

    for brand in brand_to_tool:
        brand_to_tool[brand] = list(set(brand_to_tool[brand]))

    return pf_to_tech, tech_to_brand, brand_to_tool

def generate_part_number(used_numbers, seed_offset):
    """Generate unique 8-digit part number"""
    rng = random.Random(seed_offset)
    while True:
        part_num = str(rng.randint(10000000, 99999999))
        if part_num not in used_numbers:
            used_numbers.add(part_num)
            return part_num

def generate_description(pf, rng):
    """Generate realistic part description for PF"""
    vocab = DESC_VOCAB.get(pf, ["EQUIPMENT ASSEMBLY COMPONENT"])
    return rng.choice(vocab)

def generate_records(taxonomy, pf_to_tech, tech_to_brand, brand_to_tool):
    """Generate 10,000 synthetic records across 15 PFs"""
    records = []
    used_numbers = set()
    records_per_pf = NUM_RECORDS // len(TARGET_PFS)

    print(f"Generating {NUM_RECORDS} records across {len(TARGET_PFS)} PFs")
    print(f"Target: ~{records_per_pf} records per PF\n")

    for pf_idx, pf in enumerate(TARGET_PFS):
        rng = random.Random(SEED + pf_idx)
        pf_records = 0

        # Get valid techs for this PF
        valid_techs = pf_to_tech.get(pf, [])
        if not valid_techs:
            print(f"⚠️  {pf}: NO TECHS FOUND in taxonomy")
            continue

        for record_idx in range(records_per_pf):
            # Sample TECH from this PF
            tech = rng.choice(valid_techs)

            # Sample BRAND from this TECH
            valid_brands = tech_to_brand.get(tech, [])
            if not valid_brands:
                print(f"    {pf} → {tech}: NO BRANDS")
                continue
            brand = rng.choice(valid_brands)

            # Sample TOOLNAME from this BRAND
            valid_tools = brand_to_tool.get(brand, [])
            toolname = rng.choice(valid_tools) if valid_tools else ""

            # Generate Part Number and Description
            part_number = generate_part_number(used_numbers, SEED + pf_idx + record_idx)
            description = generate_description(pf, rng)

            record = {
                "Part Number": part_number,
                "Part Description": description,
                "PRODUCT_FAMILY_NAME": pf,
                "TECHNOLOGY_NAME": tech,
                "BRAND_NAME": brand,
                "TOOLNAME": toolname,
                "BUSINESS_LINE_NAME": "SYNTHETIC",
            }
            records.append(record)
            pf_records += 1

        print(f"  {pf}: {pf_records} records")

    return records

def write_csv(records, output_path):
    """Write records to CSV"""
    columns = [
        "Part Number",
        "Part Description",
        "PRODUCT_FAMILY_NAME",
        "TECHNOLOGY_NAME",
        "BRAND_NAME",
        "TOOLNAME",
        "BUSINESS_LINE_NAME",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)

    print(f"\n✓ Written {len(records)} records to {output_path}")
    return len(records)

def main():
    print("=" * 70)
    print("SYNTHETIC PART RECORD GENERATOR")
    print("=" * 70)
    print(f"Seed: {SEED}")
    print(f"Target records: {NUM_RECORDS}")
    print(f"Target PFs: {len(TARGET_PFS)}")
    print(f"Output: {OUTPUT_CSV}\n")

    # Load taxonomy
    print("Loading taxonomy_tree.json...")
    taxonomy = load_taxonomy()
    print(f"Taxonomy loaded: {len(taxonomy.get('pf_allowed', []))} PFs")

    # Build hierarchy
    print("Building hierarchy mappings...")
    pf_to_tech, tech_to_brand, brand_to_tool = build_hierarchy(taxonomy)
    print(f"  pf_to_tech: {len(pf_to_tech)} mappings")
    print(f"  tech_to_brand: {len(tech_to_brand)} mappings")
    print(f"  brand_to_tool: {len(brand_to_tool)} mappings\n")

    # Generate records
    print("Generating synthetic records...")
    records = generate_records(taxonomy, pf_to_tech, tech_to_brand, brand_to_tool)

    # Write CSV
    print("\nWriting to CSV...")
    row_count = write_csv(records, OUTPUT_CSV)

    # Verify
    print("\n" + "=" * 70)
    print("VERIFICATION REPORT")
    print("=" * 70)
    print(f"Total records written: {row_count}")

    # Count by PF
    pf_counts = defaultdict(int)
    for record in records:
        pf_counts[record["PRODUCT_FAMILY_NAME"]] += 1

    print(f"Unique PFs: {len(pf_counts)}")
    for pf in sorted(pf_counts.keys()):
        count = pf_counts[pf]
        print(f"  {pf}: {count}")

    # Check for empty PFs
    empty_pfs = [pf for pf in TARGET_PFS if pf not in pf_counts]
    if empty_pfs:
        print(f"\n⚠️  EMPTY PFs ({len(empty_pfs)}):")
        for pf in empty_pfs:
            print(f"  - {pf}")
    else:
        print(f"\n✓ All {len(TARGET_PFS)} target PFs have records")

    # Sample validation
    if records:
        print(f"\nSample records:")
        for i in range(min(3, len(records))):
            r = records[i]
            print(f"  [{i}] {r['Part Number']} | {r['Part Description'][:40]:40s} | {r['TECHNOLOGY_NAME']}")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)

if __name__ == "__main__":
    main()
