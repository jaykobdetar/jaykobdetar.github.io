-- Create updated views with new fields

CREATE VIEW article_full_view AS
SELECT 
    a.id,
    a.title,
    a.slug,
    a.excerpt,
    a.mobile_title,
    a.mobile_excerpt,
    a.mobile_hero_image_id,
    a.status,
    a.featured,
    a.trending,
    a.publish_date,
    a.views,
    a.likes,
    a.read_time_minutes,
    a.image_url,
    a.hero_image_url,
    a.thumbnail_url,
    a.last_modified,
    a.created_at,
    a.updated_at,
    au.id as author_id,
    au.name as author_name,
    au.slug as author_slug,
    au.title as author_title,
    c.id as category_id,
    c.name as category_name,
    c.slug as category_slug,
    c.color as category_color,
    c.icon as category_icon
FROM articles a
JOIN authors au ON a.author_id = au.id
JOIN categories c ON a.category_id = c.id;

CREATE VIEW article_mobile_view AS
SELECT 
    a.id,
    a.title,
    a.slug,
    a.excerpt,
    a.mobile_title,
    a.mobile_excerpt,
    a.mobile_hero_image_id,
    a.status,
    a.featured,
    a.trending,
    a.publish_date,
    a.views,
    a.likes,
    a.read_time_minutes,
    a.image_url,
    a.hero_image_url,
    a.thumbnail_url,
    a.last_modified,
    au.id as author_id,
    au.name as author_name,
    au.slug as author_slug,
    au.title as author_title,
    c.id as category_id,
    c.name as category_name,
    c.slug as category_slug,
    c.color as category_color,
    c.icon as category_icon
FROM articles a
JOIN authors au ON a.author_id = au.id
JOIN categories c ON a.category_id = c.id
WHERE a.status = 'published';