PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "users" (
  "id" integer PRIMARY KEY NOT NULL,
  "username" text,
  "password" text,
  "email" text,
  "first_name" text,
  "last_name" text,
  "dob" text,
  "is_admin" int
);

CREATE TABLE IF NOT EXISTS "products" (
  "id" integer PRIMARY KEY NOT NULL,
  "name" text,
  "price" real,
  "brand" text,
  "category" text,
  "description" text,
  "delivery" int,
  "warranty" int,
  "image_link" text
);

CREATE TABLE IF NOT EXISTS "cart_item" (
  "id" integer PRIMARY KEY NOT NULL,
  "product_id" int UNIQUE NOT NULL,
  "cart_id" int UNIQUE NOT NULL,
  "quantity" int DEFAULT 1,
  FOREIGN KEY ("product_id") REFERENCES Product("id"),
  FOREIGN KEY ("cart_id") REFERENCES Cart("id")
);

CREATE TABLE IF NOT EXISTS "cart" (
  "id" integer PRIMARY KEY NOT NULL,
  "user_id" int UNIQUE NOT NULL
);

