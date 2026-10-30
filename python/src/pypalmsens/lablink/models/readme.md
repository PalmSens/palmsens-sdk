# Updating the model

The wire model can be updated from the Swagger API using this command:

```bash
datamodel-codegen  --url http://127.0.0.1:5000/swagger/v1/swagger.json --allow-private-network --input-file-type openapi --output _wire.py
```
