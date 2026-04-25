# import os
# import re
# import uuid
# import traceback
# import requests
# from decimal import Decimal, InvalidOperation

# from django.conf import settings
# from django.core.mail import send_mail

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# from openai import OpenAI

# from .models import ChatbotTenant, ChatSession, ChatMessage, ChatLead
# from .serializers import ChatbotTenantSerializer


# def get_env_value(key, default=None):
#     return os.getenv(key) or getattr(settings, key, default)


# OPENAI_API_KEY = get_env_value("OPENAI_API_KEY", "")
# OPENAI_MODEL = get_env_value("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")
# PROPERTY_API_URL = get_env_value(
#     "PROPERTY_API_URL",
#     "http://127.0.0.1:8000/api/admindashboard/properties/",
# )


# def get_openai_client():
#     api_key = get_env_value("OPENAI_API_KEY", "")
#     if not api_key:
#         return None
#     return OpenAI(api_key=api_key)


# def safe_text(value):
#     if value is None:
#         return ""
#     if isinstance(value, (list, tuple)):
#         return ", ".join([safe_text(v) for v in value if v])
#     if isinstance(value, dict):
#         return " ".join([safe_text(v) for v in value.values()])
#     return str(value).strip()


# def normalize_query(text):
#     text = safe_text(text).lower()
#     text = re.sub(r"[^a-z0-9₹.\s+-]", " ", text)
#     return re.sub(r"\s+", " ", text).strip()


# def format_price(value):
#     if value in [None, "", "null"]:
#         return "Price not available"

#     try:
#         price = Decimal(str(value))
#     except (InvalidOperation, ValueError):
#         return str(value)

#     if price >= 10000000:
#         cr = price / Decimal("10000000")
#         return f"₹{cr:.2f} Cr".replace(".00", "")

#     if price >= 100000:
#         lakh = price / Decimal("100000")
#         return f"₹{lakh:.2f} Lacs".replace(".00", "")

#     return f"₹{price:,.0f}"


# def get_client_ip(request):
#     forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
#     if forwarded_for:
#         return forwarded_for.split(",")[0]
#     return request.META.get("REMOTE_ADDR")

# def get_property_api_url_for_tenant(tenant):
#     if tenant and tenant.property_api_url:
#         return tenant.property_api_url

#     return PROPERTY_API_URL


# def get_property_api_headers_for_tenant(tenant):
#     headers = {
#         "Accept": "application/json",
#     }

#     if not tenant:
#         return headers

#     auth_type = tenant.property_api_auth_type or "none"
#     token = safe_text(tenant.property_api_token)
#     header_name = safe_text(tenant.property_api_key_header) or "Authorization"

#     if auth_type == "bearer" and token:
#         headers["Authorization"] = f"Bearer {token}"

#     elif auth_type == "api_key" and token:
#         headers[header_name] = token

#     return headers


# def fetch_properties(tenant=None):
#     try:
#         api_url = get_property_api_url_for_tenant(tenant)
#         headers = get_property_api_headers_for_tenant(tenant)

#         response = requests.get(api_url, headers=headers, timeout=25)
#         response.raise_for_status()
#         data = response.json()

#         if isinstance(data, dict):
#             if isinstance(data.get("results"), list):
#                 return data.get("results")
#             if isinstance(data.get("data"), list):
#                 return data.get("data")
#             if isinstance(data.get("properties"), list):
#                 return data.get("properties")
#             if isinstance(data.get("projects"), list):
#                 return data.get("projects")

#         if isinstance(data, list):
#             return data

#         return []

#     except Exception as error:
#         raise Exception(f"Property API fetch failed: {str(error)}")

# def property_to_document(property_item):
#     title = safe_text(property_item.get("title"))
#     description = safe_text(property_item.get("description"))
#     city = safe_text(property_item.get("city"))
#     location = safe_text(property_item.get("location"))
#     short_location = safe_text(property_item.get("short_location"))
#     full_address = safe_text(property_item.get("full_address"))
#     developer = safe_text(property_item.get("developer_name"))
#     price = format_price(property_item.get("price"))
#     bedrooms = safe_text(property_item.get("bedrooms"))
#     bathrooms = safe_text(property_item.get("bathrooms"))
#     rooms = safe_text(property_item.get("rooms"))
#     carpet_area = safe_text(property_item.get("carpet_area"))
#     size_sqft = safe_text(property_item.get("size_sqft"))
#     property_type = safe_text(property_item.get("property_type"))
#     property_status = safe_text(property_item.get("property_status"))
#     property_label = safe_text(property_item.get("property_label"))
#     possession_date = safe_text(property_item.get("possession_date"))
#     amenities = safe_text(property_item.get("amenities", []))

#     floor_plans = []
#     for floor in property_item.get("floor_plans", []) or []:
#         floor_plans.append(
#             f"{safe_text(floor.get('floor_name'))}: "
#             f"{safe_text(floor.get('bedrooms'))} bedrooms, "
#             f"{safe_text(floor.get('bathrooms'))} bathrooms, "
#             f"size {safe_text(floor.get('floor_size'))} {safe_text(floor.get('size_postfix'))}, "
#             f"price {format_price(floor.get('floor_price'))}. "
#             f"{safe_text(floor.get('description'))}"
#         )

#     nearby_places = []
#     for place in property_item.get("nearby_places", []) or []:
#         nearby_places.append(
#             f"{safe_text(place.get('place_name'))} - {safe_text(place.get('distance'))}"
#         )

#     seller = property_item.get("contact_seller") or {}
#     fallback_sellers = property_item.get("fallback_sellers") or []

#     seller_data = {}
#     if seller:
#         seller_data = {
#             "name": safe_text(seller.get("full_name")),
#             "email": safe_text(seller.get("email")),
#             "phone": safe_text(seller.get("phone")),
#         }
#     elif fallback_sellers:
#         first_seller = fallback_sellers[0]
#         seller_data = {
#             "name": safe_text(first_seller.get("full_name")),
#             "email": safe_text(first_seller.get("email")),
#             "phone": safe_text(first_seller.get("phone")),
#         }

#     seller_text = ""
#     if seller_data:
#         seller_text = (
#             f"Contact seller: {seller_data.get('name')}, "
#             f"Phone: {seller_data.get('phone')}, "
#             f"Email: {seller_data.get('email')}"
#         )

