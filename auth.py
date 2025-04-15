from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from app import app, db
from models import User, Contact, BlogPost, Product, Tag # Added Product and Tag models
from forms import LoginForm, BlogPostForm, ProductForm # Added ProductForm
import logging

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('auth/login.html', form=form, title='Login')

@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/auth/dashboard')
@login_required
def admin_dashboard():
    return render_template('auth/dashboard.html', title='Admin Dashboard')

# API endpoint to get contacts for the dashboard
@app.route('/api/contacts')
@login_required
def get_contacts():
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return jsonify([contact.to_dict() for contact in contacts])

# API endpoint to delete a contact
@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Contact deleted successfully'})

# Blog management routes
@app.route('/auth/blogs')
@login_required
def blog_management():
    blog_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('auth/blog_management.html', title='Blog Management', blog_posts=blog_posts)

@app.route('/auth/blogs/new', methods=['GET', 'POST'])
@login_required
def new_blog_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        slug = BlogPost.generate_slug(form.title.data)
        # Check if a blog post with this slug already exists
        if BlogPost.query.filter_by(slug=slug).first():
            slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        blog_post = BlogPost(
            title=form.title.data,
            slug=slug,
            content=form.content.data,
            summary=form.summary.data,
            published=form.published.data,
            author_id=current_user.id
        )
        # Handle tags
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name, type='blog').first()
                if not tag:
                    tag = Tag(name=tag_name, type='blog')
                    db.session.add(tag)
                blog_post.tags.append(tag)

        db.session.add(blog_post)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('blog_management'))

    return render_template('auth/blog_form.html', title='New Blog Post', form=form)

@app.route('/auth/blogs/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_blog_post(post_id):
    blog_post = BlogPost.query.get_or_404(post_id)
    form = BlogPostForm(obj=blog_post)

    if form.validate_on_submit():
        blog_post.title = form.title.data
        blog_post.content = form.content.data
        blog_post.summary = form.summary.data
        blog_post.published = form.published.data

        # Only update slug if title has changed
        if blog_post.title != form.title.data:
            slug = BlogPost.generate_slug(form.title.data)
            # Check if a blog post with this slug already exists
            if BlogPost.query.filter(BlogPost.slug == slug, BlogPost.id != post_id).first():
                slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            blog_post.slug = slug

        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('blog_management'))

    return render_template('auth/blog_form.html', title='Edit Blog Post', form=form, blog_post=blog_post)

@app.route('/auth/blogs/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_blog_post(post_id):
    blog_post = BlogPost.query.get_or_404(post_id)
    db.session.delete(blog_post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('blog_management'))


@app.route('/auth/products')
@login_required
def product_management():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('auth/product_management.html', 
                         title='Product Management', 
                         products=products)

@app.route('/auth/products/new', methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            title=form.title.data,
            content=form.content.data,
            meta_description=form.meta_description.data,
            key_features=form.key_features.data,
            technical_specs=form.technical_specs.data,
            published=form.published.data,
            author_id=current_user.id
        )
        # Handle tags
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name, type='product').first()
                if not tag:
                    tag = Tag(name=tag_name, type='product')
                    db.session.add(tag)
                product.tags.append(tag)

        db.session.add(product)
        db.session.commit()
        flash('Product created successfully!', 'success')
        return redirect(url_for('product_management'))

    return render_template('auth/product_form.html', 
                         title='New Product', 
                         form=form)

@app.route('/auth/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.title = form.title.data
        product.content = form.content.data
        product.meta_description = form.meta_description.data
        product.key_features = form.key_features.data
        product.technical_specs = form.technical_specs.data
        product.published = form.published.data
        
        # Clear existing tags and add new ones
        product.tags.clear()
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name, type='product').first()
                if not tag:
                    tag = Tag(name=tag_name, type='product')
                    db.session.add(tag)
                product.tags.append(tag)
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product_management'))
    
    # Pre-populate tags field
    form.tags.data = ','.join([tag.name for tag in product.tags])
    
    return render_template('auth/product_form.html',
                         title='Edit Product',
                         form=form,
                         product=product)

@app.route('/auth/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product_management'))