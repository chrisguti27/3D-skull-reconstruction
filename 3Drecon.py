# Thanks to the research of https://pyscience.wordpress.com/2014/09/11/surface-extraction-creating-a-mesh-from-pixel-data-using-python-and-vtk/ #

import vtk
from vtk.util import numpy_support
import os
import numpy
import plotly
from plotly.graph_objs import *

#................FUNCTIONS DEFINITION.................#
def vtkImageToNumPy(image, pixelDims):
    pointData = image.GetPointData()
    arrayData = pointData.GetArray(0)
    ArrayDicom = numpy_support.vtk_to_numpy(arrayData)
    ArrayDicom = ArrayDicom.reshape(pixelDims, order='F')

    return ArrayDicom

#Create a 2D heatmap from an array
def plotHeatmap(array, name="plot"):
    data = Data([
        Heatmap(
            z=array,
            colorscale=[[0,'black'],[1.0,'white']]
        )
    ])
    layout = Layout(
        autosize=False,
        #width = 600,
        #height = 600,
        title=name
    )
    fig = Figure(data=data, layout=layout)
    plot_url = plotly.graph_objs.Figure(fig)
    return plot_url.show()

#plot CT slice
def vtk_show(renderer1,renderer2, width=700, height=700):
    """
    3D PLOT
    """
    ren = vtk.vtkRenderer()
    ren.SetBackground(0.0,0.0,0.0)
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(ren)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renderWindow)
    renderer1.GetProperty().SetColor(1.0,1.0,1.0)
    ren.AddActor(renderer1)
    ren.AddActor(renderer2)

    renderWindow.SetSize(width, height)
    renderWindow.Render()

    iren.Initialize()
    iren.Start()

    return #Image(data)

#............READING/SORTING/GROUP DICOM FILES..........#
#colors = vtk.vtkNamedColors()
#colors.SetColor("SkinColor", [255, 125, 64, 255])
#Asignación del directorio de lectura para los archivos DICOM
PathDicom = "./vhm_head/"
#lectura de archivos dicom
reader=vtk.vtkDICOMImageReader()
reader.SetDirectoryName(PathDicom)
reader.Update()

#................. DICOM IMAGES DIMENSION ADJUSTMENT................#
# Load dimensions using `GetDataExtent`
_extent = reader.GetDataExtent()
ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]
ConstPixelSpacing = reader.GetPixelSpacing()
print(ConstPixelSpacing)

                #......Plot 2D skull slide.......#
ArrayDicom = vtkImageToNumPy(reader.GetOutput(), ConstPixelDims)
plotHeatmap(numpy.rot90(ArrayDicom[:, 256, :]), name="CT_Original")


#........ HOUNDSFIELD THRESHOLDING DATA.......#
threshold = vtk.vtkImageThreshold ()
threshold.SetInputConnection(reader.GetOutputPort())
threshold.ThresholdByLower(386)  # set value for thresholding
threshold.ReplaceInOn()
threshold.SetInValue(0)  # set all values below 386 to 0
threshold.ReplaceOutOn()
threshold.SetOutValue(1)  # set all values equal or above 386 to 1
threshold.Update()
                #......PLOT THRESHOLDED IMAGE.......#
ArrayDicom = vtkImageToNumPy(threshold.GetOutput(), ConstPixelDims)
plotHeatmap(numpy.rot90(ArrayDicom[:, 256, :]), name="CT_Thresholded")


#...........3D MESH GENERATION.........#
dmc = vtk.vtkDiscreteMarchingCubes()
dmc.SetInputConnection(threshold.GetOutputPort())
dmc.GenerateValues(1, 1, 1)
dmc.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(dmc.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(255,255,255)


#.......outline.....#

outlineData = vtk.vtkOutlineFilter()
outlineData.SetInputConnection(reader.GetOutputPort())

mapOutline = vtk.vtkPolyDataMapper()
mapOutline.SetInputConnection(outlineData.GetOutputPort())

outline = vtk.vtkActor()
outline.SetMapper(mapOutline)
outline.GetProperty().SetColor(colors.GetColor3d("White"))

#MESH PLOT
vtk_show(actor, outline, 600, 600)

#...............GENERATE .stl FILE.............#
writer = vtk.vtkSTLWriter()
writer.SetInputConnection(dmc.GetOutputPort())
writer.SetFileTypeToBinary()
writer.SetFileName("craneo.stl")
writer.Write()
