import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils import get_target_dicoms, get_hu_pixels, apply_windowing, extract_lung_mask_basic, DATA_FOLDER, OUTPUT_DIR

def run(target_id):
    patient_dir = os.path.join(OUTPUT_DIR, target_id)
    os.makedirs(patient_dir, exist_ok=True)
    print(f"  [BƯỚC 2] Xác thực tọa độ Ground Truth (Red Spot)")
    
    sorted_dicoms, nods = get_target_dicoms(DATA_FOLDER, target_id)
    ann = nods[0][0]
    mask_gt_small = ann.boolean_mask()
    bbox = ann.bbox()
    mid_z_local = mask_gt_small.shape[2] // 2
    global_z = bbox[2].start + mid_z_local
    
    target_ds = sorted_dicoms[global_z]
    hu_img = get_hu_pixels(target_ds)
    lung_img = apply_windowing(hu_img, -600, 1500)
    lung_mask = extract_lung_mask_basic(hu_img)
    clean_lung = lung_img * lung_mask
    
    gt_slice = np.zeros((target_ds.Rows, target_ds.Columns), dtype=np.uint8)
    gt_slice[bbox[0], bbox[1]] = mask_gt_small[:, :, mid_z_local]
    
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.imshow(clean_lung, cmap='gray')
    plt.title("Hình ảnh đã được xử lí (Nền X-quang đen)")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(clean_lung, cmap='gray')
    red_overlay = np.ma.masked_where(gt_slice == 0, gt_slice)
    plt.imshow(red_overlay, cmap='Reds', vmin=0, vmax=1, alpha=0.8)
    plt.title("Ánh xạ Red Spot (Tọa độ y khoa gốc)")
    plt.axis('off')

    plt.tight_layout()
    out_path = os.path.join(patient_dir, "2_Doctor_RedSpot.jpg")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"       ✅ Đã ánh xạ tọa độ khối u tại {out_path}")

if __name__ == "__main__":
    run("LIDC-IDRI-0001")
