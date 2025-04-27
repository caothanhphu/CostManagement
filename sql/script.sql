
-- Use this script to create the tables in your PostgreSQL database.

-- Create ENUM types first (PostgreSQL specific)
CREATE TYPE account_type AS ENUM ('cash', 'bank_account', 'credit_card', 'e_wallet', 'investment', 'other');
CREATE TYPE category_type AS ENUM ('expense', 'income');
CREATE TYPE recurrence_frequency AS ENUM ('daily', 'weekly', 'monthly', 'yearly');

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

-- Add trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON Users
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

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

-- End of script