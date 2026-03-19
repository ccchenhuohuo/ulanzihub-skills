# 字段映射参考

## 维度表字段 (product_category_dimension)

| 字段 | 说明 | 来源 |
|------|------|------|
| device_type | 设备类型 | CSV: devicetype |
| product_id | 产品ID | CSV: productid |
| row_num | 行号 | CSV: rownum |
| site | 站点 | CSV: site |
| sku_id | SKU ID | CSV: skuid |
| stdcategory1 | 一级分类 | CSV: stdcategory1 |
| stdcategory2 | 二级分类 | CSV: stdcategory2 |
| stdcategory3 | 三级分类 | CSV: stdcategory3 |
| year_num | 年份 | CSV: yearnum |

## CSV合并字段映射 (col_map)

```python
col_map = {
    'devicetype': 'device_type',
    'productid': 'product_id',
    'site': 'site',           # 重要：必须有！
    'skuid': 'sku_id',
    'stdcategory1': 'stdcategory1',
    'stdcategory2': 'stdcategory2',
    'stdcategory3': 'stdcategory3',
    'yearnum': 'year_num',
    'rownum': 'row_num',
}
```

## JSON转换字段映射

CSV列名已经是目标表字段格式，直接取值：

```python
converted_row = {
    'device_type': row.get('device_type', ''),
    'product_id': row.get('product_id', ''),
    'row_num': row.get('row_num', ''),
    'site': row.get('site', ''),
    'sku_id': row.get('sku_id', ''),
    'stdcategory1': row.get('stdcategory1', ''),
    'stdcategory2': row.get('stdcategory2', ''),
    'stdcategory3': row.get('stdcategory3', ''),
    'year_num': row.get('year_num', '')
}
```

## 目标表字段 (monthly_sales_with_dim)

完整字段列表见 `join_rules.md`
