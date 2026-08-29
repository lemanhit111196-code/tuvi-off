# Nguồn thuật toán & các lựa chọn trường phái

## 1. Phạm vi dữ liệu

Kho dữ liệu sinh **518.400 biến thể lá số** theo công thức:

```
60 năm Can-Chi (60 hoa giáp)
× 2 giới tính (Nam / Nữ)
× 12 tháng âm lịch
× 12 giờ
× 30 ngày âm lịch
= 60 × 2 × 12 × 12 × 30 = 518 400
```

Mỗi biến thể được "an sao" đầy đủ bằng `scripts/tuvi_engine.py` rồi ghi vào:

- `data/tuvi_518400.sqlite` — bảng `charts` (compact index).
- `data/csv_by_cuc/tuvi_by_cuc_{2..6}.csv.gz` — chi tiết đầy đủ, chia theo Ngũ Hành Cục.
- `data/json_sample/tuvi_sample_5.json` — mẫu cấu trúc một lá số.

## 2. Quy ước toạ độ cung

Mọi vị trí cung trong dữ liệu được lưu bằng **chỉ số 0..11** theo chiều thuận
kim đồng hồ, bắt đầu từ Dần:

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|----|----|----|----|----|----|----|----|----|-----|-----|
| Dần | Mão | Thìn | Tỵ | Ngọ | Mùi | Thân | Dậu | Tuất | Hợi | Tý | Sửu |

Giờ được lưu bằng `hour_index` với Tý = 0, Sửu = 1, Dần = 2, ... Hợi = 11.

Bảng tra tên (Can, Chi, Cục, 12 cung, 60 hoa giáp, các vòng sao) nằm ở
`data/metadata/dimensions.json`.

## 3. Thuật toán an sao

### 3.1 Cung Mệnh & Cung Thân

- Tháng Giêng bắt đầu ở cung Dần.
- Đi thuận đến cung của tháng sinh → coi cung đó là giờ Tý.
- Đi **nghịch** đến giờ sinh → an Mệnh.
- Đi **thuận** đến giờ sinh → an Thân.

Công thức trong code:

```python
thang = (month - 1) % 12        # Dần(0) = tháng 1
menh  = (thang - hour) % 12
than  = (thang + hour) % 12
```

### 3.2 Ngũ Hành Cục

Tra bảng theo **Thiên can năm** và **cung an Mệnh** (bảng trong
tracuutuvi.com). 5 cục được gọi tắt bằng số:

| Số | Tên cục |
|----|---------|
| 2 | Thủy Nhị Cục |
| 3 | Mộc Tam Cục |
| 4 | Kim Tứ Cục |
| 5 | Thổ Ngũ Cục |
| 6 | Hỏa Lục Cục |

### 3.3 An sao Tử Vi (14 chính tinh)

Quy tắc "bù số" để chia hết ngày cho số cục:

1. Tìm `k` nhỏ nhất để `(day + k) % cuc_so == 0`.
2. `q = (day + k) / cuc_so`.
3. Từ cung Dần là 1, đếm thuận `q` cung.
4. Nếu `k` chẵn: tiến thêm `k` cung; nếu `k` lẻ: lùi `k` cung.

Sau đó an 14 chính tinh theo quan hệ cố định (vòng Tử Vi và vòng Thiên Phủ)
được mã hoá trong `scripts/tuvi_engine.py`.

### 3.4 Phụ tinh

Mỗi bảng phụ tinh được đưa vào code dưới dạng bảng tra tĩnh:

- Theo **Thiên can** của năm: Lộc Tồn, Kình Dương, Đà La, Quang Ấn, Đường Phù,
  Thiên Khôi, Thiên Việt, Thiên Quang, Thiên Phúc, Lưu Hà, Thiên Trù, Tứ Hoá.
- Theo **Địa chi** của năm: Long Trì, Phượng Các, Giải Thần, Thiên Khốc,
  Thiên Hư, Thiên Đức, Nguyệt Đức, Hồng Loan, Thiên Hỷ, Cô Thần, Quả Tú,
  Đào Hoa, Thiên Mã, Kiếp Sát, Hoa Cái, Phá Toái, Thiên Không.
