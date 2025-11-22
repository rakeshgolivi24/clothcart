import os
from functools import wraps
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, session, current_app
)
from werkzeug.utils import secure_filename
from database.models import db, User, Category, Product, ProductImage

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["admin_id"] = user.id
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
def logout():
    session.pop("admin_id", None)
    flash("Logged out.", "info")
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    products_count = Product.query.count()
    categories_count = Category.query.count()
    return render_template(
        "admin/dashboard.html",
        products_count=products_count,
        categories_count=categories_count
    )


@admin_bp.route("/products")
@login_required
def products_list():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products_list.html", products=products)


@admin_bp.route("/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    categories = Category.query.all()

    if request.method == "POST":
        name = request.form.get("name")
        slug = request.form.get("slug")
        description = request.form.get("description")
        price = request.form.get("price")
        size_options = request.form.get("size_options")
        category_id = request.form.get("category_id")
        is_featured = bool(request.form.get("is_featured"))
        is_available = bool(request.form.get("is_available"))

        product = Product(
            name=name,
            slug=slug,
            description=description,
            price=price,
            size_options=size_options,
            category_id=category_id,
            is_featured=is_featured,
            is_available=is_available
        )
        db.session.add(product)
        db.session.commit()

        files = request.files.getlist("images")
        upload_folder = os.path.join(current_app.root_path, "static", "uploads", "products")
        os.makedirs(upload_folder, exist_ok=True)

        first = True
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)

                img = ProductImage(
                    product_id=product.id,
                    image_filename=filename,
                    is_main=first
                )
                db.session.add(img)
                first = False

        db.session.commit()
        flash("Product created successfully.", "success")
        return redirect(url_for("admin.products_list"))

    return render_template("admin/add_product.html", categories=categories)


@admin_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == "POST":
        product.name = request.form.get("name")
        product.slug = request.form.get("slug")
        product.description = request.form.get("description")
        product.price = request.form.get("price")
        product.size_options = request.form.get("size_options")
        product.category_id = request.form.get("category_id")
        product.is_featured = bool(request.form.get("is_featured"))
        product.is_available = bool(request.form.get("is_available"))

        files = request.files.getlist("images")
        upload_folder = os.path.join(current_app.root_path, "static", "uploads", "products")
        os.makedirs(upload_folder, exist_ok=True)

        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)

                img = ProductImage(
                    product_id=product.id,
                    image_filename=filename,
                    is_main=False
                )
                db.session.add(img)

        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin.products_list"))

    return render_template("admin/edit_product.html", product=product, categories=categories)


@admin_bp.route("/products/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("admin.products_list"))
