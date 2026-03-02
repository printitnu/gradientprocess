#Script to analyze images for pore and swelling detection and create 3D graphs and 2D color plots
#Before running the script, you have to ensure that the path to the images is correct and that the images are in the correct format (PNG).
#The script uses OpenCV for image processing, NumPy for numerical operations, and Matplotlib for plotting.

import os #fix calling for Windows path
import numpy as np  # Importing NumPy for numerical operations
import cv2  # Importing OpenCV for image processing
from PIL import Image # Importing PIL for image handling
import matplotlib.pyplot as plt # Importing Matplotlib for plotting
from mpl_toolkits.mplot3d import Axes3D # Importing 3D plotting toolkit


# Function to apply filters to the image
# This function applies Gaussian Blur and Median Filter to the image to reduce noise    
def apply_filters(image):
    # Apply Gaussian Blur
    blurred_img = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Apply Median Filter
    median_filtered_img = cv2.medianBlur(blurred_img, 5)
    
    # Apply Bilateral Filter for edge-preserving smoothing
    bilateral_filtered_img = cv2.bilateralFilter(median_filtered_img, 9, 75, 75)
    
    return bilateral_filtered_img

# Function to analyze a single image for pores and swelling
# This function takes an image path as input, processes the image to identify pores and swelling,
def analyze_image(image_path):
    """
    Analyze the given image to identify and quantify pores and swelling areas.

    Parameters:
    image_path (str): Path to the image file.

    Returns:
    dict: A dictionary containing analysis results for each sample area.
    """
    #print(f"Analyzing image: {image_path}")
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Image not loaded. Check the file path and file integrity for {image_path}.")
        return None
    
    original_file_name = os.path.splitext(os.path.basename(image_path))[0]
    
    sample_areas = {
        'Sample 1': (130, 270, 130, 270),
        'Sample 2': (130, 270, 330, 470),
        'Sample 3': (330, 470, 130, 270),
        'Sample 4': (330, 470, 330, 470)
    }
    
    results = {}
    for sample, (x1, x2, y1, y2) in sample_areas.items():
        print(f"Processing {sample} area")
        sample_img = img[y1:y2, x1:x2]
        
        filtered_img = apply_filters(sample_img)
        
        output_path_filter = f'C:/Users/wilsjo/py/abctoanalyze/output/filtered_samples/{original_file_name}_filtered_{sample}.png'
        cv2.imwrite(output_path_filter, filtered_img)
        
        _, black_areas = cv2.threshold(filtered_img, 50, 255, cv2.THRESH_BINARY_INV)
        
        num_labels, labels_im = cv2.connectedComponents(black_areas)
        for label in range(1, num_labels):
            if np.sum(labels_im == label) < 4:
                black_areas[labels_im == label] = 0
        
        contours, _ = cv2.findContours(black_areas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        pores = np.zeros_like(black_areas)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w <= 15 and h <= 15:
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                if circularity > 0.4:
                    cv2.drawContours(pores, [contour], -1, 255, -1)
        
        # Improved swelling detection using dark and light regions side by side
        mean_intensity = np.mean(filtered_img)
        _, dark_regions = cv2.threshold(filtered_img, mean_intensity - 30, 255, cv2.THRESH_BINARY_INV)
        _, light_regions = cv2.threshold(filtered_img, mean_intensity + 30, 255, cv2.THRESH_BINARY)
        
        dark_contours, _ = cv2.findContours(dark_regions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        light_contours, _ = cv2.findContours(light_regions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        filtered_dark_contours = [cnt for cnt in dark_contours if cv2.boundingRect(cnt)[3] >= 30]
        filtered_light_contours = [cnt for cnt in light_contours if cv2.boundingRect(cnt)[3] >= 30]
        
        dark_mask = np.zeros_like(filtered_img)
        light_mask = np.zeros_like(filtered_img)
        cv2.drawContours(dark_mask, filtered_dark_contours, -1, 255, -1)
        cv2.drawContours(light_mask, filtered_light_contours, -1, 255, -1)
        
        combined_mask = cv2.bitwise_or(dark_mask, light_mask)
        
        kernel = np.ones((15, 15), np.uint8)
        dilated_combined_mask = cv2.dilate(combined_mask, kernel, iterations=1)
        
        swelling_contours, _ = cv2.findContours(dilated_combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        swelling = np.zeros_like(dilated_combined_mask)
        cv2.drawContours(swelling, swelling_contours, -1, 255, -1)
        
        total_pixels = filtered_img.size
        pore_density = np.sum(pores == 255) / total_pixels * 100
        swelling_density = np.sum(swelling == 255) / total_pixels * 100
        
        marked_img = cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
        marked_img[swelling == 255] = [0, 0, 255]
        marked_img[pores == 255] = [255, 0, 0]
        
        results[sample] = {
            'pore_density': pore_density,
            'swelling_density': swelling_density,
            'marked_img': marked_img,
            'pores': pores,
            'swelling': swelling,
            'sample_img': filtered_img
        }
    
    return results



# Function to process all images in a folder
# This function takes a folder path as input, processes each image in the folder sorted by oldest timestamp first
def process_folder(folder_path):
    #print(f"Processing folder: {folder_path}")
    # Get list of image files sorted by modification time (oldest first)
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')],
                         key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
    
    all_results = {}
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        results = analyze_image(image_path)
        
        if results is not None:
            all_results[image_file] = results
            
            # Save the marked images
            output_dir = os.path.join(folder_path, 'output')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            for sample, data in results.items():
                output_path = os.path.join(output_dir, f"{sample}_{image_file}")
                Image.fromarray(data['marked_img']).save(output_path)
                #print(f"Saved marked image for {sample} of {image_file}")
    
    return all_results

# Function to create 3D graphs and 2D color plots
# This function takes the results from the analysis and creates 3D graphs and 2D color plots for each sample
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os

height_z = 170 # number of analyzed images in z direction
pixels_in_img = 140

def create_3d_graph(all_results, folder_path, sample_size_mm):
    print("Creating 3D graphs")
    samples = ['Sample 1', 'Sample 2', 'Sample 3', 'Sample 4']  
    z_spacing = 0.07  # Height per image in mm
    
    voxel_height = pixels_in_img  # Height of each voxel in layers. THIS IS LENGTH OF IMAGE IN PIXELS
    voxel_width = 10  # Square voxels (x,z) for simplicity
    voxel_z_height = voxel_width
    voxel_z_height_to_mm = voxel_z_height * z_spacing  # Conversion factor based on sample size
    pixel_to_mm = sample_size_mm / pixels_in_img  # Conversion factor based on sample size
    
    print("Available samples in all_results:")
    for image_file, data in all_results.items():
        print(f"{image_file}: {list(data.keys())}")
    
    for sample in samples:
        fig = plt.figure(figsize=(14,6))
        
        # Create 3D plot
        ax3d = fig.add_subplot(121, projection='3d')
        
        # Set the view angle to view 3d plot
        ax3d.view_init(elev=30, azim=290)  

        z_offset = 0

        num_voxels_z_height = height_z // voxel_z_height #adjust 170 to number of images imported int(len(sample['sample_img']))
        #voxel_counts = np.zeros((num_voxels_z_height, pixels_in_img))  # Initialize voxel count array
        
        sample_data_exists = False
        total_pixels = 0
        total_pixels_x = 0
        total_pixels_y = 0
        total_pixels_z = 0
        
        # Initialize 3D array for voxel counts
        height, width = data[sample]['sample_img'].shape
        print(f"Image dimensions: {height} x {width}")
       
        num_voxels_width = width // voxel_width
        voxel_counts_3d = np.zeros((height, width, height_z)) #height // voxel_height
        z=0
        for image_file, data in all_results.items():            
            if sample in data:
                sample_data_exists = True
                pores_coords = np.column_stack(np.where(data[sample]['pores'] == 255))
                swelling_coords = np.column_stack(np.where(data[sample]['swelling'] == 255))

                total_pixels += data[sample]['pores'].size
                total_pixels_x = data[sample]['pores'].shape[1]  # Width of the image
                total_pixels_y = data[sample]['pores'].shape[0]  # Height of the image
                total_pixels_z += 1  # Each image represents one layer in z

                if len(pores_coords) > 0:
                    ax3d.scatter(pores_coords[:,1], pores_coords[:,0], z_offset,
                                c='red', marker='o', s=10, alpha=0.15, label='Pores' if z_offset == 0 else "")
                    for coord in pores_coords:
                        x, y = coord
                        #z_index = int(z_offset // voxel_z_height_to_mm)  # Ensure z_index is an integer
                        #print(f"z_offset: {z_offset}, z_index: {z_index}, x: {x}, y: {y}")
                        if z < height_z and x < pixels_in_img:
                            #voxel_counts[z, x] += 1  
                            if (0 <= y < pixels_in_img and 
                                0 <= x < pixels_in_img and 
                                0 <= z < height_z):
                                voxel_counts_3d[y, x, z] += 1  # Collect data for 2D plot

                if len(swelling_coords) > 0:
                    ax3d.scatter(swelling_coords[:,1], swelling_coords[:,0], z_offset,
                                c='blue', marker='o', s=10, alpha=0.15, label='Swelling' if z_offset == 0 else "")

                # Increment z_offset after processing each image
                z_offset += z_spacing
                #print(f"After incrementing, z_offset: {z_offset}, z_index: {z_index}")
            z = z+1


        if not sample_data_exists:
            print(f"Data for {sample} is missing.")
            continue  # This continue statement is now correctly inside the loop

        print(f"Sample: {sample}, Total pixels: {total_pixels}, Total pixels in x: {total_pixels_x}, Total pixels in y: {total_pixels_y}, Total pixels in z: {total_pixels_z}")

        # Enable 3D grid
        ax3d.grid(True)

        # Set ticks and labels for the 3D plot
        tick_interval = pixels_in_img / 5  # Define tick interval for both plots
        x_ticks = np.arange(0, 144, tick_interval)
        x_labels = [f'{tick * pixel_to_mm:.1f}' for tick in x_ticks]

        ax3d.set_xticks(x_ticks)
        ax3d.set_xticklabels(x_labels)

        y_ticks = np.arange(0, 144, tick_interval)
        y_labels = [f'{tick * pixel_to_mm:.1f}' for tick in y_ticks]

        ax3d.set_yticks(y_ticks)
        ax3d.set_yticklabels(y_labels)

        # Set custom z ticks
        total_z_height = height_z*z_spacing  # Total height in mm
        z_ticks = np.arange(0, total_z_height+0.5, 3)  # Define tick interval tick_interval*pixel_to_mm
        z_labels = [f'{tick * 1:.1f}' for tick in z_ticks]
        ax3d.set_zticks(z_ticks)
        ax3d.set_zticklabels(z_labels)



        #ax3d.set_zlabel('Height (mm)')
        ax3d.set_xlabel('Width (mm)')
        ax3d.set_ylabel('Length (mm)')
        
        # Add legend to the 3D plot
        handles, labels = ax3d.get_legend_handles_labels()
        unique_labels = dict(zip(labels, handles))
        legend = ax3d.legend(unique_labels.values(), unique_labels.keys())
        for handle in legend.legend_handles:
            handle._sizes = [30]  # Increase the size of the legend markers
        
        # Create custom colormap for the density map
        colors = ['red', 'orange', 'yellow', 'green']
        cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors)
        
        # Create 2D color plot
        ax2d = fig.add_subplot(122)
        
        #print(voxel_counts_3d)

        # Calculate pore density for each voxel across all layers
        density_map = np.zeros((num_voxels_z_height, num_voxels_width))
        total_pixels_per_voxel_list = []
        
        print(f"Pore pixels in each voxel for {sample}:")
        total_overall_pore_count = 0
        total_overall_pixel_count = 0
        for i in range(num_voxels_z_height):
            for j in range(num_voxels_width):
                total_pore_count = 0
                # Loop through all pixels within the current voxel
                for z in range(i * voxel_z_height, (i + 1) * voxel_z_height):
                    for width in range(j * voxel_width, (j + 1) * voxel_width):
                        total_pore_count += np.sum(voxel_counts_3d[:, width, z])
                
                #print(f"Processing voxel ({i}, {j})")
                total_pixels_in_voxel = voxel_z_height * voxel_width * pixels_in_img  # Correct calculation
                pore_density = ((total_pixels_in_voxel - total_pore_count) / total_pixels_in_voxel) * 100
                density_map[i, j] = min(pore_density, 100)  # Ensure density does not exceed 100%

                total_overall_pixel_count += total_pixels_in_voxel
                total_overall_pore_count += total_pore_count

                
                total_pixels_per_voxel_list.append(total_pixels_in_voxel)
                #print(f"Voxel ({i}, {j}): {total_pore_count} pore pixels, Total pixels in voxel: {total_pixels_in_voxel}, Density: {pore_density:.2f}%")
        #print(f"Total pixels per voxel list: {total_pixels_per_voxel_list}")
        mean_total_pixels_per_voxel = np.mean(total_pixels_per_voxel_list)
        #print(f"Mean number of pixels per voxel in {sample}: {mean_total_pixels_per_voxel}")
        
        total_overall_density = ((total_overall_pixel_count - total_overall_pore_count) / total_overall_pixel_count) * 100
        print(f"Total overall density for {sample}: {total_overall_density:.2f}%")

        # Plot the density map
        cax = ax2d.imshow(density_map, cmap=cmap, interpolation='nearest', aspect='auto', vmin=95, vmax=100)
        
        # Add density values as text on top of each voxel color
        for i in range(density_map.shape[0]):
            for j in range(density_map.shape[1]):
                ax2d.text(j, i, f'{int(density_map[i,j])}', ha='center', va='center', color='black')
        
        ax2d.set_xlabel('Width (mm)')
        ax2d.set_ylabel('Height (mm)')
        
        # Set ticks and labels for the 2D plot
        x_ticks = np.linspace(0, num_voxels_width, 6) - (voxel_width*pixel_to_mm/2)
        x_labels = [f'{tick * voxel_width * pixel_to_mm:.1f}' for tick in np.linspace(num_voxels_width, 0, 6)]
        ax2d.set_xticks(x_ticks)
        ax2d.set_xticklabels(x_labels)
        
        # Set y ticks and labels
        #y_ticks = np.arange(0, height_z // voxel_z_height, step=1) + (voxel_z_height_to_mm/2)
        #y_labels = [f'{tick * voxel_z_height_to_mm:.1f}' for tick in y_ticks]
        y_ticks = np.arange(0, num_voxels_z_height+0.5, num_voxels_z_height/4) -(0.5) # (voxel_z_height_to_mm/2)  # 
        y_labels = [f'{tick * voxel_z_height_to_mm + 0.4:.1f}' for tick in y_ticks]
        ax2d.set_yticks(y_ticks)
        ax2d.set_yticklabels(y_labels)

        
        # Invert the y-axis to match the 3D plot DEPENDING 3D ON ROTATION
        ax2d.invert_yaxis()
        ax2d.invert_xaxis()
        
        # Add color bar to the 2D plot
        fig.colorbar(cax, ax=ax2d, orientation='vertical', label='Density based on BSE threshold (%)')
        
        # Save the combined 3D and 2D plot
        output_dir = os.path.join(folder_path, 'output')
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f"{sample}_3d_2d_graph.png"), dpi=300)  
        print(f"Saved 3D and 2D graph for {sample}")

    plt.show()








































folder_path = 'C:/Users/wilsjo/py/abctoanalyze'
sample_size_mm = 12.9  # User-defined sample size in mm
all_results = process_folder(folder_path)
create_3d_graph(all_results, folder_path, sample_size_mm)


#check cv2 defis
print(cv2.imread)
print(cv2.IMREAD_GRAYSCALE)
print(cv2.threshold)
print(cv2.imwrite)

