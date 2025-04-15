from app import app, db
from models import User, BlogPost
from werkzeug.security import generate_password_hash
import logging

def seed_database():
    with app.app_context():
        # Check if admin user already exists
        if User.query.filter_by(username='Dinesh').first() is None:
            logging.info("Creating admin user 'Dinesh'")
            # Create admin user
            admin_user = User(
                username='Dinesh',
                email='kogabemanagement@gmail.com',
                password_hash=generate_password_hash('!@#$%^&*')
            )
            db.session.add(admin_user)
            db.session.commit()
            
            # Create a sample blog post
            sample_post = BlogPost(
                title='Welcome to Kogabe Security Blog',
                slug='welcome-to-kogabe-security-blog',
                content='''
                <h2>Welcome to Our Security Blog</h2>
                <p>At Kogabe, we're committed to keeping you informed about the latest developments in cyber security. Our team of experts will be regularly sharing insights, best practices, and tips to help you protect your digital assets.</p>
                
                <h3>What to Expect</h3>
                <p>Our blog will cover a wide range of topics including:</p>
                <ul>
                    <li>Web application security</li>
                    <li>Network security testing</li>
                    <li>Phishing awareness</li>
                    <li>Vulnerability assessments</li>
                    <li>Industry trends and news</li>
                </ul>
                
                <h3>Stay Connected</h3>
                <p>We invite you to bookmark our blog and check back regularly for new content. If you have questions or topics you'd like us to cover, please <a href="/contact">contact us</a>.</p>
                
                <p>Thank you for choosing Kogabe for your security needs!</p>
                ''',
                summary='Learn about our new blog and what to expect from Kogabe\'s security experts',
                published=True,
                author_id=admin_user.id
            )
            db.session.add(sample_post)
            db.session.commit()
            logging.info("Created sample blog post")
            
        else:
            logging.info("Admin user already exists, skipping seed")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    seed_database()
    logging.info("Database seeding complete")