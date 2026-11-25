# Nexora hybrid recommendation system

## What it uses

The recommender is a hybrid ranker, not a fixed list of popular products. It combines:

1. **Content similarity (TF-IDF + cosine similarity):** product name, brand, category, description and product-specification keywords.
2. **User intent profile:** recent views, searches, wishlist saves, cart additions and completed purchases. Stronger actions receive higher weights; recent actions decay more slowly than old actions.
3. **Collaborative filtering (item-to-item co-interaction):** customers who interacted with the same seed products contribute their other product interactions. This only becomes useful after genuine customer activity has accumulated.
4. **Preference affinity:** category, brand and observed spending range.
5. **Cold-start/popularity:** Bayesian-smoothed rating/review signals plus curated trending/featured flags when there is little or no history.
6. **Negative feedback and diversity:** dismissed items are demoted; previously purchased items are demoted; repeated brands/categories are limited in the final slate.

Current rank blend for users with behavioural history:

- 34% content similarity
- 30% collaborative signal
- 14% category/brand/price preference
- 12% popularity
- 10% product-page context

The blend is a starting point. It should be tuned against real offline metrics (HitRate@K, Recall@K, NDCG@K, conversion rate) after enough real interactions have been collected. No recommender can be called “perfect” without a representative dataset and measured evaluation.

## API

- `GET /api/recommendations/` — personalized recommendations for the authenticated user; cold-start picks for guests.
- `GET /api/recommendations/?product_id=12` — similar alternatives to product 12, excluding the viewed product itself.
- Optional query parameters: `limit` (1–30), `min_price`, `max_price`, `category` (category ID), `search`.
- `POST /api/recommendations/track/` — requires JWT authentication. JSON body:

```json
{"event_type":"VIEW","product_id":12}
```

Supported events: `VIEW`, `WISHLIST`, `CART`, `PURCHASE`, `SEARCH`, `DISMISS`. Search events use `{"event_type":"SEARCH","query":"wireless headphones"}`. The app records product clicks, wishlist saves, cart additions and completed order items. The order endpoint records purchases inside the order transaction.

Each recommendation response includes `recommendation_score` and `recommendation_reason` alongside normal product fields.

## Database setup / migration

From `backend/`:

```powershell
python manage.py migrate --fake-initial
```

`--fake-initial` lets Django recognize the recommendations table if it was previously created by `migrate --run-syncdb`; if it does not exist, Django creates it normally. Back up the database before applying schema changes.

Seed the illustrative catalogue (safe to re-run; does not delete users or orders):

```powershell
python manage.py seed_products
```

The seeded products are a **demo catalogue**, not a verified live retailer feed. Ratings and review counts are set to zero until genuine reviews are collected. Replace sample prices, stock and images with seller/inventory data before accepting real orders.

## Important operational notes

- Personalized learning requires customers to be signed in so events can be linked to a customer account. Guest users receive cold-start/product-context results; anonymous event tracking is intentionally not stored.
- Do not generate fake views, purchases, ratings or review counts to make the recommender appear trained. Real event quality is more important than event volume.
- Keep the recommendation endpoint behind normal API rate limits in production and monitor database query latency as the interaction table grows. For a large catalogue, move TF-IDF matrix construction to a scheduled cached artefact and use a dedicated recommendation service/vector index.
