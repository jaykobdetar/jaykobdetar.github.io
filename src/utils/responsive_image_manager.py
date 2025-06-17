"""
Responsive Image Manager for Mobile Optimization
Manages responsive image metadata and HTML generation without requiring PIL
"""

import os
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .logger import get_logger
from ..database.db_manager import DatabaseManager

logger = get_logger(__name__)

class ResponsiveImageManager:
    """Manages responsive images and generates optimized HTML"""
    
    # Standard responsive breakpoints
    BREAKPOINTS = {
        'mobile': [320, 480, 640],
        'tablet': [768, 1024],
        'desktop': [1200, 1440, 1920]
    }
    
    # Supported formats
    FORMATS = ['jpeg', 'webp', 'avif']
    
    def __init__(self, base_images_dir: str = "assets/images", db_manager: Optional[DatabaseManager] = None):
        self.base_images_dir = Path(base_images_dir)
        self.db = db_manager or DatabaseManager()
        
        # Ensure directories exist
        self.base_images_dir.mkdir(parents=True, exist_ok=True)
        (self.base_images_dir / "responsive").mkdir(exist_ok=True)
        
    def register_image_variants(self, image_id: int, original_width: int, original_height: int) -> Dict[str, List[Dict]]:
        """Register planned image variants in database (for when images are processed)"""
        try:
            aspect_ratio = original_width / original_height
            variants = {}
            
            # Calculate variants for each device type
            for device_type, widths in self.BREAKPOINTS.items():
                variants[device_type] = []
                
                for width in widths:
                    # Skip if width is larger than original
                    if width > original_width:
                        continue
                        
                    height = int(width / aspect_ratio)
                    
                    # Register variants in different formats
                    for format_name in self.FORMATS:
                        variant_info = {
                            'variant_type': device_type,
                            'width': width,
                            'height': height,
                            'format': format_name,
                            'filename': f"img_{image_id}_{device_type}_{width}x{height}.{format_name}",
                            'file_size': 0,  # Will be updated when actual file is created
                            'quality': 85 if format_name == 'jpeg' else 80
                        }
                        variants[device_type].append(variant_info)
            
            # Store variants in database
            self._store_variants_in_db(image_id, variants)
            
            logger.info(f"Registered {sum(len(v) for v in variants.values())} planned variants for image {image_id}")
            return variants
            
        except Exception as e:
            logger.error(f"Failed to register image variants for image {image_id}: {e}")
            return {}
    
    def _store_variants_in_db(self, image_id: int, variants: Dict[str, List[Dict]]) -> None:
        """Store image variants in database"""
        try:
            # Clear existing variants for this image
            self.db.execute_write("DELETE FROM image_variants WHERE image_id = ?", (image_id,))
            
            # Insert new variants
            for device_variants in variants.values():
                for variant in device_variants:
                    self.db.execute_write("""
                        INSERT INTO image_variants 
                        (image_id, variant_type, width, height, format, filename, file_size, quality)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        image_id,
                        variant['variant_type'],
                        variant['width'],
                        variant['height'],
                        variant['format'],
                        variant['filename'],
                        variant['file_size'],
                        variant['quality']
                    ))
            
            logger.info(f"Stored variant metadata for image {image_id} in database")
            
        except Exception as e:
            logger.error(f"Failed to store variants in database: {e}")
    
    def generate_responsive_html(self, image_id: int, alt_text: str = '', css_classes: str = '', 
                                 loading: str = 'lazy') -> str:
        """Generate responsive HTML with srcset attributes"""
        try:
            # Get image variants from database
            variants = self.db.execute_query("""
                SELECT * FROM image_variants 
                WHERE image_id = ? 
                ORDER BY variant_type, width, format
            """, (image_id,))
            
            if not variants:
                # Fallback to original image
                original = self.db.execute_query(
                    "SELECT local_filename FROM images WHERE id = ?", (image_id,)
                )
                if original:
                    return f'<img src="assets/images/{original[0]["local_filename"]}" alt="{alt_text}" class="{css_classes}" loading="{loading}">'
                return f'<img src="assets/images/placeholder.jpg" alt="{alt_text}" class="{css_classes}" loading="{loading}">'
            
            # Group variants by format and device type
            webp_variants = [v for v in variants if v['format'] == 'webp']
            jpeg_variants = [v for v in variants if v['format'] == 'jpeg']
            
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
                desktop_jpeg = [v for v in jpeg_variants if v['variant_type'] == 'desktop']
                
                if mobile_jpeg:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in mobile_jpeg])
                    html_parts.append(f'    <source media="(max-width: 640px)" srcset="{srcset}" sizes="100vw">')
                
                if tablet_jpeg:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in tablet_jpeg])
                    html_parts.append(f'    <source media="(max-width: 1024px)" srcset="{srcset}" sizes="50vw">')
            
            # Fallback img element
            fallback_variant = jpeg_variants[0] if jpeg_variants else variants[0]
            fallback_src = f"assets/images/responsive/{fallback_variant['filename']}"
            html_parts.append(f'    <img src="{fallback_src}" alt="{alt_text}" class="{css_classes}" loading="{loading}">')
            
            html_parts.append('</picture>')
            
            return '\n'.join(html_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate responsive HTML for image {image_id}: {e}")
            # Fallback to simple img tag
            return f'<img src="assets/images/placeholder.jpg" alt="{alt_text}" class="{css_classes}" loading="{loading}">'
    
    def create_placeholder_image_records(self) -> None:
        """Create database records for placeholder images"""
        try:
            placeholders = {
                'article': {'width': 1200, 'height': 600, 'filename': 'article_placeholder.jpg'},
                'author': {'width': 400, 'height': 400, 'filename': 'author_placeholder.jpg'},
                'category': {'width': 600, 'height': 300, 'filename': 'category_placeholder.jpg'},
                'trending': {'width': 800, 'height': 400, 'filename': 'trending_placeholder.jpg'}
            }
            
            for content_type, info in placeholders.items():
                # Check if placeholder already exists
                existing = self.db.execute_query("""
                    SELECT id FROM images 
                    WHERE content_type = ? AND local_filename = ? AND is_placeholder = 1
                """, (content_type, info['filename']))
                
                if existing:
                    continue
                
                # Insert placeholder record
                placeholder_id = self.db.execute_write("""
                    INSERT INTO images 
                    (content_type, content_id, image_type, local_filename, alt_text, 
                     width, height, is_placeholder, created_at)
                    VALUES (?, 0, 'placeholder', ?, ?, ?, ?, 1, datetime('now'))
                """, (content_type, info['filename'], f"{content_type.title()} placeholder", 
                      info['width'], info['height']))
                
                # Register variants for placeholder
                if placeholder_id:
                    self.register_image_variants(placeholder_id, info['width'], info['height'])
                
                logger.info(f"Created placeholder record for {content_type}: {info['filename']}")
            
        except Exception as e:
            logger.error(f"Failed to create placeholder image records: {e}")
    
    def get_image_variants_info(self, image_id: int) -> Dict:
        """Get comprehensive information about image variants"""
        try:
            # Get base image info
            image_info = self.db.execute_query(
                "SELECT * FROM images WHERE id = ?", (image_id,)
            )
            
            if not image_info:
                return {}
            
            image = image_info[0]
            
            # Get variants grouped by device type and format
            variants = self.db.execute_query("""
                SELECT * FROM image_variants 
                WHERE image_id = ? 
                ORDER BY variant_type, width, format
            """, (image_id,))
            
            # Group variants
            grouped = {'mobile': [], 'tablet': [], 'desktop': []}
            formats_available = set()
            
            for variant in variants:
                device_type = variant['variant_type']
                if device_type in grouped:
                    grouped[device_type].append(variant)
                    formats_available.add(variant['format'])
            
            return {
                'id': image['id'],
                'original': image,
                'variants_by_device': grouped,
                'formats_available': list(formats_available),
                'total_variants': len(variants),
                'responsive_html': self.generate_responsive_html(image_id, alt_text=image.get('alt_text', ''))
            }
            
        except Exception as e:
            logger.error(f"Failed to get image variants info for {image_id}: {e}")
            return {}
    
    def setup_sample_images(self) -> None:
        """Set up sample image records for testing responsive functionality"""
        try:
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
                },
                {
                    'content_type': 'author',
                    'content_id': 1,
                    'image_type': 'profile',
                    'filename': 'author_jessica_kim.jpg',
                    'alt_text': 'Jessica Kim Author Profile Picture',
                    'width': 400,
                    'height': 400
                }
            ]
            
            for img_data in sample_images:
                # Check if image already exists
                existing = self.db.execute_query("""
                    SELECT id FROM images 
                    WHERE content_type = ? AND content_id = ? AND image_type = ?
                """, (img_data['content_type'], img_data['content_id'], img_data['image_type']))
                
                if existing:
                    image_id = existing[0]['id']
                    logger.info(f"Image already exists with ID {image_id}, registering variants")
                else:
                    # Insert new image record
                    image_id = self.db.execute_write("""
                        INSERT INTO images 
                        (content_type, content_id, image_type, local_filename, alt_text, 
                         width, height, is_placeholder, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 0, datetime('now'))
                    """, (
                        img_data['content_type'], img_data['content_id'], img_data['image_type'],
                        img_data['filename'], img_data['alt_text'], 
                        img_data['width'], img_data['height']
                    ))
                    logger.info(f"Created sample image record: {img_data['filename']}")
                
                # Register responsive variants
                if image_id:
                    self.register_image_variants(image_id, img_data['width'], img_data['height'])
            
        except Exception as e:
            logger.error(f"Failed to set up sample images: {e}")
    
    def generate_css_for_responsive_images(self) -> str:
        """Generate CSS for responsive image optimization"""
        css = """
/* Responsive Image Styles */
picture {
    display: block;
    width: 100%;
}

picture img {
    width: 100%;
    height: auto;
    display: block;
}

/* Optimize image loading */
img[loading="lazy"] {
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
}

img[loading="lazy"].loaded {
    opacity: 1;
}

/* Responsive image containers */
.image-container {
    position: relative;
    overflow: hidden;
    background-color: #f3f4f6;
}

.image-container.loading::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    animation: loading 1.5s infinite;
}