- Theo **tháng** sinh: Tả Phù, Hữu Bật, Thiên Hình, Thiên Diêu, Thiên Y,
  Thiên Giải, Địa Giải.
- Theo **giờ** sinh: Văn Xương, Văn Khúc, Thai Phụ, Phong Cáo, Địa Không, Địa Kiếp.
- Theo **ngày**: Tam Thai, Bát Tọa, Ân Quang, Thiên Quý.
- Vòng **Trường Sinh**, vòng **Thái Tuế**, vòng **Lộc Tồn**.
- Hỏa Tinh / Linh Tinh.
- Tuần, Triệt; Thiên La, Địa Võng, Thiên Thương, Thiên Sứ, Đẩu Quân,
  Thiên Tài, Thiên Thọ.

Một số vòng phụ thuộc giới tính + âm dương can năm:

- **Dương Nam / Âm Nữ**: Vòng Trường Sinh và vòng Lộc Tồn đi **nghịch**;
  Hỏa Tinh đi **thuận**, Linh Tinh đi **nghịch**.
- **Âm Nam / Dương Nữ**: ngược lại.

## 4. Nguồn tham khảo chính

1. **Cách an sao Tử Vi** — `https://tracuutuvi.com/an-sao-tu-vi.html`
   (bảng Cục, quy tắc an Tử Vi, cung Mệnh/Thân).
2. **9 bước an sao lá số Tử Vi** — `https://phongthuynguyenhoang.com/an-sao-la-so-tu-vi/`
   (14 chính tinh, các bảng phụ tinh theo Can/Chi/Tháng/Giờ, Tuần/Triệt,
   vòng Trường Sinh, Thái Tuế, Lộc Tồn, Hỏa Linh).
3. **Sao Ân Quang, Thiên Quý** — `https://tuvi.cohoc.net/sao-an-quang-thien-quy-bo-sao-dep-nhat-trong-tu-vi-nid-6990.html`
   (quy tắc Quang Quý theo Văn Xương / Văn Khúc).
4. **Hỏa Linh & các trường phái** — `http://hoctuvi.blogspot.com/2014/02/ban-luan-ve-sao-hoa-tinh-linh-tinh-theo.html`
   và `http://hoctuvi.blogspot.com/2014/02/cach-sao-hoa-tinh-va-linh-tinh.html`.

## 5. Các lựa chọn trường phái cần chú ý

Dữ liệu dùng **Bắc phái bảng an sao phổ biến tại Việt Nam**, với vài lựa chọn
có trường phái khác nhau:

- **Hỏa/Linh Tinh cho nhóm tuổi Tỵ, Dậu, Sửu**: dùng **Hỏa khởi Mão,
  Linh khởi Tuất** (bảng Đắc Lộc). Một số trường phái dùng **Tuất / Mão**.
  Vì vậy các cột `pos_hoa_tinh`, `pos_linh_tinh` là theo lựa chọn này.
- **Tháng nhuận**: kho dữ liệu coi tháng giêng là tháng 1 và ngày 1..30 đơn thuần;
  nếu cần tháng nhuận, nên xử lý trước khi chọn `year_index/month/day`.
- **Giờ Tý**: quy ước giờ Tý = `hour_index 0`. Không quy đổi múi giờ / ngày
  giao tiếp trong dữ liệu này; ứng dụng nên xử lý phần chuyển đổi lịch Âm-Dương
  và giờ sinh trước khi dùng bảng.
- **Tứ Hoá**: dùng bảng Tứ Hoá truyền thống (`HOA_LOC_BY_CAN`, ...). Các tên
  sao nhận Hoá (VD can Giáp: Hóa Lộc = Liêm Trinh) nằm trong
  `data/metadata/dimensions.json`.

## 6. Tái tạo dữ liệu

```bash
python3 scripts/generate_warehouse.py
```

Toàn bộ file dữ liệu sinh ra (`.sqlite`, `.csv.gz`) được `.gitignore` để không
đẩy dữ liệu lớn lên Git; chỉ giữ scripts, docs, metadata nhỏ và file mẫu.
