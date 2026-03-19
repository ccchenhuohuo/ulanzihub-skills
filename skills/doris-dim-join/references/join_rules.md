# JOIN 规则与 SQL 模板

## Join Key 规则

| 站点 | Join Key | 说明 |
|------|----------|------|
| CN | product_id + year_num | 使用product_id匹配 |
| US/JP/DE | sku_id + year_num + site | 使用sku_id+site匹配 |
| MX/BR | - | 数据全部剔除（不参与JOIN） |

## SQL 模板

### 1. 修改维度表字段名

```sql
ALTER TABLE flywheel.product_category_dimension
CHANGE COLUMN category_1 stdcategory1 VARCHAR(100);

ALTER TABLE flywheel.product_category_dimension
CHANGE COLUMN category_2 stdcategory2 VARCHAR(100);

ALTER TABLE flywheel.product_category_dimension
CHANGE COLUMN category_3 stdcategory3 VARCHAR(100);
```

### 2. 创建目标表

```sql
CREATE TABLE flywheel.monthly_sales_with_dim (
  platform VARCHAR(20),
  site VARCHAR(20),
  product_id VARCHAR(50),
  sku_id VARCHAR(50),
  product_title VARCHAR(1024),
  sku_title VARCHAR(3000),
  product_title_cn VARCHAR(1024),
  product_url VARCHAR(255),
  product_image VARCHAR(512),

  -- 新增dim表的分类字段
  stdcategory1 VARCHAR(100),
  stdcategory2 VARCHAR(100),
  stdcategory3 VARCHAR(100),
  device_type VARCHAR(50),

  -- 保留其他销售字段
  brand_name VARCHAR(255),
  std_brand_name VARCHAR(255),
  shop_id VARCHAR(100),
  shop_name VARCHAR(255),
  manufacturer VARCHAR(255),
  media VARCHAR(50),
  count BIGINT,
  discount_price DOUBLE,
  discount_sales DOUBLE,
  page_price DOUBLE,
  page_sales DOUBLE,
  product_listing_time VARCHAR(100),
  month_dt VARCHAR(100)
) ENGINE=OLAP
DUPLICATE KEY(platform, site, product_id, sku_id, month_dt)
DISTRIBUTED BY HASH(product_id) BUCKETS 50;
```

### 3. CN站点JOIN

> 使用 product_id + year_num 匹配

```sql
INSERT INTO flywheel.monthly_sales_with_dim
(platform, site, product_id, sku_id, month_dt, stdcategory1, stdcategory2, stdcategory3, device_type,
 product_title, sku_title, product_title_cn, product_url, product_image, category_1, category_2, category_3,
 category_4, category_5, category_id, category_name, sub_category, category_1_cn, category_2_cn, category_3_cn,
 category_4_cn, category_5_cn, sub_category_cn, brand_name, std_brand_name, shop_id, shop_name, manufacturer,
 media, count, discount_price, discount_sales, page_price, page_sales, product_listing_time)
SELECT m.platform, m.site, m.product_id, m.sku_id, m.month_dt, d.stdcategory1, d.stdcategory2, d.stdcategory3, d.device_type,
 m.product_title, m.sku_title, m.product_title_cn, m.product_url, m.product_image, m.category_1, m.category_2, m.category_3,
 m.category_4, m.category_5, m.category_id, m.category_name, m.sub_category, m.category_1_cn, m.category_2_cn, m.category_3_cn,
 m.category_4_cn, m.category_5_cn, m.sub_category_cn, m.brand_name, m.std_brand_name, m.shop_id, m.shop_name, m.manufacturer,
 m.media, m.count, m.discount_price, m.discount_sales, m.page_price, m.page_sales, m.product_listing_time
FROM flywheel.monthly_sales_wide_new m
INNER JOIN flywheel.product_category_dimension d
ON m.site = 'cn'
AND m.product_id = d.product_id
AND SUBSTRING(m.month_dt, 1, 4) = CAST(d.year_num AS CHAR)
WHERE m.site = 'cn'
```

### 4. US/JP/DE站点JOIN

> 使用 sku_id + site + year_num 匹配
> **MX/BR站点数据直接剔除，不参与JOIN**

```sql
INSERT INTO flywheel.monthly_sales_with_dim
(platform, site, product_id, sku_id, month_dt, stdcategory1, stdcategory2, stdcategory3, device_type,
 product_title, sku_title, product_title_cn, product_url, product_image, category_1, category_2, category_3,
 category_4, category_5, category_id, category_name, sub_category, category_1_cn, category_2_cn, category_3_cn,
 category_4_cn, category_5_cn, sub_category_cn, brand_name, std_brand_name, shop_id, shop_name, manufacturer,
 media, count, discount_price, discount_sales, page_price, page_sales, product_listing_time)
SELECT m.platform, m.site, m.product_id, m.sku_id, m.month_dt, d.stdcategory1, d.stdcategory2, d.stdcategory3, d.device_type,
 m.product_title, m.sku_title, m.product_title_cn, m.product_url, m.product_image, m.category_1, m.category_2, m.category_3,
 m.category_4, m.category_5, m.category_id, m.category_name, m.sub_category, m.category_1_cn, m.category_2_cn, m.category_3_cn,
 m.category_4_cn, m.category_5_cn, m.sub_category_cn, m.brand_name, m.std_brand_name, m.shop_id, m.shop_name, m.manufacturer,
 m.media, m.count, m.discount_price, m.discount_sales, m.page_price, m.page_sales, m.product_listing_time
FROM flywheel.monthly_sales_wide_new m
INNER JOIN flywheel.product_category_dimension d
ON m.sku_id = d.sku_id
AND m.site = d.site
AND SUBSTRING(m.month_dt, 1, 4) = CAST(d.year_num AS CHAR)
WHERE m.site IN ('US', 'JP', 'DE')
```

## JOIN字段对照表

| 用途 | 事实表字段 | 维度表字段 | 说明 |
|------|------------|------------|------|
| Join Key1(CN) | product_id | product_id | CN站点用product_id |
| Join Key1(US) | sku_id | sku_id | US/JP/DE用sku_id |
| Join Key2 | year_num(计算) | year_num | 从month_dt推导 |
| Join Key3(US) | site | site | US/JP/DE需站点也匹配 |
| **新增字段1** | - | stdcategory1 | 来自维度表 |
| **新增字段2** | - | stdcategory2 | 来自维度表 |
| **新增字段3** | - | stdcategory3 | 来自维度表 |
| **新增字段4** | - | device_type | 来自维度表 |

## 查询目标表结构

在编写INSERT前，先查询目标表列顺序：

```sql
DESC flywheel.monthly_sales_with_dim
```
