<h1 align="center">Hệ Thống Xử Lý Ảnh Y Tế DICOM 🚀</h1>

<p align="center">
  <strong>Hệ thống Xử lý Tiền trạm Dữ liệu Y tế (CT Scans) & Trực quan hoá Đa chiều</strong><br>
  <em>(Đồ án 1 - Xử lý Khối u Phổi với chuẩn LIDC-IDRI)</em>
</p>

## 🖼️ Preview (Cấu trúc Đầu ra)
Dưới đây là chuỗi xử lý tự động của hệ thống đối với một hồ sơ bệnh nhân tiêu biểu (Ví dụ: `LIDC-IDRI-0001`). Hệ thống hoạt động theo dây chuyền tịnh tiến:

*(Lưu ý: Khi đẩy Source Code lên Github, hãy tự chụp và Upload 3 ảnh kết quả mẫu vào đây nhé!)*
- **Bước 1: Tiền Xử Lý (Cleaning)** `1_Z_Slice_Preprocessed.jpg`
- **Bước 2: Đối chiếu Chuyên gia (Ground Truth)** `2_Doctor_RedSpot.jpg`
- **Bước 3: Dựng Không Gian 3D (Object Rendering)** `3_Scale_3D_FullSize.obj`

---

## 🛠 Cấu trúc Mã Nguồn (Source Code)
Mã nguồn được thiết kế dưới cấu trúc Master Pipeline phân tách Module hóa:

- `src/utils.py`: Bộ thư viện dùng chung chứa cơ chế thu thập dữ liệu (DICOM loading), toán học lọc độ X-Quang (HU), Cửa sổ hóa (Windowing) và khử viền phổi.
- `src/step1_preprocess.py`: Tìm lát cắt Z chứa khối u từ Pylidc và tự động xả mỡ/xương.
- `src/step2_redspot.py`: Nhúng tọa độ y án bác sĩ đính kèm lên hình bằng phương thức Masking Đỏ chuẩn hóa.
- `src/step3_3d_scale.py`: Sử dụng thuật toán Marching Cubes, tạo lưới đa giác (Vertices/Faces) xuất thành `.obj` Không gian 3D nguyên khối mà không làm kẹt cấu hình máy.
- `src/run_storyline.py`: File Tổng Kịch Bản. Quét kho dữ liệu và thực thi theo dây chuyền Batch Processing cho hàng loạt bệnh nhân.

## ⚙️ Cài Đặt (Installation)
**1. Tải môi trường Python**
```bash
git clone https://github.com/hdung274/HCMUT-Proj1-AI_DICOM.git
cd HCMUT-Proj1-AI_DICOM
pip install -r requirements.txt
```

**2. Đẩy Dữ Liệu LIDC**
Sự chuẩn bị của Pipeline này yêu cầu CSDL `LIDC-IDRI`. Hãy bỏ DICOM data vào thư mục `/data/`. 

**3. Khởi chạy Dây chuyền:**
```bash
python src/run_storyline.py
```
*(Kết quả sẽ tự động được xả vào Root/output dựa trên từng ID bệnh nhân rành mạch)*
