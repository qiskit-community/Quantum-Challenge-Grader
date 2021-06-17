from ipywidgets import Output, HTML
from ipycytoscape import CytoscapeWidget
from IPython.display import display, clear_output
from networkx.algorithms.shortest_paths import unweighted
from plotly.subplots import make_subplots
from plotly import graph_objects as go
from copy import deepcopy
from typing import Optional, Tuple
import pandas as pd
import numpy as np
import networkx as nx


def weighted_graph(graph: nx.Graph, weight_range: Tuple[float,float]=(-1,1), integer_weights: bool = True, seed: Optional[int] = None) -> nx.Graph:
    '''
    Takes an unweighted input graph and returns a weighted graph where the weights are uniformly sampled at random
    Args:
        graph: Unweighted graph to add edge weights to
        weight_range: Range of weights to sample from
        integer_weights: Specifies whether weights should be integer (True) or float (False)
        seed: A seed for the random number generator
    Returns:
        The weighted graph
    '''
    if seed is not None:
        np.random.seed(seed)

    weighted_graph = deepcopy(graph)
    for edge in weighted_graph.edges:
        if integer_weights:
            weighted_graph[edge[0]][edge[1]]['weight'] = np.random.randint(int(weight_range[0]), int(weight_range[1]))
        else:
            weighted_graph[edge[0]][edge[1]]['weight'] = np.random.uniform(weight_range[0], weight_range[1])
    
    return weighted_graph

def display_maxcut_widget(graph: nx.Graph):
    '''
    Displays a MaxCut widget for a networkx graph
    Args:
        graph: The graph to display
    '''

    #Initialize Out widget for displaying cut value and cytoscape widget to display graph
    out= Output()
    cyto = CytoscapeWidget()
    cyto.graph.add_graph_from_networkx(graph)
    selected_ids = []

    def update(node):
        '''
        Update method to be called when anode is selected
        Args:
            node: Selected node from cytoscape widget
        '''

        #Update selected node IDs
        node_id = int(node['data']['id'])
        if node_id in selected_ids:
            selected_ids.remove(node_id)
        else:
            selected_ids.append(node_id)

        #Update style of graph accordingly
        #Base style to be applied to non-selected nodes and edges
        style = [
            {
                'selector': 'node',
                'css': {
                    'background-color': '#33B1FF'
                }
            },
            {
                'selector': 'edge',
                'css': {
                    'line-color': '#DFDFDF',
                    'label': 'data(weight)'
                }
            }
        ]

        #Update style for selected nodes
        for id in selected_ids:
            style.append(
                {
                    'selector': f'node[id = "{id}"]',
                    'css': {
                        'background-color':  '#002C9C'

                    }
                }
            )

        #Calculate cut weight and update style for edges in cut
        weight = 0
        for id_0 in range(graph.number_of_nodes()):
            for id_1 in range(graph.number_of_nodes()):
                if (id_0 in selected_ids and not id_1 in selected_ids) or (id_1 in selected_ids and not id_0 in selected_ids):
                    #Update edge style
                    style = style + [
                        {
                            'selector': f'edge[target = "{id_0}"][source = "{id_1}"]',
                            'css': {
                                'line-color': '#D12765'

                            }
                        },
                        {
                            'selector': f'edge[target = "{id_1}"][source = "{id_0}"]',
                            'css': {
                                'line-color': '#D12765'
                            }
                        }
                    ]
                    
                    #Update weight
                    try:
                        weight += 0.5*graph[id_0][id_1].get('weight',1.0)
                    except KeyError:
                        pass
        

        cyto.set_style(style)

        #Clear output and display new cut value
        with out:
            clear_output()
            display(HTML(value=f'<p style="font-size:20px"> Cut weight: {weight} </p>'))

    #Bind update method to click event and set base style
    cyto.on('node','click',update)
    cyto.on('edge','click',update)
    cyto.set_style([{
                        'selector': 'node',
                        'css': {
                            'background-color': '#33B1FF'
                        }
                    },
                    {
                        'selector': 'edge',
                        'css': {
                            'line-color': '#DFDFDF',
                            'label': 'data(weight)'
                        }
                    }
    ])

    #Display widget
    display(cyto)
    display(out)

