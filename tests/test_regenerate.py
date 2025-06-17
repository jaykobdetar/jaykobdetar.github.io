
import sys
import os
sys.path.append('/mnt/c/Users/jayko/OneDrive/Desktop/news/Template_News_Site-main (1)/Template_News_Site-main/src')

try:
    from integrators.category_integrator import CategoryIntegrator
    from models.category import Category
    
    # Create a test category
    test_category = Category({
        'id': 'test',
        'name': 'Test Category',
        'description': 'Test mobile support',
        'color': '#6366f1'
    })
    
    integrator = CategoryIntegrator()
    html = integrator.generate_category_page(test_category, [])
    
    # Write test file
    os.makedirs('test_mobile', exist_ok=True)
    with open('test_mobile/category_test_mobile.html', 'w') as f:
        f.write(html)
    
    print("✅ Test category page generated with mobile support")
    
except Exception as e:
    print(f"❌ Error generating test page: {e}")