#     document = f"""
# Property ID: {safe_text(property_item.get("id"))}
# Project Name: {title}
# Description: {description}
# City: {city}
# Location: {location}
# Short Location: {short_location}
# Full Address: {full_address}
# Developer: {developer}
# Price: {price}
# Raw Price: {safe_text(property_item.get("price"))}
# Property Type: {property_type}
# Property Status: {property_status}
# Property Label: {property_label}
# Rooms: {rooms}
# Bedrooms: {bedrooms}
# Bathrooms: {bathrooms}
# Carpet Area: {carpet_area}
# Size Sqft: {size_sqft}
# Possession Date: {possession_date}
# Amenities: {amenities}
# Floor Plans: {" | ".join(floor_plans)}
# Nearby Places: {" | ".join(nearby_places)}
# Video URL: {safe_text(property_item.get("video_url"))}
# Map URL: {safe_text(property_item.get("map_embed_url"))}
# Main Image: {safe_text(property_item.get("imageSrc"))}
# {seller_text}
# """.strip()

#     return {
#         "id": property_item.get("id"),
#         "title": title,
#         "city": city,
#         "location": location or short_location,
#         "developer": developer,
#         "price": price,
#         "bedrooms": bedrooms,
#         "bathrooms": bathrooms,
#         "carpet_area": carpet_area,
#         "image": property_item.get("imageSrc"),
#         "seller": seller_data,
#         "raw": property_item,
#         "document": document,
#         "search_text": normalize_query(document),
#     }


# def extract_budget_number(query):
#     query = query.lower()

#     patterns = [
#         r"under\s+(\d+)\s*cr",
#         r"below\s+(\d+)\s*cr",
#         r"budget\s+(\d+)\s*cr",
#         r"(\d+)\s*cr",
#         r"under\s+(\d+)\s*lakh",
#         r"below\s+(\d+)\s*lakh",
#         r"budget\s+(\d+)\s*lakh",
#         r"(\d+)\s*lakh",
#         r"under\s+(\d+)\s*lac",
#         r"below\s+(\d+)\s*lac",
#         r"(\d+)\s*lac",
#     ]

#     for pattern in patterns:
#         match = re.search(pattern, query)
#         if match:
#             number = int(match.group(1))
#             if "cr" in pattern:
#                 return number * 10000000
#             return number * 100000

#     return None


# def get_property_price_number(property_item):
#     try:
#         return float(property_item.get("price") or 0)
#     except Exception:
#         return 0


# def score_property(query, doc):
#     query_normalized = normalize_query(query)
#     query_words = [word for word in query_normalized.split() if len(word) >= 2]

#     score = 0
#     search_text = doc["search_text"]
#     raw = doc["raw"]

#     for word in query_words:
#         if word in search_text:
#             score += 2

#     city = normalize_query(raw.get("city"))
#     location = normalize_query(raw.get("location"))
#     short_location = normalize_query(raw.get("short_location"))
#     developer = normalize_query(raw.get("developer_name"))
#     title = normalize_query(raw.get("title"))

#     if city and city in query_normalized:
#         score += 25
#     if location and location in query_normalized:
#         score += 18
#     if short_location and short_location in query_normalized:
#         score += 18
#     if developer and developer in query_normalized:
#         score += 18

#     title_words = [w for w in title.split() if len(w) >= 3]
#     for word in title_words:
#         if word in query_normalized:
#             score += 6

#     bedrooms = safe_text(raw.get("bedrooms"))
#     for bhk in ["1", "2", "3", "4", "5"]:
#         if f"{bhk} bhk" in query_normalized and bedrooms == bhk:
#             score += 30

#     budget = extract_budget_number(query_normalized)
#     if budget:
#         property_price = get_property_price_number(raw)
#         if property_price and property_price <= budget:
#             score += 25
#         elif property_price and property_price > budget:
#             score -= 8

#     if "rent" in query_normalized and raw.get("property_status") == "for-rent":
#         score += 25
#     if "sale" in query_normalized and raw.get("property_status") == "for-sale":
#         score += 25
#     if "buy" in query_normalized and raw.get("property_status") == "for-sale":
#         score += 25

#     return score


# def is_property_related_question(question):
#     q = normalize_query(question)

#     property_keywords = [
#         "property",
#         "project",
#         "projects",
#         "latest",
#         "flat",
#         "home",
#         "house",
#         "apartment",
#         "bhk",
#         "bedroom",
#         "price",
#         "budget",
#         "rent",
#         "sale",
#         "buy",
#         "location",
#         "city",
#         "developer",
#         "amenities",
#         "possession",
#         "rera",
#         "carpet",
#         "area",
#         "site visit",
#         "brokerage",
#         "floor",
#         "parking",
#         "mumbai",
#         "thane",
#         "pune",
#         "goregaon",
#         "andheri",
#         "malad",
#         "borivali",
#         "mira road",
#     ]

#     return any(keyword in q for keyword in property_keywords)

# def retrieve_relevant_properties(question, limit=5, tenant=None):
#     properties = fetch_properties(tenant=tenant)
#     documents = [property_to_document(item) for item in properties]

#     scored_docs = []
#     for doc in documents:
#         score = score_property(question, doc)
#         scored_docs.append({**doc, "score": score})

#     scored_docs = sorted(scored_docs, key=lambda item: item["score"], reverse=True)
#     relevant_docs = [doc for doc in scored_docs if doc["score"] > 0]

#     if not relevant_docs:
#         relevant_docs = get_latest_properties(limit=limit, tenant=tenant)

#     return relevant_docs[:limit]

# def get_latest_properties(limit=3, tenant=None):
#     properties = fetch_properties(tenant=tenant)

#     def sort_key(item):
#         return item.get("posting_date") or item.get("created_at") or item.get("id") or ""

#     properties = sorted(properties, key=sort_key, reverse=True)
#     return [property_to_document(item) for item in properties[:limit]]


# def make_properties_payload(properties):
#     payload = []
#     for item in properties:
#         payload.append(
#             {
#                 "id": item.get("id"),
#                 "title": item.get("title"),
#                 "city": item.get("city"),
#                 "location": item.get("location"),
#                 "developer": item.get("developer"),
#                 "price": item.get("price"),
#                 "bedrooms": item.get("bedrooms"),
#                 "bathrooms": item.get("bathrooms"),
#                 "carpet_area": item.get("carpet_area"),
#                 "image": item.get("image"),
#                 "score": item.get("score", 0),
#             }
#         )
#     return payload


# def build_ai_answer(question, relevant_properties, random_question=False):
#     openai_client = get_openai_client()

#     if not openai_client:
#         raise Exception("OPENAI_API_KEY missing hai. Backend .env me OPENAI_API_KEY add karke server restart karo.")

#     context = "\n\n---\n\n".join([item["document"] for item in relevant_properties])

#     if random_question:
#         system_prompt = """
# You are a helpful AI assistant for a real estate website.

# User may ask any general/random question. Answer that question normally and helpfully.
# After answering, softly suggest latest property options from provided property data.
# Do not invent property details.
# If property data is provided, only use that data for project suggestions.
# Keep answer simple, professional, and Hinglish if user writes Hinglish.
# """
#     else:
#         system_prompt = """
# You are a helpful real estate AI assistant for a property website.

