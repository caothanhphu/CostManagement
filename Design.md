
Backend Python của bạn sẽ sử dụng thư viện `supabase-py` để tương tác với database PostgreSQL và dịch vụ Auth của Supabase. Hầu hết các API dưới đây (trừ đăng nhập/đăng ký) sẽ yêu cầu người dùng phải xác thực (thường thông qua JWT token do Supabase Auth cung cấp).

Dưới đây là danh sách các API được đề xuất, tuân theo nguyên tắc RESTful và hoạt động trên các mô hình dữ liệu đã thiết kế:

**Lưu ý:**

* `{user_id}`, `{account_id}`, `{category_id}`, etc. là các tham số đường dẫn (path parameters).
* Backend sẽ tự động lấy `user_id` từ thông tin xác thực (JWT token) thay vì truyền trực tiếp qua URL trong hầu hết các trường hợp để đảm bảo người dùng chỉ thao tác trên dữ liệu của chính họ. Danh sách dưới đây liệt kê các endpoint logic, việc triển khai cụ thể sẽ lấy `user_id` từ context xác thực.
* `(Auth Required)`: Đánh dấu các endpoint yêu cầu xác thực.

---

**I. Authentication & User Profile (Xác thực & Hồ sơ người dùng)**

* **`POST /auth/signup`**
    * **Mô tả:** Đăng ký người dùng mới thông qua Supabase Auth.
    * **Request Body:** `{ email, password, data (optional: full_name) }`
    * **Response:** Thông tin người dùng và session (bao gồm access token).
* **`POST /auth/login`**
    * **Mô tả:** Đăng nhập người dùng bằng email/password thông qua Supabase Auth.
    * **Request Body:** `{ email, password }`
    * **Response:** Thông tin người dùng và session (bao gồm access token).
* **`POST /auth/logout`** `(Auth Required)`
    * **Mô tả:** Đăng xuất người dùng (vô hiệu hóa session/token phía Supabase).
    * **Response:** Success/Failure message.
* **`GET /auth/user`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin người dùng đang đăng nhập từ Supabase Auth.
    * **Response:** Thông tin chi tiết người dùng (id, email, role, user_metadata,...).
* **`PUT /profile`** `(Auth Required)`
    * **Mô tả:** Cập nhật thông tin hồ sơ người dùng (ví dụ: tên, đơn vị tiền tệ mặc định - lưu trong bảng `Users` của bạn).
    * **Request Body:** `{ full_name, default_currency }`
    * **Response:** Thông tin hồ sơ đã cập nhật.

**II. Accounts (Tài khoản/Nguồn tiền)**

* **`POST /accounts`** `(Auth Required)`
    * **Mô tả:** Tạo một tài khoản/nguồn tiền mới cho người dùng.
    * **Request Body:** `{ account_name, account_type, initial_balance, currency }`
    * **Response:** Thông tin tài khoản vừa tạo.
* **`GET /accounts`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách tất cả tài khoản của người dùng (chỉ lấy các tài khoản `is_active=true` hoặc có tham số lọc).
    * **Query Params (Optional):** `is_active=true/false`
    * **Response:** Mảng các đối tượng tài khoản.
