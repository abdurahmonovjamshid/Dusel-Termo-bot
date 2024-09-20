from bot.models import Product, Material

file_path = 'pft tovarlar.txt'

# Open the file and start reading it
with open(file_path, 'r', encoding='utf-8') as file:
    next(file)  # Skip the header row
    
    # Loop over each line in the file
    for line in file:
        # Split the line into itemcode and name
        itemcode, name = line.strip().split("\t")
        
        # Create and save the Product object
        Product.objects.create(itemcode=itemcode, name=name)


# Define the path to the uploaded file
file_path = 'materials.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    next(file)  # Skip the header row
    
    # Loop through each line in the file
    for line in file:
        product_itemcode, product_name, material_itemcode, material_name = line.strip().split("\t")
        
        # Retrieve the Product object using the itemcode
        product = Product.objects.filter(itemcode=product_itemcode).first()
        
        if product:
            # Create or get the Material object based on the itemcode
            material, created = Material.objects.get_or_create(itemcode=material_itemcode, defaults={'name': material_name})
            
            # Link the material to the product
            material.products.add(product)
            
            # Save the material object
            material.save()

import random
from datetime import timedelta, date
from bot.models import Report, Product, Material, TgUser  # Adjust the import to your app structure

# Helper function to generate random date
def random_date(start_date, end_date):
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

# Parameters
start_date = date(2024, 9, 13)
end_date = date(2024, 9, 20)
products = list(Product.objects.all())
materials = list(Material.objects.all())
users = list(TgUser.objects.all())

# Randomly generate 100 Report objects
for _ in range(100):
    report = Report.objects.create(
        machine_num=random.randint(1, 23),  # Random machine number between 1 and 99
        date=random_date(start_date, end_date),
        default_value=random.choice(["Kun", "Tun"]),
        product=random.choice(products),
        termoplast_measure=round(random.uniform(0.5, 10.0), 2),  # Random float between 0.5 and 10.0
        defect_measure=round(random.uniform(0.0, 5.0), 2),  # Random float between 0.0 and 5.0
        waste_measure=round(random.uniform(0.0, 3.0), 2),  # Random float between 0.0 and 3.0
        material=random.choice(materials),
        quantity=round(random.uniform(1.0, 100.0), 2),  # Random float between 1.0 and 100.0
        is_confirmed=random.choice([True, False]),
        user=random.choice(users)
    )

print("100 Reports created!")