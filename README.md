# Morphological characterization based on the unsupervised clustering method and Fourier transform by mathematical descriptors in sedimentary grains: application to the Amazon basin petrographic images

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

with $\sigma$ representing the standard deviation that controls the degree of smoothing. Larger values of $\sigma$ produce stronger blurring effects, while smaller values preserve finer details. The convolution process replaces each pixel value with a weighted average of its neighbors, where the weights decrease radially according to the Gaussian distribution. This property ensures that local intensity variations are smoothed in a spatially coherent manner, effectively reducing high-frequency noise while preserving global structural features and relatively smooth edges Gonzalez, 2002. Unlike simple averaging filters, the Gaussian filter minimizes edge distortion due to its isotropic and smoothly decaying kernel. In the context of granular morphology analysis, the application of Gaussian smoothing aims to approximate more closely the physical contour of the grains by removing artificial pixel-level irregularities. This operation contributes to a more stable estimation of geometric descriptors, such as area, perimeter, and radial distances, without significantly altering the macroscopic structure of the objects. Consequently, the smoothing stage enhances the robustness and reliability of the quantitative analysis, ensuring that the extracted morphological characteristics reflect intrinsic grain properties rather than digital noise artifacts.

### Grain grouping using DBSCAN

The clustering of groups was performed using the DBSCAN (Density-Based Spatial Clustering of Applications with Noise) algorithm, implemented in the Scikit-Learn library Pedregosa, 2011. DBSCAN is a density-based clustering method, as shown in figure , which identifies sets of spatially connected points based on the local concentration of the samples, being able to consider clusters with arbitrary geometry and automatically separate points classified as noise Ester, 1996. This characteristic is particularly relevant in the context of petrographic images, in which mineral grains exhibit irregular shapes and heterogeneous spatial distribution. Formally, consider a set of points $\mathcal{X} = \{ \mathbf{x}_i \in \mathbb{R}^2 \}$, where each point $\mathbf{x}_i = (x_i, y_i)$ represents the spatial coordinate of a pixel belonging to the previously segmented solid phase. Define the environment $\varepsilon$ of a point $\mathbf{x}_i$ as the set

$$
N_{\varepsilon}(\mathbf{x}_i) = \left\{ \mathbf{x}_j \in \mathcal{X} \;:\; \lVert \mathbf{x}_i - \mathbf{x}_j \rVert_2 \leq \varepsilon \right\},
$$

where $\lVert \cdot \rVert_2$ denotes the Euclidean norm and $\varepsilon > 0$ corresponds to the maximum radius of spatial influence. A point $\mathbf{x}_i$ is classified as a kernel point if it satisfies the condition

$$
|N_{\varepsilon}(\mathbf{x}_i)| \geq \text{minimum number of samples},
$$

where Minimum number of Samples represents the minimum number of points needed to characterize a high-density region. Points that do not meet these criteria but belong to the neighborhood of a core point are classified as edge points, while those that do not meet any of these conditions are considered noise. The formation of clusters is based on the concept of density reach. A point $\mathbf{x}_j$ is here directly realized by density from $\mathbf{x}_i$ if $\mathbf{x}_j \in N_{\varepsilon}(\mathbf{x}_i)$ and $\mathbf{x}_i$ to a core point. Two points belong to the same cluster if there exists a finite sequence of points $\{\mathbf{x}_k\}$ such that each point in the sequence is directly realized by the density of the previous point. Thus, a cluster is defined as a maximal set of densely connected points.

In this work, the DBSCAN settings were adjusted to reflect the spatial scale and morphology of the mineral grains collected in the images. The $\varepsilon$ parameter was set to 20 pixels, a value obtained from empirical tests that considered the average distance between pixels belonging to the same grain and the typical separation between adjacent grains. This choice ensures that density connectivity specifically represents the physical continuity of each grain, avoiding the merging of specific structures. The minimum number of samples parameter was set to 50, based on statistical analysis of the distribution of the number of pixels per grain after segmentation. These limits act as a minimum density guideline, ensuring that only regions with sufficient area and physical relevance are defined as valid clusters. Small pixel clusters that cause noise or imperfections in the segmentation process are thus automatically discarded.

### Filling in the Gaps

To correct discontinuities within the segmented grains, morphological processing techniques were used to fill internal regions disconnected from the outer edge. The `binary fill holes` method, available in the SciPy library by Virtanen, 2020, was used to automatically fill internal holes, ensuring the continuity of the segmented structures. This approach is based on identifying closed regions within the binary masks of the image and then replacing them with pixels belonging to the main object. Additionally, the `remove small holes` function, present in the `morphology` class of the Scikit-Image library by VanDerWalt, 2014, was applied to eliminate small internal voids that may arise as artifacts of the segmentation process. The parameters used for this step include the Area Limit to define the minimum size of the area to be preserved, removing small regions that may contain processing artifacts. In addition, Connectivity is used to determine the connection considered to define whether a region should be filled or not. These processes ensure the continuity of the identified grains, eliminating segmentation failures and improving the accuracy of the analysis.