# Rules:
# 1. Answer only from the provided property context for project/property details.
# 2. Do not invent project names, prices, locations, amenities, possession dates, or seller details.
# 3. If data is missing, say that the detail is not available.
# 4. Keep the answer professional, simple, and helpful.
# 5. If user asks for property suggestions, show matching projects in a clean format.
# 6. Always encourage enquiry or site visit when suitable.
# 7. Answer in Hinglish/Hindi style if the user asks in Hinglish.
# 8. Do not mention internal API, RAG, JSON, or system logic to the user.
# """

#     user_prompt = f"""
# User Question:
# {question}

# Available Property Data:
# {context}

# Now give the best possible answer.
# """

#     try:
#         response = openai_client.chat.completions.create(
#             model=OPENAI_MODEL,
#             messages=[
#                 {"role": "system", "content": system_prompt.strip()},
#                 {"role": "user", "content": user_prompt.strip()},
#             ],
#             temperature=0.35,
#             max_tokens=800,
#         )

#         return response.choices[0].message.content.strip()
#     except Exception as error:
#         raise Exception(f"OpenAI API error: {str(error)}")


# def get_tenant_from_request(request):
#     widget_key = (
#         request.data.get("widget_key")
#         or request.query_params.get("widget_key")
#         or request.headers.get("X-Widget-Key")
#     )

#     if widget_key:
#         return ChatbotTenant.objects.filter(
#             widget_key=widget_key,
#             is_active=True,
#         ).first()

#     return ChatbotTenant.objects.filter(is_active=True).first()


# def get_or_create_session(request, tenant):
#     session_id = request.data.get("session_id")

#     if not session_id:
#         session_id = str(uuid.uuid4())

#     session, created = ChatSession.objects.get_or_create(
#         session_id=session_id,
#         defaults={
#             "tenant": tenant,
#             "source_url": request.data.get("source_url") or "",
#             "ip_address": get_client_ip(request),
#             "user_agent": request.META.get("HTTP_USER_AGENT", ""),
#         },
#     )

#     if tenant and session.tenant_id != tenant.id:
#         session.tenant = tenant
#         session.save(update_fields=["tenant"])

#     return session


# def send_lead_email_to_admin_and_seller(lead, tenant):
#     subject = f"New Chatbot Lead - {lead.name}"

#     message = f"""
# New chatbot lead received.

# Name: {lead.name}
# Phone: {lead.phone}
# Email: {lead.email or "Not provided"}
# Requirement: {lead.requirement or "Not provided"}

# Property: {lead.property_title or "Not selected"}
# Seller: {lead.seller_name or "Not available"}
# Seller Phone: {lead.seller_phone or "Not available"}
# Seller Email: {lead.seller_email or "Not available"}

# Source URL: {lead.source_url or "Not available"}
# """

#     from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
#     admin_email = None

#     if tenant and tenant.admin_email:
#         admin_email = tenant.admin_email
#     else:
#         admin_email = getattr(settings, "ADMIN_EMAIL", None)

#     if admin_email:
#         try:
#             send_mail(subject, message, from_email, [admin_email], fail_silently=False)
#             lead.is_email_sent_to_admin = True
#         except Exception:
#             lead.is_email_sent_to_admin = False

#     if lead.seller_email:
#         try:
#             send_mail(subject, message, from_email, [lead.seller_email], fail_silently=False)
#             lead.is_email_sent_to_seller = True
#         except Exception:
#             lead.is_email_sent_to_seller = False

#     lead.save(update_fields=["is_email_sent_to_admin", "is_email_sent_to_seller"])


# class AIChatbotHealthAPIView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def get(self, request):
#         openai_key = get_env_value("OPENAI_API_KEY", "")
#         return Response(
#             {
#                 "status": "ok",
#                 "message": "AI chatbot API is running",
#                 "property_api": PROPERTY_API_URL,
#                 "openai_model": OPENAI_MODEL,
#                 "openai_key_loaded": bool(openai_key),
#                 "admin_email_loaded": bool(getattr(settings, "ADMIN_EMAIL", "")),
#             }
#         )


# class ChatbotConfigAPIView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def get(self, request):
#         tenant = get_tenant_from_request(request)

#         if not tenant:
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Chatbot tenant not found. Admin panel me widget_key create karo.",
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         return Response(
#             {
#                 "success": True,
#                 "config": ChatbotTenantSerializer(tenant).data,
#             }
#         )


# class AIChatbotAPIView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def post(self, request):
#         question = request.data.get("message") or request.data.get("question")

#         if not question:
#             return Response(
#                 {"success": False, "message": "Message is required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             tenant = get_tenant_from_request(request)
#             session = get_or_create_session(request, tenant)

#             ChatMessage.objects.create(
#                 session=session,
#                 role="user",
#                 message=question,
#             )

#             random_question = not is_property_related_question(question)

#             if random_question:
#                 latest_limit = tenant.latest_project_limit if tenant else 3
#                 relevant_properties = get_latest_properties(
#                     limit=latest_limit,
#                     tenant=tenant,
#                 )
#             else:
#                 relevant_properties = retrieve_relevant_properties(
#                     question,
#                     limit=5,
#                     tenant=tenant,
#                 )

#             answer = build_ai_answer(
#                 question=question,
#                 relevant_properties=relevant_properties,
#                 random_question=random_question,
#             )

#             properties_payload = make_properties_payload(relevant_properties)

#             ChatMessage.objects.create(
#                 session=session,
#                 role="bot",
#                 message=answer,
#                 properties_payload=properties_payload,
#             )

#             return Response(
#                 {
#                     "success": True,
#                     "session_id": session.session_id,
#                     "answer": answer,
#                     "is_random_question": random_question,
#                     "properties": properties_payload,
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as error:
#             print("AI CHATBOT ERROR:")
#             print(traceback.format_exc())

#             return Response(
#                 {
#                     "success": False,
#                     "message": str(error),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


# class ChatLeadCreateAPIView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def post(self, request):
#         try:
#             tenant = get_tenant_from_request(request)
#             session = get_or_create_session(request, tenant)

#             name = safe_text(request.data.get("name"))
#             phone = safe_text(request.data.get("phone"))
#             email = safe_text(request.data.get("email"))
#             requirement = safe_text(request.data.get("requirement"))
#             property_id = request.data.get("property_id")
#             source_url = request.data.get("source_url") or ""

#             if not name or not phone:
#                 return Response(
#                     {
#                         "success": False,
#                         "message": "Name and phone are required.",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             selected_property = None
#             seller_data = {}

#             if property_id:
#                 properties = fetch_properties(tenant=tenant)
#                 for item in properties:
#                     if str(item.get("id")) == str(property_id):
#                         selected_property = property_to_document(item)
#                         seller_data = selected_property.get("seller") or {}
#                         break

#             lead = ChatLead.objects.create(
#                 tenant=tenant,
#                 session=session,
#                 name=name,
#                 phone=phone,
#                 email=email or None,
#                 requirement=requirement or None,
#                 property_id=property_id or None,
#                 property_title=selected_property.get("title") if selected_property else "",
#                 seller_name=seller_data.get("name", ""),
#                 seller_email=seller_data.get("email", ""),
#                 seller_phone=seller_data.get("phone", ""),
#                 source_url=source_url,
#             )

#             session.visitor_name = name
#             session.visitor_phone = phone
#             session.visitor_email = email or None
#             session.source_url = source_url or session.source_url
#             session.save(
#                 update_fields=[
#                     "visitor_name",
#                     "visitor_phone",
#                     "visitor_email",
#                     "source_url",
#                 ]
#             )

#             ChatMessage.objects.create(
#                 session=session,
#                 role="system",
#                 message=f"Lead captured: {name}, {phone}, {email}, Requirement: {requirement}",
#             )

#             send_lead_email_to_admin_and_seller(lead, tenant)

#             return Response(
#                 {
#                     "success": True,
#                     "message": "Thank you! Our team will contact you shortly.",
#                     "lead_id": lead.id,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )

#         except Exception as error:
#             print("AI CHATBOT LEAD ERROR:")
#             print(traceback.format_exc())

#             return Response(
#                 {
#                     "success": False,
#                     "message": str(error),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )



















import os
import re
import uuid
import traceback
import requests
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from openai import OpenAI

from .models import (
    ChatbotTenant,
    ChatbotPropertyCache,
    ChatSession,
    ChatMessage,
    ChatLead,
)
from .serializers import ChatbotTenantSerializer


def get_env_value(key, default=None):
    return os.getenv(key) or getattr(settings, key, default)


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
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (list, tuple)):
        return ", ".join([safe_text(v) for v in value if v not in [None, "", [], {}]])
    if isinstance(value, dict):
        return " ".join([safe_text(v) for v in value.values()])
    return str(value).strip()


