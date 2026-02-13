# Pull Request (Merge Request) Template

## 1. Mục tiêu PR
- (Mô tả ngắn gọn mục tiêu của PR này, ví dụ: Hoàn thiện chức năng quản lý user, phân quyền, xác thực, ...)

## 2. Nội dung thay đổi chính
- [ ] ...
- [ ] ...
- [ ] ...

## 3. Chưa hoàn thành / Lưu ý
- [ ] ...
- [ ] ...

---

## ✅ Checklist Review PR

### Code/Feature
- [ ] Đã kiểm tra toàn bộ chức năng chính hoạt động đúng
- [ ] Đã việt hóa toàn bộ UI/UX, toast, error, label role/quyền
- [ ] Đã kiểm tra đồng bộ dữ liệu FE/BE sau mọi thao tác CRUD
- [ ] Đã bảo vệ API nhạy cảm bằng JWT, phân quyền
- [ ] Đã kiểm tra UI/UX popup xác nhận action nguy hiểm (nếu có)

### Security/Bảo mật
- [ ] Đã kiểm tra mã hóa mật khẩu, không lưu plain text
- [ ] Đã kiểm tra xác thực JWT, phân quyền backend
- [ ] Đã kiểm tra không hardcode secret/key trong codebase

### UI/UX
- [ ] Đã kiểm tra hiển thị avatar, label, badge, toast, error
- [ ] Đã kiểm tra responsive, không vỡ layout

### Khác
- [ ] Đã kiểm tra proxy /static và /api hoạt động đúng
- [ ] Đã kiểm tra log backend khi upload file, không lỗi ghi file
- [ ] Đã kiểm tra các lỗi thường gặp (403, 404, 401) đều có toast rõ ràng

---

**Reviewer lưu ý:**
- Nếu phát hiện bug/blocker, comment rõ vị trí và steps để tái hiện
- Nếu có đề xuất tối ưu, UX, bảo mật, vui lòng ghi chú cụ thể 