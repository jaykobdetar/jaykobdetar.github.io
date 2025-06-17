"""
Image Processing Utility for Mobile Optimization
Handles responsive image generation, format conversion, and optimization
"""

import os
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import hashlib
from PIL import Image, ImageOps
from PIL.ImageFile import ImageFile
import io

from .logger import get_logger
from ..database.db_manager import DatabaseManager

logger = get_logger(__name__)

class ImageProcessor:
    """Handles responsive image generation and optimization"""
    
    # Standard responsive breakpoints
    BREAKPOINTS = {
        'mobile': [320, 480, 640],
        'tablet': [768, 1024],
        'desktop': [1200, 1440, 1920]
    }
    
    # Supported formats for conversion
    FORMATS = ['JPEG', 'WEBP', 'AVIF']
    
    # Quality settings for different formats
    QUALITY_SETTINGS = {
        'JPEG': 85,
        'WEBP': 80,
        'AVIF': 75
    }
    
    def __init__(self, base_images_dir: str = "assets/images", db_manager: Optional[DatabaseManager] = None):
        self.base_images_dir = Path(base_images_dir)
        self.db = db_manager or DatabaseManager()
        
        # Ensure directories exist
        self.base_images_dir.mkdir(parents=True, exist_ok=True)
        (self.base_images_dir / "responsive").mkdir(exist_ok=True)
        
    def generate_responsive_variants(self, original_image_path: str, image_id: int) -> Dict[str, List[Dict]]:
        """Generate responsive variants for an image"""
        try:
            # Load original image
            with Image.open(original_image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                
                variants = {}
                
                # Generate variants for each device type
                for device_type, widths in self.BREAKPOINTS.items():
                    variants[device_type] = []
                    
                    for width in widths:
                        # Skip if width is larger than original
                        if width > original_width:
                            continue
                            
                        height = int(width / aspect_ratio)
                        
                        # Generate variants in different formats
                        for format_name in self.FORMATS:
                            try:
                                variant_info = self._create_variant(
                                    img, image_id, device_type, width, height, format_name
                                )
                                if variant_info:
                                    variants[device_type].append(variant_info)
                                    
                            except Exception as e:
                                logger.warning(f"Failed to create {format_name} variant {width}x{height}: {e}")
                                continue
                
                # Store variants in database
                self._store_variants_in_db(image_id, variants)
                
                logger.info(f"Generated {sum(len(v) for v in variants.values())} variants for image {image_id}")
                return variants
                
        except Exception as e:
            logger.error(f"Failed to generate responsive variants for {original_image_path}: {e}")
            return {}
    
    def _create_variant(self, img: Image.Image, image_id: int, device_type: str, 
                       width: int, height: int, format_name: str) -> Optional[Dict]:
        """Create a single image variant"""
        try:
            # Resize image
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Generate filename
            format_ext = 'jpg' if format_name == 'JPEG' else format_name.lower()
            filename = f"img_{image_id}_{device_type}_{width}x{height}.{format_ext}"
            variant_path = self.base_images_dir / "responsive" / filename
            
            # Save with appropriate quality
            quality = self.QUALITY_SETTINGS.get(format_name, 85)
            save_kwargs = {'format': format_name, 'quality': quality, 'optimize': True}
            
            # Additional settings for specific formats
            if format_name == 'WEBP':
                save_kwargs['method'] = 6  # Better compression
            elif format_name == 'AVIF':
                save_kwargs['speed'] = 6  # Balance between speed and compression
            
            resized_img.save(variant_path, **save_kwargs)
            
            # Get file size
            file_size = variant_path.stat().st_size
            
            return {
                'variant_type': device_type,
                'width': width,
                'height': height,
                'format': format_name.lower(),
                'filename': filename,
                'file_size': file_size,
                'quality': quality
            }
            
        except Exception as e:
            logger.error(f"Failed to create variant {width}x{height} in {format_name}: {e}")
            return None
    
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
            
            logger.info(f"Stored variants for image {image_id} in database")
            
        except Exception as e:
            logger.error(f"Failed to store variants in database: {e}")
    
    def generate_srcset_html(self, image_id: int, image_type: str = 'hero', 
                            alt_text: str = '', css_classes: str = '') -> str:
        """Generate HTML with responsive srcset attributes"""
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
                    return f'<img src="assets/images/{original[0]["local_filename"]}" alt="{alt_text}" class="{css_classes}" loading="lazy">'
                return ""
            
            # Group variants by format and device type
            webp_variants = [v for v in variants if v['format'] == 'webp']
            jpeg_variants = [v for v in variants if v['format'] == 'jpeg']
            
            # Build picture element
            html = ['<picture>']
            
            # WebP sources (if available)
            if webp_variants:
                mobile_webp = [v for v in webp_variants if v['variant_type'] == 'mobile']
                tablet_webp = [v for v in webp_variants if v['variant_type'] == 'tablet']
                desktop_webp = [v for v in webp_variants if v['variant_type'] == 'desktop']
                
                if mobile_webp:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in mobile_webp])
                    html.append(f'  <source media="(max-width: 640px)" srcset="{srcset}" type="image/webp" sizes="100vw">')
                
                if tablet_webp:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in tablet_webp])
                    html.append(f'  <source media="(max-width: 1024px)" srcset="{srcset}" type="image/webp" sizes="50vw">')
                
                if desktop_webp:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in desktop_webp])
                    html.append(f'  <source srcset="{srcset}" type="image/webp" sizes="33vw">')
            
            # JPEG fallback sources
            if jpeg_variants:
                mobile_jpeg = [v for v in jpeg_variants if v['variant_type'] == 'mobile']
                tablet_jpeg = [v for v in jpeg_variants if v['variant_type'] == 'tablet']
                desktop_jpeg = [v for v in jpeg_variants if v['variant_type'] == 'desktop']
                
                if mobile_jpeg:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in mobile_jpeg])
                    html.append(f'  <source media="(max-width: 640px)" srcset="{srcset}" sizes="100vw">')
                
                if tablet_jpeg:
                    srcset = ', '.join([f"assets/images/responsive/{v['filename']} {v['width']}w" for v in tablet_jpeg])
                    html.append(f'  <source media="(max-width: 1024px)" srcset="{srcset}" sizes="50vw">')
            
            # Fallback img element
            fallback_variant = jpeg_variants[0] if jpeg_variants else variants[0]
            fallback_src = f"assets/images/responsive/{fallback_variant['filename']}"
            html.append(f'  <img src="{fallback_src}" alt="{alt_text}" class="{css_classes}" loading="lazy">')
            
            html.append('</picture>')
            
            return '\n'.join(html)
            
        except Exception as e:
            logger.error(f"Failed to generate srcset HTML for image {image_id}: {e}")
            # Fallback to simple img tag
            return f'<img src="assets/images/placeholder.jpg" alt="{alt_text}" class="{css_classes}" loading="lazy">'
    
    def optimize_existing_images(self) -> Dict[str, int]:
        """Optimize all existing images in the database"""
        results = {'processed': 0, 'failed': 0, 'skipped': 0}
        
        try:
            # Get all images from database
            images = self.db.execute_query("""
                SELECT id, local_filename, content_type, content_id, image_type 
                FROM images 
                WHERE is_placeholder = 0
            """)
            
            for image in images:
                image_path = self.base_images_dir / image['local_filename']
                
                if not image_path.exists():
                    logger.warning(f"Image file not found: {image_path}")
                    results['skipped'] += 1
                    continue
                
                try:
                    # Check if variants already exist
                    existing_variants = self.db.execute_query(
                        "SELECT COUNT(*) as count FROM image_variants WHERE image_id = ?",
                        (image['id'],)
                    )
                    
                    if existing_variants and existing_variants[0]['count'] > 0:
                        logger.info(f"Variants already exist for image {image['id']}, skipping")
                        results['skipped'] += 1
                        continue
                    
                    # Generate responsive variants
                    variants = self.generate_responsive_variants(str(image_path), image['id'])
                    
                    if variants:
                        results['processed'] += 1
                        logger.info(f"Processed image {image['id']}: {image['local_filename']}")
                    else:
                        results['failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to process image {image['id']}: {e}")
                    results['failed'] += 1
            
            logger.info(f"Image optimization complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to optimize existing images: {e}")
            return results
    
    def create_placeholder_variants(self) -> None:
        """Create responsive variants for placeholder images"""
        try:
            # Create placeholder images for different content types
            placeholders = {
                'article': (1200, 600, '#4F46E5'),
                'author': (400, 400, '#8B5CF6'),
                'category': (600, 300, '#10B981'),
                'trending': (800, 400, '#F59E0B')
            }
            
            for content_type, (width, height, color) in placeholders.items():
                # Create placeholder image
                img = Image.new('RGB', (width, height), color)
                
                # Add text overlay (if PIL supports it)
                try:
                    from PIL import ImageDraw, ImageFont
                    draw = ImageDraw.Draw(img)
                    
                    # Try to use a font, fallback to default
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                    except:
                        font = ImageFont.load_default()
                    
                    text = f"{content_type.title()}\nPlaceholder"
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    x = (width - text_width) // 2
                    y = (height - text_height) // 2
                    
                    draw.text((x, y), text, fill='white', font=font, anchor='mm')
                    
                except ImportError:
                    pass  # Skip text if font features not available
                
                # Save placeholder
                placeholder_path = self.base_images_dir / f"{content_type}_placeholder.jpg"
                img.save(placeholder_path, 'JPEG', quality=85)
                
                logger.info(f"Created placeholder: {placeholder_path}")
                
        except Exception as e:
            logger.error(f"Failed to create placeholder variants: {e}")
    
    def get_image_info(self, image_id: int) -> Dict:
        """Get comprehensive image information including variants"""
        try:
            # Get base image info
            image_info = self.db.execute_query(
                "SELECT * FROM images WHERE id = ?", (image_id,)
            )
            
            if not image_info:
                return {}
            
            image = image_info[0]
            
            # Get variants
            variants = self.db.execute_query("""
                SELECT * FROM image_variants 
                WHERE image_id = ? 
                ORDER BY variant_type, width
            """, (image_id,))
            
            # Group variants by type
            grouped_variants = {}
            for variant in variants:
                device_type = variant['variant_type']
                if device_type not in grouped_variants:
                    grouped_variants[device_type] = []
                grouped_variants[device_type].append(variant)
            
            return {
                'id': image['id'],
                'original': image,
                'variants': grouped_variants,
                'total_variants': len(variants),
                'srcset_html': self.generate_srcset_html(image_id, alt_text=image.get('alt_text', ''))
            }
            
        except Exception as e:
            logger.error(f"Failed to get image info for {image_id}: {e}")
            return {}

def main():
    """CLI interface for image processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process images for mobile optimization')
    parser.add_argument('--optimize-all', action='store_true', help='Optimize all existing images')
    parser.add_argument('--create-placeholders', action='store_true', help='Create placeholder images')
    parser.add_argument('--image-id', type=int, help='Process specific image by ID')
    
    args = parser.parse_args()
    
    processor = ImageProcessor()
    
    if args.optimize_all:
        print("Optimizing all existing images...")
        results = processor.optimize_existing_images()
        print(f"Results: {results}")
    
    if args.create_placeholders:
        print("Creating placeholder images...")
        processor.create_placeholder_variants()
    
    if args.image_id:
        print(f"Processing image {args.image_id}...")
        # Get image path from database
        db = DatabaseManager()
        image_info = db.execute_query("SELECT local_filename FROM images WHERE id = ?", (args.image_id,))
        if image_info:
            image_path = f"assets/images/{image_info[0]['local_filename']}"
            variants = processor.generate_responsive_variants(image_path, args.image_id)
            print(f"Generated variants: {variants}")
        else:
            print(f"Image {args.image_id} not found in database")

if __name__ == "__main__":
    main()