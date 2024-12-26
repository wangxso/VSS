import networkx as nx
import matplotlib.pyplot as plt
import random

class V2XNetwork:
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id  # 每辆车的唯一标识
        self.connections = {}

    def connect(self, target_id, vehicle_info, connection_type):
        """
        建立与目标车辆的连接 (车与车之间的连接)。
        """
        if target_id in self.connections:
            # print(f"已经与目标 {target_id} 建立了连接。")
            return False

        # 模拟建立连接的逻辑
        info = {}
        info['vehicle'] = vehicle_info
        info['connection_type'] = connection_type
        self.connections[target_id] = info
        # print(f"成功建立与目标 {target_id} 的 {connection_type} 连接。")
        return True

    def disconnect(self, target_id):
        """
        断开与目标车辆的连接。
        """
        if target_id not in self.connections:
            return False
        del self.connections[target_id]
        return True

    def merge_connections(self, other_network):
        """
        合并另一个车辆的连接字典到当前车辆的网络中。
        """
        self.connections.update(other_network.connections)
        return self.connections

    def get_connections(self):
        """
        获取当前车辆的连接字典。
        """
        return self.connections




    def visualize(self):
        """
        可视化当前所有连接的车辆网络图，节点和边的颜色都是随机的。
        """
        G = nx.Graph()

        # 添加节点和边，并包含连接类型（仅限车辆之间的连接）
        for target_id, connection_info in self.connections.items():
            conn_type = connection_info['connection_type']
            G.add_node(target_id)
            for other_target, other_connection_info in self.connections.items():
                if target_id != other_target:  # 避免自环
                    other_conn_type = other_connection_info['connection_type']
                    # 在这里为边添加连接类型作为属性
                    G.add_edge(target_id, other_target, connection_type=conn_type)

        # 使用固定布局确保节点位置的一致性
        pos = nx.spring_layout(G, seed=42)  # 使用固定的种子确保一致的节点位置

        # 创建边的标签，显示连接类型
        edge_labels = nx.get_edge_attributes(G, 'connection_type')


        # 随机化边的颜色（每条边一个随机颜色）
        # edge_color_list = [(random.random(), random.random(), random.random()) for _ in G.edges]
        edge_color_list = ['black' for _ in G.edges]

        # 随机化节点的颜色（每个节点一个随机颜色）
        # node_color_list = [(random.random(), random.random(), random.random()) for _ in G.nodes]
        node_color_list = ['lightblue' for _ in G.nodes]

        # 绘制图形，节点和边的颜色都使用随机颜色
        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color=node_color_list, font_size=10, font_weight='bold', edge_color=edge_color_list)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        # 添加额外的信息（车辆类型）
        node_labels = nx.get_node_attributes(G, 'info')
        vehicle_labels = {k: f"{v['vehicle_type']}" for k, v in node_labels.items()}

        nx.draw_networkx_labels(G, pos, labels=vehicle_labels, font_size=8, font_weight='normal', font_color='darkred')

        plt.title("V2X 车辆网络图")
        plt.show()




# 创建几十辆车和随机连接
vehicle_ids = [f"Vehicle_{i}" for i in range(1, 10)]
vehicle_types = ["car", "truck", "bus", "motorcycle", "van"]
connection_types = ["V2V", "V2I"]

# 创建网络实例
global_network = V2XNetwork("Global_Network")

# 随机生成连接
for vehicle_id in vehicle_ids:
    vehicle_network = V2XNetwork(vehicle_id)
    num_connections = random.randint(9,9)  # 每辆车有2到5个连接
    connections = random.sample(vehicle_ids, num_connections)  # 随机连接其他车辆
    for connection in connections:
        if connection != vehicle_id:  # 避免连接自己
            vehicle_type = random.choice(vehicle_types)
            connection_type = random.choice(connection_types)
            vehicle_network.connect(connection, {"vehicle_type": vehicle_type}, connection_type)

    # 合并到全局网络
    global_network.merge_connections(vehicle_network)

# 输出合并后的连接
print("合并后的连接：")
for vehicle, details in global_network.get_connections().items():
    print(f"{vehicle}: {details}")

# 可视化合并后的连接
global_network.visualize()
