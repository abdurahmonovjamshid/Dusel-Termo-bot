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