def normalize_query(text):
    text = safe_text(text).lower()
    text = re.sub(r"[^a-z0-9₹.\s+-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def pretty_key(key):
    key = str(key).replace("_", " ").replace("-", " ").replace(".", " ")
    return key.title()


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def get_nested_value(data, path, default=""):
    """
    Supports:
    title
    project.name
    images.0.image_url
    gallery.0.url
    """
    try:
        value = data

        for key in str(path).split("."):
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                if str(key).isdigit():
                    index = int(key)
                    value = value[index] if 0 <= index < len(value) else default
                else:
                    return default
            else:
                return default

        return value if value not in [None, "", [], {}] else default

    except Exception:
        return default


def get_first_existing(data, candidates, default=""):
    for key in candidates:
        value = get_nested_value(data, key)
        if value not in [None, "", [], {}]:
            return value
    return default


def flatten_json(data, parent_key="", output=None):
    """
    Any API format ko readable text me convert karta hai.
    Nested dict/list sab support hai.
    """
    if output is None:
        output = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else str(key)

            if isinstance(value, (dict, list)):
                flatten_json(value, new_key, output)
            else:
                if value not in [None, "", [], {}]:
                    output.append(f"{pretty_key(new_key)}: {safe_text(value)}")

    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_key = f"{parent_key}.{index}"
            if isinstance(item, (dict, list)):
                flatten_json(item, new_key, output)
            else:
                if item not in [None, "", [], {}]:
                    output.append(f"{pretty_key(new_key)}: {safe_text(item)}")

    return output


def format_price(value):
    if value in [None, "", "null"]:
        return ""

    raw = str(value).replace(",", "").replace("₹", "").strip()

    try:
        price = Decimal(raw)
    except (InvalidOperation, ValueError):
        return safe_text(value)

    if price >= 10000000:
        cr = price / Decimal("10000000")
        return f"₹{cr:.2f} Cr".replace(".00", "")

    if price >= 100000:
        lakh = price / Decimal("100000")
        return f"₹{lakh:.2f} Lacs".replace(".00", "")

    return f"₹{price:,.0f}"


def get_dynamic_title(item):
    return safe_text(
        get_first_existing(
            item,
            [
                "title",
                "project_title",
                "project_name",
                "name",
                "property_name",
                "building_name",
                "post_title",
                "project.name",
                "property.title",
                "property.name",
                "listing_title",
                "listing.name",
            ],
            "Property",
        )
    )


def get_dynamic_id(item):
    value = get_first_existing(
        item,
        [
            "id",
            "_id",
            "property_id",
            "project_id",
            "listing_id",
            "slug",
            "code",
            "property_code",
            "project_code",
            "rera",
            "maharera",
        ],
        "",
    )

    if value:
        return safe_text(value)

    title = get_dynamic_title(item)
    slug = normalize_query(title).replace(" ", "-")
    return slug or str(uuid.uuid4())


def get_dynamic_location(item):
    return safe_text(
        get_first_existing(
            item,
            [
                "location",
                "short_location",
                "address",
                "full_address",
                "city",
                "area",
                "locality",
                "neighborhood",
                "project_location",
                "property_location",
                "project.location",
                "property.location",
                "property.address",
                "listing.location",
                "listing.address",
            ],
            "",
        )
    )


def get_dynamic_city(item):
    return safe_text(
        get_first_existing(
            item,
            [
                "city",
                "city_name",
                "project_city",
                "property_city",
                "address.city",
                "location.city",
                "property.city",
                "project.city",
            ],
            "",
        )
    )


def get_dynamic_price(item):
    value = get_first_existing(
        item,
        [
            "price",
            "starting_price",
            "amount",
            "cost",
            "min_price",
            "base_price",
            "offer_price",
            "all_in_price",
            "price_text",
            "pricing.starting_price",
            "pricing.price",
            "pricing.amount",
            "property.price",
            "project.price",
            "listing.price",
        ],
        "",
    )
    return format_price(value) or safe_text(value)


def get_raw_price_number(item):
    value = get_first_existing(
        item,
        [
            "price",
            "starting_price",
            "amount",
            "cost",
            "min_price",
            "base_price",
            "offer_price",
            "all_in_price",
            "pricing.starting_price",
            "pricing.price",
            "pricing.amount",
            "property.price",
            "project.price",
            "listing.price",
        ],
        "",
    )

    try:
        raw = str(value).replace(",", "").replace("₹", "").strip()
        return float(raw)
    except Exception:
        return 0


def get_dynamic_image(item):
    value = get_first_existing(
        item,
        [
            "imageSrc",
            "image",
            "image_url",
            "main_image",
            "featured_image",
            "thumbnail",
            "photo",
            "cover_image",
            "banner_image",
            "property_image",
            "project_image",
            "images.0.image_url",
            "images.0.image",
            "images.0.url",
            "gallery.0.image",
            "gallery.0.url",
            "photos.0.url",
            "photos.0.image",
        ],
        "",
    )

    if value:
        return safe_text(value)

    images = item.get("images") or item.get("gallery") or item.get("photos")
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict):
            return safe_text(
                first.get("image_url")
                or first.get("image")
                or first.get("url")
                or first.get("src")
            )
        return safe_text(first)

    return ""


