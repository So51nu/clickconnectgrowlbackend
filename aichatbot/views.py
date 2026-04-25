import os
import re
import uuid
import traceback
import requests
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from openai import OpenAI

from .models import ChatbotTenant, ChatSession, ChatMessage, ChatLead
from .serializers import ChatbotTenantSerializer


def get_env_value(key, default=None):
    return os.getenv(key) or getattr(settings, key, default)


OPENAI_API_KEY = get_env_value("OPENAI_API_KEY", "")
OPENAI_MODEL = get_env_value("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")
PROPERTY_API_URL = get_env_value(
    "PROPERTY_API_URL",
    "http://127.0.0.1:8000/api/admindashboard/properties/",
)


def get_openai_client():
    api_key = get_env_value("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join([safe_text(v) for v in value if v])
    if isinstance(value, dict):
        return " ".join([safe_text(v) for v in value.values()])
    return str(value).strip()


def normalize_query(text):
    text = safe_text(text).lower()
    text = re.sub(r"[^a-z0-9₹.\s+-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def format_price(value):
    if value in [None, "", "null"]:
        return "Price not available"

    try:
        price = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return str(value)

    if price >= 10000000:
        cr = price / Decimal("10000000")
        return f"₹{cr:.2f} Cr".replace(".00", "")

    if price >= 100000:
        lakh = price / Decimal("100000")
        return f"₹{lakh:.2f} Lacs".replace(".00", "")

    return f"₹{price:,.0f}"


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

def get_property_api_url_for_tenant(tenant):
    if tenant and tenant.property_api_url:
        return tenant.property_api_url

    return PROPERTY_API_URL


def get_property_api_headers_for_tenant(tenant):
    headers = {
        "Accept": "application/json",
    }

    if not tenant:
        return headers

    auth_type = tenant.property_api_auth_type or "none"
    token = safe_text(tenant.property_api_token)
    header_name = safe_text(tenant.property_api_key_header) or "Authorization"

    if auth_type == "bearer" and token:
        headers["Authorization"] = f"Bearer {token}"

    elif auth_type == "api_key" and token:
        headers[header_name] = token

    return headers


def fetch_properties(tenant=None):
    try:
        api_url = get_property_api_url_for_tenant(tenant)
        headers = get_property_api_headers_for_tenant(tenant)

        response = requests.get(api_url, headers=headers, timeout=25)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict):
            if isinstance(data.get("results"), list):
                return data.get("results")
            if isinstance(data.get("data"), list):
                return data.get("data")
            if isinstance(data.get("properties"), list):
                return data.get("properties")
            if isinstance(data.get("projects"), list):
                return data.get("projects")

        if isinstance(data, list):
            return data

        return []

    except Exception as error:
        raise Exception(f"Property API fetch failed: {str(error)}")

def property_to_document(property_item):
    title = safe_text(property_item.get("title"))
    description = safe_text(property_item.get("description"))
    city = safe_text(property_item.get("city"))
    location = safe_text(property_item.get("location"))
    short_location = safe_text(property_item.get("short_location"))
    full_address = safe_text(property_item.get("full_address"))
    developer = safe_text(property_item.get("developer_name"))
    price = format_price(property_item.get("price"))
    bedrooms = safe_text(property_item.get("bedrooms"))
    bathrooms = safe_text(property_item.get("bathrooms"))
    rooms = safe_text(property_item.get("rooms"))
    carpet_area = safe_text(property_item.get("carpet_area"))
    size_sqft = safe_text(property_item.get("size_sqft"))
    property_type = safe_text(property_item.get("property_type"))
    property_status = safe_text(property_item.get("property_status"))
    property_label = safe_text(property_item.get("property_label"))
    possession_date = safe_text(property_item.get("possession_date"))
    amenities = safe_text(property_item.get("amenities", []))

    floor_plans = []
    for floor in property_item.get("floor_plans", []) or []:
        floor_plans.append(
            f"{safe_text(floor.get('floor_name'))}: "
            f"{safe_text(floor.get('bedrooms'))} bedrooms, "
            f"{safe_text(floor.get('bathrooms'))} bathrooms, "
            f"size {safe_text(floor.get('floor_size'))} {safe_text(floor.get('size_postfix'))}, "
            f"price {format_price(floor.get('floor_price'))}. "
            f"{safe_text(floor.get('description'))}"
        )

    nearby_places = []
    for place in property_item.get("nearby_places", []) or []:
        nearby_places.append(
            f"{safe_text(place.get('place_name'))} - {safe_text(place.get('distance'))}"
        )

    seller = property_item.get("contact_seller") or {}
    fallback_sellers = property_item.get("fallback_sellers") or []

    seller_data = {}
    if seller:
        seller_data = {
            "name": safe_text(seller.get("full_name")),
            "email": safe_text(seller.get("email")),
            "phone": safe_text(seller.get("phone")),
        }
    elif fallback_sellers:
        first_seller = fallback_sellers[0]
        seller_data = {
            "name": safe_text(first_seller.get("full_name")),
            "email": safe_text(first_seller.get("email")),
            "phone": safe_text(first_seller.get("phone")),
        }

    seller_text = ""
    if seller_data:
        seller_text = (
            f"Contact seller: {seller_data.get('name')}, "
            f"Phone: {seller_data.get('phone')}, "
            f"Email: {seller_data.get('email')}"
        )

    document = f"""
Property ID: {safe_text(property_item.get("id"))}
Project Name: {title}
Description: {description}
City: {city}
Location: {location}
Short Location: {short_location}
Full Address: {full_address}
Developer: {developer}
Price: {price}
Raw Price: {safe_text(property_item.get("price"))}
Property Type: {property_type}
Property Status: {property_status}
Property Label: {property_label}
Rooms: {rooms}
Bedrooms: {bedrooms}
Bathrooms: {bathrooms}
Carpet Area: {carpet_area}
Size Sqft: {size_sqft}
Possession Date: {possession_date}
Amenities: {amenities}
Floor Plans: {" | ".join(floor_plans)}
Nearby Places: {" | ".join(nearby_places)}
Video URL: {safe_text(property_item.get("video_url"))}
Map URL: {safe_text(property_item.get("map_embed_url"))}
Main Image: {safe_text(property_item.get("imageSrc"))}
{seller_text}
""".strip()

    return {
        "id": property_item.get("id"),
        "title": title,
        "city": city,
        "location": location or short_location,
        "developer": developer,
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "carpet_area": carpet_area,
        "image": property_item.get("imageSrc"),
        "seller": seller_data,
        "raw": property_item,
        "document": document,
        "search_text": normalize_query(document),
    }


def extract_budget_number(query):
    query = query.lower()

    patterns = [
        r"under\s+(\d+)\s*cr",
        r"below\s+(\d+)\s*cr",
        r"budget\s+(\d+)\s*cr",
        r"(\d+)\s*cr",
        r"under\s+(\d+)\s*lakh",
        r"below\s+(\d+)\s*lakh",
        r"budget\s+(\d+)\s*lakh",
        r"(\d+)\s*lakh",
        r"under\s+(\d+)\s*lac",
        r"below\s+(\d+)\s*lac",
        r"(\d+)\s*lac",
    ]

    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            number = int(match.group(1))
            if "cr" in pattern:
                return number * 10000000
            return number * 100000

    return None


def get_property_price_number(property_item):
    try:
        return float(property_item.get("price") or 0)
    except Exception:
        return 0


def score_property(query, doc):
    query_normalized = normalize_query(query)
    query_words = [word for word in query_normalized.split() if len(word) >= 2]

    score = 0
    search_text = doc["search_text"]
    raw = doc["raw"]

    for word in query_words:
        if word in search_text:
            score += 2

    city = normalize_query(raw.get("city"))
    location = normalize_query(raw.get("location"))
    short_location = normalize_query(raw.get("short_location"))
    developer = normalize_query(raw.get("developer_name"))
    title = normalize_query(raw.get("title"))

    if city and city in query_normalized:
        score += 25
    if location and location in query_normalized:
        score += 18
    if short_location and short_location in query_normalized:
        score += 18
    if developer and developer in query_normalized:
        score += 18

    title_words = [w for w in title.split() if len(w) >= 3]
    for word in title_words:
        if word in query_normalized:
            score += 6

    bedrooms = safe_text(raw.get("bedrooms"))
    for bhk in ["1", "2", "3", "4", "5"]:
        if f"{bhk} bhk" in query_normalized and bedrooms == bhk:
            score += 30

    budget = extract_budget_number(query_normalized)
    if budget:
        property_price = get_property_price_number(raw)
        if property_price and property_price <= budget:
            score += 25
        elif property_price and property_price > budget:
            score -= 8

    if "rent" in query_normalized and raw.get("property_status") == "for-rent":
        score += 25
    if "sale" in query_normalized and raw.get("property_status") == "for-sale":
        score += 25
    if "buy" in query_normalized and raw.get("property_status") == "for-sale":
        score += 25

    return score


def is_property_related_question(question):
    q = normalize_query(question)

    property_keywords = [
        "property",
        "project",
        "projects",
        "latest",
        "flat",
        "home",
        "house",
        "apartment",
        "bhk",
        "bedroom",
        "price",
        "budget",
        "rent",
        "sale",
        "buy",
        "location",
        "city",
        "developer",
        "amenities",
        "possession",
        "rera",
        "carpet",
        "area",
        "site visit",
        "brokerage",
        "floor",
        "parking",
        "mumbai",
        "thane",
        "pune",
        "goregaon",
        "andheri",
        "malad",
        "borivali",
        "mira road",
    ]

    return any(keyword in q for keyword in property_keywords)

def retrieve_relevant_properties(question, limit=5, tenant=None):
    properties = fetch_properties(tenant=tenant)
    documents = [property_to_document(item) for item in properties]

    scored_docs = []
    for doc in documents:
        score = score_property(question, doc)
        scored_docs.append({**doc, "score": score})

    scored_docs = sorted(scored_docs, key=lambda item: item["score"], reverse=True)
    relevant_docs = [doc for doc in scored_docs if doc["score"] > 0]

    if not relevant_docs:
        relevant_docs = get_latest_properties(limit=limit, tenant=tenant)

    return relevant_docs[:limit]

def get_latest_properties(limit=3, tenant=None):
    properties = fetch_properties(tenant=tenant)

    def sort_key(item):
        return item.get("posting_date") or item.get("created_at") or item.get("id") or ""

    properties = sorted(properties, key=sort_key, reverse=True)
    return [property_to_document(item) for item in properties[:limit]]


def make_properties_payload(properties):
    payload = []
    for item in properties:
        payload.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "city": item.get("city"),
                "location": item.get("location"),
                "developer": item.get("developer"),
                "price": item.get("price"),
                "bedrooms": item.get("bedrooms"),
                "bathrooms": item.get("bathrooms"),
                "carpet_area": item.get("carpet_area"),
                "image": item.get("image"),
                "score": item.get("score", 0),
            }
        )
    return payload


