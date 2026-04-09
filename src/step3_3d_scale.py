import os
import numpy as np
from skimage import measure
from skimage.segmentation import clear_border
from utils import get_target_dicoms, DATA_FOLDER, OUTPUT_DIR

def run(target_id):
    patient_dir = os.path.join(OUTPUT_DIR, target_id)
    os.makedirs(patient_dir, exist_ok=True)
    print(f"  [BƯỚC 3] Trực quan hóa Không gian 3D (Định dạng OBJ)")
    
    sorted_dicoms, nods = get_target_dicoms(DATA_FOLDER, target_id)
    
    image = np.stack([s.pixel_array for s in sorted_dicoms])
    image = image.astype(np.int16)
    image[image <= -2000] = 0
    intercept = sorted_dicoms[0].RescaleIntercept
    slope = sorted_dicoms[0].RescaleSlope
    if slope != 1:
        image = (image.astype(np.float64) * slope).astype(np.int16)
    image += np.int16(intercept)
    
    lung_mask = np.where((image < -300) & (image > -1000), 1, 0)
    # Lọc khí ngoài màng phổi
    for i in range(lung_mask.shape[0]):
        lung_mask[i] = clear_border(lung_mask[i])
        
    nodule_vol = np.zeros_like(lung_mask, dtype=np.uint8)

    for nod_cluster in nods:
        mask_gt_small = nod_cluster[0].boolean_mask()
        bbox = nod_cluster[0].bbox()
        z_start, z_stop = bbox[2].start, bbox[2].stop
        y_start, y_stop = bbox[0].start, bbox[0].stop
        x_start, x_stop = bbox[1].start, bbox[1].stop
        try:
            nodule_vol[z_start:z_stop, y_start:y_stop, x_start:x_stop] = np.logical_or(
                nodule_vol[z_start:z_stop, y_start:y_stop, x_start:x_stop], 
                np.transpose(mask_gt_small, (2, 0, 1))
            )
        except: pass

    # Hệ số nén lưới 3D (Đổi 3 để đúc file siêu tốc và chống đơ PPT)
    shrink_factor = 3 
    lung_shrunk = lung_mask[::shrink_factor, ::shrink_factor, ::shrink_factor]
    nod_shrunk = nodule_vol[::shrink_factor, ::shrink_factor, ::shrink_factor]
    
    verts_lung, faces_lung, _, _ = measure.marching_cubes(lung_shrunk, 0.5)
    
    if np.sum(nod_shrunk) > 0:
        verts_nod, faces_nod, _, _ = measure.marching_cubes(nod_shrunk, 0.5)
    else:
        verts_nod = faces_nod = None

    # Thuật toán đúc thẳng mã nguồn file Object 3D thay vì render rườm rà qua Matplotlib
    obj_name = "3_Scale_3D_FullSize"
    obj_file = os.path.join(patient_dir, f"{obj_name}.obj")
    mtl_file = os.path.join(patient_dir, f"{obj_name}.mtl")
    
    with open(mtl_file, "w") as f:
        f.write("newmtl LungMaterial\n")
        f.write("Ka 0.1 0.7 0.8\nKd 0.1 0.7 0.8\nKs 0.0 0.0 0.0\nd 0.08\n\n") # Xanh lam trong suốt
        f.write("newmtl NoduleMaterial\n")
        f.write("Ka 1.0 0.0 0.0\nKd 1.0 0.0 0.0\nKs 0.2 0.2 0.2\nd 1.0\n") # Đỏ máu nguyên khối đặc
        
    with open(obj_file, "w") as f:
        f.write(f"mtllib {obj_name}.mtl\n")
        v_lung_ct = len(verts_lung)
        for v in verts_lung: f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        f.write("usemtl LungMaterial\n")
        for face in faces_lung: f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
            
        if verts_nod is not None:
            for v in verts_nod: f.write(f"v {v[0]} {v[1]} {v[2]}\n")
            f.write("usemtl NoduleMaterial\n")
            for face in faces_nod: 
                f.write(f"f {face[0]+1+v_lung_ct} {face[1]+1+v_lung_ct} {face[2]+1+v_lung_ct}\n")
                
    print(f"       ✅ Đã xuất mô hình 3D: {obj_file}")

if __name__ == "__main__":
    run("LIDC-IDRI-0001")
