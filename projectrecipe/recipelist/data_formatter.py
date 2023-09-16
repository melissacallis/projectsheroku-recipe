
import pandas as pd

def format_nutrition_data(nutrition_data):
    formatted_data = []
    for data_list in nutrition_data:
        for data in data_list:
            formatted_data.append({
                'name': data.get('name', 'N/A'),
                'calories': data.get('calories', 'N/A'),
                'serving_size_g': data.get('serving_size_g', 'N/A'),
                'fat_total_g': data.get('fat_total_g', 'N/A'),
                'fat_saturated_g': data.get('fat_saturated_g', 'N/A'),
                'protein_g': data.get('protein_g', 'N/A'),
                'sodium_mg': data.get('sodium_mg', 'N/A'),
                'potassium_mg': data.get('potassium_mg', 'N/A'),
                'cholesterol_mg': data.get('cholesterol_mg', 'N/A'),
                'carbohydrates_total_g': data.get('carbohydrates_total_g', 'N/A'),
                'fiber_g': data.get('fiber_g', 'N/A'),
                'sugar_g': data.get('sugar_g', 'N/A'),
            })
            formatted_data = format_nutrition_data(nutrition_data)
    print(formatted_data)
    return formatted_data





