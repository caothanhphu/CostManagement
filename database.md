Chắc chắn rồi, đây là nội dung file SQL của bạn được chuyển đổi sang định dạng Markdown (MD).

```markdown
# Tài liệu Lược đồ Cơ sở dữ liệu PostgreSQL

Script này định nghĩa cấu trúc cho một cơ sở dữ liệu PostgreSQL, bao gồm các kiểu dữ liệu tùy chỉnh (ENUM), bảng, hàm, trigger và index.

## Các Kiểu Dữ liệu Tùy chỉnh (ENUM Types)

Các kiểu ENUM sau được tạo để đảm bảo tính nhất quán của dữ liệu cho các trường cụ thể:

* **`account_type`**: Xác định loại tài khoản.
    * `'cash'`
    * `'bank_account'`
    * `'credit_card'`
    * `'e_wallet'`
    * `'investment'`
    * `'other'`
* **`category_type`**: Phân loại danh mục là thu nhập hay chi phí.
    * `'expense'`
    * `'income'`
* **`recurrence_frequency`**: Định nghĩa tần suất lặp lại cho các giao dịch.
    * `'daily'`
    * `'weekly'`
    * `'monthly'`
    * `'yearly'`

```sql
-- Create ENUM types first (PostgreSQL specific)
CREATE TYPE account_type AS ENUM ('cash', 'bank_account', 'credit_card', 'e_wallet', 'investment', 'other');
CREATE TYPE category_type AS ENUM ('expense', 'income');
CREATE TYPE recurrence_frequency AS ENUM ('daily', 'weekly', 'monthly', 'yearly');
```

## Hàm và Trigger Cập nhật Timestamp

Một hàm và các trigger tương ứng được tạo để tự động cập nhật trường `updated_at` mỗi khi một hàng trong các bảng được chỉ định được cập nhật.

```sql
-- Add trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

Hàm `trigger_set_timestamp()` này được sử dụng bởi các trigger trên các bảng `Users`, `Accounts`, `Categories`, `Transactions`, `Budgets`, `Goals`, `Tags`, và `RecurringTransactions`.

## Bảng: Users

Lưu trữ thông tin người dùng.

| Tên Cột          | Kiểu Dữ liệu   | Ràng buộc / Chú thích                                  |
| :--------------- | :------------- | :----------------------------------------------------- |
| `user_id`        | `BIGSERIAL`    | Khóa chính                                             |
| `username`       | `VARCHAR(50)`  | `UNIQUE`, `NOT NULL`                                   |
| `email`          | `VARCHAR(255)` | `UNIQUE`, `NOT NULL`                                   |
| `password_hash`  | `VARCHAR(255)` | `NOT NULL`                                             |
| `full_name`      | `VARCHAR(100)` |                                                        |
| `default_currency`| `VARCHAR(3)`   | `NOT NULL`, `DEFAULT 'VND'`                           |
| `created_at`     | `TIMESTAMPTZ`  | `NOT NULL`, `DEFAULT NOW()`                            |
| `updated_at`     | `TIMESTAMPTZ`  | `NOT NULL`, `DEFAULT NOW()` (Tự động cập nhật bởi trigger) |

**Trigger:**
* `set_timestamp_users`: Thực thi `trigger_set_timestamp()` trước khi cập nhật.

```sql
-- Table: Users
CREATE TABLE Users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    default_currency VARCHAR(3) NOT NULL DEFAULT 'VND',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON Users
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
```

## Bảng: Accounts

Lưu trữ thông tin tài khoản của người dùng.

| Tên Cột           | Kiểu Dữ liệu     | Ràng buộc / Chú thích                                                            |
| :---------------- | :--------------- | :------------------------------------------------------------------------------- |
| `account_id`      | `BIGSERIAL`      | Khóa chính                                                                       |
| `user_id`         | `BIGINT`         | `NOT NULL`, Khóa ngoại tham chiếu `Users(user_id)`, `ON DELETE CASCADE`           |
| `account_name`    | `VARCHAR(100)`   | `NOT NULL`                                                                       |
| `account_type`    | `account_type`   | `NOT NULL` (Sử dụng ENUM `account_type`)                                         |
| `initial_balance` | `DECIMAL(18, 2)` | `NOT NULL`, `DEFAULT 0.00`                                                       |
| `current_balance` | `DECIMAL(18, 2)` | `NOT NULL`, `DEFAULT 0.00`                                                       |
| `currency`        | `VARCHAR(3)`     | `NOT NULL`                                                                       |
| `is_active`       | `BOOLEAN`        | `NOT NULL`, `DEFAULT TRUE` (Cho phép ẩn/lưu trữ tài khoản)                        |
| `created_at`      | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()`                                                      |
| `updated_at`      | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()` (Tự động cập nhật bởi trigger)                       |

