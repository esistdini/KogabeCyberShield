import os
import glob
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required
from app import app, db
from models import Contact, BlogPost
from forms import ContactForm
import logging

# Helper function to get blog posts
def get_blog_posts():
    # Get blog posts from the database
    blog_posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    
    blogs = []
    for post in blog_posts:
        blogs.append({
            'name': post.slug,
            'title': post.title,
            'created': post.created_at,
            'summary': post.summary,
            'url': url_for('blog_post', name=post.slug)
        })
    
    return blogs

# Helper function to get products
def get_products():
    from models import Product
    products = Product.query.filter_by(published=True).order_by(Product.created_at.desc()).all()
    return [{
        'name': str(product.id),
        'title': product.title,
        'url': url_for('product_detail', name=str(product.id))
    } for product in products]

# Home page
@app.route('/')
def index():
    form = ContactForm()
    return render_template('index.html', title='Cyber Security Solutions', form=form)

# Blog listing page
@app.route('/blog/')
def blog():
    blogs = get_blog_posts()
    return render_template('blog.html', title='Blog', blogs=blogs)

# Blog post detail
@app.route('/blog/<name>')
def blog_post(name):
    # Get blog post from database by slug
    blog_post = BlogPost.query.filter_by(slug=name, published=True).first_or_404()
    
    return render_template('blog_template.html', 
                          title=blog_post.title, 
                          content=blog_post.content, 
                          blog_post=blog_post)

# About us page
@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

# Contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            contact = Contact(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                message=form.message.data
            )
            db.session.add(contact)
            db.session.commit()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving contact: {str(e)}")
            flash('An error occurred while sending your message. Please try again.', 'danger')
        
    return render_template('contact.html', title='Contact Us', form=form)

# Services page
@app.route('/service')
def service():
    return render_template('service.html', title='Our Services')

# Products listing page
@app.route('/product/')
def product():
    products = get_products()
    return render_template('product.html', title='Products', products=products)

# Product detail
@app.route('/product/<name>')
def product_detail(name):
    from models import Product
    product = Product.query.get_or_404(int(name))
    if not product.published:
        abort(404)
    return render_template('product_template.html', 
                         title=product.title, 
                         content=product.content,
                         product=product)

# Default auth route redirects to login
@app.route('/auth')
def auth():
    return redirect(url_for('login'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error=404, message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error=500, message='Server error'), 500