@keyframes loading {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* Mobile-specific optimizations */
@media (max-width: 640px) {
    .image-container {
        border-radius: 0.5rem;
    }
    
    picture img {
        border-radius: 0.5rem;
    }
}

/* Tablet optimizations */
@media (min-width: 641px) and (max-width: 1024px) {
    .image-container {
        border-radius: 0.75rem;
    }
}

/* Desktop optimizations */
@media (min-width: 1025px) {
    .image-container {
        border-radius: 1rem;
    }
}
"""
        return css

def main():
    """CLI interface for responsive image management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage responsive images for mobile optimization')
    parser.add_argument('--setup-placeholders', action='store_true', help='Set up placeholder image records')
    parser.add_argument('--setup-samples', action='store_true', help='Set up sample image records')
    parser.add_argument('--image-id', type=int, help='Get info for specific image')
    parser.add_argument('--generate-css', action='store_true', help='Generate responsive image CSS')
    
    args = parser.parse_args()
    
    manager = ResponsiveImageManager()
    
    if args.setup_placeholders:
        print("Setting up placeholder image records...")
        manager.create_placeholder_image_records()
        print("✓ Placeholder records created")
    
    if args.setup_samples:
        print("Setting up sample image records...")
        manager.setup_sample_images()
        print("✓ Sample image records created")
    
    if args.image_id:
        print(f"Getting info for image {args.image_id}...")
        info = manager.get_image_variants_info(args.image_id)
        if info:
            print(f"Image: {info['original']['local_filename']}")
            print(f"Total variants: {info['total_variants']}")
            print(f"Formats available: {info['formats_available']}")
            print("\nResponsive HTML:")
            print(info['responsive_html'])
        else:
            print(f"Image {args.image_id} not found")
    
    if args.generate_css:
        print("Generating responsive image CSS...")
        css = manager.generate_css_for_responsive_images()
        with open('responsive_images.css', 'w') as f:
            f.write(css)
        print("✓ CSS written to responsive_images.css")

if __name__ == "__main__":
    main()