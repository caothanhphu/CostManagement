# **Kiến trúc Project API Python với PostgreSQL và JWT**

Dựa trên lược đồ cơ sở dữ liệu PostgreSQL được cung cấp, chúng ta sẽ thiết kế một kiến trúc API backend bằng Python, sử dụng JWT cho xác thực và tương tác trực tiếp với cơ sở dữ liệu local. Kiến trúc này tuân theo nguyên tắc phân lớp để đảm bảo tính modular, dễ bảo trì và mở rộng.

## **1\. Các Thành phần Chính**

* **Web Framework:** FastAPI . FastAPI được ưa chuộng cho các API hiện đại nhờ hiệu suất cao, hỗ trợ async/await và tự động tạo tài liệu API (Swagger UI).  
* **Database Interaction:** SQLAlchemy (ORM) kết hợp với Psycopg2 (PostgreSQL adapter). SQLAlchemy cung cấp lớp trừu tượng mạnh mẽ cho việc tương tác cơ sở dữ liệu, giúp code độc lập hơn với chi tiết cụ thể của DB và hỗ trợ quản lý session hiệu quả.  
* **Authentication:** Thư viện PyJWT để tạo, ký, mã hóa, giải mã và xác minh JWT.  
* **Password Hashing:** Thư viện passlib (hỗ trợ bcrypt) để mã hóa mật khẩu một cách an toàn.  
* **Configuration Management:** Sử dụng biến môi trường (environment variables) hoặc thư viện như python-dotenv để quản lý các cấu hình nhạy cảm (chuỗi kết nối DB, secret key JWT).  
* **Dependency Management:** pip và requirements.txt hoặc Poetry/Pipenv.

## **2\. Các Lớp Kiến trúc (Architectural Layers)**

Kiến trúc sẽ được phân chia thành các lớp rõ ràng:

* **Lớp Trình bày (Presentation Layer):**  
  * Chứa các endpoint API (sử dụng FastAPI APIRouter).  
  * Xử lý việc nhận request HTTP, phân tích cú pháp dữ liệu đầu vào (sử dụng Pydantic models), xác thực token JWT, ủy quyền (kiểm tra quyền truy cập của người dùng).  
  * Gọi các hàm xử lý logic từ Lớp Dịch vụ.  
  * Định dạng dữ liệu trả về (response) theo chuẩn API (JSON) và xử lý lỗi.  
  * **Công nghệ:** FastAPI, Pydantic.  
* **Lớp Dịch vụ (Service Layer / Business Logic Layer):**  
  * Chứa logic nghiệp vụ cốt lõi của ứng dụng.  
  * Nhận dữ liệu đã được xác thực và kiểm tra từ Lớp Trình bày.  
  * Thực hiện các thao tác phức tạp liên quan đến nhiều bảng hoặc cần tính toán (ví dụ: tạo giao dịch và cập nhật số dư tài khoản, tính toán báo cáo).  
  * Gọi các phương thức tương tác DB từ Lớp Truy cập Dữ liệu.  
  * Đảm bảo tính toàn vẹn dữ liệu và áp dụng các quy tắc nghiệp vụ.  
  * **Công nghệ:** Python classes/functions, tương tác với Lớp Truy cập Dữ liệu.  
* **Lớp Truy cập Dữ liệu (Data Access Layer / Repository Layer / CRUD Layer):**  
  * Chịu trách nhiệm tương tác trực tiếp với cơ sở dữ liệu.  
  * Chứa các hàm CRUD cơ bản cho từng mô hình dữ liệu (User, Account, Transaction, v.v.).  
  * Sử dụng ORM (SQLAlchemy) để thực hiện các truy vấn SQL.  
  * Ẩn đi chi tiết cụ thể của cơ sở dữ liệu khỏi Lớp Dịch vụ.  
  * **Công nghệ:** SQLAlchemy ORM, Python classes/functions.  
* **Lớp Cơ sở dữ liệu (Database Layer):**  
  * Cơ sở dữ liệu PostgreSQL với lược đồ đã cung cấp.  
  * **Công nghệ:** PostgreSQL.  
* **Thành phần Xác thực (Authentication Component):**  
  * Module riêng biệt xử lý logic đăng ký, đăng nhập, tạo/xác minh JWT.  
  * Sử dụng thư viện JWT và password hashing.  
  * Được sử dụng bởi Lớp Trình bày (đặc biệt là các endpoint /auth/\*) và như một dependency cho các endpoint yêu cầu xác thực.  
