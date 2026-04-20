# Article-Dscriptors

### Methodoloy

For the development of this work, a number of approaches were commonly used for loading and processing petrographic images. The pre-processing stage was carried out using a set of modules such as Numpy, Scikit-Image, Scipy, OpenCV and Matplotlib, within the Python programming language. This is an open-source programming language for users. The complete system was implemented using matrices and optimization algorithms, following the steps of prepro-cessing with computer vision techniques, segmentation using density-based methods and morphological analysis with mathematical operation. The flowchart shown in figure 3 illustrates the structure of the model proposed in this work. This visual representation aims to organize and demonstrate the main methodological steps adopted, making it easier to understand the steps taken. The diagram has been divided into sequential blocks showing the stages of the study, from data preparation, through pre-processing and processing, to the final stage of analysis and interpretation of the results. Each part of the flowchart represents an essential phase in the development of the study.

### Image Loading and Pre-Processing

The images used were obtained from rock samples analyzed under a microscope, with a resolution of 100 µm. To load the images, the OpenCV library was used, which allows image files in various formats to be read using the cv2.imread \cite{Bradski2000} function. After reading, in order to highlight the mineral characteristics and structures contained in each sample, the RGB scale was converted to grayscale using the cvtColor function, converting each pixel of the image to a corresponding light intensity level on the grayscale.

### Segmentation by Color Mask

The first stage of the segmentation procedure consisted of generating a binary mask from the original image, with the objective of isolating exclusively the regions corresponding to the grains of interest. This step is fundamental in digital image processing workflows, as it transforms a multichannel color image into a simplified logical representation, in which each pixel is classified either as belonging to the object (grain) or to the background. By reducing the problem to a binary domain, subsequent geometric and morphological analyses can be performed with greater robustness and computational efficiency. Initially, the image was loaded in RGB format, meaning that each pixel is represented by a triplet of intensity values corresponding to the red, green, and blue channels, respectively. The target colors associated with the grains were provided in hexadecimal notation and subsequently converted into the RGB color space, yielding vectors of the form $c = (R, G, B)$. Since real images are subject to illumination variations, sensor noise, and compression artifacts, an exact color match is generally impractical. For this reason, a tolerance parameter $\tau$ was introduced to define an admissible interval around each color component. For a given reference color $c = (R, G, B)$, the tolerance $\tau$ defines lower and upper bounds in each channel, resulting in the following vectors:

$$
\mathbf{L} = \big(\max(R - \tau, 0), \, \max(G - \tau, 0), \, \max(B - \tau, 0)\big),
$$

$$
\mathbf{U} = \big(\min(R + \tau, 255), \, \min(G + \tau, 255), \, \min(B + \tau, 255)\big),
$$

the operators $\max(\cdot)$ and $\min(\cdot)$ ensure that the interval limits remain within the valid range of the RGB space, namely $[0, 255]$ for each channel. Geometrically, this tolerance defines a rectangular prism in the three-dimensional RGB space, within which pixel colors are considered sufficiently similar to the reference grain color. Each pixel of the original image, denoted by $I(x,y)$ at spatial position $(x,y)$, was then evaluated component-wise. A pixel was classified as belonging to the grain if and only if its RGB vector lay within the closed interval defined by $[\mathbf{L}, \mathbf{U}]$ in all three components simultaneously. This decision rule can be expressed formally as:

$$
M(x,y) =
\begin{cases}
1, & \text{if } \mathbf{L} \leq I(x,y) \leq \mathbf{U}, \\
0, & \text{otherwise},
\end{cases}
$$

where $M(x,y)$ represents the resulting binary mask. In this representation, pixels labeled with value $1$ correspond to candidate grain regions, while pixels labeled with $0$ correspond to the background or to regions not matching the specified chromatic criteria. This operation effectively performs a color-based thresholding in the RGB space, producing a preliminary segmentation. However, the binary mask obtained after color thresholding may contain multiple disconnected regions, including small artifacts caused by noise, reflections, or minor color fluctuations. To address this issue, a connected component labeling procedure was applied. This algorithm identifies contiguous pixel clusters according to a predefined neighborhood connectivity (typically 4-connectivity or 8-connectivity), assigning a unique label to each distinct region. As a result, the binary image is decomposed into a set of individually identifiable objects.
