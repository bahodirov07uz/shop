from .models import SiteSettings, StaticPage, TemplateEdit, Cards, PageTitle


def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
        pages = StaticPage.objects.all()
        template_edit = TemplateEdit.objects.all().first()
        cards = Cards.objects.filter(is_about=False)
        about_cards = Cards.objects.filter(is_about=True)
    except SiteSettings.DoesNotExist:
        settings = None
        pages = None
        template_edit = None
        cards = None
        about_cards = None
    return {
        "site_settings": settings,
        "pages": pages,
        "template_settings": template_edit,
        "cards": cards,
        "about_cards": about_cards,
    }


def page_titles(request):
    try:
        pt = PageTitle.objects.first()
        titles = {
            "home": pt.home or "Bosh sahifa",
            "catalog": pt.catalog or "Katalog",
            "detail": pt.detail or "Mahsulot tafsiloti",
            "about": pt.about or "Biz haqimizda",
            "profile": pt.profile or "Profil",
            "cart": pt.cart or "Savatcha",
            "checkout": pt.checkout or "Buyurtma rasmiylash",
            "login": pt.login or "Kirish",
            "register": pt.register or "Royxatdan otish",
            "privacy": pt.privacy or "Maxfiylik siyosati",
            "payment_deliver": pt.payment_deliver or "Tolov va yetkazib berish",
        }
    except Exception:
        titles = {
            "home": "Bosh sahifa",
            "catalog": "Katalog",
            "detail": "Mahsulot tafsiloti",
            "about": "Biz haqimizda",
            "profile": "Profil",
            "cart": "Savatcha",
            "checkout": "Buyurtma rasmiylash",
            "privacy": "Maxfiylik siyosati",
            "payment_deliver": "Tolov va yetkazib berish",
        }
    return {"page_titles": titles}