* **Worker Giao dịch Lặp lại (Recurring Transaction Worker):**  
  * Một tiến trình nền hoặc tác vụ được lập lịch riêng biệt.  
  * Định kỳ kiểm tra bảng RecurringTransactions.  
  * Tạo các bản ghi Transactions mới dựa trên các định nghĩa lặp lại có next\_due\_date đến hạn hoặc đã quá hạn.  
  * Cập nhật next\_due\_date và last\_created\_date trong bảng RecurringTransactions.  
  * Có thể sử dụng các thư viện như Celery, APScheduler.

## **3\. Luồng Hoạt động (Flow)**

1. **Đăng ký/Đăng nhập:**  
   * Client gửi request POST đến /auth/signup hoặc /auth/login.  
   * Lớp Trình bày nhận request, validate dữ liệu.  
   * Lớp Trình bày gọi hàm tương ứng trong Thành phần Xác thực.  
   * Thành phần Xác thực tương tác với Lớp Truy cập Dữ liệu (User CRUD) để lưu/lấy thông tin người dùng và kiểm tra mật khẩu.  
   * Nếu đăng nhập thành công, Thành phần Xác thực tạo JWT chứa user\_id.  
   * Lớp Trình bày trả về thông tin người dùng và JWT cho Client.  
2. **Request yêu cầu Xác thực (ví dụ: GET /accounts):**  
   * Client gửi request GET đến /accounts kèm theo JWT trong header Authorization: Bearer \<token\>.  
   * Lớp Trình bày (sử dụng Dependency Injection) xác minh JWT. Nếu token hợp lệ, user\_id được trích xuất và đưa vào context của request. Nếu không hợp lệ, trả về lỗi 401 Unauthorized.  
   * Lớp Trình bày gọi hàm tương ứng trong Lớp Dịch vụ (ví dụ: account\_service.get\_user\_accounts(user\_id)).  
   * Lớp Dịch vụ gọi hàm tương ứng trong Lớp Truy cập Dữ liệu (ví dụ: account\_crud.get\_by\_user\_id(user\_id)).  
   * Lớp Truy cập Dữ liệu thực hiện truy vấn DB bằng SQLAlchemy để lấy dữ liệu Accounts chỉ thuộc về user\_id đó.  
   * Dữ liệu được trả về qua các lớp: Lớp Truy cập Dữ liệu \-\> Lớp Dịch vụ \-\> Lớp Trình bày.  
   * Lớp Trình bày định dạng dữ liệu thành JSON và trả về cho Client.  
3. **Tạo Giao dịch (POST /transactions):**  
   * Client gửi request POST đến /transactions kèm JWT và dữ liệu giao dịch.  
   * Lớp Trình bày xác minh JWT, trích xuất user\_id, validate dữ liệu request (bao gồm kiểm tra account\_id và category\_id có tồn tại trong DB hay không).  
   * Lớp Trình bày gọi hàm trong Lớp Dịch vụ (transaction\_service.create\_transaction(user\_id, transaction\_data)).  
   * Lớp Dịch vụ:  
     * Kiểm tra lại account\_id và category\_id có thuộc về người dùng đó không (hoặc là danh mục hệ thống).  
     * Xác định transaction\_type từ category\_id.  
     * Bắt đầu một transaction DB.  
     * Gọi transaction\_crud.create(...) để lưu giao dịch mới.  
     * Tính toán số dư mới cho tài khoản.  
     * Gọi account\_crud.update\_balance(...) để cập nhật current\_balance trong bảng Accounts.  
     * Commit transaction DB.  
   * Lớp Trình bày trả về thông tin giao dịch đã tạo.

## **4\. Cấu trúc Project Đề xuất (Ví dụ với FastAPI)**