**Indexes:**
* `idx_accounts_user_id`: Trên cột `user_id`.

**Trigger:**
* `set_timestamp_accounts`: Thực thi `trigger_set_timestamp()` trước khi cập nhật.

```sql
-- Table: Accounts
CREATE TABLE Accounts (
    account_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    account_type account_type NOT NULL,
    initial_balance DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    current_balance DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE, -- To allow hiding/archiving accounts
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE -- If user is deleted, their accounts are also deleted
);

CREATE INDEX idx_accounts_user_id ON Accounts(user_id);

CREATE TRIGGER set_timestamp_accounts
BEFORE UPDATE ON Accounts
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
```

## Bảng: Categories

Lưu trữ các danh mục chi tiêu và thu nhập (cả mặc định của hệ thống và tùy chỉnh của người dùng).

| Tên Cột              | Kiểu Dữ liệu     | Ràng buộc / Chú thích                                                                                                |
| :------------------- | :--------------- | :------------------------------------------------------------------------------------------------------------------- |
| `category_id`        | `BIGSERIAL`      | Khóa chính                                                                                                           |
| `user_id`            | `BIGINT`         | Có thể `NULL` (cho danh mục hệ thống), Khóa ngoại tham chiếu `Users(user_id)`, `ON DELETE CASCADE` (cho danh mục người dùng) |
| `category_name`      | `VARCHAR(100)`   | `NOT NULL`, Phải là duy nhất cho mỗi user (hoặc duy nhất cho hệ thống nếu `user_id` là `NULL`)                      |
| `parent_category_id` | `BIGINT`         | Khóa ngoại tự tham chiếu `Categories(category_id)`, `ON DELETE SET NULL` (biến thành danh mục cấp cao nhất nếu cha bị xóa) |
| `category_type`      | `category_type`  | `NOT NULL` (Sử dụng ENUM `category_type`)                                                                            |
| `icon`               | `VARCHAR(50)`    |                                                                                                                      |
| `is_custom`          | `BOOLEAN`        | `NOT NULL`, `DEFAULT TRUE` (Phân biệt danh mục tùy chỉnh và hệ thống)                                               |
| `created_at`         | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()`                                                                                          |
| `updated_at`         | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()` (Tự động cập nhật bởi trigger)                                                           |

**Indexes:**
* `idx_categories_system_name`: `UNIQUE` trên `category_name` khi `user_id IS NULL`.
* `idx_categories_user_name`: `UNIQUE` trên (`user_id`, `category_name`) khi `user_id IS NOT NULL`.
* `idx_categories_user_id`: Trên cột `user_id`.
* `idx_categories_parent_id`: Trên cột `parent_category_id`.
* `idx_categories_type`: Trên cột `category_type`.

**Trigger:**
* `set_timestamp_categories`: Thực thi `trigger_set_timestamp()` trước khi cập nhật.

```sql
-- Table: Categories
CREATE TABLE Categories (
    category_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT, -- Nullable for system default categories
    category_name VARCHAR(100) NOT NULL,
    parent_category_id BIGINT, -- Self-referencing for sub-categories
    category_type category_type NOT NULL,
    icon VARCHAR(50),
    is_custom BOOLEAN NOT NULL DEFAULT TRUE, -- Flag for custom vs system categories
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_category
        FOREIGN KEY(user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE, -- If user is deleted, their custom categories are also deleted
    CONSTRAINT fk_parent_category
        FOREIGN KEY(parent_category_id)
        REFERENCES Categories(category_id)
        ON DELETE SET NULL -- If parent category is deleted, make sub-category top-level
);

-- Ensure unique category name per user (and for system categories)
-- For system categories (user_id IS NULL), name must be unique
CREATE UNIQUE INDEX idx_categories_system_name ON Categories (category_name) WHERE user_id IS NULL;
-- For user categories, name must be unique within that user's categories
CREATE UNIQUE INDEX idx_categories_user_name ON Categories (user_id, category_name) WHERE user_id IS NOT NULL;

CREATE INDEX idx_categories_user_id ON Categories(user_id);
CREATE INDEX idx_categories_parent_id ON Categories(parent_category_id);
CREATE INDEX idx_categories_type ON Categories(category_type);

CREATE TRIGGER set_timestamp_categories
BEFORE UPDATE ON Categories
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
```

