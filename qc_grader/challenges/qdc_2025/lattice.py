"""
Library for constructing and visualizing LGTs in an 
IBM's Heavy-Hex lattice.
This module provides tools to:
- Generate Heavy-Hex lattice layouts (nodes and edges).
- Map qubit coordinates to logical qubit indices.
- Retrieve IBM backend-specific qubit layouts.
- Plot the lattice and highlight specific qubits.

Dependencies:
    - numpy
    - matplotlib

Authors: César Benito, Jesús Cobos
"""

from functools import cached_property
from typing import List, Union, Tuple, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------

def backends_objs_to_names(backends_arr):
        """
        Convert backend objects or names into a standardized list of backend names.

        Args:
            backends_arr: A single backend object/name or an iterable of them.

        Returns:
            str or list of str: Corresponding backend names.
        """       
        if isinstance(backends_arr, str):
            backends_arr = [backends_arr]
        else:
            try:
                backends_arr = list(backends_arr)
            except TypeError:
                backends_arr = [backends_arr]


        backends_name_arr = []
        for backend in backends_arr:
            if isinstance(backend, str):
                backends_name_arr.append(backend)
            else:
                backends_name_arr.append(backend.name)

        return backends_name_arr if len(backends_name_arr) > 1 else backends_name_arr[0]


# ---------------------------------------------------------------------------
# Core Data Structures
# ---------------------------------------------------------------------------

class vertex:

    """Represents a vertex (node) in the Heavy-Hex lattice."""

    def __init__(self, coords, qubit):
        """
        Args:
            coords (tuple[int, int]): Lattice coordinates of the vertex.
            qubit (int): Logical qubit index assigned to this vertex.
        """
        self.coords = coords
        self.qubit = qubit
        self.downwards = (coords[0]+coords[1])%2 == 1

    def __repr__(self) -> str:
        return f"<Vertex {self.coords} -> Qb: {self.qubit}>"

