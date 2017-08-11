# -*- coding: utf-8 -*-


import os
from os.path import basename
from osgeo import gdal
from osgeo import gdalconst
import numpy as np
import scipy.ndimage
from folderManager import initialize

# Import custom modules
import spatialIO as spio


def main(options):

    # Prepare the folders for outputs:
    initialize(options)
    # For direct file input
    if not os.path.isdir(options['src']):
        options['filePath'] = options['src']

        processing(options)

    if os.path.isdir(options['src']):
        if not options['src'].endswith('/'):
            options['src'] = options['src'] + '/'

        file_list = os.listdir(options['src'])
        inputDir = options['src']

        # Iterate each file for processing and exports
        for k, file_list in enumerate(file_list):
            # File checker
            if file_list.lower().endswith('.tif'):
                options['filePath'] = inputDir + file_list

                # Process each file
                processing(options)


def processing(options):
    '''
    Extract Forest zones from canopy height model with respect to minimal
    legal shape size. Output are forest zones, forest contour, isolated trees
    '''
    # Import CHM raster data
    data, geotransform, prj_wkt = spio.rasterReader(options['filePath'])
    options['geotransform'] = geotransform
    options['prj_wkt'] = prj_wkt
    RasterYSize, RasterXSize = data.shape

    # Filter non realstic data
    data = (data < 60) * (data > 1) * data

    ########################################################################
    # Compute a priori forest zones
    ########################################################################

    # Compute no-tree/forest binary data
    forest_mask = data > 0

    # Fill the small holes which are to small to be considered as clearings
    holes = forest_mask < 1
    holes = filterElementsBySize(holes, options['MaxAreaThres'])

    # Remove the small forest islands which are to small to be considered
    # as forest zones

    forest_mask = holes < 1
    forest_zones = filterElementsBySize(forest_mask, options['MinAreaThres'])

    ########################################################################
    # Select trees at the outline of forests zones and isolated trees
    ########################################################################

    # Create kernel
    radius = options['WinRad']
    kernel = np.zeros((2*radius+1, 2*radius+1))
    y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
    mask = x**2 + y**2 <= radius**2
    kernel[mask] = 1

    # Computing outline
    forest_eroded = scipy.ndimage.binary_erosion(forest_zones, kernel)
    forest_outline = forest_zones - forest_eroded

    # Computing inner elements
    forest_inside = forest_zones - forest_outline

    # Computing small elements
    forest_isolated = forest_mask - forest_zones
    # Computing contour and isolated trees for selection purposes
    forest_selected = forest_isolated + forest_outline

    filename = basename(os.path.splitext(options['filePath'])[0])

    export(options, filename, forest_mask, forest_zones, forest_outline,
           forest_isolated, forest_selected)

    return


def filterElementsBySize(elements, size):
    ''' This function filters bool grids by elements size'''
    # Get the array dimensions
    RasterYSize, RasterXSize = elements.shape

    # Label the different zones
    labeled_array, num_features = scipy.ndimage.label(
        elements, structure=None, output=np.int)

    # Initiate the new elements array
    # elements_new = np.zeros((RasterYSize, RasterXSize), dtype=np.bool)

    # filter the elements by size
    matches = np.bincount(labeled_array.ravel()) > size

    # Get the IDs corresponding to matches
    match_feat_ID = np.nonzero(matches)[0]
    valid_match_feat_ID = np.setdiff1d(match_feat_ID, [0, num_features])

    elements_new = np.in1d(labeled_array, valid_match_feat_ID
                           ).reshape(labeled_array.shape)

    return elements_new


def export(options, filename, forest_mask, forest_zones, forest_outline,
           forest_isolated, forest_selected):
    '''
    Export the results to files
    '''
    # export raster results
    forest_maskPath = options['dst'] + 'tif/' + filename + '_forest_mask.tif'
    spio.rasterWriter(forest_mask, forest_maskPath, options['geotransform'],
                      options['prj_wkt'], gdal.GDT_Byte)

    forest_zonesPath = options['dst'] + 'tif/' + filename + '_forest_zones.tif'
    spio.rasterWriter(forest_zones, forest_zonesPath, options['geotransform'],
                      options['prj_wkt'], gdal.GDT_Byte)

    forest_selectedPath = options['dst'] + 'tif/' + filename + \
        '_forest_selected.tif'
    spio.rasterWriter(forest_selected, forest_selectedPath,
                      options['geotransform'], options['prj_wkt'],
                      gdal.GDT_Byte)
    # vectorize the forest zones
    polyPath = options['dst'] + 'shp/' + filename + '_forest_zones.shp'
    spio.polygonizer(forest_zonesPath, forest_zonesPath, polyPath)


if __name__ == "__main__":
    main(options)
