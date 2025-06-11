#!/usr/bin/env python3
"""
Setup script for responsive images system
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_responsive_images():
    """Set up responsive image system"""
    db_path = 'data/infnews.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Standard responsive breakpoints
            BREAKPOINTS = {
                'mobile': [320, 480, 640],
                'tablet': [768, 1024],
                'desktop': [1200, 1440, 1920]
            }
            
            FORMATS = ['jpeg', 'webp']
            
            print("Setting up placeholder image records...")
            
            # Create placeholder image records
            placeholders = {
                'article': {'width': 1200, 'height': 600, 'filename': 'article_placeholder.jpg'},
                'author': {'width': 400, 'height': 400, 'filename': 'author_placeholder.jpg'},
                'category': {'width': 600, 'height': 300, 'filename': 'category_placeholder.jpg'},
                'trending': {'width': 800, 'height': 400, 'filename': 'trending_placeholder.jpg'}
            }
            
            for content_type, info in placeholders.items():
                # Check if placeholder already exists
                cursor.execute("""
                    SELECT id FROM images 
                    WHERE content_type = ? AND local_filename = ? AND is_placeholder = 1
                """, (content_type, info['filename']))
                
                existing = cursor.fetchone()
                if existing:
                    print(f"✓ Placeholder for {content_type} already exists")
                    continue
                
                # Insert placeholder record
                cursor.execute("""
                    INSERT INTO images 
                    (content_type, content_id, image_type, local_filename, alt_text, 
                     width, height, is_placeholder, created_at)
                    VALUES (?, 0, 'placeholder', ?, ?, ?, ?, 1, datetime('now'))
                """, (content_type, info['filename'], f"{content_type.title()} placeholder", 
                      info['width'], info['height']))
                
                placeholder_id = cursor.lastrowid
                print(f"✓ Created placeholder for {content_type}: {info['filename']} (ID: {placeholder_id})")
                
                # Register variants for placeholder
                if placeholder_id:
                    register_image_variants(cursor, placeholder_id, info['width'], info['height'], BREAKPOINTS, FORMATS)
            
            print("\nSetting up sample image records...")
            
            # Sample image data
            sample_images = [
                {
                    'content_type': 'article',
                    'content_id': 10,
                    'image_type': 'hero',
                    'filename': 'article_10_hero.jpg',
                    'alt_text': 'Platform Update News Article Hero Image',
                    'width': 1200,
                    'height': 600
                }
            ]
            
            for img_data in sample_images:
                # Check if image already exists
                cursor.execute("""
                    SELECT id FROM images 
                    WHERE content_type = ? AND content_id = ? AND image_type = ?
                """, (img_data['content_type'], img_data['content_id'], img_data['image_type']))
                
                existing = cursor.fetchone()
                if existing:
                    image_id = existing['id']
                    print(f"✓ Sample image already exists with ID {image_id}")
                else:
                    # Insert new image record
                    cursor.execute("""
                        INSERT INTO images 
                        (content_type, content_id, image_type, local_filename, alt_text, 
                         width, height, is_placeholder, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 0, datetime('now'))
                    """, (
                        img_data['content_type'], img_data['content_id'], img_data['image_type'],
                        img_data['filename'], img_data['alt_text'], 
                        img_data['width'], img_data['height']
                    ))
                    
                    image_id = cursor.lastrowid
                    print(f"✓ Created sample image: {img_data['filename']} (ID: {image_id})")
                
                # Register responsive variants
                if image_id:
                    register_image_variants(cursor, image_id, img_data['width'], img_data['height'], BREAKPOINTS, FORMATS)
            
            conn.commit()
            print("\n✅ Responsive image system setup complete!")
            return True
            
    except Exception as e:
        print(f"❌ Error setting up responsive images: {e}")
        return False

def register_image_variants(cursor, image_id, original_width, original_height, breakpoints, formats):
    """Register image variants in database"""
    try:
        aspect_ratio = original_width / original_height
        variant_count = 0
        
        # Clear existing variants
        cursor.execute("DELETE FROM image_variants WHERE image_id = ?", (image_id,))
        
        # Calculate variants for each device type
        for device_type, widths in breakpoints.items():
            for width in widths:
                # Skip if width is larger than original
                if width > original_width:
                    continue
                    
                height = int(width / aspect_ratio)
                
                # Register variants in different formats
                for format_name in formats:
                    filename = f"img_{image_id}_{device_type}_{width}x{height}.{format_name}"
                    quality = 85 if format_name == 'jpeg' else 80
                    
                    cursor.execute("""
                        INSERT INTO image_variants 
                        (image_id, variant_type, width, height, format, filename, file_size, quality)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (image_id, device_type, width, height, format_name, filename, 0, quality))
                    
                    variant_count += 1
        
        print(f"  → Registered {variant_count} variants for image {image_id}")
        
    except Exception as e:
        print(f"  ❌ Failed to register variants for image {image_id}: {e}")

