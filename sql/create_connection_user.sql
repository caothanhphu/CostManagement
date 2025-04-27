-- Script tạo database và user cho Cost Management App

-- Tạo User mới với mật khẩu được chỉ định
-- LƯU Ý: Mật khẩu sẽ hiển thị rõ trong script này. Hãy cẩn thận về bảo mật.
CREATE USER costuser WITH PASSWORD 'xZ6q5E-TdZ24mKc';

-- Tạo Database mới
CREATE DATABASE costdb;

-- Cấp tất cả quyền trên database mới cho user mới
GRANT ALL PRIVILEGES ON DATABASE costdb TO costuser;

-- (Tùy chọn nhưng khuyến nghị) Đặt user mới làm chủ sở hữu database mới
ALTER DATABASE costdb OWNER TO costuser;

-- *** Sau khi chạy các lệnh trên, bạn cần kết nối vào database 'costdb' ***
-- *** bằng user 'costuser' để chạy các lệnh tạo bảng bên dưới (nếu muốn). ***
-- *** Hoặc bạn có thể cấp quyền trên schema public ngay từ đây: ***

-- Kết nối tạm thời vào DB mới để cấp quyền schema (chỉ hoạt động trong psql)
-- Nếu không dùng psql, hãy kết nối lại vào DB 'costdb' bằng user 'postgres' hoặc 'costuser' rồi chạy các lệnh GRANT dưới đây.
-- \c costdb

-- Cấp quyền sử dụng và tạo đối tượng trên schema 'public' cho user mới
-- Điều này cần thiết để user có thể tạo bảng, sequence,... trong schema mặc định.
GRANT USAGE, CREATE ON SCHEMA public TO costuser;

-- (Tùy chọn nhưng hữu ích) Cấp quyền mặc định cho các đối tượng sẽ được tạo trong tương lai
-- Để user 'costuser' có thể truy cập các bảng/sequence/function được tạo bởi user khác (nếu có) trong schema public
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO costuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO costuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO costuser;


-- Hoàn tất! Bây giờ bạn có thể kết nối vào database 'costdb' bằng user 'costuser'
-- và chạy script tạo bảng (sql/script.sql) của bạn.
