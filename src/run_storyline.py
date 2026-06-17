import os
import gc
import pylidc as pl
import concurrent.futures
import step1_preprocess
import step2_redspot
import step3_3d_scale
from utils import DATA_FOLDER, get_target_dicoms

def process_patient(args):
    idx, pid, total = args
    print(f"\n>>> ĐANG XỬ LÝ BỆNH NHÂN: {pid} [{idx}/{total}] <<<", flush=True)
    try:
        dicoms, nods = get_target_dicoms(DATA_FOLDER, pid)
        if not dicoms or not nods:
            return False
            
        step1_preprocess.run(pid, sorted_dicoms=dicoms, nods=nods)
        step2_redspot.run(pid, sorted_dicoms=dicoms, nods=nods)
        step3_3d_scale.run(pid, sorted_dicoms=dicoms, nods=nods)
        
        # Giải phóng memory bắt buộc
        del dicoms
        del nods
        gc.collect()
        
        return True
    except Exception as e:
        print(f"   ⚠️ Lỗi bỏ qua ca {pid}: {e}", flush=True)
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("THỰC THI HỆ THỐNG TIỀN XỬ LÝ ẢNH DICOM HÀNG LOẠT (BATCH PROCESSING)")
    print("="*50)
    
    scans = pl.query(pl.Scan).all()
    valid_pids = []
    
    print("Đang quét danh mục bệnh nhân trên ổ cứng (nhanh)...", flush=True)
    for scan in scans:
        if scan.patient_id not in valid_pids:
            # Tra cứu nhanh bằng đường dẫn ổ cứng thay vì load nén DICOM nặng
            path1 = os.path.join(DATA_FOLDER, 'LIDC-IDRI', scan.patient_id)
            path2 = os.path.join(DATA_FOLDER, scan.patient_id)
            
            if os.path.exists(path1) or os.path.exists(path2):
                valid_pids.append(scan.patient_id)
                # Dừng sau 20 mẫu để tiết kiệm thời gian (có thể tăng nếu cần)
                if len(valid_pids) == 20: 
                    break
                
    total_valid = len(valid_pids)
    print(f"\n🎯 Đã tìm thấy {total_valid} hồ sơ hợp lệ. Bắt đầu tiền xử lý Đa Luồng (Multithreading)...")
    
    args_list = [(idx+1, pid, total_valid) for idx, pid in enumerate(valid_pids)]
    
    # Sử dụng 4 luồng song song dựa trên 4 nhân CPU của i5-1135G7
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(process_patient, args_list))
        
    print("\n" + "="*50)
    print("✅ QUÁ TRÌNH KẾT XUẤT ĐÃ HOÀN TẤT!")
    print("Tất cả kết quả đã được lưu trữ trong thư mục 'output', phân loại theo từng ca bệnh.")
    print("Tệp .OBJ đã sẵn sàng để tích hợp vào báo cáo kỹ thuật.")
    print("="*50)