def get_dynamic_bhk(item):
    value = get_first_existing(
        item,
        [
            "bedrooms",
            "bedroom",
            "bhk",
            "configuration",
            "config",
            "unit_type",
            "typology",
            "property_config",
            "project_config",
            "flat_type",
            "apartment_type",
            "property.bedrooms",
            "project.configuration",
            "listing.bhk",
        ],
        "",
    )
    return safe_text(value)


def get_dynamic_bathrooms(item):
    value = get_first_existing(
        item,
        [
            "bathrooms",
            "bathroom",
            "baths",
            "toilets",
            "property.bathrooms",
            "listing.bathrooms",
        ],
        "",
    )
    return safe_text(value)


def get_dynamic_carpet_area(item):
    value = get_first_existing(
        item,
        [
            "carpet_area",
            "area",
            "size",
            "size_sqft",
            "floor_size",
            "builtup_area",
            "super_builtup_area",
            "rera_carpet",
            "property.area",
            "property.carpet_area",
            "project.carpet_area",
            "listing.area",
        ],
        "",
    )
    return safe_text(value)


def get_dynamic_developer(item):
    return safe_text(
        get_first_existing(
            item,
            [
                "developer_name",
                "developer",
                "builder",
                "builder_name",
                "company",
                "brand",
                "agency",
                "project.developer",
                "developer.name",
                "builder.name",
                "company.name",
            ],
            "",
        )
    )


def extract_seller_data(item):
    seller = (
        item.get("contact_seller")
        or item.get("seller")
        or item.get("agent")
        or item.get("sales_person")
        or {}
    )
    fallback_sellers = (
        item.get("fallback_sellers")
        or item.get("agents")
        or item.get("sellers")
        or item.get("sales_team")
        or []
    )

    if isinstance(seller, dict) and seller:
        return {
            "name": safe_text(
                seller.get("full_name")
                or seller.get("name")
                or seller.get("seller_name")
                or seller.get("agent_name")
            ),
            "email": safe_text(
                seller.get("email")
                or seller.get("seller_email")
                or seller.get("agent_email")
            ),
            "phone": safe_text(
                seller.get("phone")
                or seller.get("mobile")
                or seller.get("contact")
                or seller.get("seller_phone")
                or seller.get("agent_phone")
            ),
        }

    if isinstance(fallback_sellers, list) and fallback_sellers:
        first = fallback_sellers[0]
        if isinstance(first, dict):
            return {
                "name": safe_text(first.get("full_name") or first.get("name")),
                "email": safe_text(first.get("email")),
                "phone": safe_text(first.get("phone") or first.get("mobile")),
            }

    return {}


def property_to_dynamic_document(item):
    """
    Main dynamic converter.
    Kisi bhi tenant API ke fields ko read karega.
    Unknown/extra fields bhi All Available API Fields me AI ko milenge.
    """
    external_id = get_dynamic_id(item)
    title = get_dynamic_title(item)
    city = get_dynamic_city(item)
    location = get_dynamic_location(item)
    price = get_dynamic_price(item)
    image = get_dynamic_image(item)
    bhk = get_dynamic_bhk(item)
    bathrooms = get_dynamic_bathrooms(item)
    carpet_area = get_dynamic_carpet_area(item)
    developer = get_dynamic_developer(item)
    seller_data = extract_seller_data(item)

    flattened_lines = flatten_json(item)
    flattened_text = "\n".join(flattened_lines)

    document = f"""
Auto Detected Main Details:
Property ID: {external_id}
Title/Project Name: {title}
City: {city}
Location: {location}
Price: {price}
BHK/Configuration: {bhk}
Bathrooms: {bathrooms}
Carpet Area/Size: {carpet_area}
Developer/Builder: {developer}
Image: {image}
Seller Name: {seller_data.get("name", "")}
Seller Phone: {seller_data.get("phone", "")}
Seller Email: {seller_data.get("email", "")}

All Available API Fields:
{flattened_text}
""".strip()

    return {
        "id": external_id,
        "title": title,
        "city": city,
        "location": location or city,
        "developer": developer,
        "price": price or "Price not available",
        "bedrooms": bhk,
        "bathrooms": bathrooms,
        "carpet_area": carpet_area,
        "image": image,
        "seller": seller_data,
        "raw": item,
        "document": document,
        "flattened_text": flattened_text,
        "search_text": normalize_query(document),
        "raw_price_number": get_raw_price_number(item),
    }


def get_property_api_url_for_tenant(tenant):
    if tenant and tenant.property_api_url:
        return tenant.property_api_url
    return PROPERTY_API_URL


def get_property_api_headers_for_tenant(tenant):
    headers = {"Accept": "application/json"}

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


def extract_items_from_api_response(data):
    """
    Supported formats:
    1. [ {...}, {...} ]
    2. { results: [...] }
    3. { data: [...] }
    4. { properties: [...] }
    5. { projects: [...] }
    6. { listings: [...] }
    7. { payload: { results: [...] } }
    """
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    direct_keys = [
        "results",
        "data",
        "properties",
        "projects",
        "listings",
        "items",
        "records",
    ]

    for key in direct_keys:
        if isinstance(data.get(key), list):
            return data.get(key)

    for value in data.values():
        if isinstance(value, dict):
            nested = extract_items_from_api_response(value)
            if nested:
                return nested

    return []


def sync_property_cache(tenant, items):
    if not tenant:
        return

    for item in items:
        if not isinstance(item, dict):
            continue

        doc = property_to_dynamic_document(item)

        ChatbotPropertyCache.objects.update_or_create(
            tenant=tenant,
            external_id=str(doc["id"]),
            defaults={
                "title": doc["title"][:255] if doc["title"] else "",
                "location": doc["location"][:255] if doc["location"] else "",
                "price_text": doc["price"][:255] if doc["price"] else "",
                "image_url": doc["image"] or None,
                "raw_data": item,
                "flattened_text": doc["flattened_text"],
            },
        )


