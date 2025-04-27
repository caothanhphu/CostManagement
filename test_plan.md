Tuyệt vời! Việc thiết kế kịch bản test (test plan/test scenarios) hợp lý cho integration test là rất quan trọng. Mục tiêu là đảm bảo các API endpoint hoạt động đúng như mong đợi khi tương tác với database Supabase thực tế (phiên bản test).

Dưới đây là một dàn ý và các kịch bản test gợi ý, tập trung vào việc kiểm tra luồng dữ liệu, logic nghiệp vụ và tương tác với database test:

**Nguyên tắc chung:**

1.  **Database Test Riêng Biệt:** Luôn sử dụng một project Supabase riêng biệt cho testing. **Không bao giờ** chạy trên database production.
2.  **Quản lý Trạng thái (State Management):** Mỗi test case nên chạy độc lập. Điều này đòi hỏi:
    * **Setup:** Chuẩn bị dữ liệu cần thiết trước khi chạy test (ví dụ: tạo user test, tạo sẵn account/category nếu cần).
    * **Teardown:** Dọn dẹp dữ liệu đã tạo ra sau khi test chạy xong (ví dụ: xóa user test, xóa các bản ghi đã tạo). Sử dụng `pytest fixtures` với `scope="function"` và `yield` là cách tốt để quản lý việc này.
3.  **Dữ liệu Test:** Sử dụng dữ liệu hợp lệ, không hợp lệ (để kiểm tra validation), dữ liệu biên (số 0, ngày cuối tháng,...), và dữ liệu đặc biệt (chuỗi rỗng, ký tự đặc biệt nếu có thể).
4.  **Xác thực (Authentication):** Hầu hết các API đều yêu cầu xác thực. Cần có cơ chế tạo/lấy token hợp lệ cho user test để đưa vào header `Authorization: Bearer <token>`.
5.  **Kiểm tra (Assertions):** Không chỉ kiểm tra status code và response body của API, mà còn cần (khi thích hợp) truy vấn lại database (thông qua API `GET` hoặc trực tiếp nếu cần) để xác nhận dữ liệu đã được lưu/cập nhật/xóa đúng cách.

**Kịch bản Test Chi tiết theo Nhóm API:**

*(Lưu ý: Mỗi gạch đầu dòng lớn là một kịch bản cần kiểm thử. Bạn có thể chia nhỏ hơn nữa.)*

**I. Authentication & User Profile (`/auth`, `/profile`)**

* **Signup:**
    * **Happy Path:** Đăng ký thành công với email/password hợp lệ (+ tên nếu có). Kiểm tra response chứa thông tin user và session token. *Xác nhận:* Có thể login lại bằng thông tin vừa đăng ký.
    * **Lỗi - Email đã tồn tại:** Đăng ký với email đã được sử dụng. Kiểm tra status code 400/409 và thông báo lỗi phù hợp.
    * **Lỗi - Dữ liệu không hợp lệ:** Đăng ký với password quá ngắn, email sai định dạng. Kiểm tra status code 422 (Unprocessable Entity).
* **Login:**
    * **Happy Path:** Đăng nhập thành công với email/password đúng. Kiểm tra response chứa user/session token.
    * **Lỗi - Sai thông tin:** Đăng nhập với email sai hoặc password sai. Kiểm tra status code 401 (Unauthorized) và thông báo lỗi.
    * **Lỗi - User không tồn tại:** Đăng nhập với email chưa đăng ký. Kiểm tra status code 401.
* **Logout:**
    * **Happy Path:** Gọi logout với token hợp lệ. Kiểm tra status code 200 và message thành công. *Xác nhận:* Token đó không còn dùng được cho các API khác (gọi `/auth/user` phải trả về lỗi 401).
    * **Lỗi - Không có token:** Gọi logout không kèm token. Kiểm tra status code 401.
    * **Lỗi - Token không hợp lệ/hết hạn:** Gọi logout với token sai/cũ. Kiểm tra status code 401.
* **Get User Info (`/auth/user`):**
    * **Happy Path:** Gọi với token hợp lệ. Kiểm tra status code 200 và response chứa thông tin user chính xác (id, email, metadata).
    * **Lỗi - Không có token/Token không hợp lệ:** Kiểm tra status code 401.
