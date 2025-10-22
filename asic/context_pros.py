from .models import SiteSettings,StaticPage,TemplateEdit,Cards

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
        'site_settings': settings,
        'pages':pages,
        'template_settings':template_edit,
        'cards':cards,
        'about_cards':about_cards
    }
    
from .models import PageTitle

def page_titles(request):
    titles = {}
    try:
        pt = PageTitle.objects.first()
        titles = {
            "home": pt.home or "Главная страница",
            "catalog": pt.catalog or "Каталог",
            "detail": pt.detail or "Детали продукта",
            "about": pt.about or "О нас",
            "profile": pt.profile or "Профиль",
            "cart": pt.cart or "Корзина",
            "checkout": pt.checkout or "Оформление заказа",
            "login": pt.login or "Login",
            "register": pt.register or "Register",
            "privacy": pt.privacy or "Политика конфиденциальности",
            "payment_deliver": pt.payment_deliver or "Оплата и доставка",
        }
    except:
        # Agar hech narsa DBda bo‘lmasa ham default ishlaydi
        titles = {
            "home": "Главная страница",
            "catalog": "Каталог",
            "detail": "Детали продукта",
            "about": "О нас",
            "profile": "Профиль",
            "cart": "Корзина",
            "checkout": "Оформление заказа",
            "privacy": "Политика конфиденциальности",
            "payment_deliver": "Оплата и доставка",
        }
    return {"page_titles": titles}
