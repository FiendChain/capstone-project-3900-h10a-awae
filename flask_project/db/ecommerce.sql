PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "users" (
  "id" integer PRIMARY KEY NOT NULL,
  "username" text UNIQUE COLLATE NOCASE NOT NULL,
  "password" text,
  "email" text,
  "phone" int,
  "is_admin" int,
  "is_authenticated" int
);

CREATE TABLE IF NOT EXISTS "products" (
  "id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  "name" text,
  "unit_price" real,
  "brand" text,
  "category" text,
  "description" text,
  "delivery_days" int,
  "warranty_days" int,
  "stock" int,
  "image_url" text
);

CREATE TABLE IF NOT EXISTS "cart_item" (
  "id" integer PRIMARY KEY NOT NULL,
  "product_id" int NOT NULL,
  "user_id" int NOT NULL,
  "quantity" int NOT NULL,
  FOREIGN KEY ("product_id") REFERENCES Product("id"),
  FOREIGN KEY ("user_id") REFERENCES Cart("id")
);

CREATE TABLE IF NOT EXISTS "cart" (
  "id" integer PRIMARY KEY NOT NULL,
  "user_id" int UNIQUE NOT NULL
);

