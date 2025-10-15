#!/usr/bin/env python
"""Parser for demographics and other metadata."""
import logging
import pandas as pd
import subprocess
from pathlib import Path

WORK_DIR=Path("/Users/nbourke/GD/atom/unity/fw-gears/fw-iBEAT/ibeat2-0.1.1-68edf10819decb5e72ca2248/work")
OUT_DIR=Path("/Users/nbourke/GD/atom/unity/fw-gears/fw-iBEAT/ibeat2-0.1.1-68edf10819decb5e72ca2248/output")

log = logging.getLogger(__name__)


def get_tissue_volume(tissue_file, lower, upper):
    """Run fslstats and return volume in mm³."""
    try:
        result = subprocess.run([
            "fslstats",
            str(tissue_file),
            "-l", str(lower),
            "-u", str(upper),
            "-V"
        ], capture_output=True, text=True, check=True)
        
        # fslstats -V returns: "voxel_count volume_mm3"
        return float(result.stdout.split()[1])
    except (subprocess.CalledProcessError, IndexError, ValueError) as e:
        log.error(f"Failed to get tissue volume for {tissue_file}: {e}")
        raise


def housekeeping():
    """Process tissue volumes and save measurements."""
    
    acq = "t2"
    subject = "sub-01"
    session = "ses-01"

    tissue_file = WORK_DIR / "T2-iso-skullstripped-tissue.nii.gz"
    subcortical_file = WORK_DIR / "T2-iso-skullstripped-subcortical-segmentation.nii.gz"

    # Check if tissue file exists
    if not tissue_file.exists():
        log.error(f"Tissue file not found: {tissue_file}")
        raise FileNotFoundError(f"Required file missing: {tissue_file}")
    
    log.info("Calculating tissue volumes...")
    
    # Get tissue volumes
    csf_vol = get_tissue_volume(tissue_file, 0.5, 1.5)
    gm_vol = get_tissue_volume(tissue_file, 1.5, 2.5)
    wm_vol = get_tissue_volume(tissue_file, 2.5, 3.5)

    # Add subcortical GM volume if file exists
    if subcortical_file.exists():
        subcortical_gm_vol = get_tissue_volume(subcortical_file, 0.5, 13.5)
        lh_thalamus_vol = get_tissue_volume(subcortical_file, 1.5, 2.5)
        lh_caudate_vol = get_tissue_volume(subcortical_file, 2.5, 3.5)
        lh_putamen_vol = get_tissue_volume(subcortical_file, 3.5, 4.5)
        lh_globus_pallidus_vol = get_tissue_volume(subcortical_file, 4.5, 5.5)
        lh_hippocampus_vol = get_tissue_volume(subcortical_file, 5.5, 6.5)
        lh_amygdala_vol = get_tissue_volume(subcortical_file, 6.5, 7.5)
        rh_thalamus_vol = get_tissue_volume(subcortical_file, 7.5, 8.5)
        rh_caudate_vol = get_tissue_volume(subcortical_file, 8.5, 9.5)
        rh_putamen_vol = get_tissue_volume(subcortical_file, 9.5, 10.5)
        rh_globus_pallidus_vol = get_tissue_volume(subcortical_file, 10.5, 11.5)
        rh_hippocampus_vol = get_tissue_volume(subcortical_file, 11.5, 12.5)
        rh_amygdala_vol = get_tissue_volume(subcortical_file, 12.5, 13.5)


    
    # Create or append to CSV
    csv_path = OUT_DIR / f"sub-{subject}_ses-{session}_tissue_measurements.csv"
    data = {
        'subject': [subject],
        'session': [session],
        'acquisition': [acq],
        'csf_volume_mm3': [csf_vol],
        'gm_volume_mm3': [gm_vol],
        'wm_volume_mm3': [wm_vol],
        'subcortical_gm_volume_mm3': [subcortical_gm_vol],
        'lh_caudate_volume_mm3': [lh_caudate_vol],
        'lh_putamen_volume_mm3': [lh_putamen_vol],
        'lh_globus_pallidus_volume_mm3': [lh_globus_pallidus_vol],
        'lh_thalamus_volume_mm3': [lh_thalamus_vol],
        'lh_hippocampus_volume_mm3': [lh_hippocampus_vol],
        'lh_amygdala_volume_mm3': [lh_amygdala_vol],
        'rh_caudate_volume_mm3': [rh_caudate_vol],
        'rh_putamen_volume_mm3': [rh_putamen_vol],
        'rh_globus_pallidus_volume_mm3': [rh_globus_pallidus_vol],
        'rh_thalamus_volume_mm3': [rh_thalamus_vol],
        'rh_hippocampus_volume_mm3': [rh_hippocampus_vol],
        'rh_amygdala_volume_mm3': [rh_amygdala_vol],
        'subcortical_gm_volume_mm3': [subcortical_gm_vol]
    }
    
    df = pd.DataFrame(data)
    
    # Append or create CSV
    if csv_path.exists():
        df.to_csv(csv_path, mode='a', header=False, index=False)
        log.info(f"Appended measurements to {csv_path}")
    else:
        df.to_csv(csv_path, index=False)
        log.info(f"Created measurements file: {csv_path}")

# run 
housekeeping()