your\_project\_name/  
├── app/  
│   ├── \_\_init\_\_.py  
│   ├── main.py             \# Khởi tạo FastAPI app, cấu hình CORS, include routers  
│   ├── api/  
│   │   ├── \_\_init\_\_.py  
│   │   ├── v1/             \# Versioning API (có thể bỏ qua nếu chỉ có 1 version)  
│   │   │   ├── \_\_init\_\_.py  
│   │   │   ├── endpoints/  \# Routers cho từng nhóm API (Presentation Layer)  
│   │   │   │   ├── \_\_init\_\_.py  
│   │   │   │   ├── auth.py  
│   │   │   │   ├── accounts.py  
│   │   │   │   ├── categories.py  
│   │   │   │   ├── transactions.py  
│   │   │   │   ├── budgets.py  
│   │   │   │   ├── goals.py  
│   │   │   │   ├── tags.py  
│   │   │   │   ├── recurring\_transactions.py  
│   │   │   │   ├── reports.py  
│   │   │   ├── dependencies.py \# Các hàm Dependency Injection (DB session, current user)  
│   │   │   ├── schemas.py      \# Pydantic models cho request/response data  
│   ├── core/  
│   │   ├── \_\_init\_\_.py  
│   │   ├── config.py         \# Load cấu hình từ biến môi trường  
│   │   ├── security.py       \# Hàm băm mật khẩu, tạo/xác minh JWT  
│   │   ├── database.py       \# Cấu hình kết nối DB, tạo session  
│   ├── crud/               \# Lớp Truy cập Dữ liệu (CRUD operations)  
│   │   ├── \_\_init\_\_.py  
│   │   ├── base.py           \# Lớp CRUD base chung  
│   │   ├── user.py           \# CRUD cho User  
│   │   ├── account.py        \# CRUD cho Account  
│   │   ├── category.py       \# CRUD cho Category  
│   │   ├── transaction.py    \# CRUD cho Transaction  
│   │   ├── budget.py         \# CRUD cho Budget  
│   │   ├── goal.py           \# CRUD cho Goal  
│   │   ├── tag.py            \# CRUD cho Tag  
│   │   ├── recurring\_transaction.py \# CRUD cho RecurringTransaction  
│   ├── models/             \# Định nghĩa các mô hình SQLAlchemy ORM  
│   │   ├── \_\_init\_\_.py  
│   │   ├── user.py  
│   │   ├── account.py  
│   │   ├── category.py  
│   │   ├── transaction.py  
│   │   ├── budget.py  
│   │   ├── goal.py  
│   │   ├── tag.py  
│   │   ├── recurring\_transaction.py  
│   ├── services/           \# Lớp Dịch vụ (Business Logic)  
│   │   ├── \_\_init\_\_.py  
│   │   ├── auth\_service.py  
│   │   ├── account\_service.py  
│   │   ├── transaction\_service.py  
│   │   ├── budget\_service.py  
│   │   ├── goal\_service.py  
│   │   ├── report\_service.py  
│   ├── worker/             \# (Optional) Folder cho worker giao dịch lặp lại  
│   │   ├── \_\_init\_\_.py  
│   │   ├── recurring\_task.py \# Logic của worker  
│   │   ├── scheduler.py      \# Cấu hình scheduler (ví dụ: APScheduler)  
├── tests/                  \# Unit và Integration tests  
├── .env                    \# File chứa biến môi trường  
├── requirements.txt        \# Danh sách các thư viện cần cài đặt  
└── Dockerfile              \# (Optional) File cấu hình Docker

## **5\. Các Điểm Cần Lưu ý Khi Triển khai**

* **Quản lý Session DB:** Sử dụng scoped\_session của SQLAlchemy hoặc Dependency Injection của FastAPI để đảm bảo mỗi request có một session DB riêng biệt và được đóng/rollback đúng cách.  
* **Xử lý Lỗi:** Triển khai xử lý lỗi tập trung (ví dụ: sử dụng @app.exception\_handler trong FastAPI) để trả về các phản hồi lỗi nhất quán (ví dụ: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error).  
* **Kiểm tra Quyền Sở hữu Dữ liệu:** Tại Lớp Dịch vụ (hoặc Lớp Truy cập Dữ liệu), luôn kiểm tra xem dữ liệu mà người dùng đang cố gắng truy cập/thao tác có thuộc về user\_id của họ hay không.  
* **Validation Dữ liệu:** Sử dụng Pydantic models để validate dữ liệu đầu vào từ request body và query parameters.  
* **Bảo mật Mật khẩu:** Luôn sử dụng thuật toán băm mạnh (như bcrypt) và salt khi lưu trữ mật khẩu.  
* **Bảo mật JWT Secret:** Giữ bí mật JWT secret key và không commit nó vào source code. Sử dụng biến môi trường.  
* **Transactions DB:** Sử dụng transaction trong SQLAlchemy khi thực hiện nhiều thao tác DB liên quan đến nhau (ví dụ: tạo giao dịch và cập nhật số dư tài khoản) để đảm bảo tính nhất quán.  
* **Giao dịch Lặp lại:** Thiết kế worker một cách cẩn thận để xử lý các trường hợp lỗi, đảm bảo giao dịch không bị tạo trùng lặp và cập nhật next\_due\_date chính xác.