### Calculating the Center of Mass

The determination of the center of mass of each segmented grain constitutes a fundamental step in the geometric characterization process, as it establishes a stable and physically meaningful reference point for subsequent morphological measurements. In this work, the center of mass was computed using the function \texttt{center\_of\_mass} available in the SciPy library \cite{Virtanen2020}, which implements a discrete formulation of the classical barycenter definition applied to digital images. Let $R(i,j)$ denote the binary representation of a segmented grain in a two-dimensional image domain of size $n \times m$, where pixels belonging to the grain assume value $1$ and background pixels assume value $0$. In this formulation, the grain is treated as a discrete mass distribution in which each foreground pixel contributes equally to the total mass. This assumption corresponds to considering a uniform density model, which is appropriate when the objective is purely geometric characterization rather than physical density estimation. The total mass $M$ of the grain is defined as the sum of all foreground pixel values:

$$
M = \sum_{i=1}^{n} \sum_{j=1}^{m} R(i, j),
$$

which, in the binary case, corresponds simply to the total number of pixels that compose the grain region. This scalar quantity is directly proportional to the grain area in pixel units and provides a normalization factor for the centroid computation. The coordinates of the center of mass $(x_c, y_c)$ are obtained by computing the first-order spatial moments of the binary region and normalizing them by the total mass. Formally, the horizontal coordinate is given by:

$$
x_c = \frac{1}{M} \sum_{i=1}^{n} \sum_{j=1}^{m} i \cdot R(i, j),
$$

and the vertical coordinate is defined as:

$$
y_c = \frac{1}{M} \sum_{i=1}^{n} \sum_{j=1}^{m} j \cdot R(i, j).
$$

These expressions correspond to the discrete analog of the continuous centroid definition:

$$
\mathbf{r}_c = \frac{1}{M} \int_{\Omega} \mathbf{r} \, dA,
$$

where $\Omega$ represents the domain of the object. In the digital case, the integral is replaced by finite summations over the pixel grid. The resulting point $(x_c, y_c)$ represents the equilibrium position of the region under the assumption of uniform mass distribution. From a geometric standpoint, the center of mass possesses several desirable properties. It is invariant under translation, meaning that shifting the grain in the image does not alter its relative position within the object. Furthermore, it provides a stable central reference even for irregular or non-convex shapes, since it depends on the global distribution of pixels rather than on local contour features. In the context of the present study, the center of mass plays a central role in the transformation of the contour representation into polar coordinates. By using $(x_c, y_c)$ as the origin for radial sampling, it becomes possible to define the function $r(\theta)$ describing the distance from the centroid to the boundary in different angular directions. Consequently, the accuracy of the center of mass estimation directly influences the stability of radius computation and the reliability of the subsequent Fourier-based modeling.

### Radius Calculation

For each segmented grain, the radial distances were computed from the previously determined center of mass, which serves as a geometrically consistent reference point for the polar representation of the contour. The use of the center of mass ensures that the radial sampling is invariant with respect to translation and provides a physically meaningful origin for morphological measurements. This choice is particularly appropriate in granular analysis, since it minimizes directional bias and allows the contour to be described as a single-valued function in polar coordinates. Let $R \subset \mathbb{Z}^2$ denote the set of pixels belonging to the segmented grain in the binary image. Consider a set of $N$ evenly spaced angular directions $\{\theta_k\}_{k=0}^{N-1}$, defined in the interval $[0, 2\pi]$, such that

$$
\theta_k = \frac{2\pi k}{N}, \quad k = 0,1,\dots,N-1,
$$

For each direction $\theta_k$, a discrete radial search is performed starting from the center of mass $(x_c, y_c)$ and progressing outward along the ray defined by that angle. The objective is to determine the first point along the ray that no longer belongs to the grain region $R$. Therefore, the radius $r_k$ associated with the direction $\theta_k$ is defined as the smallest integer $r$ for which the corresponding point lies outside the segmented region. Mathematically, this radius is determined by

$$
r_k = \min \left\{ r \in \mathbb{N} \mid (x_c + r \cos \theta_k,\; y_c + r \sin \theta_k) \notin R \right\},
$$

