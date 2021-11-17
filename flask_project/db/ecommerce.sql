PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "user" (
  "id" integer PRIMARY KEY NOT NULL,
  "username" text UNIQUE COLLATE NOCASE NOT NULL,
  "password" text NOT NULL,
  "email" text NOT NULL,
  "phone" int NOT NULL,
  "is_admin" int NOT NULL,
  "is_authenticated" int NOT NULL
);



CREATE TABLE IF NOT EXISTS "product" (
  "id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  "name" text NOT NULL,
  "unit_price" real NOT NULL,
  "brand" text,
  "category" text NOT NULL,
  "description" text,
  "delivery_days" int NOT NULL,
  "warranty_days" int NOT NULL,
  "stock" int NOT NULL,
  "image_url" text,
  "is_deleted" int NOT NULL
);

CREATE TABLE IF NOT EXISTS "cart_item" (
  "id" integer PRIMARY KEY NOT NULL,
  "product_id" int NOT NULL,
  "user_id" int NOT NULL,
  "quantity" int NOT NULL,
  FOREIGN KEY ("product_id") REFERENCES product("id"),
  FOREIGN KEY ("user_id") REFERENCES cart("id")
);

CREATE TABLE IF NOT EXISTS "billing" (
  "id" integer PRIMARY KEY NOT NULL,
  "user_id" int UNIQUE NOT NULL,
  "address" text,
  "country" text,
  "state" text,
  "zip_code" text,
  FOREIGN KEY ("user_id") REFERENCES user("id")
);

CREATE TABLE IF NOT EXISTS "payment" (
  "id" integer PRIMARY KEY NOT NULL,
  "user_id" int UNIQUE NOT NULL,
  "name" text,
  "number" text,
  "expiry" text,
  "cvc" text,
  FOREIGN KEY ("user_id") REFERENCES user("id")
);

CREATE TABLE IF NOT EXISTS "billing_past" (
  "id" integer PRIMARY KEY NOT NULL,
  "address" text,
  "country" text,
  "state" text,
  "zip_code" text
);

CREATE TABLE IF NOT EXISTS "payment_past" (
  "id" integer PRIMARY KEY NOT NULL,
  "name" text,
  "number" text,
  "expiry" text,
  "cvc" text
);

CREATE TABLE IF NOT EXISTS "order2" (
  "id" integer PRIMARY KEY NOT NULL,
  "user_id" int NOT NULL,
  "payment_past_id" int NOT NULL,
  "billing_past_id" int NOT NULL,
  "subtotal" real NOT NULL,
  "discount" real NOT NULL,
  "total_cost" real NOT NULL,
  "total_items" int  NOT NULL,
  FOREIGN KEY ("user_id") REFERENCES user("id"),
  FOREIGN KEY ("payment_past_id") REFERENCES payment_past("id"),
  FOREIGN KEY ("billing_past_id") REFERENCES billing_past("id")
);

CREATE TABLE IF NOT EXISTS "order2_item" (
  "id" integer PRIMARY KEY NOT NULL,
  "order2_id" int NOT NULL,
  "product_id" int NOT NULL,
  "quantity" int not NULL,
  "price" real not NULL,
  FOREIGN KEY ("order2_id") REFERENCES order2("id"),
  FOREIGN KEY ("product_id") REFERENCES product("id")

);

CREATE TABLE IF NOT EXISTS "cafepass" (
  "id" integer PRIMARY KEY NOT NULL,
  "user_id" int NOT NULL,
  "paid" int NOT NULL,
  "net_xp" int NOT NULL,
  "level" int NOT NULL,
  FOREIGN KEY ("user_id") REFERENCES user("id")
);

CREATE TABLE IF NOT EXISTS "level" (
  "id" integer PRIMARY KEY NOT NULL,
  "level" int NOT NULL,
  "xp" int NOT NULL,
  "discount_free" real NOT NULL,
  "discount_paid" real NOT NULL
);