* **Update Profile (`/profile`):**
    * **Happy Path:** Cập nhật `full_name` và/hoặc `default_currency` với token hợp lệ. Kiểm tra status code 200, response chứa thông tin đã cập nhật. *Xác nhận:* Gọi `/auth/user` hoặc truy vấn DB thấy thông tin mới.
    * **Lỗi - Không có dữ liệu:** Gọi PUT mà không có field nào trong body. Kiểm tra status code 400.
    * **Lỗi - Không có token/Token không hợp lệ:** Kiểm tra status code 401.

**II. Accounts (`/accounts`)**

* **Create Account:**
    * **Happy Path:** Tạo account mới với đủ thông tin hợp lệ. Kiểm tra 201, response body, `current_balance` == `initial_balance`. *Xác nhận:* Gọi `GET /accounts/{id}` lấy lại được account này.
    * **Lỗi - Dữ liệu không hợp lệ:** Thiếu `account_name`, `account_type` sai enum, `currency` sai định dạng. Kiểm tra 422.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **List Accounts:**
    * **Happy Path:** Lấy danh sách account khi chưa có account nào (trả về list rỗng). Tạo 1-2 accounts, gọi lại API, kiểm tra danh sách trả về đúng số lượng và thông tin cơ bản.
    * **Happy Path - Filter:** Tạo account active/inactive, gọi API với filter `is_active=true` và `is_active=false`, kiểm tra kết quả lọc đúng.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Get Account by ID:**
    * **Happy Path:** Tạo account, lấy ID, gọi `GET /accounts/{id}`. Kiểm tra 200 và dữ liệu chi tiết khớp.
    * **Lỗi - Not Found:** Gọi với ID không tồn tại hoặc ID của user khác. Kiểm tra 404.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Update Account:**
    * **Happy Path:** Tạo account, gọi `PUT /accounts/{id}` để đổi tên, `account_type`, `is_active`. Kiểm tra 200, response body. *Xác nhận:* Gọi `GET /accounts/{id}` thấy thông tin mới.
    * **Lỗi - Not Found:** Gọi PUT với ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Dữ liệu không hợp lệ:** `account_type` sai enum. Kiểm tra 422.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Delete Account:**
    * **Happy Path (Không có giao dịch):** Tạo account, gọi `DELETE /accounts/{id}`. Kiểm tra 204. *Xác nhận:* Gọi `GET /accounts/{id}` trả về 404.
    * **Lỗi - Còn giao dịch (Nếu dùng `ON DELETE RESTRICT`):** Tạo account, tạo transaction liên quan, gọi `DELETE /accounts/{id}`. Kiểm tra status code lỗi (409 Conflict hoặc tương tự) và thông báo lỗi.
    * **Lỗi - Not Found:** Gọi DELETE với ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.

**III. Categories (`/categories`)**

* **(Setup)** Cần kiểm tra cả category hệ thống (nếu có) và category do user tạo.
* **Create Category:**
    * **Happy Path:** Tạo category mới (cả loại income/expense), tạo category con (có `parent_category_id`). Kiểm tra 201, response body. *Xác nhận:* `GET /categories` thấy category mới.
    * **Lỗi - Dữ liệu không hợp lệ:** Thiếu `category_name`, `category_type` sai. Kiểm tra 422.
    * **Lỗi - Trùng tên:** Tạo category với tên đã tồn tại của user đó. Kiểm tra 409 Conflict.
    * **Lỗi - `parent_category_id` không tồn tại:** Kiểm tra 400/404.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **List Categories:**
    * **Happy Path:** Lấy danh sách (ban đầu chỉ có system?), tạo vài category custom, gọi lại API, kiểm tra có cả system và custom.
    * **Happy Path - Filter:** Lọc theo `type=income`, `type=expense`, `is_custom=true`, `is_custom=false`. Kiểm tra kết quả.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Get Category by ID:** (Tương tự Get Account by ID)
* **Update Category:**
    * **Happy Path:** Tạo category custom, cập nhật tên, icon, parent. Kiểm tra 200, response. *Xác nhận:* GET lại thấy thông tin mới.
    * **Lỗi - Cập nhật category hệ thống:** Cố gắng PUT category có `user_id=null` hoặc `is_custom=false`. Kiểm tra lỗi (403 Forbidden hoặc 404).
    * **Lỗi - Not Found:** PUT ID không tồn tại / của user khác. Kiểm tra 404.
    * **Lỗi - Trùng tên:** Cập nhật tên thành tên đã tồn tại khác. Kiểm tra 409.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Delete Category:**
    * **Happy Path (Không có giao dịch/budget):** Tạo category custom, DELETE. Kiểm tra 204. *Xác nhận:* GET lại trả về 404.
    * **Lỗi - Xóa category hệ thống:** Cố gắng DELETE category có `user_id=null`. Kiểm tra lỗi (403 hoặc 404).
    * **Lỗi - Còn giao dịch/budget (Nếu dùng `ON DELETE RESTRICT`):** Tạo category, tạo transaction/budget liên quan, DELETE category. Kiểm tra 409 Conflict.
    * **Lỗi - Not Found:** DELETE ID không tồn tại / của user khác. Kiểm tra 404.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.