def build_ai_answer(question, relevant_properties, random_question=False):
    openai_client = get_openai_client()

    if not openai_client:
        raise Exception("OPENAI_API_KEY missing hai. Backend .env me OPENAI_API_KEY add karke server restart karo.")

    context = "\n\n---\n\n".join([item["document"] for item in relevant_properties])

    if random_question:
        system_prompt = """
You are a helpful AI assistant for a real estate website.

User may ask any general/random question. Answer that question normally and helpfully.
After answering, softly suggest latest property options from provided property data.
Do not invent property details.
If property data is provided, only use that data for project suggestions.
Keep answer simple, professional, and Hinglish if user writes Hinglish.
"""
    else:
        system_prompt = """
You are a helpful real estate AI assistant for a property website.

Rules:
1. Answer only from the provided property context for project/property details.
2. Do not invent project names, prices, locations, amenities, possession dates, or seller details.
3. If data is missing, say that the detail is not available.
4. Keep the answer professional, simple, and helpful.
5. If user asks for property suggestions, show matching projects in a clean format.
6. Always encourage enquiry or site visit when suitable.
7. Answer in Hinglish/Hindi style if the user asks in Hinglish.
8. Do not mention internal API, RAG, JSON, or system logic to the user.
"""

    user_prompt = f"""
User Question:
{question}

Available Property Data:
{context}

Now give the best possible answer.
"""

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()},
            ],
            temperature=0.35,
            max_tokens=800,
        )

        return response.choices[0].message.content.strip()
    except Exception as error:
        raise Exception(f"OpenAI API error: {str(error)}")


