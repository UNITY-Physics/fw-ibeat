#!/usr/bin/env python
"""The run script."""
import logging
import subprocess
from shared.utils.curate_output import demo

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

OUT_DIR = ("/flywheel/v0/output")

def main(context: GearToolkitContext) -> None:

    input = gear_context.get_input_path("input")
    t2 = gear_context.get_input_path("t2")
    demographics = demo (context)


    # Extract parameters
    t1 = input
    t2 = t2
    age = demographics['age']
    sub_name = demographics['subject_label']


    # Build command
    cmd = [
        "/usr/local/InfantPipeline/bin/iBEAT",
        "--t1", t1,
        "--t2", t2,
        "--age", age,
        "--out_dir", str(OUT_DIR)
    ]

    print("Running command:", " ".join(cmd))

    # Run iBEAT
    subprocess.run(cmd, check=True)

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)
