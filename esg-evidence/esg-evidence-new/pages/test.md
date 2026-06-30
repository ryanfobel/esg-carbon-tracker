# Test Connection

```sql test_query
SELECT 'Hello from DuckDB' as message, current_timestamp as now
```

<DataTable data={test_query}/>

```sql schemas
SHOW SCHEMAS
```

<DataTable data={schemas}/>

```sql tables
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'marts'
```

<DataTable data={tables}/>