def generate_responsive_html(image_id, alt_text='', css_classes='', loading='lazy'):
    """Generate responsive HTML for an image"""
    db_path = 'data/infnews.db'
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get image variants from database
            cursor.execute("""
                SELECT * FROM image_variants 
                WHERE image_id = ? 
                ORDER BY variant_type, width, format
            """, (image_id,))
            
            variants = cursor.fetchall()
            
            if not variants:
                # Fallback to original image
                cursor.execute("SELECT local_filename FROM images WHERE id = ?", (image_id,))
                original = cursor.fetchone()
                if original:
                    return f'<img src="assets/images/{original["local_filename"]}" alt="{alt_text}" class="{css_classes}" loading="{loading}">'
                return f'<img src="assets/images/placeholder.jpg" alt="{alt_text}" class="{css_classes}" loading="{loading}">'
            
            # Group variants by format and device type
            webp_variants = [dict(v) for v in variants if v['format'] == 'webp']
            jpeg_variants = [dict(v) for v in variants if v['format'] == 'jpeg']
            
            # Build picture element
            html_parts = ['<picture>']
            
            # WebP sources (modern browsers)
            if webp_variants:
                mobile_webp = [v for v in webp_variants if v['variant_type'] == 'mobile']
                tablet_webp = [v for v in webp_variants if v['variant_type'] == 'tablet']
                desktop_webp = [v for v in webp_variants if v['variant_type'] == 'desktop']
                
                if mobile_webp:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in mobile_webp])
                    html_parts.append(f'    <source media="(max-width: 640px)" srcset="{srcset}" type="image/webp" sizes="100vw">')
                
                if tablet_webp:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in tablet_webp])
                    html_parts.append(f'    <source media="(max-width: 1024px)" srcset="{srcset}" type="image/webp" sizes="50vw">')
                
                if desktop_webp:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in desktop_webp])
                    html_parts.append(f'    <source srcset="{srcset}" type="image/webp" sizes="33vw">')
            
            # JPEG fallback sources
            if jpeg_variants:
                mobile_jpeg = [v for v in jpeg_variants if v['variant_type'] == 'mobile']
                tablet_jpeg = [v for v in jpeg_variants if v['variant_type'] == 'tablet']
                
                if mobile_jpeg:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in mobile_jpeg])
                    html_parts.append(f'    <source media="(max-width: 640px)" srcset="{srcset}" sizes="100vw">')
                
                if tablet_jpeg:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in tablet_jpeg])
                    html_parts.append(f'    <source media="(max-width: 1024px)" srcset="{srcset}" sizes="50vw">')
            
            # Fallback img element
            fallback_variant = jpeg_variants[0] if jpeg_variants else dict(variants[0])
            fallback_src = f"assets/images/responsive/{fallback_variant['filename']}"
            html_parts.append(f'    <img src="{fallback_src}" alt="{alt_text}" class="{css_classes}" loading="{loading}">')
            
            html_parts.append('</picture>')
            
            return '\n'.join(html_parts)
            
    except Exception as e:
        print(f"Failed to generate responsive HTML for image {image_id}: {e}")
        return f'<img src="assets/images/placeholder.jpg" alt="{alt_text}" class="{css_classes}" loading="{loading}">'

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Set up responsive images system')
    parser.add_argument('--setup', action='store_true', help='Set up responsive image system')
    parser.add_argument('--test-html', type=int, help='Generate test HTML for image ID')
    
    args = parser.parse_args()
    
    if args.setup:
        setup_responsive_images()
    
    if args.test_html:
        print(f"\nTest HTML for image {args.test_html}:")
        html = generate_responsive_html(args.test_html, alt_text="Test image", css_classes="w-full h-48 object-cover")
        print(html)
    
    if not args.setup and not args.test_html:
        setup_responsive_images()

if __name__ == "__main__":
    main()