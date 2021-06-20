# 3D Skull-reconstruction

##A Python algorithm based on image segmentation by Hounsfield's threshold to generate a 3-Dimensional skull model.

The process has three phases, sorting, thresholding, and mesh smoothing. The three first steps used the VTK library for python, and for the last, you could use MeshLab, or your preferred software for mesh processing. Finally, a smoothed STL model is gotten.

![Diagram Skull Hithub](https://user-images.githubusercontent.com/57780789/122680893-7bd3df00-d1e9-11eb-9b9b-860f4e5c0194.png)