where $(x_c, y_c)$ are the coordinates of the center of mass and the pair $(x_c + r \cos \theta_k, y_c + r \sin \theta_k)$ represents the discretized parametric equation of a straight line in the direction $\theta_k$. In computational terms, this procedure corresponds to a directional boundary detection algorithm, in which the transition between object and background pixels defines the effective contour position. Because the image domain is discrete, the radial increment $r$ is taken in integer pixel units. Consequently, the detected radius corresponds to the first background pixel encountered along the ray, which approximates the geometric intersection between the ideal continuous ray and the grain boundary. The accuracy of this approximation depends on the angular resolution $N$ and on the image resolution, both of which directly influence the fidelity of the reconstructed contour. Once the full set of radii $\{r_k\}_{k=0}^{N-1}$ is obtained, the contour of the grain can be represented in polar form as a discrete function $r(\theta_k)$. This representation transforms the two-dimensional geometric boundary into a one-dimensional radial signal, which is particularly suitable for subsequent spectral analysis using the Fourier series. Since the radii are initially measured in pixel units, a conversion to physical units is required to ensure dimensional consistency and allow comparison between different samples. Let $\alpha$ denote the spatial calibration factor of the image, expressed in micrometers per pixel ($\mu$m/pixel). The conversion from pixels to micrometers is performed according to

$$
r_k^{\mu m} = r_k \cdot \alpha,
\label{eq:conversao}
$$

where $r_k^{\mu m}$ represents the physical radius corresponding to the angular direction $\theta_k$. This scaling operation preserves the geometric proportions of the contour while embedding the measurements in a physically interpretable metric space. The resulting set of calibrated radii provides a complete quantitative description of the grain boundary in polar coordinates. From this dataset, it is possible to extract morphological parameters such as mean radius, radial variance, anisotropy, and boundary irregularity. Furthermore, this radial representation constitutes the fundamental input for the Fourier-based modeling and spectral roughness analysis developed in the subsequent sections. In this way, the radius calculation stage establishes the essential link between digital image segmentation and mathematical contour modeling, ensuring that the geometric characterization is both numerically consistent and physically meaningful.

### Modeling with Fourier Series

Mathematical modeling to obtain the representation of the radii using Fourier series is a classical spectral analysis technique that allows a periodic function, or a periodically extended function, to be expressed as a sum of sine and cosine terms with different frequencies, amplitudes, and phases. In the context of this work, the radii calculated at different angular directions from the center of mass are interpreted as a discrete function $r(\theta)$, where $\theta$ represents the polar angle and $r$ corresponds to the radial distance to the grain boundary in that direction. Since the angular variable varies in the interval $[0, 2\pi]$, the function naturally admits a periodic extension, which justifies the formal application of the Fourier series decomposition. The angular discretization is performed by sampling $N$ equally spaced directions, resulting in the finite set of radii $\{r_k\}_{k=1}^{N}$, where $N$ corresponds to the total number of angles considered in the contour representation. This discrete representation transforms the continuous geometric description of the boundary into a numerical problem, enabling the application of the Discrete Fourier Transform (DFT). The DFT of the radii is defined as

$$
C_n = \sum_{k=0}^{N-1} r_k e^{-i 2\pi n k / N},
$$

where $C_n$ are the complex Fourier coefficients associated with the harmonic of order $n$, $i$ is the imaginary unit, and the complex exponential term defines the orthogonal spectral basis. Each coefficient $C_n$ contains information about both the amplitude and the phase of the corresponding frequency component. From a geometric perspective, low-order coefficients are associated with the global shape of the grain, whereas higher-order coefficients describe local variations of the boundary, such as small-scale irregularities and fine roughness features. The spectral decomposition enables the interpretation of the contour as the superposition of independent harmonic contributions acting at different spatial scales. This multiscale property is particularly relevant for sedimentary grain characterization, since it allows the separation of the overall geometry, typically related to transport and depositional history, from small-scale boundary irregularities that may be associated with abrasion, micro-fracturing, or segmentation artifacts. To promote smoothing of the radial profile and reduce the influence of high-frequency noise introduced during segmentation or discretization, a spectral filtering procedure is applied. This procedure consists of retaining only the first $H$ Fourier coefficients and setting the remaining higher-frequency coefficients to zero, according to:

$$
C_n = 0 \quad \text{for} \quad n > H.
$$

This truncation acts as a low-pass filter in the spectral domain, removing high-frequency components that generally correspond to abrupt boundary oscillations. Geometrically, this operation preserves the dominant structural features of the grain while attenuating very fine fluctuations that may not represent morphologically significant characteristics. The reconstruction of the smoothed radii $\{\tilde{r}_k\}_{k=1}^{N}$ is obtained through the Inverse Discrete Fourier Transform (IFFT), defined as

$$
\tilde{r}_k = \frac{1}{N} \sum_{n=0}^{N-1} C_n e^{i 2\pi n k / N}.
$$

This operation reconstructs the radial function in the spatial domain from the filtered spectral coefficients. Since the IFFT is mathematically consistent with the DFT, the reconstructed contour remains structurally coherent with the original representation, differing only by the exclusion of the truncated high-frequency components. A fundamental advantage of this approach lies in the explicit control of the smoothing level through the parameter $H$. Smaller values of $H$ produce smoother contours dominated by low-frequency components and global geometry, whereas larger values allow progressively finer boundary details to be recovered. Therefore, the number of harmonics $H$ acts as a multiscale regularization parameter, enabling adaptive adjustment of the contour representation according to the morphological complexity of each grain.
