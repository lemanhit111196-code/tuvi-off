# Schema kho dữ liệu 518.400 lá số Tử Vi

## 1. SQLite – bảng `charts` (compact index)

- File: `data/tuvi_518400.sqlite`
- Số dòng: **518.400**
- Số cột: **40**

Tất cả cột là số nguyên (trừ `chart_id`). Toạ độ cung 0=Dần..11=Sửu; giờ 0=Tý..11=Hợi.

| Cột | Ý nghĩa |
|---|---|
| `chart_id` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `year_index` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `year_can_index` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `year_chi_index` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `gender_code` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `lunar_month` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `lunar_day` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `hour_index` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `duong_nam` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `am_nu` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `vong_thuan` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `hoa_thuan` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `menh_cung` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `than_cung` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `cuc_so` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `menh_can_index` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `menh_chi_index` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `than_can_index` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `than_chi_index` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `lai_nhan_cung` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `tu_vi_cung` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_tu_vi` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_thien_co` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_thai_duong` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_vu_khuc` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_thien_dong` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_liem_trinh` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_thien_phu` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_thai_am` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_tham_lang` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_cu_mon` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_thien_tuong` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_thien_luong` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_that_sat` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_pha_quan` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_van_xuong` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_van_khuc` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_loc_ton` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_hoa_tinh` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |
| `pos_linh_tinh` | vị trí/giá trị số (tra tên bằng `metadata/dimensions.json`) |

## 2. CSV nén – đầy đủ chi tiết (kho partition)

Gồm 5 file `data/csv_by_cuc/tuvi_by_cuc_{{2..6}}.csv.gz`, chia theo `cuc_so`; mỗi file 103.680 dòng.

- Số cột: **156**

- Gồm metadata, **12 cột `cung_label_*`** (tên cung theo vị trí địa bàn), và toàn bộ cột `pos_*`.

- Tên cung dùng chuẩn **thuận chiều kim đồng hồ từ Mệnh** trong `docs/nguon-algorithm.md`.

### 2.1 Bảng cột đầy đủ

- `chart_id`
- `year_index`
- `year_can_index`
- `year_chi_index`
- `gender_code`
- `gender_label`
- `lunar_month`
- `lunar_day`
- `hour_index`
- `hour_label`
- `duong_nam`
- `am_nu`
- `vong_thuan`
- `hoa_thuan`
- `menh_cung`
- `menh_cung_label`
- `than_cung`
- `than_cung_label`
- `cuc_so`
- `cuc_hanh`
- `cuc`
- `menh_can_index`
- `menh_chi_index`
- `than_can_index`
- `than_chi_index`
- `lai_nhan_cung`
- `tu_vi_cung`
- `group_cuc`
- `group_tu_vi`
- `group_menh`
- `group_than`
- `group_nam`
- `group_gio`
- `group_thang`
- `group_gioi_tinh`
- `cung_label_0`
- `cung_label_1`
- `cung_label_2`
- `cung_label_3`
- `cung_label_4`
- `cung_label_5`
- `cung_label_6`
- `cung_label_7`
- `cung_label_8`
- `cung_label_9`
- `cung_label_10`
- `cung_label_11`
- `pos_tu_vi`
- `pos_thien_co`
- `pos_thai_duong`
- `pos_vu_khuc`
- `pos_thien_dong`
- `pos_liem_trinh`
- `pos_thien_phu`
- `pos_thai_am`
- `pos_tham_lang`
- `pos_cu_mon`
- `pos_thien_tuong`
- `pos_thien_luong`
- `pos_that_sat`
- `pos_pha_quan`
- `pos_truong_sinh`
- `pos_duong`
- `pos_thai`
- `pos_tuyet`
- `pos_mo`
- `pos_tu`
- `pos_benh`
- `pos_suy`
- `pos_de_vuong`
- `pos_lam_quan`
- `pos_quan_doi`
- `pos_moc_duc`
- `pos_thai_tue`
- `pos_thieu_duong`
- `pos_tang_mon`
- `pos_thieu_am`
- `pos_quan_phu`
- `pos_tu_phu`
- `pos_tue_pha`
- `pos_long_duc`
- `pos_bach_ho`
- `pos_phuc_duc`
- `pos_dieu_khach`
- `pos_truc_phu`
- `pos_loc_ton`
- `pos_bac_sy`
- `pos_luc_sy`
- `pos_thanh_long`
- `pos_tieu_hao`
- `pos_tuong_quan`
- `pos_tau_thu`
- `pos_phi_liem`
- `pos_hy_than`
- `pos_benh_phu`
- `pos_dai_hao`
- `pos_phuc_binh`
- `pos_thien_quang`
- `pos_thien_phuc`
- `pos_luu_ha`
- `pos_thien_tru`
- `pos_quang_an_can`
- `pos_kinh_duong`
- `pos_da_la`
- `pos_thien_khoi`
- `pos_thien_viet`
- `pos_long_tri`
- `pos_phuong_cac`
- `pos_giai_than`
- `pos_thien_khoc`
- `pos_thien_hu`
- `pos_thien_duc`
- `pos_nguyet_duc`
- `pos_hong_loan`
- `pos_thien_hy`
- `pos_co_than`
- `pos_qua_tu`
- `pos_dao_hoa`
- `pos_thien_ma`
- `pos_kiep_sat`
- `pos_hoa_cai`
- `pos_pha_toai`
- `pos_thien_khong`
- `pos_ta_phu`
- `pos_huu_bat`
- `pos_thien_hinh`
- `pos_thien_dieu`
- `pos_thien_y`
- `pos_thien_giai`
- `pos_dia_giai`
- `pos_van_xuong`
- `pos_van_khuc`
- `pos_thai_phu`
- `pos_phong_cao`
- `pos_dia_khong`
- `pos_dia_kiep`
- `pos_hoa_tinh`
- `pos_linh_tinh`
- `pos_tam_thai`
- `pos_bat_toa`
- `pos_an_quang`
- `pos_thien_quy`
- `pos_tuan`
- `pos_triet_1`
- `pos_triet_2`
- `pos_thien_la`
- `pos_dia_vong`
- `pos_thien_thuong`
- `pos_thien_su`
- `pos_dau_quan`
- `pos_thien_tai`
- `pos_thien_tho`
- `pos_hoa_loc`
- `pos_hoa_quyen`
- `pos_hoa_khoa`
- `pos_hoa_ky`
