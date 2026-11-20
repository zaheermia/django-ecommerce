# API Plan

## What the API sends back
- **Store** - id, vendor, name, description
- **Product** - id, store, name, description, price, stock
- **Review** - id, product, buyer, rating, comment, date

It sends JSON. Add `?format=xml` to the URL to get XML.

## Endpoints
Everyone has to log in with Basic Auth first.

| Method | URL | Who | Use case |
|---|---|---|---|
| GET | /api/stores/ | everyone | View Store |
| POST | /api/stores/ | vendors | Create Store |
| GET | /api/vendors/{id}/stores/ | everyone | View Store |
| GET | /api/stores/{id}/products/ | everyone | View Product |
| POST | /api/stores/{id}/products/ | the store's vendor | Create Product |
| GET | /api/stores/{id}/reviews/ | the store's vendor | View All Reviews |

## Diagrams
- `Use Case Diagram.png`
- `Sequence Diagram - Stores.png`
- `Sequence Diagram - Products.png`
- `Sequence Diagram - Vendors and Reviews.png`
- `Class Diagram.png`
- `crud_matrix.md`
