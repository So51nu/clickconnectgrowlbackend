from django.core.management.base import BaseCommand
from footermenu.models import FooterSection, FooterMenuItem


FOOTER_DATA = [
    {
        "title": "Domestic cities",
        "slug": "domestic",
        "section_type": "tab",
        "order": 1,
        "items": [],
    },
    {
        "title": "International cities",
        "slug": "international",
        "section_type": "tab",
        "order": 2,
        "items": [
            {"title": "No found", "url": "/", "order": 1},
        ],
    },
    {
        "title": "Regions",
        "slug": "regions",
        "section_type": "tab",
        "order": 3,
        "items": [],
    },
    {
        "title": "Countries",
        "slug": "countries",
        "section_type": "tab",
        "order": 4,
        "items": [],
    },
    {
        "title": "Places to stay",
        "slug": "places",
        "section_type": "tab",
        "order": 5,
        "items": [
            {"title": "Homestays", "url": "/", "order": 1},
            {"title": "5-Star Hotels", "url": "/", "order": 2},
            {"title": "Cottages", "url": "/", "order": 3},
            {"title": "Guest Houses", "url": "/", "order": 4},
            {"title": "Beach Hotels", "url": "/", "order": 5},
            {"title": "Villas", "url": "/", "order": 6},
            {"title": "Luxury Hotels", "url": "/", "order": 7},
            {"title": "3-Star Hotels", "url": "/", "order": 8},
            {"title": "Resorts", "url": "/", "order": 9},
            {"title": "Family Hotels", "url": "/", "order": 10},
            {"title": "Apartments", "url": "/", "order": 11},
            {"title": "Farm stays", "url": "/", "order": 12},
            {"title": "Hostels", "url": "/", "order": 13},
            {"title": "Luxury Tents", "url": "/", "order": 14},
            {"title": "4-Star Hotels", "url": "/", "order": 15},
            {"title": "Capsule Hotels", "url": "/", "order": 16},
            {"title": "Cheap hotels", "url": "/", "order": 17},
            {"title": "Pet-Friendly Hotels", "url": "/", "order": 18},
            {"title": "Boats", "url": "/", "order": 19},
            {"title": "Serviced apartments", "url": "/", "order": 20},
        ],
    },
    {
        "title": "Support",
        "slug": "support",
        "section_type": "column",
        "order": 10,
        "items": [
            {"title": "Manage your property enquiries", "url": "/contact", "order": 1},
            {"title": "Contact Customer Service", "url": "/contact", "order": 2},
            {"title": "Help Center", "url": "/faq", "order": 3},
        ],
    },
    {
        "title": "Discover",
        "slug": "discover",
        "section_type": "column",
        "order": 11,
        "items": [
            {"title": "New Launch Projects", "url": "/property-gird-top-search?property_label=new-listing", "order": 1},
            {"title": "Featured Projects", "url": "/property-gird-top-search?property_label=featured", "order": 2},
            {"title": "Properties for Sale", "url": "/property-gird-top-search?property_status=for-sale", "order": 3},
            {"title": "Developers", "url": "/developers", "order": 4},
            {"title": "Cities", "url": "/cities", "order": 5},
            {"title": "Blog", "url": "/blog-list", "order": 6},
        ],
    },
    {
        "title": "Terms and settings",
        "slug": "terms-and-settings",
        "section_type": "column",
        "order": 12,
        "items": [
            {"title": "Privacy Policy", "url": "/privacy-policy", "order": 1},
            {"title": "Terms of Service", "url": "/terms-and-conditions", "order": 2},
            {"title": "Accessibility Statement", "url": "/", "order": 3},
            {"title": "Grievance Officer", "url": "/contact", "order": 4},
        ],
    },
    {
        "title": "Partners",
        "slug": "partners",
        "section_type": "column",
        "order": 13,
        "items": [
            {"title": "Seller Login", "url": "#modalLogin", "order": 1, "is_login_modal": True},
            {"title": "List your property", "url": "/contact", "order": 2},
            {"title": "Become a partner", "url": "/contact", "order": 3},
            {"title": "Partner help", "url": "/contact", "order": 4},
        ],
    },
    {
        "title": "About",
        "slug": "about",
        "section_type": "column",
        "order": 14,
        "items": [
            {"title": "About Growl Real Estate", "url": "/about", "order": 1},
            {"title": "How We Work", "url": "/about", "order": 2},
            {"title": "Careers", "url": "/contact", "order": 3},
            {"title": "Corporate contact", "url": "/contact", "order": 4},
            {"title": "Content guidelines", "url": "/", "order": 5},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed default footer menu sections and items"

    def handle(self, *args, **options):
        for section_data in FOOTER_DATA:
            items = section_data.pop("items", [])

            section, _ = FooterSection.objects.update_or_create(
                slug=section_data["slug"],
                defaults=section_data,
            )

            for item_data in items:
                FooterMenuItem.objects.update_or_create(
                    section=section,
                    title=item_data["title"],
                    defaults={
                        "url": item_data.get("url", "/"),
                        "order": item_data.get("order", 0),
                        "is_active": item_data.get("is_active", True),
                        "is_login_modal": item_data.get("is_login_modal", False),
                    },
                )

        self.stdout.write(self.style.SUCCESS("Footer menu seeded successfully."))