from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from food_web.models import db, ContactLinks, Banner
from datetime import datetime
import os
from flask import current_app
import sqlite3
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)

@views.route('/')
def home():
    now = datetime.now()
    shop = request.args.get('shop', 'default') 

    # Get currently active banners (offers) for this shop
    active_banners = Banner.query.filter(
        Banner.start_time <= now,
        Banner.end_time >= now
    ).order_by(Banner.uploaded_at.desc()).all()

    if not active_banners:
        # Fallback to default images (from static folder)
        active_banners = [
            {'image_path': 'default_banners/banner1.jpeg'},
            {'image_path': 'default_banners/banner2.jpeg'},
            {'image_path': 'default_banners/banner3.jpeg'}
        ]

    return render_template('index.html', banners=active_banners, shop=shop)

@views.route('/dashboard')
@views.route('/dashboard/<shop_name>')
def dashboard(shop_name=None):
    # Get shop from URL parameter or query string
    shop = shop_name or request.args.get('shop', 'default')
    links = ContactLinks.query.first()
    
    return render_template('dashboard.html', links=links, shop=shop)

@views.route('/dashboard/<shop_name>', methods=['POST'])
@views.route('/dashboard', methods=['POST'])
def dashboard_post(shop_name=None):
    shop = shop_name or request.args.get('shop', 'default')
    links = ContactLinks.query.first()

    if request.method == 'POST':
        # Check if it's an offer image upload
        if 'offer_image' in request.files:
            offer_image = request.files['offer_image']
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')

            # Save image securely
            if offer_image and offer_image.filename != '':
                # Create secure filename
                filename = secure_filename(offer_image.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename

                # Save inside food_web/static/uploads
                uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)

                save_path = os.path.join(uploads_dir, filename)
                offer_image.save(save_path)

                # Convert time strings to datetime objects for today
                today = datetime.today().date()
                start_dt = datetime.combine(today, datetime.strptime(start_time, "%H:%M").time())
                end_dt = datetime.combine(today, datetime.strptime(end_time, "%H:%M").time())

                # Check if Banner model has shop_name field
                try:
                    # Try to create with shop_name (if the field exists)
                    banner = Banner(
                        image_path='uploads/' + filename, 
                        start_time=start_dt, 
                        end_time=end_dt,
                        shop_name=shop
                    )
                except TypeError:
                    # If shop_name field doesn't exist, create without it
                    banner = Banner(
                        image_path='uploads/' + filename, 
                        start_time=start_dt, 
                        end_time=end_dt
                    )
                
                db.session.add(banner)
                db.session.commit()

                flash('Offer uploaded successfully!')
                return redirect(url_for('views.dashboard', shop_name=shop))

        else:
            # Handle contact link updates
            facebook = request.form.get('facebook')
            instagram = request.form.get('instagram')
            whatsapp = request.form.get('whatsapp')

            if links:
                links.facebook = facebook
                links.instagram = instagram
                links.whatsapp = whatsapp
            else:
                links = ContactLinks(facebook=facebook, instagram=instagram, whatsapp=whatsapp)
                db.session.add(links)

            db.session.commit()
            flash('Links updated successfully!')
            return redirect(url_for('views.dashboard', shop_name=shop))

    return render_template('dashboard.html', links=links, shop=shop)

def get_db_connection():
    """Get database connection - ensure this points to the correct database file"""
    db_path = os.path.join(current_app.instance_path, 'site.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@views.route('/api/live-offers')
def get_live_offers():
    shop = request.args.get('shop')

    try:
        now = datetime.now()

        try:
            active_offers = Banner.query.filter(
                Banner.shop_name == shop,
                Banner.start_time <= now,
                Banner.end_time >= now
            ).order_by(Banner.uploaded_at.desc()).all()
        except AttributeError:
            active_offers = Banner.query.filter(
                Banner.start_time <= now,
                Banner.end_time >= now
            ).order_by(Banner.uploaded_at.desc()).all()

        offers = []
        for i, banner in enumerate(active_offers):
            offers.append({
                'id': f"offer-{banner.id}",
                'position': 2,
                'imageUrl': url_for('static', filename=banner.image_path, _external=True),  # ✅ fixed
                'title': 'Special Offer',
                'subtitle': 'Limited time offer!',
                'badge': 'LIVE OFFER',
                'ctaText': 'Grab Now',
                'ctaLink': '#'
            })

        return jsonify(offers)

    except Exception as e:
        print(f"Error fetching live offers: {e}")
        return jsonify([])
