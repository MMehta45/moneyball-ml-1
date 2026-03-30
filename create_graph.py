import networkx as nx

dummy_data = {
    "CS1336": {"name": "Intro to CS", "credit_hours":3, "prereqs": [], "is_transferable": False, "availability": ["Fall", "Spring"], "difficulty": 0.5, "expected_gpa": 3.1},
    "CS1337": {"name": "Computer Science I","credit_hours":3, "prereqs": ["CS1336"], "is_transferable": False, "availability": ["Fall", "Spring"],"difficulty": 0.8, "expected_gpa": 3.1},
    "CS2336": {"name": "Computer Science II", "credit_hours":3,"prereqs": ["CS1337"], "is_transferable": False,"availability": ["Fall", "Spring"],"difficulty": 0.9, "expected_gpa": 3.1},
    "ARTS1301": {"name": "Art Appreciation","credit_hours":3, "prereqs": [], "is_transferable": False, "availability": ["Fall", "Spring"],"difficulty": 0.2, "expected_gpa": 3.1}
}
def create_graph(data):
    degree_flow = nx.DiGraph()
    for course in data:
        info = data[course]
        degree_flow.add_node(course, name=info['name'], credit_hours=info['credit_hours'], is_transferable=info['is_transferable'],difficulty=info['difficulty'], expected_gpa=info["expected_gpa"])        
        for prereq_course in info["prereqs"]:
           degree_flow.add_edge(prereq_course, course)
    return degree_flow
           

