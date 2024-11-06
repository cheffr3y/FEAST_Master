def convert_units(quantity, uom):
    # Normalize the input uom by removing trailing 's' or 'es'
    uom = uom.lower().strip()
    if uom.endswith('es'):
        uom = uom[:-2]
    elif uom.endswith('s'):
        uom = uom[:-1]

    conversions = {
        # Volume conversions
        'fl oz': {'conversion_factor': 128, 'new_uom': 'gallon'},
        'oz': {'conversion_factor': 16, 'new_uom': 'pound'},
        'tsp': {'conversion_factor': 3, 'new_uom': 'tbsp'},
        'tbsp': {'conversion_factor': 16, 'new_uom': 'cup'},
        'cup': {'conversion_factor': 4, 'new_uom': 'quart'},
        'quart': {'conversion_factor': 4, 'new_uom': 'gallon'},
        
        # Additional volume conversions
        'ml': {'conversion_factor': 1000, 'new_uom': 'liter'},
        'cl': {'conversion_factor': 100, 'new_uom': 'liter'},
        
        # Weight conversions
        'gram': {'conversion_factor': 1000, 'new_uom': 'kg'},
        'kg': {'conversion_factor': 2.205, 'new_uom': 'pound'},
        
        # Common recipe conversions
        'stick': {'conversion_factor': 4, 'new_uom': 'cup'},  # for butter
        'pinch': {'conversion_factor': 4, 'new_uom': 'tsp'},  # approximate
        'dash': {'conversion_factor': 8, 'new_uom': 'tsp'},  # approximate
        
        # Additional Imperial conversions
        'pint': {'conversion_factor': 2, 'new_uom': 'quart'},
        'gallon': {'conversion_factor': 4, 'new_uom': 'quart'}
    }

    if uom in conversions:
        conversion_factor = conversions[uom]['conversion_factor']
        new_uom = conversions[uom]['new_uom']
        if quantity >= conversion_factor:
            new_quantity = quantity / conversion_factor
            # Add 's' to the new unit if quantity is greater than 1
            if new_quantity > 1:
                new_uom = f"{new_uom}s"
            return new_quantity, new_uom

    # Add 's' to the original unit if quantity is greater than 1
    if quantity > 1:
        uom = f"{uom}s"
    return quantity, uom