from app import db
from flask_login import UserMixin
from datetime import datetime
from slugify import slugify

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Contact {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone or 'Not provided',
            'message': self.message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'blog' or 'product'
    products = db.relationship('Product', secondary='product_tags', back_populates='tags')
    product_tags = db.relationship('ProductTags', back_populates='tag')

    def __repr__(self):
        return f'<Tag {self.name}>'

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    meta_description = db.Column(db.String(160), nullable=True, default='')
    key_features = db.Column(db.Text, nullable=True, default='')
    technical_specs = db.Column(db.Text, nullable=True, default='')
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    author = db.relationship('User', backref=db.backref('products', lazy=True))
    product_tags = db.relationship('ProductTags', back_populates='product', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='product_tags', back_populates='products')

    def __repr__(self):
        return f'<Product {self.title}>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(300), nullable=True)
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.relationship('Tag', secondary='post_tags', backref='blog_posts')
    author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))

    @staticmethod
    def generate_slug(title):
        return slugify(title)

class PostTags(db.Model):
    __tablename__ = 'post_tags'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)

    post = db.relationship('BlogPost', backref=db.backref('post_tags', lazy=True))
    tag = db.relationship('Tag', backref=db.backref('post_tags', lazy=True))

    def __repr__(self):
        return f'<PostTags {self.id}>'

class ProductTags(db.Model):
    __tablename__ = 'product_tags'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)

    product = db.relationship('Product', back_populates='product_tags')
    tag = db.relationship('Tag', back_populates='product_tags')

    def __repr__(self):
        return f'<ProductTags {self.id}>'