Kiến trúc này cung cấp một nền tảng vững chắc để xây dựng API backend quản lý tài chính cá nhân của bạn bằng Python và PostgreSQL local.



**Thiết kế API Backend (Python + PostgreSQL Local)**

Backend Python của bạn sẽ sử dụng cơ sở dữ liệu PostgreSQL local. Các API dưới đây sẽ yêu cầu người dùng phải xác thực thông qua JWT token.

Dưới đây là danh sách các API được đề xuất, tuân theo nguyên tắc RESTful và hoạt động trên các mô hình dữ liệu đã thiết kế:

**Lưu ý:**

* `{user_id}`, `{account_id}`, `{category_id}`, etc. là các tham số đường dẫn (path parameters).
* Backend sẽ tự động lấy `user_id` từ thông tin xác thực trong JWT token (sau khi giải mã và xác thực token) thay vì truyền trực tiếp qua URL trong hầu hết các trường hợp để đảm bảo người dùng chỉ thao tác trên dữ liệu của chính họ. Danh sách dưới đây liệt kê các endpoint logic, việc triển khai cụ thể sẽ lấy `user_id` từ context xác thực của yêu cầu.
* `(Auth Required)`: Đánh dấu các endpoint yêu cầu người dùng phải gửi kèm JWT token hợp lệ trong header (thường là `Authorization: Bearer <token>`). Backend sẽ xác thực token và lấy `user_id` từ đó.

---

**I. Authentication & User Profile (Xác thực & Hồ sơ người dùng)**

* **`POST /auth/signup`**
    * **Mô tả:** Đăng ký người dùng mới. Lưu thông tin người dùng (bao gồm mật khẩu đã mã hóa) vào cơ sở dữ liệu.
    * **Request Body:** `{ email, password, data (optional: full_name) }`
    * **Response:** Thông tin người dùng (không bao gồm mật khẩu) và JWT (access token).
* **`POST /auth/login`**
    * **Mô tả:** Đăng nhập bằng email/password. Xác thực thông tin với cơ sở dữ liệu, nếu thành công sẽ tạo và trả về JWT (Access Token).
    * **Request Body:** `{ email, password }`
    * **Response:** Thông tin người dùng (không bao gồm mật khẩu) và JWT (access token).
* **`POST /auth/logout`** `(Auth Required)`
    * **Mô tả:** Đăng xuất người dùng. Với JWT stateless, hành động này thường là xóa token ở phía client. Nếu cần vô hiệu hóa token server-side, có thể triển khai cơ chế blacklist token.
    * **Response:** Success/Failure message.
* **`GET /auth/user`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin người dùng đang đăng nhập từ cơ sở dữ liệu, dựa vào `user_id` lấy từ JWT token.
    * **Response:** Thông tin chi tiết người dùng (id, email, role, user_metadata,...).
* **`PUT /profile`** `(Auth Required)`
    * **Mô tả:** Cập nhật thông tin hồ sơ người dùng (ví dụ: tên, đơn vị tiền tệ mặc định - lưu trong bảng `Users` của bạn). `user_id` được lấy từ token.
    * **Request Body:** `{ full_name, default_currency }`
    * **Response:** Thông tin hồ sơ đã cập nhật.

**II. Accounts (Tài khoản/Nguồn tiền)**

* **`POST /accounts`** `(Auth Required)`
    * **Mô tả:** Tạo một tài khoản/nguồn tiền mới cho người dùng (lấy `user_id` từ token).
    * **Request Body:** `{ account_name, account_type, initial_balance, currency }`
    * **Response:** Thông tin tài khoản vừa tạo.
* **`GET /accounts`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách tất cả tài khoản của người dùng (lấy `user_id` từ token). Chỉ lấy các tài khoản `is_active=true` hoặc có tham số lọc.
    * **Query Params (Optional):** `is_active=true/false`
    * **Response:** Mảng các đối tượng tài khoản.
