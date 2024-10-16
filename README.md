# Primvar Visualization Extension [zha.customdata.vizualization]

A simple extension to visualize data saved on meshes.

If a transform contains children on any custom attached numeral primvars (int, float, double), either as a single value for a mesh or if the length of the attached values matches the count of vertices or the count of faces on the mesh, the extension is able to pick them up, and visualize the values as primvar colors on the meshes on the minimum to the maximum range.

The extension will create variants on the parent transform with the name of the given primvars on applying the visualisation colors.

Additionally the extension shows a value distribution of the attached values to give additional graphic insights on the attached data.

