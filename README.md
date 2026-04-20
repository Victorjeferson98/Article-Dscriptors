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

For each connected component, the area $A$ was computed as the total number of pixels belonging to that region. A minimum area threshold $A_{\min}$, defined by the user, was then applied to eliminate small regions considered irrelevant for the morphological analysis. Formally, components satisfying $A < A_{\min}$ were discarded, as they are likely to correspond to segmentation noise or spurious detections rather than actual grains. The final output of this stage was a refined binary mask containing only connected regions with area greater than or equal to $A_{\min}$. This refined mask ensures that subsequent geometric computations, such as center of mass determination and radial sampling, are performed exclusively on grains with sufficient spatial significance. Consequently, the segmentation process establishes a reliable foundation for quantitative morphological characterization, minimizing the propagation of noise and ensuring consistency in the analysis pipeline.

### Watershed Separation of Sticky Grains

Although the initial color-based segmentation and area filtering produce a refined binary mask, situations frequently arise in which adjacent grains remain merged into a single connected component. This phenomenon typically occurs when grains are in physical contact or when the segmentation process fails to detect narrow background gaps between them. As a consequence, multiple grains may be erroneously treated as a single object, compromising the accuracy of subsequent geometric and morphological measurements. To address this issue, a marker-controlled watershed segmentation strategy was employed, using the Euclidean Distance Transform (EDT) as the underlying topographic representation. Let $\Omega_0$ denote the set of background pixels in the binary mask and $\Omega_1$ the set of foreground pixels corresponding to the segmented grains. The Euclidean Distance Transform assigns to each pixel $(x,y) \in \Omega_1$ a scalar value equal to the shortest Euclidean distance to any background pixel. Formally, the distance map $D(x,y)$ is defined as:

$$
D(x,y) = \min_{(u,v) \in \Omega_0} \sqrt{(x-u)^2 + (y-v)^2},
$$

Geometrically, $D(x,y)$ represents the radius of the largest disk centered at $(x,y)$ that can be entirely inscribed within the grain region. Therefore, pixels located near the geometric centers of individual grains tend to exhibit higher distance values, while pixels near the boundaries present lower values. The resulting distance map can be interpreted as a continuous topographic surface, in which peaks correspond approximately to grain centers and valleys correspond to inter-grain boundaries. The local maxima of the function $D(x,y)$ were identified and used as internal markers $M_i$ for the watershed algorithm. Each marker ideally corresponds to a distinct grain, serving as a seed point from which region growth will originate. The accuracy of this marker detection step is crucial, as it directly influences the quality of the final separation. In practice, small spurious maxima may be suppressed using morphological filtering or thresholding to avoid over-segmentation. To perform the separation, the watershed operator was applied to the negated distance map $-D(x,y)$. The negation converts the peaks of $D(x,y)$ into basins in $-D(x,y)$, allowing the algorithm to simulate a flooding process starting from the predefined markers. Conceptually, the watershed transform treats the image as a topographic relief: water is allowed to fill the basins beginning at each marker location, and as the flooding progresses, expanding regions compete for space. The boundaries between regions are established where two expanding fronts meet, which typically occurs along narrow contact zones between adjacent grains. The output of the watershed segmentation is a labeled image defined by:

$$
L(x,y) \in \{1, 2, \dots, N\},
$$

where $N$ represents the total number of detected grains and each integer label uniquely identifies the region to which the pixel $(x,y)$ belongs. In this representation, previously merged grains are separated into distinct connected components, each corresponding to an individual morphological unit. This marker-controlled watershed approach provides a mathematically consistent and geometrically intuitive solution to the problem of sticky grains. By leveraging the intrinsic geometric information encoded in the distance transform, the method ensures that separation occurs preferentially along minimal cross-sectional regions, which are typically associated with inter-grain contact zones. Consequently, the watershed refinement step enhances the reliability of the segmentation pipeline, preserving the integrity of individual grains and enabling accurate subsequent computations of area, center of mass, and radial contour representation.

### Extraction of Segmented Grain Boundaries

