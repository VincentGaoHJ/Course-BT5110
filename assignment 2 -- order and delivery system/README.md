- **Inventory List**
   - Search for the stock inventory base on the item and warehouse name submitted. No need to specify the full name, AppLine will retrieve all the stock whose item name and warehouse name contains the submitted keywords.
   - AppLine also will conduct the Inventory Search if only one keyword (item or warehouse) provided.

- **Add New Stock to the Warehouse**
   - AppLine will list all possible combinations based on the submitted information. For example, if there is no item AA in the warehouse BB, you could input A and B, and AA and BB will appear in this section, choose it to add item AA to the warehouse BB.
     
   - And only the item and the warehouse keyword are both specified, this section(adding new stock to the warehouse) will appear. I set this constraint because only one keyword will lead to too many combinations regarding that database has so many items and warehouses.