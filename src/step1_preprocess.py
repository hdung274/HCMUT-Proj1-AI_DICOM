import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils import get_target_dicoms, get_hu_pixels, apply_windowing, extract_lung_mask_basic, DATA_FOLDER, OUTPUT_DIR

def run(target_id):
    patient_dir = os.path.join(OUTPUT_DIR, target_id)
    os.makedirs(patient_dir, exist_ok=True)
    print(f"  [BƯỚC 1] Tiền xử lý ảnh X-Quang 2D")
    
    sorted_dicoms, nods = get_target_dicoms(DATA_FOLDER, target_id)
    if not sorted_dicoms: return
    
    ann = nods[0][0] # Focus on primary nodule
    bbox = ann.bbox()
    mid_z_local = ann.boolean_mask().shape[2] // 2
    global_z = bbox[2].start + mid_z_local
    
    target_ds = sorted_dicoms[global_z]
    hu_img = get_hu_pixels(target_ds)
    lung_img = apply_windowing(hu_img, -600, 1500)
    lung_mask = extract_lung_mask_basic(hu_img)
    clean_lung = lung_img * lung_mask

    plt.figure(figsize=(16, 4))
    
    plt.subplot(1, 4, 1)
    plt.imshow(target_ds.pixel_array, cmap='gray')
    plt.title(f"1. Raw DICOM Array\n(Z_Index: {global_z})")
    plt.axis('off')

    plt.subplot(1, 4, 2)
    plt.imshow(lung_img, cmap='gray')
    plt.title("2. Lung Windowing\n(-600 HU, 1500 Width)")
    plt.axis('off')

    plt.subplot(1, 4, 3)
    plt.imshow(lung_mask, cmap='bone')
    plt.title("3. Lọc cấu trúc phổi\n(Thuật toán Threshold)")
    plt.axis('off')

    plt.subplot(1, 4, 4)
    plt.imshow(clean_lung, cmap='gray')
    plt.title("4. Giai đoạn Hoàn Thiện\n(Hình ảnh đã được xử lí)")
    plt.axis('off')

    plt.tight_layout()
    out_path = os.path.join(patient_dir, "1_Z_Slice_Preprocessed.jpg")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"       ✅ Đã xuất báo cáo tại {out_path}")

if __name__ == "__main__":
    run("LIDC-IDRI-0001")
