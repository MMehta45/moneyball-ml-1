import networkx as nx
import matplotlib.pyplot as plt

dummy_data = {
    "CS1336": {"name": "Intro to CS", "prereqs": [], "difficulty": 0.5},
    "CS1337": {"name": "Computer Science I", "prereqs": ["CS1336"], "difficulty": 0.8},
    "CS2336": {"name": "Computer Science II", "prereqs": ["CS1337"], "difficulty": 0.9},
    "ARTS1301": {"name": "Art Appreciation", "prereqs": [], "difficulty": 0.2}
}

def create_graph(data):
    degree_flow = nx.DiGraph()
    for course in data:
        info = data[course]
        degree_flow.add_node(course, name=info['name'], difficulty=info['difficulty'])        
        for prereq_course in info["prereqs"]:
           degree_flow.add_edge(prereq_course, course)
    return degree_flow
           

sample_graph = create_graph(dummy_data)

position = nx.spring_layout(sample_graph)
nx.draw_networkx_nodes(sample_graph, position, node_color='lightblue', node_size=2000)
nx.draw_networkx_edges(sample_graph, position, arrowstyle='->', arrowsize=20)
nx.draw_networkx_labels(sample_graph, position, font_size=10, font_weight='bold')

plt.title("Degree Plan Graph")
plt.axis('off')
plt.show()