def QAOA_widget(landscape_file, ax = None, xaxis_range = None, yaxis_range = None, trajectory={'beta_0': [], 'gamma_0':[], 'energy': []}, samples = None):
    '''
    Returns a figure showing 
        1) the energy landscape of a p=1 QAOA instance with the trajectory of an optimization process
        2) A line plot describing the evolution of the measured energy
        3) A bar plot of the final measurement samples 
    Args:
        landscape_file: csv file contanining landscape data
        ax: axes to plot on
        x_axis_range: x axis range of the QAOA landscape plot
        y_axis_range: y axis range of the QAOA landscape plot
        trajectory: Optimization trajectory given as a dictionary of lists for keys 'beta_0','gamma_0' and 'energy'
        samples: The samples of the final state
    Returns:
        Figure displaying QAOA instance and optimization process
    '''
    #Read data from landscape file
    df = pd.read_csv(landscape_file)
    #The landscape files contain negative energy values, so we need to adjust the sign
    df['energy'] = -df['energy']
    df = df.pivot(index='beta_0', columns='gamma_0', values='energy')
    matrix = df.to_numpy()
    beta_values = df.index.tolist()
    gamma_values = df.columns.tolist()

    #Create plot of energy surface
    surface_plot = go.Surface(
        x=gamma_values, 
        y=beta_values,
        z=matrix,
        coloraxis = 'coloraxis'
    )

    #Create trace for optimizer trajectory on energy landscape
    scatter_plot = go.Scatter3d(
        x=trajectory['gamma_0'], 
        y=trajectory['beta_0'], 
        #We add a small offset to the height of the trajectory points to make the trajectory more visible
        z=[ x + 0.05 for x in trajectory['energy']],
        marker=dict(
            size=4,
            color=trajectory['energy'],
            colorscale = 'GnBu'
        ),
        line=dict(
            color='darkblue',
            width=2
        )
    )  

    #Create line plot for plotting energy evolution
    line_plot = go.Scatter(
        x=list(range(len(trajectory['energy']))), 
        y=trajectory['energy'], 
        mode='lines+markers', 
        marker=dict(color=trajectory['energy'], coloraxis="coloraxis", size = 5),
        line = dict(color = 'darkblue')
    )

    #Create bar plot of final samples
    if samples is not None:
        samples = sorted(samples, key = lambda x: x.probability)
        probabilities = [sample.probability for sample in samples]
        values = [sample.fval for sample in samples]
        bitstrings = [''.join([str(int(i)) for i in sample.x]) for sample in samples]
        sample_plot = go.Bar(x = bitstrings, y = probabilities, marker=dict(color=values, coloraxis="coloraxis"))
    else:
        sample_plot = []

    #Create figure combining all plots into one
    fig = make_subplots(rows = 1, cols = 3, subplot_titles = ['QAOA Energy Landscape', 'Energy value', 'Final Samples'], column_widths=[0.5, 0.25,0.25], specs=[[{"type": "scatter3d"}, {"type": "scatter"}, {"type": "bar"}]])
    fig.update_layout(width=1800,height=600, coloraxis=dict(colorscale='plasma'), showlegend=False)
    fig.add_trace(surface_plot, row=1, col=1)
    fig.add_trace(scatter_plot, row=1, col=1)
    fig.add_trace(sample_plot, row=1, col=3)
    fig.add_trace(line_plot, row=1, col=2)
    fig.update_scenes(
        xaxis = 
        {
            'range': [0,4*np.pi]
        },
        yaxis =
        {
            'range': [0,np.pi]
        },
        xaxis_title =  '\u03b3',
        yaxis_title =  '\u03b2',
        aspectratio = 
        {
            'x':3,
            'y':1,
            'z':1
        },
        row = 1,
        col=1
    )
    fig.update_xaxes(title_text="Number of iterations", row=1, col=2)
    fig.update_xaxes(type="category", row=1, col=3)
    fig.update_yaxes(title_text="Measured Energy", row=1, col=2)
    fig.update_yaxes(title_text="Probability", row=1, col=3)

    return fig

unweighted_graphs = {
    'barbell': nx.barbell_graph(4,0),
    'circular_small': nx.cycle_graph(5),
    'circular_large': nx.cycle_graph(10),
    'fully_connected_small': nx.complete_graph(5),
    'fully_connected_large': nx.complete_graph(10)
}

graphs = {}
for graph_name, graph in unweighted_graphs.items():
    graphs[graph_name + '_unweighted'] = graph
    graphs[graph_name + '_float(-1_1)'] = weighted_graph(graph = graph, weight_range = (-1,1), integer_weights = False, seed = 42)
    graphs[graph_name + '_int(-5_5)'] =  weighted_graph(graph = graph, weight_range = (-5,5), integer_weights = True, seed = 42)
