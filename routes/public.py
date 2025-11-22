# from flask import Blueprint, render_template
# from database.models import Product, Category
# from urllib.parse import quote

# public_bp = Blueprint("public", __name__)

# SHOP_WHATSAPP_NUMBER = "919876543210"

# @public_bp.route("/")
# def home():
#     featured = Product.query.filter_by(is_featured=True, is_available=True).limit(8).all()
#     categories = Category.query.all()
#     return render_template("home.html", featured=featured, categories=categories)

# @public_bp.route("/products")
# @public_bp.route("/category/<slug>")
# def products(slug=None):
#     categories = Category.query.all()
#     query = Product.query.filter_by(is_available=True)
#     if slug:
#         query = query.join(Category).filter(Category.slug == slug)
#     return render_template("products.html", products=query.all(), categories=categories)

# @public_bp.route("/product/<slug>")
# def product_detail(slug):
#     product = Product.query.filter_by(slug=slug, is_available=True).first_or_404()
#     msg = f"Hi, I want to order: {product.name} - ₹{product.price}"
#     url = f"https://wa.me/{SHOP_WHATSAPP_NUMBER}?text={quote(msg)}"
#     return render_template("product_detail.html", product=product, whatsapp_url=url)


from flask import Blueprint, render_template
from urllib.parse import quote
from database.models import Product, Category

public_bp = Blueprint("public", __name__)

SHOP_WHATSAPP_NUMBER = "919030562005"  # change per client later


@public_bp.route("/")
def home():
    featured = Product.query.filter_by(is_featured=True, is_available=True).limit(8).all()
    categories = Category.query.all()
    return render_template("home.html", featured=featured, categories=categories)


@public_bp.route("/products")
@public_bp.route("/category/<string:slug>")
def products(slug=None):
    categories = Category.query.all()
    query = Product.query.filter_by(is_available=True)
    active_category = None

    if slug:
        query = query.join(Category).filter(Category.slug == slug)
        active_category = Category.query.filter_by(slug=slug).first()

    products_list = query.all()
    return render_template(
        "products.html",
        products=products_list,
        categories=categories,
        active_category=active_category
    )


@public_bp.route("/product/<string:slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_available=True).first_or_404()

    msg = (
        f"Hi, I saw your demo clothing website!\n"
        f"I'm interested in creating a similar online catalog for my shop.\n"
        f"Please contact me."
    )
    encoded = quote(msg)
    whatsapp_url = f"https://wa.me/{SHOP_WHATSAPP_NUMBER}?text={encoded}"

    main_image = None
    if product.images:
        main_image = next((img for img in product.images if img.is_main), product.images[0])

    return render_template(
        "product_detail.html",
        product=product,
        main_image=main_image,
        whatsapp_url=whatsapp_url,
    )