def fetch_properties(tenant=None):
    try:
        api_url = get_property_api_url_for_tenant(tenant)
        headers = get_property_api_headers_for_tenant(tenant)

        response = requests.get(api_url, headers=headers, timeout=25)
        response.raise_for_status()
        data = response.json()

        items = extract_items_from_api_response(data)

        if tenant and getattr(tenant, "auto_sync_property_cache", False):
            sync_property_cache(tenant, items)

        return [item for item in items if isinstance(item, dict)]

    except Exception as error:
        if tenant:
            cached_items = list(
                ChatbotPropertyCache.objects.filter(tenant=tenant)
                .order_by("-last_synced_at")
                .values_list("raw_data", flat=True)
            )
            if cached_items:
                return cached_items

        raise Exception(f"Property API fetch failed: {str(error)}")


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


def score_property(query, doc):
    query_normalized = normalize_query(query)
    query_words = [word for word in query_normalized.split() if len(word) >= 2]

    score = 0
    search_text = doc.get("search_text", "")

    for word in query_words:
        if word in search_text:
            score += 3

    title = normalize_query(doc.get("title"))
    city = normalize_query(doc.get("city"))
    location = normalize_query(doc.get("location"))
    developer = normalize_query(doc.get("developer"))
    bhk = normalize_query(doc.get("bedrooms"))

    if title and any(part in query_normalized for part in title.split() if len(part) >= 3):
        score += 20

    if city and city in query_normalized:
        score += 25

    if location and any(part in query_normalized for part in location.split() if len(part) >= 3):
        score += 20

    if developer and any(part in query_normalized for part in developer.split() if len(part) >= 3):
        score += 15

    for bhk_num in ["1", "2", "3", "4", "5"]:
        if f"{bhk_num} bhk" in query_normalized and bhk_num in bhk:
            score += 25

    budget = extract_budget_number(query_normalized)
    raw_price = doc.get("raw_price_number") or 0

    if budget and raw_price:
        if raw_price <= budget:
            score += 20
        else:
            score -= 8

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
        "builder",
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
        "details",
        "configuration",
        "unit",
        "tower",
    ]

    return any(keyword in q for keyword in property_keywords)


def get_latest_properties(limit=3, tenant=None):
    properties = fetch_properties(tenant=tenant)
    docs = [property_to_dynamic_document(item) for item in properties]

    def sort_key(doc):
        raw = doc.get("raw") or {}
        return (
            raw.get("posting_date")
            or raw.get("created_at")
            or raw.get("updated_at")
            or raw.get("date")
            or str(raw.get("id") or "")
        )

    docs = sorted(docs, key=sort_key, reverse=True)
    return docs[:limit]


def retrieve_relevant_properties(question, limit=5, tenant=None):
    properties = fetch_properties(tenant=tenant)
    docs = [property_to_dynamic_document(item) for item in properties]

    scored_docs = []
    for doc in docs:
        scored_docs.append({**doc, "score": score_property(question, doc)})

    scored_docs = sorted(scored_docs, key=lambda item: item["score"], reverse=True)
    relevant_docs = [doc for doc in scored_docs if doc["score"] > 0]

    if not relevant_docs:
        return get_latest_properties(limit=limit, tenant=tenant)

    return relevant_docs[:limit]


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
                "all_fields": item.get("raw") or {},
            }
        )

    return payload


