## s3 file structure
### CSV
```
_id, name, Email
0, "Andrew", "Andrew@email.com"
1, "Bob", "bob@email.com"
2, "Claire", "claire@email.com"
```

### JSON
JSON format must be a list of objects representing rows, with a key-value pair for each column.
```
[
  {
    _id: 0,
    name: "Andrew", 
    Email: "Andrew@email.com"
  },
  {
    _id: 1,
    name: "Bob", 
    Email: "bob@email.com"
  },
  {
    _id: 2,
    name: "Claire", 
    Email: "claire@email.com"
  }
]
```
