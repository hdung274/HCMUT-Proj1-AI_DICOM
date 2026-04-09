import numpy as np
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

if not hasattr(np, 'int'): np.int = int
if not hasattr(np, 'float'): np.float = float
if not hasattr(np, 'bool'): np.bool = bool

import os
import pydicom
import pylidc as pl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def get_hu_pixels(ds):
    intercept = getattr(ds, 'RescaleIntercept', 0)
    slope = getattr(ds, 'RescaleSlope', 1)
    return ds.pixel_array.astype(np.float32) * slope + intercept

def apply_windowing(image_hu, window_center, window_width):
    img_min = window_center - window_width // 2
    img_max = window_center + window_width // 2
    windowed = np.clip(image_hu, img_min, img_max)
    return ((windowed - img_min) / (img_max - img_min) * 255).astype(np.uint8)

def extract_lung_mask_basic(image_hu):
    lung_mask = np.where((image_hu < -300) & (image_hu > -1000), 1, 0)
    return lung_mask.astype(np.uint8)

def get_target_dicoms(data_folder, target_id="LIDC-IDRI-0001"):
    scan = pl.query(pl.Scan).filter(pl.Scan.patient_id == target_id).first()
    if not scan: return None, None
    nods = scan.cluster_annotations()
    if not nods: return None, None
    
    uid = scan.series_instance_uid
    dicoms = []
    for root, _, files in os.walk(data_folder):
        for file in files:
            if file.lower().endswith('.dcm'):
                path = os.path.join(root, file)
                try:
                    ds = pydicom.dcmread(path, stop_before_pixels=True)
                    if ds.SeriesInstanceUID == uid:
                        dicoms.append((float(ds.ImagePositionPatient[2]), path))
                except: pass
                
    dicoms.sort(key=lambda x: x[0])
    sorted_dicoms = []
    for _, path in dicoms:
        sorted_dicoms.append(pydicom.dcmread(path))
        
    return sorted_dicoms, nods
