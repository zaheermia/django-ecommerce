# CRUD Matrix

V = Vendor, B = Buyer

| Entity | Create | Read | Update | Delete |
|---|---|---|---|---|
| Store | V | V, B | V | V |
| Product | V | V, B | V | V |
| Review | B | V, B | B | B |
| Vendor (User) | V (register) | B | - | - |
| Order | B (checkout) | B | - | - |
| OrderItem | B (checkout) | B | - | - |

## Notes
- Vendors can only update and delete their own stores and products
- Buyers can only update and delete their own reviews
- Orders can't be changed after checkout because they are the invoice
- The entities come from the class diagram (`Class Diagram.png`)