## Bảng: Transactions

Lưu trữ các giao dịch tài chính của người dùng.

| Tên Cột           | Kiểu Dữ liệu     | Ràng buộc / Chú thích                                                                 |
| :---------------- | :--------------- | :------------------------------------------------------------------------------------ |
| `transaction_id`  | `BIGSERIAL`      | Khóa chính                                                                            |
| `user_id`         | `BIGINT`         | `NOT NULL`, Khóa ngoại tham chiếu `Users(user_id)`, `ON DELETE CASCADE`                |
| `account_id`      | `BIGINT`         | `NOT NULL`, Khóa ngoại tham chiếu `Accounts(account_id)`, `ON DELETE RESTRICT`         |
| `category_id`     | `BIGINT`         | `NOT NULL`, Khóa ngoại tham chiếu `Categories(category_id)`, `ON DELETE RESTRICT`      |
| `amount`          | `DECIMAL(18, 2)` | `NOT NULL`, `CHECK (amount >= 0)` (Số tiền luôn dương)                                 |
| `transaction_type`| `category_type`  | `NOT NULL` (Lưu trữ tường minh loại để truy vấn dễ hơn, sử dụng ENUM `category_type`) |
| `transaction_date`| `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()`                                                           |
| `description`     | `TEXT`           |                                                                                       |
| `location`        | `VARCHAR(255)`   |                                                                                       |
| `created_at`      | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()`                                                           |
| `updated_at`      | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()` (Tự động cập nhật bởi trigger)                            |

**Indexes:**
* `idx_transactions_user_id`: Trên cột `user_id`.
* `idx_transactions_account_id`: Trên cột `account_id`.
* `idx_transactions_category_id`: Trên cột `category_id`.
* `idx_transactions_date`: Trên cột `transaction_date`.
* `idx_transactions_type`: Trên cột `transaction_type`.

**Trigger:**
* `set_timestamp_transactions`: Thực thi `trigger_set_timestamp()` trước khi cập nhật.

```sql
-- Table: Transactions
CREATE TABLE Transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    account_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    amount DECIMAL(18, 2) NOT NULL CHECK (amount >= 0), -- Amount is always positive
    transaction_type category_type NOT NULL, -- Explicitly store type for easier querying
    transaction_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT,
    location VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_transaction
        FOREIGN KEY(user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE, -- If user is deleted, their transactions are deleted
    CONSTRAINT fk_account_transaction
        FOREIGN KEY(account_id)
        REFERENCES Accounts(account_id)
        ON DELETE RESTRICT, -- Prevent deleting account if transactions exist (or handle in logic)
    CONSTRAINT fk_category_transaction
        FOREIGN KEY(category_id)
        REFERENCES Categories(category_id)
        ON DELETE RESTRICT -- Prevent deleting category if transactions exist (or handle in logic)
);

CREATE INDEX idx_transactions_user_id ON Transactions(user_id);
CREATE INDEX idx_transactions_account_id ON Transactions(account_id);
CREATE INDEX idx_transactions_category_id ON Transactions(category_id);
CREATE INDEX idx_transactions_date ON Transactions(transaction_date);
CREATE INDEX idx_transactions_type ON Transactions(transaction_type);

CREATE TRIGGER set_timestamp_transactions
BEFORE UPDATE ON Transactions
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
```

## Bảng: Budgets

Lưu trữ ngân sách do người dùng thiết lập cho các danh mục cụ thể trong một khoảng thời gian.

