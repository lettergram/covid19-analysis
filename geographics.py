import os
import glob
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter  
import imageio

def create_us_map_by_year(geo_us_data, column_to_analyze,
                          gif_name, image_dir,
                          title=None, ymin=None, ymax=None, color_map='GnBu'):

    """
    :param geo_us_data: Pandas data frame, with geopandas data <--- NECESSARY
    """
    
    # Create a snapshot of each year
    years = state_data.sort_values(by=['year']).dropna(
        subset=[column_to_analyze]
    )['year'].unique()
    
    country_data = {}
    for year in years:
        year_filter = geo_us_data['Year'] == year
        country_data[year] = geo_us_data.where(year_filter).dropna(
            subset=[column_to_analyze]
        )

    # Create image directory if necessary
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    # Generate figures
    if not ymin:
        ymin = 0
    if not ymax:
        ymax = max(geo_us_data.dropna(
            subset=[column_to_analyze]
        )[column_to_analyze])
    
    for year in years:

        print(column_to_analyze + ", Generating " + str(year))
        
        # Assumes matplotlib backend
        fig = country_data[year].plot(column=column_to_analyze,
                                      cmap=color_map,
                                      figsize=(20,10), legend=True,
                                      vmin=ymin, vmax=ymax,
                                      norm=plt.Normalize(vmin=ymin, vmax=ymax))

        # Zoom to Continental U.S.
        fig.set_xlim(-125, -67)
        fig.set_ylim(24, 49)
    
        fig.axis('off')
    
        fig.set_title(title, fontdict={'fontsize': '28', 'fontweight' : '4'})

        fig.annotate(year, xy=(0.1, .3), xycoords='figure fraction',
                     horizontalalignment='left', verticalalignment='top',
                     fontsize=35)
    
        us_map = fig.get_figure()
        us_map.savefig(image_dir+"us_"+str(year)+'.png',
                       dpi=150, bbox_inches='tight')
        us_map.tight_layout()

    # Create gif, images should be in order due to name
    image_files = glob.glob(image_dir+"*")
    image_files.sort()
    images = [imageio.imread(image) for image in image_files]
    imageio.mimwrite(gif_name, images, fps=1, palettesize=128)
