import glob
import json
import networkx as nx

def load_problem(dirfn, printtxt=True):
    graphsfn = dirfn + "problem_graph_*.json"
    anglefn = dirfn + "angles.json"
    upperfn = dirfn + "upper_bounds.json"
    lowerfn = dirfn + "lower_bounds.json"
    
    if printtxt:
        print("loading", graphsfn)

    try:
        graphs = []
        num_graphs = len(glob.glob(graphsfn))
        for i in range(num_graphs):
            f = dirfn + f"problem_graph_{i}.json"
            
            graphs.append(nx.node_link_graph(json.load(open(f, 'r')), edges="links"))
        if len(graphs) != num_graphs:
            raise Exception

    except Exception as e:
        print("Wasn't able to load graphs from " + graphsfn + ", error:" + str(e))
        return None, None, None, None
    try:
        angles = json.load(open(anglefn, 'r'))
        if len(angles) == 0:
            raise Exception
    except Exception as e:
        print("Wasn't able to load QAOA angles from " + anglefn + ", error:" + str(e))
        return None, None, None, None
    try:
        upper = json.load(open(upperfn, 'r'))
        if len(upper) == 0:
            raise Exception
    except Exception as e:
        print("Wasn't able to load upper bounds from " + upperfn + ", error:" + str(e))
        return None, None, None, None

    try:
        lower = json.load(open(lowerfn, 'r'))
        if len(lower) == 0:
            raise Exception
    except Exception as e:
        print("Wasn't able to load lower bounds from " + lowerfn + ", error:" + str(e))
        return None, None, None, None
    return graphs, angles, upper, lower