| Tên Cột       | Kiểu Dữ liệu     | Ràng buộc / Chú thích                                                                                             |
| :------------ | :--------------- | :--------------------------------------------------------------------------------------------------------------- |
| `budget_id`   | `BIGSERIAL`      | Khóa chính                                                                                                       |
| `user_id`     | `BIGINT`         | `NOT NULL`, Khóa ngoại tham chiếu `Users(user_id)`, `ON DELETE CASCADE`                                           |
| `category_id` | `BIGINT`         | `NOT NULL`, Khóa ngoại tham chiếu `Categories(category_id)`, `ON DELETE CASCADE` (Xóa ngân sách nếu danh mục bị xóa) |
| `amount`      | `DECIMAL(18, 2)` | `NOT NULL`, `CHECK (amount > 0)`                                                                                 |
| `start_date`  | `DATE`           | `NOT NULL`                                                                                                       |
| `end_date`    | `DATE`           | `NOT NULL`, `CHECK (start_date <= end_date)`                                                                     |
| `created_at`  | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()`                                                                                      |
| `updated_at`  | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()` (Tự động cập nhật bởi trigger)                                                       |

**Ràng buộc:**
* `unique_budget_period`: `UNIQUE` trên (`user_id`, `category_id`, `start_date`, `end_date`) để tránh trùng lặp ngân sách.
* `valid_dates`: `CHECK (start_date <= end_date)`.

**Indexes:**
* `idx_budgets_user_id`: Trên cột `user_id`.
* `idx_budgets_category_id`: Trên cột `category_id`.
* `idx_budgets_period`: Trên cột (`start_date`, `end_date`).

**Trigger:**
* `set_timestamp_budgets`: Thực thi `trigger_set_timestamp()` trước khi cập nhật.

```sql
-- Table: Budgets
CREATE TABLE Budgets (
    budget_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    amount DECIMAL(18, 2) NOT NULL CHECK (amount > 0),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_budget
        FOREIGN KEY(user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_category_budget
        FOREIGN KEY(category_id)
        REFERENCES Categories(category_id)
        ON DELETE CASCADE, -- If category deleted, associated budget deleted
    CONSTRAINT unique_budget_period UNIQUE (user_id, category_id, start_date, end_date), -- Prevent duplicate budgets for same category/period
    CONSTRAINT valid_dates CHECK (start_date <= end_date)
);

CREATE INDEX idx_budgets_user_id ON Budgets(user_id);
CREATE INDEX idx_budgets_category_id ON Budgets(category_id);
CREATE INDEX idx_budgets_period ON Budgets(start_date, end_date);

CREATE TRIGGER set_timestamp_budgets
BEFORE UPDATE ON Budgets
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
```

## Bảng: Goals

Lưu trữ các mục tiêu tài chính của người dùng.