def build_ai_answer(question, relevant_properties, random_question=False):
    openai_client = get_openai_client()

    if not openai_client:
        raise Exception(
            "OPENAI_API_KEY missing hai. Backend .env me OPENAI_API_KEY add karke server restart karo."
        )

    context = "\n\n--- PROPERTY DATA ---\n\n".join(
        [item["document"] for item in relevant_properties]
    )

    system_prompt = """
You are a helpful AI chatbot for a real estate/property website.

Rules:
1. Every tenant property API can have different fields and different format.
2. Use Auto Detected Main Details and All Available API Fields from context.
3. Do not invent project names, prices, locations, amenities, possession, RERA, seller details, or any property data.
4. If any detail is not available in context, clearly say that detail is not available.
5. If user asks a random/general question, answer it normally and then softly suggest latest properties from context.
6. Keep answer professional, simple, and helpful.
7. Answer in Hinglish/Hindi if user writes in Hinglish/Hindi.
8. Do not mention API, JSON, RAG, backend, internal fields, or system logic.
9. When suggesting properties, use clean format with project name, location, price, configuration, and CTA for enquiry/site visit.
"""

    user_prompt = f"""
User Question:
{question}

Available Property Data:
{context}

Now answer the user.
"""

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()},
            ],
            temperature=0.3,
            max_tokens=900,
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
        tenant_count = ChatbotTenant.objects.count()

        return Response(
            {
                "status": "ok",
                "message": "AI chatbot API is running",
                "property_api": PROPERTY_API_URL,
                "openai_model": OPENAI_MODEL,
                "openai_key_loaded": bool(openai_key),
                "admin_email_loaded": bool(getattr(settings, "ADMIN_EMAIL", "")),
                "tenant_count": tenant_count,
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

            if not tenant:
                return Response(
                    {
                        "success": False,
                        "message": "Chatbot tenant not found. Please valid widget_key bhejo.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

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

            if not tenant:
                return Response(
                    {
                        "success": False,
                        "message": "Chatbot tenant not found. Please valid widget_key bhejo.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            session = get_or_create_session(request, tenant)

            name = safe_text(request.data.get("name"))
            phone = safe_text(request.data.get("phone"))
            email = safe_text(request.data.get("email"))
            requirement = safe_text(request.data.get("requirement"))
            property_id = safe_text(request.data.get("property_id"))
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
                    doc = property_to_dynamic_document(item)
                    if str(doc.get("id")) == str(property_id):
                        selected_property = doc
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


class ChatbotWidgetJSAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        js_code = r"""
(function () {
  if (window.GrowlChatbotLoaded) return;
  window.GrowlChatbotLoaded = true;

  var config = window.GROWL_CHATBOT_CONFIG || {};
  var API_BASE = config.apiBase || "http://127.0.0.1:8000";
  var WIDGET_KEY = config.widgetKey || "growl-main";

  var sessionId = localStorage.getItem("growl_external_chat_session_id") || "";
  var botConfig = {
    bot_name: "Property AI Assistant",
    welcome_message: "Hi! Main aapki property search me help kar sakta hoon.",
    primary_color: "#FF7A1A",
    secondary_color: "#0B1320"
  };

  var isOpen = false;
  var messages = [{ role: "bot", text: botConfig.welcome_message }];

  function createEl(tag, styles, text) {
    var el = document.createElement(tag);
    if (styles) {
      Object.keys(styles).forEach(function (key) {
        el.style[key] = styles[key];
      });
    }
    if (text) el.textContent = text;
    return el;
  }

  function fetchConfig() {
    fetch(API_BASE + "/api/aichatbot/config/?widget_key=" + encodeURIComponent(WIDGET_KEY))
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.success && data.config) {
          botConfig = data.config;
          messages = [{ role: "bot", text: botConfig.welcome_message }];
          render();
        }
      })
      .catch(function () {});
  }

  function saveSession(newSessionId) {
    if (!newSessionId) return;
    sessionId = newSessionId;
    localStorage.setItem("growl_external_chat_session_id", newSessionId);
  }

  function sendMessage(text) {
    if (!text || !text.trim()) return;

    messages.push({ role: "user", text: text });
    messages.push({ role: "bot", text: "Searching best answer...", loading: true });
    render();

    fetch(API_BASE + "/api/aichatbot/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Widget-Key": WIDGET_KEY
      },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
        widget_key: WIDGET_KEY,
        source_url: window.location.href
      })
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok || !data.success) throw new Error(data.message || "API Error");
          return data;
        });
      })
      .then(function (data) {
        saveSession(data.session_id);
        messages = messages.filter(function (m) { return !m.loading; });
        messages.push({
          role: "bot",
          text: data.answer,
          properties: data.properties || []
        });
        render();
      })
      .catch(function (error) {
        messages = messages.filter(function (m) { return !m.loading; });
        messages.push({ role: "bot", text: "Chatbot Error: " + error.message });
        render();
      });
  }

  function submitLead(formData, propertyId) {
    fetch(API_BASE + "/api/aichatbot/lead/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Widget-Key": WIDGET_KEY
      },
      body: JSON.stringify({
        name: formData.name,
        phone: formData.phone,
        email: formData.email,
        requirement: formData.requirement,
        property_id: propertyId || "",
        session_id: sessionId,
        widget_key: WIDGET_KEY,
        source_url: window.location.href
      })
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok || !data.success) throw new Error(data.message || "Lead submit failed");
          return data;
        });
      })
      .then(function (data) {
        messages.push({ role: "bot", text: data.message || "Thank you! Our team will contact you shortly." });
        render();
      })
      .catch(function (error) {
        messages.push({ role: "bot", text: "Lead submit nahi hua: " + error.message });
        render();
      });
  }

  function inputStyle() {
    return {
      width: "100%",
      marginBottom: "10px",
      outline: "none",
      border: "1px solid rgba(255,255,255,0.12)",
      background: "#0B1320",
      color: "#FFFFFF",
      borderRadius: "12px",
      padding: "12px",
      fontSize: "13px",
      boxSizing: "border-box",
      fontFamily: "Arial, sans-serif"
    };
  }

  function openLeadPopup(property) {
    var overlay = createEl("div", {
      position: "fixed",
      inset: "0",
      background: "rgba(0,0,0,0.55)",
      zIndex: "1000001",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "18px"
    });

    var box = createEl("div", {
      width: "360px",
      maxWidth: "100%",
      background: "#111827",
      border: "1px solid rgba(255,255,255,0.12)",
      borderRadius: "18px",
      padding: "16px",
      boxShadow: "0 24px 70px rgba(0,0,0,0.35)",
      fontFamily: "Arial, sans-serif"
    });

    var title = createEl("h3", {
      margin: "0 0 12px",
      color: "#FFFFFF",
      fontSize: "17px",
      fontWeight: "800"
    }, "Get Property Assistance");

    var nameInput = createEl("input", inputStyle());
    nameInput.placeholder = "Your Name *";

    var phoneInput = createEl("input", inputStyle());
    phoneInput.placeholder = "Phone Number *";

    var emailInput = createEl("input", inputStyle());
    emailInput.placeholder = "Email";

    var reqInput = createEl("textarea", inputStyle());
    reqInput.placeholder = "Requirement";
    reqInput.style.minHeight = "76px";
    reqInput.style.resize = "none";
    reqInput.value = property && property.title ? "I am interested in " + property.title : "";

    var submit = createEl("button", {
      width: "100%",
      border: "none",
      background: botConfig.primary_color || "#FF7A1A",
      color: "#FFFFFF",
      borderRadius: "12px",
      padding: "12px",
      fontWeight: "800",
      cursor: "pointer"
    }, "Submit Enquiry");

    var close = createEl("button", {
      width: "100%",
      marginTop: "8px",
      border: "1px solid rgba(255,255,255,0.12)",
      background: "transparent",
      color: "#FFFFFF",
      borderRadius: "12px",
      padding: "10px",
      cursor: "pointer"
    }, "Close");

    close.onclick = function () {
      document.body.removeChild(overlay);
    };

    submit.onclick = function () {
      if (!nameInput.value.trim() || !phoneInput.value.trim()) {
        alert("Please name aur phone number fill karo.");
        return;
      }

      submitLead({
        name: nameInput.value,
        phone: phoneInput.value,
        email: emailInput.value,
        requirement: reqInput.value
      }, property && property.id ? property.id : "");

      document.body.removeChild(overlay);
    };

    box.appendChild(title);
    box.appendChild(nameInput);
    box.appendChild(phoneInput);
    box.appendChild(emailInput);
    box.appendChild(reqInput);
    box.appendChild(submit);
    box.appendChild(close);

    overlay.appendChild(box);
    document.body.appendChild(overlay);
  }

  function render() {
    var oldRoot = document.getElementById("growl-ai-chatbot-root");
    if (oldRoot) oldRoot.remove();

    var root = createEl("div");
    root.id = "growl-ai-chatbot-root";
    document.body.appendChild(root);

    var floatingBtn = createEl("button", {
      position: "fixed",
      right: "24px",
      bottom: "24px",
      width: "62px",
      height: "62px",
      borderRadius: "50%",
      border: "none",
      background: "linear-gradient(135deg, " + (botConfig.primary_color || "#FF7A1A") + ", #FF6A00)",
      color: "#FFFFFF",
      fontWeight: "800",
      fontSize: "18px",
      boxShadow: "0 14px 35px rgba(255,122,26,0.35)",
      zIndex: "999999",
      cursor: "pointer",
      fontFamily: "Arial, sans-serif"
    }, "AI");

    floatingBtn.onclick = function () {
      isOpen = true;
      render();
    };

    root.appendChild(floatingBtn);

    if (!isOpen) return;

    var chatBox = createEl("div", {
      position: "fixed",
      right: "24px",
      bottom: "98px",
      width: "410px",
      maxWidth: "calc(100vw - 32px)",
      height: "610px",
      maxHeight: "calc(100vh - 130px)",
      background: botConfig.secondary_color || "#0B1320",
      borderRadius: "22px",
      boxShadow: "0 24px 70px rgba(0,0,0,0.35)",
      overflow: "hidden",
      display: "flex",
      flexDirection: "column",
      zIndex: "999999",
      border: "1px solid rgba(255,255,255,0.08)",
      fontFamily: "Arial, sans-serif"
    });

    var header = createEl("div", {
      padding: "18px",
      background: "linear-gradient(135deg, #0F1B2D, #1A2333)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      borderBottom: "1px solid rgba(255,255,255,0.08)"
    });

    var headerText = createEl("div");

    var h3 = createEl("h3", {
      margin: "0",
      color: "#FFFFFF",
      fontSize: "17px",
      fontWeight: "800"
    }, botConfig.bot_name || "Property AI Assistant");

    var p = createEl("p", {
      margin: "4px 0 0",
      color: "#9CA3AF",
      fontSize: "12px"
    }, "Ask about projects, price, BHK & location");

    headerText.appendChild(h3);
    headerText.appendChild(p);

    var closeBtn = createEl("button", {
      width: "34px",
      height: "34px",
      borderRadius: "50%",
      border: "1px solid rgba(255,255,255,0.12)",
      background: "rgba(255,255,255,0.06)",
      color: "#FFFFFF",
      fontSize: "24px",
      cursor: "pointer",
      lineHeight: "28px"
    }, "×");

    closeBtn.onclick = function () {
      isOpen = false;
      render();
    };

    header.appendChild(headerText);
    header.appendChild(closeBtn);

    var messagesArea = createEl("div", {
      flex: "1",
      padding: "16px",
      overflowY: "auto",
      background: "radial-gradient(circle at top, rgba(255,122,26,0.08), transparent 34%), #0B1320"
    });

    messages.forEach(function (msg) {
      var row = createEl("div", {
        display: "flex",
        justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
        marginBottom: "12px"
      });

      var bubble = createEl("div", {
        maxWidth: "88%",
        borderRadius: "16px",
        padding: "12px 13px",
        background: msg.role === "user"
          ? "linear-gradient(135deg, " + (botConfig.primary_color || "#FF7A1A") + ", #FF6A00)"
          : "#111827",
        color: "#E5E7EB",
        border: msg.role === "user" ? "none" : "1px solid rgba(255,255,255,0.08)",
        whiteSpace: "pre-wrap",
        fontSize: "13.5px",
        lineHeight: "1.55"
      }, msg.text);

      if (Array.isArray(msg.properties) && msg.properties.length > 0) {
        var list = createEl("div", {
          marginTop: "12px",
          display: "grid",
          gap: "10px"
        });

        msg.properties.slice(0, 3).forEach(function (property) {
          var card = createEl("div", {
            display: "flex",
            gap: "10px",
            background: "#0B1320",
            borderRadius: "14px",
            padding: "9px",
            border: "1px solid rgba(255,255,255,0.08)"
          });

          if (property.image) {
            var img = createEl("img", {
              width: "72px",
              height: "72px",
              borderRadius: "12px",
              objectFit: "cover",
              flexShrink: "0"
            });
            img.src = property.image;
            card.appendChild(img);
          }

          var content = createEl("div", { flex: "1" });

          var title = createEl("h4", {
            margin: "0 0 4px",
            color: "#FFFFFF",
            fontSize: "13px",
            fontWeight: "800"
          }, property.title || "Property");

          var meta = createEl("p", {
            margin: "0 0 3px",
            color: "#9CA3AF",
            fontSize: "11.5px"
          }, property.location || property.city || "");

          var price = createEl("p", {
            margin: "0 0 6px",
            color: "#9CA3AF",
            fontSize: "11.5px"
          }, (property.bedrooms || "Config not available") + " • " + (property.price || "Price not available"));

          var enquire = createEl("button", {
            border: "none",
            background: botConfig.primary_color || "#FF7A1A",
            color: "#FFFFFF",
            borderRadius: "999px",
            padding: "6px 10px",
            fontSize: "11px",
            fontWeight: "700",
            cursor: "pointer"
          }, "Enquire");

          enquire.onclick = function () {
            openLeadPopup(property);
          };

          content.appendChild(title);
          content.appendChild(meta);
          content.appendChild(price);
          content.appendChild(enquire);

          card.appendChild(content);
          list.appendChild(card);
        });

        bubble.appendChild(list);
      }

      row.appendChild(bubble);
      messagesArea.appendChild(row);
    });

    var quickActions = createEl("div", {
      display: "flex",
      gap: "8px",
      padding: "10px 12px 0",
      background: "#0F1B2D"
    });

    [
      { label: "Latest Projects", text: "latest project" },
      { label: "Site Visit", text: "Site visit book karna hai" },
      { label: "Contact Me", lead: true }
    ].forEach(function (btn) {
      var b = createEl("button", {
        border: "1px solid rgba(255,255,255,0.1)",
        background: "#111827",
        color: "#E5E7EB",
        borderRadius: "999px",
        padding: "8px 10px",
        fontSize: "11px",
        cursor: "pointer"
      }, btn.label);

      b.onclick = function () {
        if (btn.lead) {
          openLeadPopup(null);
        } else {
          sendMessage(btn.text);
        }
      };

      quickActions.appendChild(b);
    });

    var inputArea = createEl("div", {
      padding: "12px",
      background: "#0F1B2D",
      borderTop: "1px solid rgba(255,255,255,0.08)",
      display: "flex",
      gap: "10px"
    });

    var input = createEl("textarea", {
      flex: "1",
      resize: "none",
      outline: "none",
      border: "1px solid rgba(255,255,255,0.1)",
      background: "#111827",
      color: "#FFFFFF",
      borderRadius: "14px",
      padding: "12px 13px",
      fontSize: "13px",
      minHeight: "44px",
      fontFamily: "Arial, sans-serif"
    });

    input.placeholder = "Example: Mumbai me 2 BHK under 1 Cr batao...";

    input.onkeydown = function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        var value = input.value;
        input.value = "";
        sendMessage(value);
      }
    };

    var sendBtn = createEl("button", {
      border: "none",
      borderRadius: "14px",
      background: botConfig.primary_color || "#FF7A1A",
      color: "#FFFFFF",
      padding: "0 18px",
      fontWeight: "800",
      cursor: "pointer"
    }, "Send");

    sendBtn.onclick = function () {
      var value = input.value;
      input.value = "";
      sendMessage(value);
    };

    inputArea.appendChild(input);
    inputArea.appendChild(sendBtn);

    chatBox.appendChild(header);
    chatBox.appendChild(messagesArea);
    chatBox.appendChild(quickActions);
    chatBox.appendChild(inputArea);

    root.appendChild(chatBox);

    setTimeout(function () {
      messagesArea.scrollTop = messagesArea.scrollHeight;
    }, 50);
  }

  fetchConfig();
  render();
})();
"""
        return HttpResponse(js_code, content_type="application/javascript")