def get_tenant_from_request(request):
    widget_key = (
        request.data.get("widget_key")
        or request.query_params.get("widget_key")
        or request.headers.get("X-Widget-Key")
    )

    if widget_key:
        return ChatbotTenant.objects.filter(
            widget_key=widget_key,
            is_active=True,
        ).first()

    return ChatbotTenant.objects.filter(is_active=True).first()


def get_or_create_session(request, tenant):
    session_id = request.data.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())

    session, created = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={
            "tenant": tenant,
            "source_url": request.data.get("source_url") or "",
            "ip_address": get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        },
    )

    if tenant and session.tenant_id != tenant.id:
        session.tenant = tenant
        session.save(update_fields=["tenant"])

    return session


def send_lead_email_to_admin_and_seller(lead, tenant):
    subject = f"New Chatbot Lead - {lead.name}"

    message = f"""
New chatbot lead received.

Name: {lead.name}
Phone: {lead.phone}
Email: {lead.email or "Not provided"}
Requirement: {lead.requirement or "Not provided"}

Property: {lead.property_title or "Not selected"}
Seller: {lead.seller_name or "Not available"}
Seller Phone: {lead.seller_phone or "Not available"}
Seller Email: {lead.seller_email or "Not available"}

Source URL: {lead.source_url or "Not available"}
"""

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    admin_email = None

    if tenant and tenant.admin_email:
        admin_email = tenant.admin_email
    else:
        admin_email = getattr(settings, "ADMIN_EMAIL", None)

    if admin_email:
        try:
            send_mail(subject, message, from_email, [admin_email], fail_silently=False)
            lead.is_email_sent_to_admin = True
        except Exception:
            lead.is_email_sent_to_admin = False

    if lead.seller_email:
        try:
            send_mail(subject, message, from_email, [lead.seller_email], fail_silently=False)
            lead.is_email_sent_to_seller = True
        except Exception:
            lead.is_email_sent_to_seller = False

    lead.save(update_fields=["is_email_sent_to_admin", "is_email_sent_to_seller"])


class AIChatbotHealthAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        openai_key = get_env_value("OPENAI_API_KEY", "")
        return Response(
            {
                "status": "ok",
                "message": "AI chatbot API is running",
                "property_api": PROPERTY_API_URL,
                "openai_model": OPENAI_MODEL,
                "openai_key_loaded": bool(openai_key),
                "admin_email_loaded": bool(getattr(settings, "ADMIN_EMAIL", "")),
            }
        )


class ChatbotConfigAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        tenant = get_tenant_from_request(request)

        if not tenant:
            return Response(
                {
                    "success": False,
                    "message": "Chatbot tenant not found. Admin panel me widget_key create karo.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "config": ChatbotTenantSerializer(tenant).data,
            }
        )


class AIChatbotAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        question = request.data.get("message") or request.data.get("question")

        if not question:
            return Response(
                {"success": False, "message": "Message is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tenant = get_tenant_from_request(request)
            session = get_or_create_session(request, tenant)

            ChatMessage.objects.create(
                session=session,
                role="user",
                message=question,
            )

            random_question = not is_property_related_question(question)

            if random_question:
                latest_limit = tenant.latest_project_limit if tenant else 3
                relevant_properties = get_latest_properties(
                    limit=latest_limit,
                    tenant=tenant,
                )
            else:
                relevant_properties = retrieve_relevant_properties(
                    question,
                    limit=5,
                    tenant=tenant,
                )

            answer = build_ai_answer(
                question=question,
                relevant_properties=relevant_properties,
                random_question=random_question,
            )

            properties_payload = make_properties_payload(relevant_properties)

            ChatMessage.objects.create(
                session=session,
                role="bot",
                message=answer,
                properties_payload=properties_payload,
            )

            return Response(
                {
                    "success": True,
                    "session_id": session.session_id,
                    "answer": answer,
                    "is_random_question": random_question,
                    "properties": properties_payload,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as error:
            print("AI CHATBOT ERROR:")
            print(traceback.format_exc())

            return Response(
                {
                    "success": False,
                    "message": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChatLeadCreateAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            tenant = get_tenant_from_request(request)
            session = get_or_create_session(request, tenant)

            name = safe_text(request.data.get("name"))
            phone = safe_text(request.data.get("phone"))
            email = safe_text(request.data.get("email"))
            requirement = safe_text(request.data.get("requirement"))
            property_id = request.data.get("property_id")
            source_url = request.data.get("source_url") or ""

            if not name or not phone:
                return Response(
                    {
                        "success": False,
                        "message": "Name and phone are required.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            selected_property = None
            seller_data = {}

            if property_id:
                properties = fetch_properties(tenant=tenant)
                for item in properties:
                    if str(item.get("id")) == str(property_id):
                        selected_property = property_to_document(item)
                        seller_data = selected_property.get("seller") or {}
                        break

            lead = ChatLead.objects.create(
                tenant=tenant,
                session=session,
                name=name,
                phone=phone,
                email=email or None,
                requirement=requirement or None,
                property_id=property_id or None,
                property_title=selected_property.get("title") if selected_property else "",
                seller_name=seller_data.get("name", ""),
                seller_email=seller_data.get("email", ""),
                seller_phone=seller_data.get("phone", ""),
                source_url=source_url,
            )

            session.visitor_name = name
            session.visitor_phone = phone
            session.visitor_email = email or None
            session.source_url = source_url or session.source_url
            session.save(
                update_fields=[
                    "visitor_name",
                    "visitor_phone",
                    "visitor_email",
                    "source_url",
                ]
            )

            ChatMessage.objects.create(
                session=session,
                role="system",
                message=f"Lead captured: {name}, {phone}, {email}, Requirement: {requirement}",
            )

            send_lead_email_to_admin_and_seller(lead, tenant)

            return Response(
                {
                    "success": True,
                    "message": "Thank you! Our team will contact you shortly.",
                    "lead_id": lead.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as error:
            print("AI CHATBOT LEAD ERROR:")
            print(traceback.format_exc())

            return Response(
                {
                    "success": False,
                    "message": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )