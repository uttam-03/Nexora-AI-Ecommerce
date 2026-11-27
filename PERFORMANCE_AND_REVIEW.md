# Nexora AI E-Commerce - updates and review notes

## Updates in this revision
- Dashboard header greets the logged-in admin/seller by first name or username and shows role context.
- Profile page has an edit mode for first/last name, email, phone and bio, and supports avatar upload through the existing profile API.
- Product card imagery uses browser lazy loading and asynchronous image decoding.

## Profile API requirements
The current Django profile serializer already exposes `first_name`, `last_name`, `email`, `phone`, `avatar` and `bio`; the profile endpoint is authenticated and supports update. Ensure media storage is persistent/externally hosted on deployment, because local Render disk media may not persist across redeploys unless configured.

## Product latency investigation
- Render free instances can have cold-start latency after inactivity; distinguish first request delay from repeat requests.
- Measure catalogue endpoint latency and database query count in logs before attributing the delay.
- Images should be compressed/resized to sensible thumbnail sizes and hosted via persistent object storage/CDN if possible.
- The API uses pagination (catalogue pagination size 24). Ensure the frontend has pagination/infinite loading rather than treating the first page as the entire catalogue.
- Queryset currently uses `select_related` for category/seller and `prefetch_related` for specifications. Review product serializer for additional per-product queries.
- Consider cache headers or short-lived catalogue caching, but invalidate on product edits/stock updates.

## Additional issues worth QA
1. Customer wishlist route currently renders a placeholder rather than a persistent wishlist.
2. Shop list currently displays first page only and does not expose pagination controls.
3. Shop search is submitted manually and loading/empty/error states could be more distinct.
4. Product upload form and payment/admin action screens should be tested for validation, server errors and loading state.
5. Seller approval and role permissions must be tested with separate admin, seller, and customer accounts.
6. Ensure deployed media URLs are accessible and image upload size/type limits are enforced.
7. Validate checkout, UPI UTR verification, COD, invoice and order status flows end-to-end.
8. Use production database backups and never commit `.env`, secrets, or local database files.

## Build verification
A frontend build could not be verified in this archive environment because the bundled node_modules are missing Rollup's platform optional dependency. Run `npm ci` in frontend on a normal environment, then `npm run build`.