| Tên Cột         | Kiểu Dữ liệu     | Ràng buộc / Chú thích                                              |
| :-------------- | :--------------- | :----------------------------------------------------------------- |
| `goal_id`       | `BIGSERIAL`      | Khóa chính                                                         |
| `user_id`       | `BIGINT`         | `NOT NULL`, Khóa ngoại tham chiếu `Users(user_id)`, `ON DELETE CASCADE` |
| `goal_name`     | `VARCHAR(150)`   | `NOT NULL`                                                         |
| `target_amount` | `DECIMAL(18, 2)` | `NOT NULL`, `CHECK (target_amount > 0)`                            |
| `current_amount`| `DECIMAL(18, 2)` | `NOT NULL`, `DEFAULT 0.00`, `CHECK (current_amount >= 0)`          |
| `target_date`   | `DATE`           | Có thể `NULL` (Hạn chót tùy chọn)                                   |
| `status`        | `VARCHAR(20)`    | `NOT NULL`, `DEFAULT 'active'` (vd: 'active', 'achieved', 'cancelled') |
| `created_at`    | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()`                                        |
| `updated_at`    | `TIMESTAMPTZ`    | `NOT NULL`, `DEFAULT NOW()` (Tự động cập nhật bởi trigger)         |

**Indexes:**
* `idx_goals_user_id`: Trên cột `user_id`.

**Trigger:**
* `set_timestamp_goals`: Thực thi `trigger_set_timestamp()` trước khi cập nhật.

```sql
-- Table: Goals
CREATE TABLE Goals (
    goal_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    goal_name VARCHAR(150) NOT NULL,
    target_amount DECIMAL(18, 2) NOT NULL CHECK (target_amount > 0),
    current_amount DECIMAL(18, 2) NOT NULL DEFAULT 0.00 CHECK (current_amount >= 0),
    target_date DATE, -- Optional deadline
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- e.g., 'active', 'achieved', 'cancelled'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_goal
        FOREIGN KEY(user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_goals_user_id ON Goals(user_id);

CREATE TRIGGER set_timestamp_goals
BEFORE UPDATE ON Goals
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
```

## Bảng: Tags

Lưu trữ các thẻ (tag) do người dùng định nghĩa để gắn vào giao dịch.

| Tên Cột       | Kiểu Dữ liệu   | Ràng buộc / Chú thích                                                       |
| :------------ | :------------- | :------------------------------------------------------------------------- |
| `tag_id`      | `BIGSERIAL`    | Khóa chính                                                                 |
| `user_id`     | `BIGINT`       | `NOT NULL`, Khóa ngoại tham chiếu `Users(user_id)`, `ON DELETE CASCADE`      |
| `tag_name`    | `VARCHAR(50)`  | `NOT NULL`, `UNIQUE` trên (`user_id`, `tag_name`) (Tên thẻ duy nhất cho mỗi user) |
| `created_at`  | `TIMESTAMPTZ`  | `NOT NULL`, `DEFAULT NOW()`                                                |
| `updated_at`  | `TIMESTAMPTZ`  | `NOT NULL`, `DEFAULT NOW()` (Tự động cập nhật bởi trigger)                 |

**Ràng buộc:**
* `unique_tag_per_user`: `UNIQUE` trên (`user_id`, `tag_name`).

**Indexes:**
* `idx_tags_user_id`: Trên cột `user_id`.

**Trigger:**
* `set_timestamp_tags`: Thực thi `trigger_set_timestamp()` trước khi cập nhật.

```sql
-- Table: Tags
CREATE TABLE Tags (
    tag_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    tag_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_tag
        FOREIGN KEY(user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT unique_tag_per_user UNIQUE (user_id, tag_name) -- Ensure unique tag names per user
);

CREATE INDEX idx_tags_user_id ON Tags(user_id);

CREATE TRIGGER set_timestamp_tags
BEFORE UPDATE ON Tags
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
```

## Bảng: Transaction_Tags (Bảng nối)

Bảng trung gian để tạo mối quan hệ nhiều-nhiều giữa `Transactions` và `Tags`.

| Tên Cột          | Kiểu Dữ liệu | Ràng buộc / Chú thích                                                            |
| :--------------- | :----------- | :------------------------------------------------------------------------------- |
| `transaction_id` | `BIGINT`     | `NOT NULL`, Khóa ngoại tham chiếu `Transactions(transaction_id)`, `ON DELETE CASCADE` |
| `tag_id`         | `BIGINT`     | `NOT NULL`, Khóa ngoại tham chiếu `Tags(tag_id)`, `ON DELETE CASCADE`             |

**Ràng buộc:**
* Khóa chính phức hợp trên (`transaction_id`, `tag_id`).

**Indexes:**
* `idx_transaction_tags_tran_id`: Trên cột `transaction_id`.
* `idx_transaction_tags_tag_id`: Trên cột `tag_id`.

```sql
-- Table: Transaction_Tags (Junction Table for Many-to-Many relationship)
CREATE TABLE Transaction_Tags (
    transaction_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    PRIMARY KEY (transaction_id, tag_id), -- Composite primary key
    CONSTRAINT fk_transaction_tag_tran
        FOREIGN KEY(transaction_id)
        REFERENCES Transactions(transaction_id)
        ON DELETE CASCADE, -- If transaction is deleted, remove the tag link
    CONSTRAINT fk_transaction_tag_tag
        FOREIGN KEY(tag_id)
        REFERENCES Tags(tag_id)
        ON DELETE CASCADE -- If tag is deleted, remove the link from transactions
);

CREATE INDEX idx_transaction_tags_tran_id ON Transaction_Tags(transaction_id);
CREATE INDEX idx_transaction_tags_tag_id ON Transaction_Tags(tag_id);
```

## Bảng: RecurringTransactions

Lưu trữ thông tin về các giao dịch lặp lại (định kỳ).

| Tên Cột                   | Kiểu Dữ liệu           | Ràng buộc / Chú thích                                                              |
| :------------------------ | :--------------------- | :-------------------------------------------------------------------------------- |
| `recurring_transaction_id`| `BIGSERIAL`            | Khóa chính                                                                        |
| `user_id`                 | `BIGINT`               | `NOT NULL`, Khóa ngoại tham chiếu `Users(user_id)`, `ON DELETE CASCADE`            |
| `account_id`              | `BIGINT`               | `NOT NULL`, Khóa ngoại tham chiếu `Accounts(account_id)`, `ON DELETE RESTRICT`     |
| `category_id`             | `BIGINT`               | `NOT NULL`, Khóa ngoại tham chiếu `Categories(category_id)`, `ON DELETE RESTRICT`  |
| `amount`                  | `DECIMAL(18, 2)`       | `NOT NULL`, `CHECK (amount >= 0)`                                                 |
| `transaction_type`        | `category_type`        | `NOT NULL` (Sử dụng ENUM `category_type`)                                         |
| `description`             | `TEXT`                 |                                                                                   |
| `frequency`               | `recurrence_frequency` | `NOT NULL` (Sử dụng ENUM `recurrence_frequency`)                                  |
| `start_date`              | `DATE`                 | `NOT NULL`                                                                        |
| `end_date`                | `DATE`                 | Có thể `NULL` (nghĩa là lặp lại vô hạn), `CHECK (end_date IS NULL OR start_date <= end_date)` |
| `next_due_date`           | `DATE`                 | `NOT NULL`, `CHECK (next_due_date >= start_date)` (Ngày tạo giao dịch tiếp theo)  |
| `last_created_date`       | `DATE`                 | Có thể `NULL` (Ngày tạo giao dịch gần nhất)                                        |
| `is_active`               | `BOOLEAN`              | `NOT NULL`, `DEFAULT TRUE`                                                        |
| `created_at`              | `TIMESTAMPTZ`          | `NOT NULL`, `DEFAULT NOW()`                                                       |
| `updated_at`              | `TIMESTAMPTZ`          | `NOT NULL`, `DEFAULT NOW()` (Tự động cập nhật bởi trigger)                        |

**Ràng buộc:**
* `valid_recurring_dates`: `CHECK (end_date IS NULL OR start_date <= end_date)`.
* `valid_next_due`: `CHECK (next_due_date >= start_date)`.

**Indexes:**
* `idx_recurring_user_id`: Trên cột `user_id`.
* `idx_recurring_account_id`: Trên cột `account_id`.
* `idx_recurring_category_id`: Trên cột `category_id`.
* `idx_recurring_next_due`: Trên cột `next_due_date`.
* `idx_recurring_active`: Trên cột `is_active`.

**Trigger:**
* `set_timestamp_recurring`: Thực thi `trigger_set_timestamp()` trước khi cập nhật.

```sql
-- Table: RecurringTransactions
CREATE TABLE RecurringTransactions (
    recurring_transaction_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    account_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    amount DECIMAL(18, 2) NOT NULL CHECK (amount >= 0),
    transaction_type category_type NOT NULL,
    description TEXT,
    frequency recurrence_frequency NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE, -- Nullable means it continues indefinitely
    next_due_date DATE NOT NULL, -- Date the next transaction should be created
    last_created_date DATE, -- Date the last instance was created
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_recurring
        FOREIGN KEY(user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_account_recurring
        FOREIGN KEY(account_id)
        REFERENCES Accounts(account_id)
        ON DELETE RESTRICT, -- Or maybe SET NULL / Deactivate if account is deleted? Requires thought. RESTRICT is safer.
    CONSTRAINT fk_category_recurring
        FOREIGN KEY(category_id)
        REFERENCES Categories(category_id)
        ON DELETE RESTRICT, -- Safer
    CONSTRAINT valid_recurring_dates CHECK (end_date IS NULL OR start_date <= end_date),
    CONSTRAINT valid_next_due CHECK (next_due_date >= start_date)
);

CREATE INDEX idx_recurring_user_id ON RecurringTransactions(user_id);
CREATE INDEX idx_recurring_account_id ON RecurringTransactions(account_id);
CREATE INDEX idx_recurring_category_id ON RecurringTransactions(category_id);
CREATE INDEX idx_recurring_next_due ON RecurringTransactions(next_due_date);
CREATE INDEX idx_recurring_active ON RecurringTransactions(is_active);

CREATE TRIGGER set_timestamp_recurring
BEFORE UPDATE ON RecurringTransactions
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
```

```

Hy vọng tài liệu Markdown này hữu ích cho bạn!