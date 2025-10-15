#!/usr/bin/env python
"""The run script."""
import logging
import shutil
import subprocess
from pathlib import Path
from shared.utils.curate_output import demo
from utils.parser import housekeeping

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

WORK_DIR = Path("/flywheel/v0/work")
OUT_DIR = Path("/flywheel/v0/output")
if not WORK_DIR.exists():
    WORK_DIR.mkdir(parents=True, exist_ok=True)

def main(context: GearToolkitContext) -> None:

    # Extract parameters from gear context
    t1 = context.get_input_path("t1")
    t2 = context.get_input_path("input")

    # Get demographics
    demographics = demo(context)

    raw_age = demographics['age'].iloc[0]
    if raw_age is None:
        # maybe check context.config for a user-specified override?
        raw_age = context.config.get("age")

    try:
        age = int(raw_age)
    except (ValueError, TypeError):
        raise ValueError("Age must be an integer representing months.")
    
    # Newborn flag
    newborn = bool(context.config.get("newborn"))
    if newborn:
        print("Newborn option selected")

    # Build command
    cmd = [
        "/usr/local/InfantPipeline/bin/iBEAT",
        *(["--t1", t1] if t1 else []),
        *(["--t2", t2] if t2 else []),
        *(["--age", str(age)] if not newborn else []),
        *(["--newborn"] if newborn else []),
        "--out_dir", str(WORK_DIR),
    ]

    """
    Explanation of the conditional inclusion of --t1 argument:
    This expression evaluates to:
    1. ['--t1', t1_file] if t1_file is provided.
    2. [] (an empty list) if t1_file is None.
    
    The * (splat) operator unpacks the resulting list directly into the outer cmd list.
    """


    # Run iBEAT
    print("Running command:", " ".join(cmd))
    subprocess.run(cmd, check=True)


    # Handle outputs
    # Zip all output files
    subject = demographics['subject'].iloc[0]
    session = demographics['session'].iloc[0]
    zip_path = OUT_DIR / f"sub-{subject}_ses-{session}_iBEAT_outputs"
    shutil.make_archive(str(zip_path), 'zip', WORK_DIR)

    # Copy specific files with BIDS naming
    specific_files = [
        "T2-iso-skullstripped-tissue.nii.gz",
        "T2-iso-skullstripped-subcortical-segmentation.nii.gz",
        "T2-skullstripped.nii.gz",
        "T1-iso-skullstripped-tissue.nii.gz",
        "T1-iso-skullstripped-subcortical-segmentation.nii.gz",
        "T1-skullstripped.nii.gz"
    ]

    for filename in specific_files:
        source = WORK_DIR / filename
        if source.exists():
            # Keep the full filename as the description (minus .nii.gz)
            desc = filename.replace(".nii.gz", "")
            dest = OUT_DIR / f"sub-{subject}_ses-{session}_desc-{desc}.nii.gz"
            shutil.copy2(source, dest)
        else:
            print(f"Warning: {filename} not found in {WORK_DIR}")

    # Call the parser to handle derived metrics
    housekeeping(demographics)

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)
