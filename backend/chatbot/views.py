from decimal import Decimal, InvalidOperation
import re

from django.conf import settings
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Conversation, Message
from catalog.models import Product


class ChatView(APIView):
    """
    Nexora AI Shopping Assistant

    Features:
    - Guest users can chat
    - Logged-in users can have saved conversations
    - Searches real products from MySQL
    - Understands product categories
    - Understands budgets
    - Uses OpenAI when API key is available
    - Local fallback works without OpenAI
    """

    permission_classes = [AllowAny]

    def post(self, request):
        message = str(
            request.data.get("message", "")
        ).strip()

        if not message:
            return Response(
                {"detail": "Message is required."},
                status=400
            )

        # -------------------------------------------------
        # Current user
        # -------------------------------------------------

        user = (
            request.user
            if request.user.is_authenticated
            else None
        )

        # -------------------------------------------------
        # Get existing conversation
        # -------------------------------------------------

        conversation_id = request.data.get(
            "conversation_id"
        )

        conversation = None

        if conversation_id:
            try:
                conversation = Conversation.objects.filter(
                    id=int(conversation_id)
                ).first()
            except (ValueError, TypeError):
                conversation = None

        # Do not allow guest to use another user's
        # authenticated conversation.
        if conversation:
            if (
                conversation.user_id is not None
                and conversation.user_id != getattr(user, "id", None)
            ):
                conversation = None

        # Create new conversation
        if not conversation:
            conversation = Conversation.objects.create(
                user=user
            )

        # Preserve context for short follow-ups such as "kro", "show more".
        previous_user_messages = list(
            conversation.messages.filter(role="user")
            .order_by("-created_at").values_list("content", flat=True)[:6]
        )
        context_query = message
        short_followups = {"kro", "more", "show more", "aur dikhao", "aur batao", "yes", "haan", "ha", "okay", "ok", "compare", "best one", "which one"}
        if message.lower().strip() in short_followups and previous_user_messages:
            context_query = previous_user_messages[0]

        Message.objects.create(
            conversation=conversation,
            role="user",
            content=message
        )

        # Search using the current intent plus recent context.
        products = self.find_products(context_query)

        # -------------------------------------------------
        # Build store context
        # -------------------------------------------------

        product_context = self.build_product_context(
            products
        )

        # -------------------------------------------------
        # Try OpenAI
        # -------------------------------------------------

        answer = self.generate_openai_answer(
            conversation=conversation,
            message=message,
            product_context=product_context
        )
        ai_mode = "openai" if answer else "catalog_fallback"

        # -------------------------------------------------
        # Local fallback
        # -------------------------------------------------

        if not answer:
            answer = self.generate_local_answer(
                message=message,
                products=products,
                context_query=context_query
            )

        # -------------------------------------------------
        # Save assistant response
        # -------------------------------------------------

        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=answer
        )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return Response({
            "conversation_id": conversation.id,
            "answer": answer,
            "ai_mode": ai_mode,
            "products": [
                self.serialize_product(product)
                for product in products[:6]
            ]
        })

    # =====================================================
    # PRODUCT SEARCH
    # =====================================================

    def find_products(self, message):
        """
        Search real Nexora products.

        Budget filtering is done in Python because
        Product.sale_price is a model property.
        """

        text = message.lower()

        queryset = Product.objects.filter(
            is_active=True
        ).select_related("category")

        # -------------------------------------------------
        # Product keywords
        # -------------------------------------------------

        keywords = {
            "laptop": [
                "gaming laptop",
                "laptop",
                "notebook",
                "macbook"
            ],

            "smartphone": [
                "smartphone",
                "phone",
                "mobile",
                "iphone",
                "android"
            ],

            "headphone": [
                "headphones",
                "headphone",
                "earphones",
                "earphone",
                "earbuds",
                "airpods"
            ],

            "camera": [
                "camera",
                "dslr",
                "mirrorless"
            ],

            "monitor": [
                "gaming monitor",
                "monitor",
                "display",
                "screen"
            ],

            "keyboard": [
                "mechanical keyboard",
                "keyboard"
            ],

            "mouse": [
                "gaming mouse",
                "mouse"
            ],

            "tablet": [
                "tablet",
                "ipad"
            ],

            "gaming": [
                "gaming",
                "gamer",
                "gaming pc"
            ],
        }

        detected_type = None

        # -------------------------------------------------
        # Detect category
        # -------------------------------------------------

        for product_type, words in keywords.items():

            if any(
                word in text
                for word in words
            ):
                detected_type = product_type
                break

        # -------------------------------------------------
        # Category search
        # -------------------------------------------------

        if detected_type:

            search_q = Q()

            for word in keywords[detected_type]:

                search_q |= Q(
                    name__icontains=word
                )

                search_q |= Q(
                    description__icontains=word
                )

                search_q |= Q(
                    brand__icontains=word
                )

                search_q |= Q(
                    category__name__icontains=word
                )

            queryset = queryset.filter(search_q)

        # -------------------------------------------------
        # General search
        # -------------------------------------------------

        else:

            words = [
                word
                for word in re.findall(
                    r"[a-zA-Z0-9]+",
                    text
                )
                if len(word) >= 3
            ]

            if words:

                search_q = Q()

                for word in words[:8]:

                    search_q |= Q(
                        name__icontains=word
                    )

                    search_q |= Q(
                        brand__icontains=word
                    )

                    search_q |= Q(
                        description__icontains=word
                    )

                    search_q |= Q(
                        category__name__icontains=word
                    )

                searched = queryset.filter(
                    search_q
                )

                if searched.exists():
                    queryset = searched

        # -------------------------------------------------
        # Get database products
        # -------------------------------------------------

        products = list(
            queryset.order_by(
                "-rating",
                "-created_at"
            )
        )

        # -------------------------------------------------
        # Detect budget
        # -------------------------------------------------

        budget = self.extract_budget(
            message
        )

        # -------------------------------------------------
        # Filter by sale price
        # -------------------------------------------------

        if budget is not None:

            filtered_products = []

            for product in products:

                try:

                    product_price = Decimal(
                        str(product.sale_price)
                    )

                    if product_price <= budget:
                        filtered_products.append(
                            product
                        )

                except (
                    InvalidOperation,
                    TypeError,
                    ValueError
                ):
                    continue

            products = filtered_products

        return products[:12]

    # =====================================================
    # BUDGET DETECTION
    # =====================================================

    def extract_budget(self, message):
        """
        Understands:

        50000
        ₹50000
        ₹50,000
        50k
        50 K
        under 50000
        below 50k
        budget 40000
        within 60000
        upto 70000
        """

        text = message.lower().replace(
            ",",
            ""
        )

        patterns = [

            # under 50k
            r"(?:under|below|less than|within|upto|up to|max|budget)\s*₹?\s*(\d+(?:\.\d+)?)\s*k",

            # 50k
            r"₹?\s*(\d+(?:\.\d+)?)\s*k",

            # under 50000
            r"(?:under|below|less than|within|upto|up to|max|budget)\s*₹?\s*(\d+)",

            # ₹50000
            r"₹\s*(\d+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                try:

                    value = Decimal(
                        match.group(1)
                    )

                    if "k" in match.group(0):
                        value *= 1000

                    return value

                except (
                    InvalidOperation,
                    ValueError
                ):
                    continue

        # -------------------------------------------------
        # Plain number detection
        # Example: "budget 40000"
        # -------------------------------------------------

        if "budget" in text:

            match = re.search(
                r"budget\s*(?:is|of)?\s*₹?\s*(\d+)",
                text
            )

            if match:

                try:
                    return Decimal(
                        match.group(1)
                    )
                except (
                    InvalidOperation,
                    ValueError
                ):
                    pass

        return None

    # =====================================================
    # PRODUCT CONTEXT
    # =====================================================

    def build_product_context(self, products):

        if not products:
            return (
                "No matching products were found "
                "in the Nexora store."
            )

        lines = []

        for product in products[:12]:

            category_name = (
                product.category.name
                if product.category
                else "Technology"
            )

            lines.append(
                f"""
Product:
Name: {product.name}
Brand: {product.brand}
Category: {category_name}
Price: ₹{product.sale_price}
Rating: {product.rating}
Stock: {product.stock}
Description: {product.description[:300]}
""".strip()
            )

        return "\n\n".join(lines)

    # =====================================================
    # OPENAI
    # =====================================================

    def generate_openai_answer(
        self,
        conversation,
        message,
        product_context
    ):

        api_key = getattr(
            settings,
            "OPENAI_API_KEY",
            ""
        )

        if not api_key:
            return None

        try:

            from openai import OpenAI

            client = OpenAI(
                api_key=api_key
            )

            history = list(
                conversation.messages
                .order_by("-created_at")
                .values(
                    "role",
                    "content"
                )[:12]
            )

            history.reverse()

            system_prompt = f"""
You are Nexora AI, a friendly and intelligent
technology shopping assistant.

Nexora sells technology and electronic products.

Your job is to help customers choose products.

RULES:

1. Only discuss technology and electronics.
2. Use the Nexora store products provided below.
3. Never invent products.
4. Never invent prices.
5. Never invent stock.
6. Respect the customer's budget.
7. Mention actual product names when relevant.
8. Ask useful follow-up questions when necessary.
9. Speak naturally.
10. Support English, Hindi and Hinglish.
11. Keep responses concise and useful.
12. If no product matches, clearly explain that.

NEXORA STORE PRODUCTS:

{product_context}
"""

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            for item in history:

                role = item["role"]

                if role not in [
                    "user",
                    "assistant"
                ]:
                    continue

                messages.append({
                    "role": role,
                    "content": item["content"]
                })

            response = client.chat.completions.create(
                model=getattr(
                    settings,
                    "OPENAI_MODEL",
                    "gpt-4.1-mini"
                ),
                messages=messages,
                temperature=0.4,
                max_tokens=500
            )

            answer = (
                response
                .choices[0]
                .message
                .content
            )

            if answer:
                return answer.strip()

        except Exception as error:

            print(
                "Nexora AI Error:",
                error
            )

        return None

    # =====================================================
    # LOCAL FALLBACK
    # =====================================================

    def generate_local_answer(
        self,
        message,
        products,
        context_query=None
    ):

        text = message.lower()
        intent_text = (context_query or message).lower()

        # -------------------------------------------------
        # Greetings
        # -------------------------------------------------

        greetings = [
            "hello",
            "hi",
            "hey",
            "hii",
            "namaste"
        ]

        if any(
            word in text
            for word in greetings
        ):

            return (
                "Hi! 👋 I'm Nexora AI. "
                "Aap laptop, smartphone, gaming, "
                "headphones, camera ya kisi bhi "
                "technology product ke baare mein "
                "pooch sakte ho. "
                "Budget bhi bata sakte ho."
            )

        # -------------------------------------------------
        # Unsupported / non-product request
        # -------------------------------------------------

        if any(
            word in text
            for word in [
                "sex",
                "porn",
                "adult",
                "nude"
            ]
        ):

            return (
                "Main Nexora ka technology shopping "
                "assistant hoon, isliye main technology "
                "products aur shopping se related help "
                "kar sakta hoon. "
                "Aap laptop, smartphone, headphones, "
                "camera ya kisi gadget ke baare mein "
                "pooch sakte ho."
            )

        # -------------------------------------------------
        # No products
        # -------------------------------------------------

        if not products:

            budget = self.extract_budget(
                message
            )

            if budget:

                return (
                    f"Mujhe Nexora mein "
                    f"₹{int(budget):,} ke andar "
                    "matching product nahi mila. "
                    "Aap budget thoda increase karke "
                    "ya doosri technology category "
                    "try kar sakte ho."
                )

            return (
                "Mujhe is request ke liye matching "
                "Nexora product nahi mila. "
                "Aap product type aur budget batao, "
                "jaise '₹50,000 ke andar laptop'."
            )

        # -------------------------------------------------
        # Budget response
        # -------------------------------------------------

        budget = self.extract_budget(
            message
        )

        if budget:

            intro = (
                f"Bilkul! ₹{int(budget):,} ke andar "
                f"mujhe {len(products)} relevant "
                "products mile:"
            )

        else:

            intro = (
                "Bilkul! Aapki request ke basis par "
                "Nexora mein ye relevant products mile:"
            )

        # Context-aware, conversational fallback instead of repeating one template.
        if any(x in intent_text for x in ["camera", "dslr", "mirrorless"]):
            intro = "Camera ke liye main shortlist kar deta hoon. Ye options store mein available hain:"
        elif any(x in intent_text for x in ["laptop", "notebook", "macbook"]):
            intro = "Laptop ke liye ye options sabse relevant lag rahe hain:"
        elif any(x in intent_text for x in ["headphone", "earbud", "earphone"]):
            intro = "Audio ke liye ye options check karo:"
        elif any(x in intent_text for x in ["phone", "mobile", "smartphone"]):
            intro = "Smartphone ke liye ye options dekh sakte ho:"
        else:
            intro = "Maine tumhari request ke hisaab se ye products shortlist kiye hain:"
        lines = [intro, ""]
        for index, product in enumerate(products[:5], start=1):
            lines.append(f"{index}. {product.name} — ₹{product.sale_price} (⭐ {product.rating}/5)")
        lines.extend(["", "Inmein se kisi ka detailed comparison chahiye, ya main tumhare budget ke hisaab se best option choose kar doon?"])
        return "\n".join(lines)

    # =====================================================
    # PRODUCT SERIALIZER
    # =====================================================

    def serialize_product(
        self,
        product
    ):

        return {
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "price": str(
                product.price
            ),
            "sale_price": str(
                product.sale_price
            ),
            "rating": float(
                product.rating
            ),
            "stock": product.stock,
            "image_url": product.image_url,
            "category": (
                product.category.name
                if product.category
                else None
            ),
        }