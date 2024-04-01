def find_port_numbers(router_list, router_names):
    port_numbers = []
    for router in router_list:
        if router["router-name"] in router_names:
            port_numbers.append(router["server-port"])
    return port_numbers

router_initial = [
    {
        "router-name": "A",
        "link": ["B", "C"],
        "cost-link": [1, 1],
        "server-port": 1024,
        "con-network": ["192.168.4.0/24", "192.168.4.1/24"]
    },
    {
        "router-name": "B",
        "link": ["A", "D", "C"],
        "cost-link": [1, 1, 1],
        "server-port": 1025,
        "con-network": ["192.168.2.0/24"]
    },
    {
        "router-name": "C",
        "link": ["B", "F"],
        "cost-link": [1, 1],
        "server-port": 1026,
        "con-network": ["192.168.3.0/24"]
    }
]

router_names = ['B', 'C']
port_numbers = find_port_numbers(router_initial, router_names)
print("Port numbers for routers", router_names, "are:", port_numbers)
