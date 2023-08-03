# yes. delete the cube/light camera and then run this script

import bpy
import os
import json
import numpy as np

# Specify the directory where your .OBJ files are located
obj_dir = '/Users/simerlylab/Documents/mess/OBJ2/'

# Specify the JSON file path
json_file = '/Users/simerlylab/Desktop/Blender_Python_ABA/prettyjason.json'

# Load the JSON data
with open(json_file, 'r') as f:
    data = json.load(f)

# Colors available for collections in Blender (RGB)
collection_colors = [
    (1, 1, 1),  # White
    (0, 0, 0),  # Black
    (0.8, 0, 0),  # Red
    (0, 0.8, 0),  # Green
    (0, 0, 0.8),  # Blue
    (0.8, 0.6, 0),  # Yellow
    (0.4, 0.4, 0),  # Brown
    (0.6, 0.4, 0.8),  # Purple
]

# Function to find the closest collection color
def closest_collection_color(color):
    color = np.array(color)
    distances = [np.linalg.norm(color - np.array(c)) for c in collection_colors]
    closest_color_index = np.argmin(distances)
    return f'COLOR_{str(closest_color_index + 1).zfill(2)}'

# Create a root collection
root = bpy.data.collections.new('root')
bpy.context.scene.collection.children.link(root)

# Function to recursively set parent-child relationship
def set_hierarchy(data, parent=root):  # Default parent is root
    for item in data:
        # Create a new collection for the item
        col = bpy.data.collections.new(item['name'])
        parent.children.link(col)

        # Attempt to load the .OBJ file with the ID as its name
        try:
            bpy.ops.import_scene.obj(filepath=os.path.join(obj_dir, f"{item['id']}.obj"))
            obj = bpy.context.selected_objects[0]  # Get the imported object
            obj.hide_viewport = True if 'children' in item and item['children'] else False  # Hide the mesh if it has children

            # Rename the object
            obj.name = item['name']

            # Assign the color
            color = tuple(int(item['color_hex_triplet'][i:i+2], 16) / 255.0 for i in range(0, 6, 2))  # Convert hex to RGB
            col.color_tag = closest_collection_color(color)  # Assign the closest collection color
            
            # Remove existing materials
            obj.data.materials.clear()

            # Create a new material with the item color
            mat = bpy.data.materials.new(name=item['name'])
            mat.diffuse_color = color + (1.0,)  # Add alpha (set to 1.0)
            obj.data.materials.append(mat)

            # Move the object to the collection
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)

            # Rescale the object
            obj.scale = (0.001, 0.001, 0.001)
            
        except:
            print(f"Couldn't import .obj file for ID {item['id']}")
        
        # Recursively process children
        if 'children' in item:
            set_hierarchy(item['children'], parent=col)

# Run the function
set_hierarchy(data['msg'][0]['children'])
