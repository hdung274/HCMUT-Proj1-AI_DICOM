import os
import pylidc as pl
import step1_preprocess
import step2_redspot
import step3_3d_scale
from utils import DATA_FOLDER, get_target_dicoms

if __name__ == "__main__":
    print("\n" + "="*50)
    print("THỰC THI PIPELINE MLOPS HÀNG LOẠT (BATCH PROCESSING)")
    print("="*50)
    
    scans = pl.query(pl.Scan).all()
    valid_pids = []
    
    for scan in scans:
        if scan.patient_id not in valid_pids:
            dicoms, nods = get_target_dicoms(DATA_FOLDER, scan.patient_id)
            if dicoms and nods:
                valid_pids.append(scan.patient_id)
                # Dừng sau 20 mẫu để tiết kiệm thời gian (có thể tăng nếu cần)
                if len(valid_pids) == 20: 
                    break
                
    print(f"\n🎯 Đã tìm thấy {len(valid_pids)} hồ sơ hợp lệ. Bắt đầu quá trình tiền xử lý hàng loạt...")
    
    for idx, pid in enumerate(valid_pids):
        print(f"\n>>> ĐANG XỬ LÝ BỆNH NHÂN: {pid} [{idx+1}/{len(valid_pids)}] <<<")
        try:
            step1_preprocess.run(pid)
            step2_redspot.run(pid)
            step3_3d_scale.run(pid)
        except Exception as e:
            print(f"   ⚠️ Lỗi bỏ qua ca {pid}: {e}")
        
    print("\n" + "="*50)
    print("✅ QUÁ TRÌNH KẾT XUẤT ĐÃ HOÀN TẤT!")
    print("Tất cả kết quả đã được lưu trữ trong thư mục 'output', phân loại theo từng ca bệnh.")
    print("Tệp .OBJ đã sẵn sàng để tích hợp vào báo cáo kỹ thuật.")
    print("="*50)