Once the watershed segmentation produced the labeled image $L(x,y)$, in which each connected region corresponds to an individual grain, the next stage consisted of extracting the geometric contours associated with each segmented object. This step is fundamental for morphological analysis, since subsequent procedures such as radial sampling, curvature estimation, and Fourier modeling depend directly on an accurate representation of the grain boundary. Let $R_i$ denote the set of pixels belonging to the $i$-th grain, defined as:

$$
R_i = \{ (x,y) \; | \; L(x,y) = i \},
$$

the boundary of this region, denoted by $C_i$, is defined as the subset of pixels in $R_i$ that are adjacent to at least one pixel not belonging to the same region. In other words, a pixel lies on the contour if it marks a transition between the interior of the grain and either the background or a neighboring grain. Formally, the contour is defined as:

$$
C_i = \{ (x,y) \in R_i \; | \; \exists (u,v) \in \mathcal{N}(x,y) \text{ such that } L(u,v) \neq i \},
$$

where $\mathcal{N}(x,y)$ represents the 8-connected neighborhood of the pixel $(x,y)$. The adoption of 8-connectivity ensures that diagonal adjacency relationships are considered, resulting in a more geometrically consistent and continuous contour representation when compared to 4-connectivity. From a computational perspective, this operation corresponds to detecting boundary transitions in the labeled image, effectively performing a discrete approximation of the gradient of the region indicator function. The resulting set $C_i$ forms a one-pixel-thick outline that approximates the true geometric boundary of the grain in the digital domain. After extraction, these contours were superimposed onto the original RGB image. This overlay serves both as a qualitative validation step and as a visual verification of segmentation accuracy. By comparing the detected boundaries with the underlying image features, it becomes possible to identify potential segmentation artifacts, incomplete separations, or boundary distortions. Thus, contour extraction not only provides the geometric input required for subsequent quantitative modeling but also functions as an essential consistency check within the processing pipeline.

### Noise Smoothing and Removal

Following the segmentation and contour extraction stages, a smoothing and noise removal procedure was applied in order to attenuate high-frequency artifacts introduced during image acquisition and binary thresholding. Digital images are inherently affected by sensor noise, illumination variations, and quantization effects, all of which may introduce small-scale intensity fluctuations that do not correspond to actual physical irregularities in the grains. If not properly treated, these fluctuations may propagate through the processing pipeline and distort geometric measurements. To mitigate these effects, a Gaussian filter was applied using the OpenCV library \cite{Bradski2000}. The Gaussian filter is a linear smoothing operator based on convolution with a kernel derived from the two-dimensional normal distribution. Let $I(x,y)$ denote the input image. The filtered image $I_G(x,y)$ is obtained by:

$$
I_G(x,y) = (I * G_\sigma)(x,y),
$$

where $*$ denotes the convolution operation and $G_\sigma$ is the Gaussian kernel defined as:

$$
G_\sigma(x,y) = \frac{1}{2\pi\sigma^2} 
\exp\left(-\frac{x^2 + y^2}{2\sigma^2}\right),
$$

with $\sigma$ representing the standard deviation that controls the degree of smoothing. Larger values of $\sigma$ produce stronger blurring effects, while smaller values preserve finer details. The convolution process replaces each pixel value with a weighted average of its neighbors, where the weights decrease radially according to the Gaussian distribution. This property ensures that local intensity variations are smoothed in a spatially coherent manner, effectively reducing high-frequency noise while preserving global structural features and relatively smooth edges \cite{Gonzalez2002}. Unlike simple averaging filters, the Gaussian filter minimizes edge distortion due to its isotropic and smoothly decaying kernel. In the context of granular morphology analysis, the application of Gaussian smoothing aims to approximate more closely the physical contour of the grains by removing artificial pixel-level irregularities. This operation contributes to a more stable estimation of geometric descriptors, such as area, perimeter, and radial distances, without significantly altering the macroscopic structure of the objects. Consequently, the smoothing stage enhances the robustness and reliability of the quantitative analysis, ensuring that the extracted morphological characteristics reflect intrinsic grain properties rather than digital noise artifacts.