**IV. Transactions (`/transactions`)**

* **(Setup)** Cần có sẵn user, account, category hợp lệ.
* **Create Transaction:**
    * **Happy Path (Expense & Income):** Tạo giao dịch chi tiêu và thu nhập. Kiểm tra 201, response body (đúng `transaction_type`). *Xác nhận:*
        * Gọi `GET /transactions/{id}` lấy lại được.
        * Gọi `GET /accounts/{id}` kiểm tra `current_balance` đã cập nhật đúng (+/- amount).
    * **Happy Path (With Tags):** Tạo giao dịch kèm `tag_ids` hoặc `tag_names` (tạo tag mới). Kiểm tra response có chứa thông tin tags. *Xác nhận:* `GET /transactions/{id}` thấy tags, `GET /tags` thấy tag mới (nếu tạo bằng tên).
    * **Lỗi - Dữ liệu không hợp lệ:** Thiếu `account_id`, `category_id`, `amount` <= 0. Kiểm tra 422.
    * **Lỗi - Account/Category không tồn tại:** Dùng ID không hợp lệ/của user khác. Kiểm tra lỗi (400/404/500 tùy cách service xử lý).
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **List Transactions:**
    * **Happy Path:** Lấy danh sách khi chưa có, tạo nhiều giao dịch, lấy lại danh sách. Kiểm tra số lượng, thứ tự (mặc định theo ngày giảm dần).
    * **Happy Path - Filtering:** Test với các bộ lọc `start_date`, `end_date`, `account_id`, `category_id`, `type`. Kiểm tra kết quả lọc chính xác.
    * **Happy Path - Pagination:** Tạo nhiều hơn `limit` (ví dụ: 25), gọi API với `page=1`, `page=2`. Kiểm tra `total`, `page`, `limit`, và nội dung `data` của từng trang.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Get Transaction by ID:** (Tương tự Get Account)
* **Update Transaction:**
    * **Happy Path:** Tạo giao dịch, cập nhật `amount`, `category_id`, `account_id`, `description`, `date`. Kiểm tra 200, response body. *Xác nhận:*
        * `GET /transactions/{id}` thấy thông tin mới.
        * `GET /accounts/{id}` kiểm tra `current_balance` của account cũ và mới (nếu đổi account) đã được điều chỉnh chính xác.
    * **Lỗi - Not Found:** PUT ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Dữ liệu không hợp lệ:** `amount` <= 0, `account_id`/`category_id` không tồn tại. Kiểm tra 422 hoặc 400/404.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Delete Transaction:**
    * **Happy Path:** Tạo giao dịch, DELETE. Kiểm tra 204. *Xác nhận:*
        * `GET /transactions/{id}` trả về 404.
        * `GET /accounts/{id}` kiểm tra `current_balance` đã được hoàn trả đúng.
    * **Lỗi - Not Found:** DELETE ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Manage Transaction Tags (`/transactions/{id}/tags`):**
    * **Happy Path:** Tạo transaction, POST để thêm tag (bằng ID và tên), kiểm tra response. Gọi DELETE để xóa tag, kiểm tra 204. *Xác nhận:* `GET /transactions/{id}` thấy danh sách tags thay đổi tương ứng.
    * **Lỗi - Transaction Not Found:** POST/DELETE tag với ID transaction không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Tag Not Found (khi xóa):** DELETE tag với ID tag không tồn tại hoặc không được gắn vào transaction đó. Kiểm tra 404.
    * **Lỗi - Không có dữ liệu (khi POST):** Gửi request không có `tag_ids` hay `tag_names`. Kiểm tra 400.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.

**V. Budgets (`/budgets`)**