* **`GET /accounts/{account_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết của một tài khoản cụ thể. Backend cần kiểm tra xem tài khoản này có thuộc về người dùng đang đăng nhập hay không (lấy `user_id` từ token).
    * **Response:** Đối tượng tài khoản chi tiết.
* **`PUT /accounts/{account_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật thông tin một tài khoản (tên, loại, trạng thái active). Backend cần kiểm tra quyền sở hữu (`user_id` từ token). *Lưu ý: Cập nhật số dư nên thông qua giao dịch.*
    * **Request Body:** `{ account_name, account_type, is_active }`
    * **Response:** Thông tin tài khoản đã cập nhật.
* **`DELETE /accounts/{account_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một tài khoản. Backend cần kiểm tra quyền sở hữu (`user_id` từ token). (Nên cân nhắc: có thể chỉ đánh dấu `is_active=false` thay vì xóa cứng nếu có giao dịch liên quan).
    * **Response:** Success/Failure message.

**III. Categories (Danh mục)**

* **`POST /categories`** `(Auth Required)`
    * **Mô tả:** Tạo một danh mục tùy chỉnh mới cho người dùng (lấy `user_id` từ token).
    * **Request Body:** `{ category_name, parent_category_id (optional), category_type ('income'/'expense'), icon (optional) }`
    * **Response:** Thông tin danh mục vừa tạo.
* **`GET /categories`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách tất cả danh mục (bao gồm cả danh mục hệ thống và danh mục tùy chỉnh của người dùng - lấy `user_id` từ token).
    * **Query Params (Optional):** `type=income/expense`, `is_custom=true/false`
    * **Response:** Mảng các đối tượng danh mục.
* **`GET /categories/{category_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết một danh mục. Backend cần kiểm tra xem đây là danh mục hệ thống hay danh mục tùy chỉnh thuộc về người dùng (`user_id` từ token).
    * **Response:** Đối tượng danh mục chi tiết.
* **`PUT /categories/{category_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật một danh mục tùy chỉnh của người dùng. Backend cần kiểm tra quyền sở hữu và đảm bảo đây là danh mục tùy chỉnh (`user_id` từ token).
    * **Request Body:** `{ category_name, parent_category_id, icon }`
    * **Response:** Thông tin danh mục đã cập nhật.
* **`DELETE /categories/{category_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một danh mục tùy chỉnh. Backend cần kiểm tra quyền sở hữu và đảm bảo đây là danh mục tùy chỉnh (`user_id` từ token). Cần kiểm tra xem có giao dịch nào đang sử dụng không, hoặc xử lý logic liên quan.
    * **Response:** Success/Failure message.

**IV. Transactions (Giao dịch)**

* **`POST /transactions`** `(Auth Required)`
    * **Mô tả:** Tạo một giao dịch mới cho người dùng (`user_id` từ token). Backend cần tự động xác định `transaction_type` dựa trên `category_id`, kiểm tra `account_id` thuộc về người dùng, và cập nhật `current_balance` của `account_id`.
    * **Request Body:** `{ account_id, category_id, amount, transaction_date, description (optional), location (optional), tags (optional: list of tag_ids or tag_names) }`
    * **Response:** Thông tin giao dịch vừa tạo.
* **`GET /transactions`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách giao dịch của người dùng (`user_id` từ token), hỗ trợ lọc và phân trang.
    * **Query Params (Optional):** `start_date`, `end_date`, `account_id`, `category_id`, `type=income/expense`, `tag_id`, `page=1`, `limit=20`, `sort_by=transaction_date`, `order=desc/asc`
    * **Response:** Mảng các đối tượng giao dịch và thông tin phân trang.
* **`GET /transactions/{transaction_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết một giao dịch. Backend cần kiểm tra giao dịch này thuộc về người dùng (`user_id` từ token).
    * **Response:** Đối tượng giao dịch chi tiết (có thể kèm theo tags).
* **`PUT /transactions/{transaction_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật một giao dịch. Backend cần kiểm tra quyền sở hữu (`user_id` từ token). Cần tính toán lại số dư tài khoản nếu `amount` hoặc `account_id` thay đổi.
    * **Request Body:** `{ account_id, category_id, amount, transaction_date, description, location }`
    * **Response:** Thông tin giao dịch đã cập nhật.
* **`DELETE /transactions/{transaction_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một giao dịch. Backend cần kiểm tra quyền sở hữu (`user_id` từ token). Cần tính toán lại số dư tài khoản.
    * **Response:** Success/Failure message.
* **`POST /transactions/{transaction_id}/tags`** `(Auth Required)`
    * **Mô tả:** Gắn một hoặc nhiều tag vào giao dịch. Backend cần kiểm tra quyền sở hữu giao dịch (`user_id` từ token).
    * **Request Body:** `{ tag_ids: [id1, id2] }` hoặc `{ tag_names: ["tag1", "tag2"] }` (backend xử lý tạo tag mới cho người dùng nếu chưa có)
    * **Response:** Danh sách tag hiện tại của giao dịch.
* **`DELETE /transactions/{transaction_id}/tags/{tag_id}`** `(Auth Required)`
    * **Mô tả:** Gỡ bỏ một tag khỏi giao dịch. Backend cần kiểm tra quyền sở hữu giao dịch (`user_id` từ token).
    * **Response:** Success/Failure message.

**V. Budgets (Ngân sách)**

* **`POST /budgets`** `(Auth Required)`
    * **Mô tả:** Tạo một ngân sách mới cho người dùng (`user_id` từ token) cho một danh mục trong một khoảng thời gian. Backend cần kiểm tra `category_id` hợp lệ và có thể truy cập bởi người dùng.
    * **Request Body:** `{ category_id, amount, start_date, end_date }`
    * **Response:** Thông tin ngân sách vừa tạo.
* **`GET /budgets`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách ngân sách của người dùng (`user_id` từ token).
    * **Query Params (Optional):** `month`, `year`, `category_id`, `active_date` (lấy budget có hiệu lực vào ngày này)
    * **Response:** Mảng các đối tượng ngân sách.
* **`GET /budgets/{budget_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết một ngân sách. Backend cần kiểm tra ngân sách này thuộc về người dùng (`user_id` từ token).
    * **Response:** Đối tượng ngân sách chi tiết.
* **`PUT /budgets/{budget_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật một ngân sách. Backend cần kiểm tra quyền sở hữu (`user_id` từ token).
    * **Request Body:** `{ amount, start_date, end_date }`
    * **Response:** Thông tin ngân sách đã cập nhật.
* **`DELETE /budgets/{budget_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một ngân sách. Backend cần kiểm tra quyền sở hữu (`user_id` từ token).
    * **Response:** Success/Failure message.

**VI. Goals (Mục tiêu tiết kiệm)**

* **`POST /goals`** `(Auth Required)`
    * **Mô tả:** Tạo một mục tiêu tiết kiệm mới cho người dùng (`user_id` từ token).
    * **Request Body:** `{ goal_name, target_amount, target_date (optional) }`
    * **Response:** Thông tin mục tiêu vừa tạo.
* **`GET /goals`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách mục tiêu tiết kiệm của người dùng (`user_id` từ token).
    * **Query Params (Optional):** `status=active/achieved/cancelled`
    * **Response:** Mảng các đối tượng mục tiêu.
* **`GET /goals/{goal_id}`** `(Auth Required)`
    * **Mô tả:** Lấy thông tin chi tiết một mục tiêu. Backend cần kiểm tra mục tiêu này thuộc về người dùng (`user_id` từ token).
    * **Response:** Đối tượng mục tiêu chi tiết.
* **`PUT /goals/{goal_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật thông tin mục tiêu (tên, số tiền đích, hạn chót, trạng thái). Backend cần kiểm tra quyền sở hữu (`user_id` từ token).
    * **Request Body:** `{ goal_name, target_amount, target_date, status }`
    * **Response:** Thông tin mục tiêu đã cập nhật.
* **`PATCH /goals/{goal_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật số tiền hiện có cho mục tiêu (ví dụ: khi người dùng chuyển tiền vào mục tiêu). Backend cần kiểm tra quyền sở hữu (`user_id` từ token) và tự cộng dồn số tiền.
    * **Request Body:** `{ current_amount }` hoặc `{ contribution_amount }` (backend tự cộng dồn)
    * **Response:** Thông tin mục tiêu đã cập nhật.
* **`DELETE /goals/{goal_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một mục tiêu. Backend cần kiểm tra quyền sở hữu (`user_id` từ token).
    * **Response:** Success/Failure message.

**VII. Tags (Nhãn)**

* **`POST /tags`** `(Auth Required)`
    * **Mô tả:** Tạo một tag mới cho người dùng (`user_id` từ token).
    * **Request Body:** `{ tag_name }`
    * **Response:** Thông tin tag vừa tạo.
* **`GET /tags`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách tất cả các tag của người dùng (`user_id` từ token).
    * **Response:** Mảng các đối tượng tag.
* **`PUT /tags/{tag_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật tên của một tag. Backend cần kiểm tra quyền sở hữu (`user_id` từ token).
    * **Request Body:** `{ tag_name }`
    * **Response:** Thông tin tag đã cập nhật.
* **`DELETE /tags/{tag_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một tag. Backend cần kiểm tra quyền sở hữu (`user_id` từ token). Cần xóa các liên kết trong `Transaction_Tags` trước hoặc dùng `ON DELETE CASCADE` trong thiết kế DB.
    * **Response:** Success/Failure message.

**VIII. Recurring Transactions (Giao dịch lặp lại)**

* **`POST /recurring-transactions`** `(Auth Required)`
    * **Mô tả:** Tạo một định nghĩa giao dịch lặp lại mới cho người dùng (`user_id` từ token). Backend cần kiểm tra `account_id` và `category_id` thuộc về hoặc có thể truy cập bởi người dùng.
    * **Request Body:** `{ account_id, category_id, amount, description (optional), frequency, start_date, end_date (optional), next_due_date }`
    * **Response:** Thông tin định nghĩa vừa tạo.
* **`GET /recurring-transactions`** `(Auth Required)`
    * **Mô tả:** Lấy danh sách các định nghĩa giao dịch lặp lại của người dùng (`user_id` từ token).
    * **Query Params (Optional):** `is_active=true/false`
    * **Response:** Mảng các đối tượng định nghĩa.
* **`GET /recurring-transactions/{recurring_transaction_id}`** `(Auth Required)`
    * **Mô tả:** Lấy chi tiết một định nghĩa. Backend cần kiểm tra định nghĩa này thuộc về người dùng (`user_id` từ token).
    * **Response:** Đối tượng định nghĩa chi tiết.
* **`PUT /recurring-transactions/{recurring_transaction_id}`** `(Auth Required)`
    * **Mô tả:** Cập nhật một định nghĩa giao dịch lặp lại. Backend cần kiểm tra quyền sở hữu (`user_id` từ token).
    * **Request Body:** `{ account_id, category_id, amount, description, frequency, start_date, end_date, next_due_date, is_active }`
    * **Response:** Thông tin định nghĩa đã cập nhật.
* **`DELETE /recurring-transactions/{recurring_transaction_id}`** `(Auth Required)`
    * **Mô tả:** Xóa một định nghĩa giao dịch lặp lại. Backend cần kiểm tra quyền sở hữu (`user_id` từ token).
    * **Response:** Success/Failure message.
* **`PATCH /recurring-transactions/{recurring_transaction_id}`** `(Auth Required)`
    * **Mô tả:** Kích hoạt hoặc vô hiệu hóa một định nghĩa lặp lại. Backend cần kiểm tra quyền sở hữu (`user_id` từ token).
    * **Request Body:** `{ is_active: true/false }`
    * **Response:** Thông tin định nghĩa đã cập nhật.

**IX. Reports & Summaries (Báo cáo & Tổng hợp)**

* **`GET /reports/summary`** `(Auth Required)`
    * **Mô tả:** Lấy tổng thu, tổng chi, và dòng tiền ròng trong một khoảng thời gian cho người dùng (`user_id` từ token).
    * **Query Params:** `start_date`, `end_date`, `account_id (optional)` (nếu có account_id, kiểm tra nó thuộc về người dùng)
    * **Response:** `{ total_income, total_expense, net_flow }`
* **`GET /reports/spending-by-category`** `(Auth Required)`
    * **Mô tả:** Lấy tổng chi tiêu theo từng danh mục trong một khoảng thời gian cho người dùng (`user_id` từ token).
    * **Query Params:** `start_date`, `end_date`, `account_id (optional)` (nếu có account_id, kiểm tra nó thuộc về người dùng)
    * **Response:** Mảng các đối tượng `{ category_id, category_name, total_amount, percentage }`
* **`GET /reports/budget-status`** `(Auth Required)`
    * **Mô tả:** So sánh chi tiêu thực tế với ngân sách đã đặt trong một khoảng thời gian cho người dùng (`user_id` từ token).
    * **Query Params:** `month`, `year` (hoặc `start_date`, `end_date`)
    * **Response:** Mảng các đối tượng `{ category_id, category_name, budget_amount, actual_spending, remaining_amount }`

---


