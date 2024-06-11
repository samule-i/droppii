## s3 file structure
### CSV
```
column_1, column_2, column3, ...
c1_Value_1, c2_Value_1, c3_Value_1, ...
c1_Value_2, c2_Value_2, c3_Value_2, ...
c1_Value_3, c2_Value_3, c3_Value_3, ...
```

### JSON
JSON format must be a list of objects representing rows, with a key-value pair for each column.
```
[
  {
    column_1: c1_Value_1,
    column_2: c2_Value_1, 
    column_3: c3_Value_1
  },
  {
    column_1: c1_Value_2,
    column_2: c2_Value_2, 
    column_3: c3_Value_2
  },
  {
    column_1: c1_Value_3,
    column_2: c2_Value_3, 
    column_3: c3_Value_3
  },
  ...
]
```