* **(Setup)** Cần có user, category hợp lệ.
* **Create Budget:**
    * **Happy Path:** Tạo budget cho một category trong khoảng thời gian. Kiểm tra 201, response. *Xác nhận:* `GET /budgets/{id}` lấy lại được.
    * **Lỗi - Dữ liệu không hợp lệ:** `amount` <= 0, `start_date` > `end_date`, `category_id` không tồn tại. Kiểm tra 422 hoặc 400/404.
    * **Lỗi - Trùng lặp:** Tạo budget cho cùng category/khoảng thời gian đã tồn tại. Kiểm tra 409 Conflict.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **List Budgets:**
    * **Happy Path:** Lấy danh sách khi chưa có, tạo nhiều budget (có thể overlap, khác category), lấy lại danh sách.
    * **Happy Path - Filter:** Lọc theo `category_id`, lọc theo khoảng thời gian (`start_date`, `end_date`). Kiểm tra logic lọc (ví dụ: budget có hiệu lực *trong* khoảng thời gian lọc).
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Get Budget by ID:** (Tương tự Get Account)
* **Update Budget:**
    * **Happy Path:** Tạo budget, cập nhật `amount`, `start_date`, `end_date`. Kiểm tra 200, response. *Xác nhận:* GET lại thấy thông tin mới.
    * **Lỗi - Not Found:** PUT ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Dữ liệu không hợp lệ:** `amount` <= 0, `start_date` > `end_date`. Kiểm tra 422.
    * **Lỗi - Trùng lặp:** Cập nhật khiến budget bị trùng với budget khác. Kiểm tra 409.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **Delete Budget:** (Tương tự Delete Account, không có ràng buộc phức tạp)

**VI. Goals (`/goals`)**

* **(Setup)** Cần có user.
* **Create Goal:**
    * **Happy Path:** Tạo goal mới. Kiểm tra 201, `current_amount` = 0, `status` = 'active'. *Xác nhận:* GET lại được.
    * **Lỗi - Dữ liệu không hợp lệ:** Thiếu tên, `target_amount` <= 0. Kiểm tra 422.
    * **Lỗi - Unauthorized:** Không có token. Kiểm tra 401.
* **List Goals:**
    * **Happy Path:** Lấy danh sách khi chưa có, tạo nhiều goal, lấy lại.
    * **Happy Path - Filter:** Lọc theo `status=active`, `status=achieved`.
    * **Lỗi - Unauthorized:** Kiểm tra 401.
* **Get Goal by ID:** (Tương tự Get Account)
* **Update Goal:**
    * **Happy Path:** Tạo goal, cập nhật tên, target, date, status. Kiểm tra 200, response. *Xác nhận:* GET lại thấy thông tin mới.
    * **Lỗi - Not Found:** PUT ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Dữ liệu không hợp lệ:** `target_amount` <= 0, `status` không hợp lệ. Kiểm tra 422.
    * **Lỗi - Unauthorized:** Kiểm tra 401.
* **Contribute to Goal (`PATCH /goals/{id}/contribute`):**
    * **Happy Path:** Tạo goal, gọi PATCH với `contribution_amount`. Kiểm tra 200, `current_amount` tăng đúng.
    * **Happy Path (Achieved):** Contribute đủ để `current_amount` >= `target_amount`. Kiểm tra `status` tự động chuyển thành 'achieved'.
    * **Lỗi - Not Found:** PATCH ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Dữ liệu không hợp lệ:** `contribution_amount` <= 0. Kiểm tra 422.
    * **Lỗi - Unauthorized:** Kiểm tra 401.
* **Delete Goal:** (Tương tự Delete Account)

**VII. Tags (`/tags`)**

* **(Setup)** Cần có user.
* **Create Tag:**
    * **Happy Path:** Tạo tag mới. Kiểm tra 201 (hoặc 200 nếu service dùng get_or_create), response. *Xác nhận:* GET lại thấy tag.
    * **Happy Path (Đã tồn tại):** Tạo tag với tên đã có (viết hoa/thường khác nhau). Kiểm tra trả về tag đã tồn tại (status code 200).
    * **Lỗi - Dữ liệu không hợp lệ:** Tên rỗng. Kiểm tra 400/422.
    * **Lỗi - Unauthorized:** Kiểm tra 401.
* **List Tags:** (Tương tự List Accounts)
* **Update Tag:**
    * **Happy Path:** Tạo tag, cập nhật tên. Kiểm tra 200, response. *Xác nhận:* GET lại thấy tên mới.
    * **Lỗi - Not Found:** PUT ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Trùng tên:** Cập nhật thành tên đã tồn tại khác. Kiểm tra 409.
    * **Lỗi - Unauthorized:** Kiểm tra 401.