class edge:

    """Represents an edge (connection) in the Heavy-Hex lattice."""

    def __init__(self, coords, qubit):
        """
        Args:
            coords (tuple[float, float]): Lattice coordinates of the edge (may be half-integers).
            qubit (int): Logical qubit index assigned to this edge.
        """
        self.coords = coords
        self.qubit = qubit

        # Determine edge type and color encoding based on coordinates
        if int(coords[0]) == coords[0]:
            self.color = [1,0,2][int(coords[1]-0.5)%3]
            self.type = ['x','y'][int(coords[0]+coords[1]-0.5)%2]
        else:
            self.color = [0,1,2][(coords[1]//2+int(coords[0]-0.5)%2+2)%3]
            self.type = 'z'

    def __repr__(self) -> str:
        return f"<Edge {self.coords} -> Qb: {self.qubit}>"


# ---------------------------------------------------------------------------
# Heavy-Hex Lattice
# ---------------------------------------------------------------------------

class HeavyHexLattice:

    """
    Heavy-Hex lattice generator and analyzer.

    Attributes:
        plaquettes_width (int): Number of plaquettes in the horizontal direction.
        plaquettes_height (int): Number of plaquettes in the vertical direction.
        coords (list): All lattice coordinates (vertices + edges).
        edges (dict): Mapping of edge coordinates to Edge objects.
        vertices (dict): Mapping of vertex coordinates to Vertex objects.
    """

    def __init__(self, plaq_width, plaq_height):

        self.plaquettes_width = plaq_width
        self.plaquettes_height = plaq_height

        # Construct lattice coordinates
        width=plaq_width*2+1
        height=plaq_height

        edge_coords = []
        vertex_coords = []

        # Define vertex positions
        for i in range(height+1):
            for j in range(width+1):
                if i==0 and j == 0:
                    continue
                if i == height:
                    if j == 0 and i%2 != 0:
                        continue
                    if j == width and i%2 == 0:
                        continue
                vertex_coords.append((i,j))

        # Define edge positions (horizontal and vertical)
        for i in range(height+1):
            for j in range(width):
                if i==0 and j == 0:
                    continue
                if i == height:
                    if j == 0 and i%2 != 0:
                        continue
                    if j == width-1 and i%2 == 0:
                        continue
                edge_coords.append((i, j+0.5))

        for i in range(height):
            if i%2 == 0:
                for j in range((width+1)//2):
                    edge_coords.append((i+0.5, 2*j+1))
            else:
                for j in range(width//2+1):
                    edge_coords.append((i+0.5, 2*j))
                    
        # Combine coordinates and assign qubits
        self.coords = sorted(edge_coords+vertex_coords)
        self.edges = dict()
        self.vertices = dict()

        for (q,c) in enumerate(self.coords):
            if c in edge_coords:
                self.edges[c] = edge(c, q)
            else:
                self.vertices[c] = vertex(c, q)

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    @cached_property    
    def node_coords(self) -> List[Tuple[int, int]]:
        """List of vertex coordinates."""
        return list(self.vertices.keys())
    
    @cached_property    
    def node_qbinds(self) -> List[int]:
        """List of qubit indices corresponding to vertices."""
        return [i for i, coords in enumerate(self.coords) if coords in self.node_coords]

    @cached_property    
    def edge_coords(self) -> List[Tuple[float, float]]:
        """List of edge coordinates."""
        return list(self.edges.keys())
    
    @cached_property    
    def edge_qbinds(self) -> List[int]:
        """List of qubit indices corresponding to edges."""
        return [i for i, coords in enumerate(self.coords) if coords in self.edge_coords]

    @cached_property
    def max_x(self) -> int:
        """Maximum x-coordinate (horizontal)."""
        return max([coords[1] for coords in self.coords])

    @cached_property
    def max_y(self) -> int:
        """Maximum y-coordinate (vertical)."""
        return max([coords[0] for coords in self.coords])
    
    @cached_property
    def __len__(self) -> int:
        """Size of the lattice"""
        return len(self.coords)
    
    # -----------------------------------------------------------------------
    # Mapping and Connectivity
    # -----------------------------------------------------------------------

    def coords_to_logical_qb(self, coords):
        """
        Convert lattice coordinates to logical qubit indices.

        Args:
            coords: A coordinate tuple or list of tuples.

        Returns:
            int or list of int: Logical qubit indices.
        """
        if isinstance(coords, tuple):
            coords = [tuple(coords)]
        to_return = [self.coords.index((coord[0], coord[1])) for coord in coords]
        return to_return if len(to_return) > 1 else to_return[0]
    
    def edges_connected_to_node(self, node_coords):
        """
        Find edges connected to a given node.

        Args:
            node_coords: Coordinates of the node.

        Returns:
            list: List of edge coordinates connected to the node.
        """
        connected_edges_coords = []
        for coords in self.coords:
            if (0 <= (dx := abs(node_coords[0] - coords[0])) < 1) and (0 <= (dy := abs(node_coords[1] - coords[1])) < 1):
                if not (dx == 0 and dy == 0):
                    connected_edges_coords.append(coords)
        return connected_edges_coords
    
    def nodes_connected_to_edge(self, edge_coords):
        """
        Find nodes connected to a given edge.

        Args:
            edge_coords: Coordinates of the edge.

        Returns:
            tuple: Pair of node coordinates.
        """
        return (
            (np.floor(edge_coords[0]).astype(int), np.floor(edge_coords[1]).astype(int)),
            (np.ceil(edge_coords[0]).astype(int), np.ceil(edge_coords[1]).astype(int)),
        )    
    
    def find_qubits_downward(self):
        """
        Return matter qubits with an edge downwards.

        Returns:
            int or list of int: Logical qubit indices.
        """   
        matter_qubits = [node for node in self.vertices.values()]
        green_matter_qubits = []
        for v in matter_qubits:
            if v.downwards:
                green_matter_qubits.append(v.qubit)

        return green_matter_qubits 
    
    def find_qubits_upward(self):
        """
        Return matter qubits with an edge upwards.

        Returns:
            int or list of int: Logical qubit indices.
        """   
        matter_qubits = [node for node in self.vertices.values()]
        purple_matter_qubits = []
        for v in matter_qubits:
            if not v.downwards:
                purple_matter_qubits.append(v.qubit)

        return purple_matter_qubits 
    
    # -----------------------------------------------------------------------
    # Backend Mapping
    # -----------------------------------------------------------------------

    @staticmethod
    def get_backend_coordinates(backend):
        """
        Get the qubit coordinates for a given IBM backend.

        Args:
            backend: Backend object or backend name.

        Returns:
            list: Sorted list of qubit coordinates.
        """
        backend_name = backends_objs_to_names(backend)
        ibm_qubit_coords = []

        # Define backend-specific qubit placements
        if backend_name in ["ibm_fez", "ibm_marrakesh", "ibm_aachen", "ibm_kingston"]:
            for i in range(8):
                for j in range(16):
                    ibm_qubit_coords.append((2*i, j))
            for i in range(4):
                for j in range(4):
                    ibm_qubit_coords.append((4*i+1, 4*j+3))
            for i in range(3):
                for j in range(4):
                    ibm_qubit_coords.append((4*i+3, 4*j+1))
        elif backend_name == 'ibm_torino':
            for i in range(7):
                for j in range(15):
                    ibm_qubit_coords.append((2*i, j))
            for i in range(4):
                for j in range(4):
                    ibm_qubit_coords.append((4*i+1, 4*j))
            for i in range(3):
                for j in range(4):
                    ibm_qubit_coords.append((4*i+3, 4*j+2))

        else: # Eagle r3
            for i in range(7):
                for j in range(15):
                    if i == 0 and j == 14:
                        continue
                    if i == 6 and j == 0:
                        continue
                    ibm_qubit_coords.append((2*i, j))
            for i in range(3):
                for j in range(4):
                    ibm_qubit_coords.append((4*i+1, 4*j))
            for i in range(3):
                for j in range(4):
                    ibm_qubit_coords.append((4*i+3, 4*j+2))

        return sorted(ibm_qubit_coords)
    
    # -----------------------------------------------------------------------
    # Plotting Methods
    # -----------------------------------------------------------------------

    def plot_lattice(self, scale=1.5, number_qubits=False, first_qubit=None, backend=None, filepath=None):
        
        """
        Plot the Heavy-Hex lattice structure.

        Args:
            scale: Scaling factor for figure size and node sizes.
            number_qubits: If True, display qubit indices on the plot.
            first_qubit: Index of the first qubit (for numbering).
            backend: IBM backend object or name to align numbering with hardware layout.
            filepath: If provided, saves the plot to this file path instead of displaying it.
        """

        plt.rc("font", family="serif")

        # Collect vertex coordinates
        vertex_x = np.array([v[1] for v in sorted(list(self.vertices.keys()))], dtype=int)
        vertex_y = np.array([self.max_y - v[0] for v in sorted(list(self.vertices.keys()))], dtype=int)
        
        # Collect edge endpoints (line segments)
        edges_endpoints_x = np.array([[np.floor(e[1]), np.ceil(e[1])] for e in sorted(list(self.edges.keys()))], dtype=int)
        edges_endpoints_y = np.array([[self.max_y - np.floor(e[0]), self.max_y - np.ceil(e[0])] for e in sorted(list(self.edges.keys()))], dtype=int)
        
        # Edge center positions (diamond markers)
        edges_boxes_x = np.mean(edges_endpoints_x, axis=1)
        edges_boxes_y = np.mean(edges_endpoints_y, axis=1)
        
        # Initialize figure
        fig, ax = plt.subplots(figsize=[scale*self.max_x, scale*self.max_y])
        ax.set_aspect('equal')

        # Draw edges
        for exs, eys in zip(edges_endpoints_x, edges_endpoints_y):
            plt.plot(exs, eys, color="black")

        # Draw vertices (circles)
        plt.scatter(vertex_x, vertex_y, 350*scale, marker="o", c="white", edgecolors="black", zorder=2)
        
        # Draw edges (squares)
        plt.scatter(edges_boxes_x, edges_boxes_y, 400*scale, marker=(4, 0, 45), c="white", edgecolors="black", zorder=2)
        
        mirror = False
        if number_qubits:
            # Define labels for qubits
            if backend is None:
                start = 0 if first_qubit is None else first_qubit
                labels = [str(start + i) for i in range(len(self.coords))]
            else:
                backend = backends_objs_to_names(backend)
                initial_layout = self.initial_qubit_layout(first_qubit, backend)
                labels = [str(qb) for qb in initial_layout]
                if initial_layout[1] < initial_layout[0]:
                    mirror = True

            # Offset text for visibility
            ttransform = mpl.transforms.Affine2D().translate(0, -1*scale)
            for i, (y, x) in enumerate(self.coords):
                text = plt.text(x, self.max_y - y, labels[i], horizontalalignment="center", verticalalignment="center", fontdict={"size": 5.5*scale})
                text.set_transform(text.get_transform() + ttransform)

        # Hide axis
        plt.axis("off")

        # Mirror x-axis if backend layout requires it
        if mirror:
            ax.invert_xaxis()

        # Tight layout
        plt.ylim([-0.2, self.max_y+0.2])
        plt.tight_layout()

        # Save or display
        if filepath is not None:
            plt.savefig(filepath, dpi=300, facecolor="none")
        plt.rcdefaults()


    def initial_qubit_layout(self, first_qubit=None, backend=None, reflex=None): 
        
        """
        Compute the mapping between the logical lattice qubits and the physical 
        IBM backend qubits for a given starting point.

        Parameters
        ----------
        first_qubit : int | None, optional
            Index of the first qubit in the IBM backend layout to align with 
            the lattice origin. If None, a default is chosen depending on backend.
        backend : str | None, optional
            Name of the IBM backend. If None, uses lattice coordinates directly.
        reflex : bool | None, optional
            Whether to reflect (mirror) the lattice when aligning to the backend. 
            If None, a reflection is chosen automatically based on backend layout.

        Returns
        -------
        np.ndarray
            An array mapping each lattice coordinate index to its corresponding 
            backend qubit index.

        Raises
        ------
        ValueError
            If the chosen `first_qubit` does not correspond to a valid IBM 
            backend origin.
        """

        # Extract backend name if backend object was passed
        backend = backends_objs_to_names(backend)

        # If no starting qubit index is provided, assign defaults depending on backend
        ibm_qubit_coords = []
        if first_qubit == None:
            if backend == 'ibm_fez' or backend == "ibm_marrakesh":
                first_qubit = 3
            else:
                first_qubit = 0

        # Get the physical qubit coordinates for the chosen backend
        if backend is not None:
            ibm_qubit_coords = HeavyHexLattice.get_backend_coordinates(backend)
        else:
            ibm_qubit_coords = self.coords

        
        ibm_qubit_coords = sorted(ibm_qubit_coords)

        # Select the origin qubit in backend coordinates
        ibm_origin = ibm_qubit_coords[first_qubit]

        # Check if origin is valid
        if (ibm_origin[0]+1, ibm_origin[1]) in ibm_qubit_coords:
            # If reflection is not specified, choose it automatically
            if reflex is None:
                if (ibm_origin[0]+2,ibm_origin[1]-2) not in ibm_qubit_coords:
                    reflex = True
                else:
                    reflex = False
            # Choose the logical lattice origin based on reflection
            if reflex:
                own_origin = self.coords[0]
                for c in self.coords:
                    if c[0] == 0 and c[1] > own_origin[1]:
                        own_origin = c
            else:
                own_origin = self.coords[0]

            # Build the mapping
            initial_qubit_layout = []
            for c in self.coords:
                offset = (int(2*(c[0]-own_origin[0])), int(2*(c[1]-own_origin[1])))
                if reflex:
                    offset = (offset[0],-offset[1])
                ibm_c = (ibm_origin[0]+offset[0],ibm_origin[1]+offset[1])
                initial_qubit_layout.append(ibm_qubit_coords.index(ibm_c))

            return np.array(initial_qubit_layout)
        
        else:
            raise ValueError("Invalid initial qubit")



    def plot_highlighted_qubits(self, qubits, scale=1.5, number_qubits=False, 
                                number_highlighted=True, colors=None, filepath=""):
        """
        Plot the lattice with selected qubits highlighted.

        Args:
            qubits: list of logical qubit indices to highlight (indices into self.coords)
            scale: figure scaling factor
            number_qubits: if True display all qubit indices
            number_highlighted: if True show labels for the highlighted qubits
            colors: optional list of colors (length == len(qubits))
            filepath: if provided, saves the figure to this path
        """
        def is_edge_coords(coords):
            """Return True if coords correspond to an edge (half-integer coordinates)."""
            if type(coords) == tuple:
                return (coords[0] % 1 != 0) or (coords[1] % 1 != 0)
            else:
                try:
                    coords = np.array(coords)
                    return ~np.equal(coords.sum(axis=1) % 1, 0)
                except np.AxisError:
                    raise np.AxisError("Coords is not a valid tuple or N x 2 array")
                
        plt.rc("font", family="serif")

        # Lattice plotting coordinates
        vertex_x = np.array([v[1] for v in sorted(list(self.vertices.keys()))], dtype=int)
        vertex_y = np.array([self.max_y - v[0] for v in sorted(list(self.vertices.keys()))], dtype=int)
        edges_endpoints_x = np.array([[np.floor(e[1]), np.ceil(e[1])] for e in sorted(list(self.edges.keys()))], dtype=int)
        edges_endpoints_y = np.array([[self.max_y - np.floor(e[0]), self.max_y - np.ceil(e[0])] for e in sorted(list(self.edges.keys()))], dtype=int)
        edges_boxes_x = np.mean(edges_endpoints_x, axis=1)
        edges_boxes_y = np.mean(edges_endpoints_y, axis=1)

        # Non-highlighted indices set
        non_highlighted_qubit_inds = list(set(range(len(self.coords))) - set(np.array(qubits).tolist()))
        
        # Map logical qubit indices to arrays-of-indices for plotting
        highlighted_nodes_inds = [np.where(np.equal(self.node_qbinds, qbind))[0][0] for qbind in qubits if not is_edge_coords(self.coords[qbind]) and len(np.where(np.equal(self.node_qbinds, qbind))) > 0]
        highlighted_edges_inds = [np.where(np.equal(self.edge_qbinds, qbind))[0][0] for qbind in qubits if is_edge_coords(self.coords[qbind]) and len(np.where(np.equal(self.edge_qbinds, qbind))) > 0]
        non_highlighted_nodes_inds = [np.where(np.equal(self.node_qbinds, qbind))[0][0] for qbind in non_highlighted_qubit_inds if not is_edge_coords(self.coords[qbind]) and len(np.where(np.equal(self.node_qbinds, qbind))) > 0]
        non_highlighted_edges_inds = [np.where(np.equal(self.edge_qbinds, qbind))[0][0] for qbind in non_highlighted_qubit_inds if is_edge_coords(self.coords[qbind]) and len(np.where(np.equal(self.edge_qbinds, qbind))) > 0]

        highlighted_nodes_color_inds = [i for i, qbind in enumerate(qubits) if not is_edge_coords(self.coords[qbind])]
        highlighted_edges_color_inds = [i for i, qbind in enumerate(qubits) if is_edge_coords(self.coords[qbind])]

        # Initialize figure and colors
        fig, ax = plt.subplots(figsize=[scale*self.max_x, scale*self.max_y])
        if colors is None:
            cmap = plt.get_cmap("Set2")
            colors = np.array([cmap((i/8)%8) for i in range(len(qubits))])
        else:
            colors = np.array(colors, dtype=object)
        ax.set_aspect('equal')

        # Draw edges
        for exs, eys in zip(edges_endpoints_x, edges_endpoints_y):
            plt.plot(exs, eys, color="black")

        # Highlighted and non-highlighted nodes
        plt.scatter(vertex_x[highlighted_nodes_inds], vertex_y[highlighted_nodes_inds], 350*scale, marker="o", c=colors[highlighted_nodes_color_inds], edgecolors="black", zorder=2)
        plt.scatter(vertex_x[non_highlighted_nodes_inds], vertex_y[non_highlighted_nodes_inds], 350*scale, marker="o", c="white", edgecolors="black", zorder=2)
        
        # Highlighted and non-highlighted edge markers (squares)
        plt.scatter(edges_boxes_x[highlighted_edges_inds], edges_boxes_y[highlighted_edges_inds], 400*scale, marker=(4, 0, 45), c=colors[highlighted_edges_color_inds], edgecolors="black", zorder=2)
        plt.scatter(edges_boxes_x[non_highlighted_edges_inds], edges_boxes_y[non_highlighted_edges_inds], 400*scale, marker=(4, 0, 45), c="white", edgecolors="black", zorder=2)
        
        ttransform = mpl.transforms.Affine2D().translate(0, -1*scale)
        if number_qubits:
            labels = [str(i) for i in range(len(self.coords))]
            for i, (y, x) in enumerate(self.coords):
                text = plt.text(x, self.max_y - y, labels[i], horizontalalignment="center", verticalalignment="center", fontdict={"size": 5.5*scale})
                text.set_transform(text.get_transform() + ttransform)
        else:
            for i, qbind in enumerate(qubits):
                y, x = self.coords[qbind]
                if number_highlighted:
                    textcolor = 'black'
                    text = plt.text(x, self.max_y - y, self.coords_to_logical_qb((y, x)), horizontalalignment="center", verticalalignment="center", fontdict={"size": 5.5*scale}, color=textcolor)
                    text.set_transform(text.get_transform() + ttransform)

        # Hide axes and set layout
        plt.axis("off")
        plt.ylim([-0.2, self.max_y+0.2])
        plt.tight_layout()

        # Save or display
        if filepath:
            plt.savefig(filepath, dpi=300, facecolor="none")
        plt.rcdefaults()

