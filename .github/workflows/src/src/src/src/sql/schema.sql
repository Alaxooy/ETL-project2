CREATE DATABASE IF NOT EXISTS etl_demo;
USE etl_demo;

-- Final table with uniqueness to prevent duplicates by invoice_no + stock_code
CREATE TABLE IF NOT EXISTS transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  invoice_no VARCHAR(100) NOT NULL,
  stock_code VARCHAR(50) NOT NULL,
  description TEXT,
  quantity INT,
  invoice_date DATETIME,
  unit_price DECIMAL(10,4),
  customer_id VARCHAR(50),
  country VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_invoice_line (invoice_no, stock_code)
);

-- Staging table (persisted between runs)
CREATE TABLE IF NOT EXISTS staging_transactions (
  invoice_no VARCHAR(100),
  stock_code VARCHAR(50),
  description TEXT,
  quantity INT,
  invoice_date DATETIME,
  unit_price DECIMAL(10,4),
  customer_id VARCHAR(50),
  country VARCHAR(100)
);