* **`GET /accounts/{account_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết của một tài khoản cụ thể.
    * **Response:** Đối tượng tài khoản chi tiết.
* **`PUT /accounts/{account_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật thông tin một tài khoản (tên, loại, trạng thái active). *Lưu ý: Cập nhật số dư nên thông qua giao dịch.*
    * **Request Body:** `{ account_name, account_type, is_active }`
    * **Response:** Thông tin tài khoản đã cập nhật.
* **`DELETE /accounts/{account_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một tài khoản (nên cân nhắc: có thể chỉ đánh dấu `is_active=false` thay vì xóa cứng nếu có giao dịch liên quan).
    * **Response:** Success/Failure message.

**III. Categories (Danh mục)**

* **`POST /categories`** `(Auth Required)`
    * **Mô tả:** Tạo một danh mục tùy chỉnh mới cho người dùng.
    * **Request Body:** `{ category_name, parent_category_id (optional), category_type ('income'/'expense'), icon (optional) }`
    * **Response:** Thông tin danh mục vừa tạo.
* **`GET /categories`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách tất cả danh mục (bao gồm cả danh mục hệ thống và danh mục tùy chỉnh của người dùng).
    * **Query Params (Optional):** `type=income/expense`, `is_custom=true/false`
    * **Response:** Mảng các đối tượng danh mục.
* **`GET /categories/{category_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết một danh mục.
    * **Response:** Đối tượng danh mục chi tiết.
* **`PUT /categories/{category_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật một danh mục tùy chỉnh của người dùng.
    * **Request Body:** `{ category_name, parent_category_id, icon }`
    * **Response:** Thông tin danh mục đã cập nhật.
* **`DELETE /categories/{category_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một danh mục tùy chỉnh (cần kiểm tra xem có giao dịch nào đang sử dụng không, hoặc xử lý logic liên quan).
    * **Response:** Success/Failure message.

**IV. Transactions (Giao dịch)**

* **`POST /transactions`** `(Auth Required)`
    * **Mô tả:** Tạo một giao dịch mới. Backend cần tự động xác định `transaction_type` dựa trên `category_id` và cập nhật `current_balance` của `account_id`.
    * **Request Body:** `{ account_id, category_id, amount, transaction_date, description (optional), location (optional), tags (optional: list of tag_ids or tag_names) }`
    * **Response:** Thông tin giao dịch vừa tạo.
* **`GET /transactions`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách giao dịch của người dùng, hỗ trợ lọc và phân trang.
    * **Query Params (Optional):** `start_date`, `end_date`, `account_id`, `category_id`, `type=income/expense`, `tag_id`, `page=1`, `limit=20`, `sort_by=transaction_date`, `order=desc/asc`
    * **Response:** Mảng các đối tượng giao dịch và thông tin phân trang.
* **`GET /transactions/{transaction_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết một giao dịch.
    * **Response:** Đối tượng giao dịch chi tiết (có thể kèm theo tags).
* **`PUT /transactions/{transaction_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật một giao dịch. Cần tính toán lại số dư tài khoản nếu `amount` hoặc `account_id` thay đổi.
    * **Request Body:** `{ account_id, category_id, amount, transaction_date, description, location }`
    * **Response:** Thông tin giao dịch đã cập nhật.
* **`DELETE /transactions/{transaction_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một giao dịch. Cần tính toán lại số dư tài khoản.
    * **Response:** Success/Failure message.
* **`POST /transactions/{transaction_id}/tags`** `(Auth Required)`
    * **Mô tả:** Gắn một hoặc nhiều tag vào giao dịch.
    * **Request Body:** `{ tag_ids: [id1, id2] }` hoặc `{ tag_names: ["tag1", "tag2"] }` (backend xử lý tạo tag mới nếu chưa có)
    * **Response:** Danh sách tag hiện tại của giao dịch.
* **`DELETE /transactions/{transaction_id}/tags/{tag_id}`** `(Auth Required)`
    * **Mô tả:** Gỡ bỏ một tag khỏi giao dịch.
    * **Response:** Success/Failure message.

**V. Budgets (Ngân sách)**

* **`POST /budgets`** `(Auth Required)`
    * **Mô tả:** Tạo một ngân sách mới cho một danh mục trong một khoảng thời gian.
    * **Request Body:** `{ category_id, amount, start_date, end_date }`
    * **Response:** Thông tin ngân sách vừa tạo.
* **`GET /budgets`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách ngân sách của người dùng.
    * **Query Params (Optional):** `month`, `year`, `category_id`, `active_date` (lấy budget có hiệu lực vào ngày này)
    * **Response:** Mảng các đối tượng ngân sách.
* **`GET /budgets/{budget_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết một ngân sách.
    * **Response:** Đối tượng ngân sách chi tiết.
* **`PUT /budgets/{budget_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật một ngân sách.
    * **Request Body:** `{ amount, start_date, end_date }`
    * **Response:** Thông tin ngân sách đã cập nhật.
* **`DELETE /budgets/{budget_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một ngân sách.
    * **Response:** Success/Failure message.

**VI. Goals (Mục tiêu tiết kiệm)**

* **`POST /goals`** `(Auth Required)`
    * **Mô tả:** Tạo một mục tiêu tiết kiệm mới.
    * **Request Body:** `{ goal_name, target_amount, target_date (optional) }`
    * **Response:** Thông tin mục tiêu vừa tạo.
* **`GET /goals`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách mục tiêu tiết kiệm của người dùng.
    * **Query Params (Optional):** `status=active/achieved/cancelled`
    * **Response:** Mảng các đối tượng mục tiêu.
* **`GET /goals/{goal_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết một mục tiêu.
    * **Response:** Đối tượng mục tiêu chi tiết.
* **`PUT /goals/{goal_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật thông tin mục tiêu (tên, số tiền đích, hạn chót, trạng thái).
    * **Request Body:** `{ goal_name, target_amount, target_date, status }`
    * **Response:** Thông tin mục tiêu đã cập nhật.
* **`PATCH /goals/{goal_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật số tiền hiện có cho mục tiêu (ví dụ: khi người dùng chuyển tiền vào mục tiêu).
    * **Request Body:** `{ current_amount }` hoặc `{ contribution_amount }` (backend tự cộng dồn)
    * **Response:** Thông tin mục tiêu đã cập nhật.
* **`DELETE /goals/{goal_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một mục tiêu.
    * **Response:** Success/Failure message.

**VII. Tags (Nhãn)**

* **`POST /tags`** `(Auth Required)`
    * **Mô tả:** Tạo một tag mới cho người dùng.
    * **Request Body:** `{ tag_name }`
    * **Response:** Thông tin tag vừa tạo.
* **`GET /tags`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách tất cả các tag của người dùng.
    * **Response:** Mảng các đối tượng tag.
* **`PUT /tags/{tag_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật tên của một tag.
    * **Request Body:** `{ tag_name }`
    * **Response:** Thông tin tag đã cập nhật.
* **`DELETE /tags/{tag_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một tag (cần xóa các liên kết trong `Transaction_Tags` trước hoặc dùng `ON DELETE CASCADE`).
    * **Response:** Success/Failure message.

**VIII. Recurring Transactions (Giao dịch lặp lại)**

* **`POST /recurring-transactions`** `(Auth Required)`
    * **Mô tả:** Tạo một định nghĩa giao dịch lặp lại mới.
    * **Request Body:** `{ account_id, category_id, amount, description (optional), frequency, start_date, end_date (optional), next_due_date }`
    * **Response:** Thông tin định nghĩa vừa tạo.
* **`GET /recurring-transactions`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách các định nghĩa giao dịch lặp lại.
    * **Query Params (Optional):** `is_active=true/false`
    * **Response:** Mảng các đối tượng định nghĩa.
* **`GET /recurring-transactions/{recurring_transaction_id}`** `(Auth Required)`
    * **Mô tả:** Lấy chi tiết một định nghĩa.
    * **Response:** Đối tượng định nghĩa chi tiết.
* **`PUT /recurring-transactions/{recurring_transaction_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật một định nghĩa giao dịch lặp lại.
    * **Request Body:** `{ account_id, category_id, amount, description, frequency, start_date, end_date, next_due_date, is_active }`
    * **Response:** Thông tin định nghĩa đã cập nhật.
* **`DELETE /recurring-transactions/{recurring_transaction_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một định nghĩa giao dịch lặp lại.
    * **Response:** Success/Failure message.
* **`PATCH /recurring-transactions/{recurring_transaction_id}`** `(Auth Required)`
    * **Mô tả:** Kích hoạt hoặc vô hiệu hóa một định nghĩa lặp lại.
    * **Request Body:** `{ is_active: true/false }`
    * **Response:** Thông tin định nghĩa đã cập nhật.

**IX. Reports & Summaries (Báo cáo & Tổng hợp)**

* **`GET /reports/summary`** `(Auth Required)`
    * **Mô tả:** Lấy tổng thu, tổng chi, và dòng tiền ròng trong một khoảng thời gian.
    * **Query Params:** `start_date`, `end_date`, `account_id (optional)`
    * **Response:** `{ total_income, total_expense, net_flow }`
* **`GET /reports/spending-by-category`** `(Auth Required)`
    * **Mô tả:** Lấy tổng chi tiêu theo từng danh mục trong một khoảng thời gian.
    * **Query Params:** `start_date`, `end_date`, `account_id (optional)`
    * **Response:** Mảng các đối tượng `{ category_id, category_name, total_amount, percentage }`
* **`GET /reports/budget-status`** `(Auth Required)`
    * **Mô tả:** So sánh chi tiêu thực tế với ngân sách đã đặt trong một khoảng thời gian.
    * **Query Params:** `month`, `year` (hoặc `start_date`, `end_date`)
    * **Response:** Mảng các đối tượng `{ category_id, category_name, budget_amount, actual_spending, remaining_amount }`