* **Delete Tag:**
    * **Happy Path:** Tạo tag, tạo transaction, gắn tag vào transaction. Gọi DELETE tag. Kiểm tra 204. *Xác nhận:* `GET /tags` không còn tag, `GET /transactions/{id}` không còn tag đó trong danh sách.
    * **Lỗi - Not Found:** DELETE ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Unauthorized:** Kiểm tra 401.

**VIII. Recurring Transactions (`/recurring-transactions`)**

* **(Setup)** Cần có user, account, category.
* **Create Recurring Transaction:**
    * **Happy Path:** Tạo định nghĩa mới. Kiểm tra 201, response (có `next_due_date` hợp lý). *Xác nhận:* GET lại được.
    * **Lỗi - Dữ liệu không hợp lệ:** Thiếu trường, `amount` <= 0, `frequency`/`account_id`/`category_id` không hợp lệ. Kiểm tra 422/400/404.
    * **Lỗi - Unauthorized:** Kiểm tra 401.
* **List Recurring Transactions:** (Tương tự List Accounts, có filter `is_active`)
* **Get Recurring Transaction by ID:** (Tương tự Get Account)
* **Update Recurring Transaction:**
    * **Happy Path:** Tạo định nghĩa, cập nhật các trường (amount, frequency, dates, is_active). Kiểm tra 200, response. *Xác nhận:* GET lại thấy thông tin mới.
    * **Lỗi - Not Found:** PUT ID không tồn tại/của user khác. Kiểm tra 404.
    * **Lỗi - Dữ liệu không hợp lệ:** Kiểm tra 422/400/404.
    * **Lỗi - Unauthorized:** Kiểm tra 401.
* **Delete Recurring Transaction:** (Tương tự Delete Account)

**IX. Reports (`/reports`)**

* **(Setup)** Cần tạo một lượng dữ liệu giao dịch (thu/chi) và budget đủ đa dạng trong khoảng thời gian test.
* **Get Summary Report:**
    * **Happy Path:** Gọi API với khoảng thời gian hợp lệ. Kiểm tra 200, các giá trị `total_income`, `total_expense`, `net_flow` tính toán đúng dựa trên dữ liệu test đã tạo.
    * **Happy Path (No Data):** Gọi API với khoảng thời gian không có giao dịch. Kiểm tra các giá trị tổng là 0.
    * **Lỗi - Ngày không hợp lệ:** `start_date` > `end_date`. Kiểm tra 400.
    * **Lỗi - Unauthorized:** Kiểm tra 401.
* **Get Spending By Category Report:**
    * **Happy Path:** Gọi API với khoảng thời gian hợp lệ. Kiểm tra 200, danh sách `data` chứa đúng các category có chi tiêu, `total_amount` và `percentage` tính đúng. Kiểm tra thứ tự sắp xếp (theo amount giảm dần).
    * **Happy Path (No Spending):** Gọi API với khoảng thời gian không có chi tiêu. Kiểm tra `data` là list rỗng.
    * **Lỗi - Ngày không hợp lệ:** Kiểm tra 400.
    * **Lỗi - Unauthorized:** Kiểm tra 401.
* **Get Budget Status Report:**
    * **Happy Path:** Tạo budget, tạo giao dịch (ít hơn, bằng, nhiều hơn budget). Gọi API. Kiểm tra 200, danh sách `data` chứa đúng category có budget, các giá trị `budget_amount`, `actual_spending`, `remaining_amount`, `percentage_spent` tính đúng.
    * **Happy Path (No Budgets):** Gọi API khi không có budget nào trong kỳ. Kiểm tra `data` rỗng.
    * **Happy Path (No Spending):** Có budget nhưng không có chi tiêu. Kiểm tra `actual_spending`=0, `remaining_amount`=budget.
    * **Lỗi - Ngày không hợp lệ:** Kiểm tra 400.
    * **Lỗi - Unauthorized:** Kiểm tra 401.

**Lời khuyên:**

* Bắt đầu với các kịch bản "Happy Path" cho các chức năng CRUD cơ bản.
* Sau đó thêm các kịch bản lỗi (4xx).
* Cuối cùng là các kịch bản phức tạp hơn liên quan đến logic nghiệp vụ (cập nhật số dư, tính toán báo cáo).
* Sử dụng `pytest` markers (`@pytest.mark.integration`) để nhóm các test này lại.

Kịch bản này cung cấp một cái nhìn tổng quan. Bạn cần chi tiết hóa từng bước (dữ liệu đầu vào cụ thể, giá trị mong đợi chính xác) khi viết code test thực tế.