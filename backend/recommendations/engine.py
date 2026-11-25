from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from catalog.models import Product

def content_recommendations(product_id=None, limit=8):
    products = list(Product.objects.filter(is_active=True).select_related("category"))
    if len(products) < 2:
        return products
    corpus = [
        f"{p.brand} {p.name} {p.category.name} {p.description}"
        for p in products
    ]
    matrix = TfidfVectorizer(stop_words="english").fit_transform(corpus)
    if product_id:
        try:
            index = next(i for i,p in enumerate(products) if p.id == int(product_id))
        except StopIteration:
            index = 0
    else:
        index = 0
    scores = cosine_similarity(matrix[index:index+1], matrix).flatten()
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    return [products[i] for i,score in ranked if products[i].id != products[index].id][:limit]
