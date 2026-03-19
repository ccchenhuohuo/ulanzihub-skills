-- ============================================================
-- Doris 维度表JOIN 验证SQL模板
-- 用于验证 product_category_dimension 与 monthly_sales_wide_new 的JOIN结果
-- ============================================================

-- -------------------------------------------------------
-- 1. 检查目标表总行数
-- -------------------------------------------------------
SELECT COUNT(*) as total FROM flywheel.monthly_sales_with_dim;


-- -------------------------------------------------------
-- 2. 检查各站点分布
-- -------------------------------------------------------
SELECT site, COUNT(*) as cnt
FROM flywheel.monthly_sales_with_dim
GROUP BY site
ORDER BY cnt DESC;


-- -------------------------------------------------------
-- 3. 抽样查看数据
-- -------------------------------------------------------
SELECT
    site,
    product_id,
    sku_id,
    month_dt,
    stdcategory1,
    stdcategory2,
    stdcategory3,
    device_type
FROM flywheel.monthly_sales_with_dim
LIMIT 20;


-- -------------------------------------------------------
-- 4. 空值检查 - 检查维度字段是否有空值
-- -------------------------------------------------------
SELECT
    SUM(CASE WHEN stdcategory1 IS NULL OR stdcategory1 = '' THEN 1 ELSE 0 END) as null_stdcategory1,
    SUM(CASE WHEN stdcategory2 IS NULL OR stdcategory2 = '' THEN 1 ELSE 0 END) as null_stdcategory2,
    SUM(CASE WHEN stdcategory3 IS NULL OR stdcategory3 = '' THEN 1 ELSE 0 END) as null_stdcategory3,
    SUM(CASE WHEN device_type IS NULL OR device_type = '' THEN 1 ELSE 0 END) as null_device_type,
    COUNT(*) as total
FROM flywheel.monthly_sales_with_dim;


-- -------------------------------------------------------
-- 5. JOIN匹配率检查
-- -------------------------------------------------------
SELECT
    '维度表记录数' as metric,
    COUNT(*) as cnt
FROM flywheel.product_category_dimension
UNION ALL
SELECT
    '目标表记录数' as metric,
    COUNT(*) as cnt
FROM flywheel.monthly_sales_with_dim;


-- -------------------------------------------------------
-- 6. 各站点stdcategory分布
-- -------------------------------------------------------
SELECT
    site,
    stdcategory1,
    COUNT(*) as cnt
FROM flywheel.monthly_sales_with_dim
WHERE stdcategory1 IS NOT NULL AND stdcategory1 != ''
GROUP BY site, stdcategory1
ORDER BY site, cnt DESC
LIMIT 50;


-- -------------------------------------------------------
-- 7. 各站点device_type分布
-- -------------------------------------------------------
SELECT
    site,
    device_type,
    COUNT(*) as cnt
FROM flywheel.monthly_sales_with_dim
WHERE device_type IS NOT NULL AND device_type != ''
GROUP BY site, device_type
ORDER BY site, cnt DESC;


-- -------------------------------------------------------
-- 8. 按月份统计
-- -------------------------------------------------------
SELECT
    site,
    SUBSTRING(month_dt, 1, 7) as month,
    COUNT(*) as cnt
FROM flywheel.monthly_sales_with_dim
GROUP BY site, SUBSTRING(month_dt, 1, 7)
ORDER BY site, month DESC
LIMIT 20;


-- -------------------------------------------------------
-- 9. 验证CN站点JOIN (基于product_id)
-- -------------------------------------------------------
SELECT
    'CN站点' as site_type,
    COUNT(*) as matched_count
FROM flywheel.monthly_sales_wide_new m
INNER JOIN flywheel.product_category_dimension d
ON m.product_id = d.product_id
AND SUBSTRING(m.month_dt, 1, 4) = CAST(d.year_num AS CHAR)
WHERE m.site = 'cn';


-- -------------------------------------------------------
-- 10. 验证US/JP/DE站点JOIN (基于sku_id + site)
-- -------------------------------------------------------
SELECT
    'US/JP/DE站点' as site_type,
    COUNT(*) as matched_count
FROM flywheel.monthly_sales_wide_new m
INNER JOIN flywheel.product_category_dimension d
ON m.sku_id = d.sku_id
AND m.site = d.site
AND SUBSTRING(m.month_dt, 1, 4) = CAST(d.year_num AS CHAR)
WHERE m.site IN ('US', 'JP', 'DE');


-- -------------------------------------------------------
-- 11. 检查目标表结构
-- -------------------------------------------------------
DESC flywheel.monthly_sales_with_dim;


-- -------------------------------------------------------
-- 12. 检查维度表结构
-- -------------------------------------------------------
DESC flywheel.product_category_dimension;
