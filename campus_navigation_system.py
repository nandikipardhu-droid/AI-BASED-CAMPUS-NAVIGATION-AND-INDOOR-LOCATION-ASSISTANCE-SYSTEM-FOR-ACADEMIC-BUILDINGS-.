"""
AI-Based Campus Navigation and Indoor Location Assistance System
Implements pathfinding, location tracking, and campus mapping
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, deque
import heapq
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class CampusNavigationSystem:
    def __init__(self):
        self.buildings = {}
        self.locations = {}
        self.graph = defaultdict(list)
        self.user_queries = []
        self.navigation_paths = []
        
    def generate_campus_data(self, n_buildings=25, n_locations=150):
        """Generate synthetic campus building and location data"""
        np.random.seed(42)
        
        # Generate buildings
        building_types = ['Academic', 'Laboratory', 'Administrative', 'Library', 'Cafeteria', 'Sports']
        building_names = [
            'Engineering Block', 'Science Building', 'Arts Complex', 'Medical Wing',
            'Computer Center', 'Physics Lab', 'Chemistry Lab', 'Biology Lab',
            'Main Library', 'Student Center', 'Administration Building', 'Auditorium',
            'Gymnasium', 'Cafeteria North', 'Cafeteria South', 'Parking A',
            'Parking B', 'Parking C', 'Hostel A', 'Hostel B', 'Hostel C',
            'Conference Hall', 'Seminar Room', 'Innovation Hub', 'Tech Park'
        ]
        
        for i in range(n_buildings):
            building_id = f'B{i+1:03d}'
            x = np.random.uniform(0, 1000)
            y = np.random.uniform(0, 800)
            building_type = np.random.choice(building_types)
            
            self.buildings[building_id] = {
                'name': building_names[i % len(building_names)],
                'type': building_type,
                'x': x,
                'y': y,
                'floors': np.random.randint(1, 6),
                'capacity': np.random.randint(100, 1000),
                'accessibility': np.random.choice([True, False], p=[0.7, 0.3])
            }
        
        # Generate locations within buildings
        location_types = ['Classroom', 'Laboratory', 'Office', 'Restroom', 'Cafeteria', 'Entrance', 'Elevator', 'Staircase']
        
        for i in range(n_locations):
            location_id = f'L{i+1:04d}'
            building_id = np.random.choice(list(self.buildings.keys()))
            building = self.buildings[building_id]
            
            # Add slight offset to building coordinates
            x = building['x'] + np.random.uniform(-50, 50)
            y = building['y'] + np.random.uniform(-50, 50)
            
            self.locations[location_id] = {
                'name': f'{location_types[i % len(location_types)]} {i+1}',
                'type': location_types[i % len(location_types)],
                'building': building_id,
                'floor': np.random.randint(1, building['floors'] + 1),
                'x': x,
                'y': y,
                'accessibility': np.random.choice([True, False], p=[0.6, 0.4])
            }
        
        # Build graph with connections
        location_list = list(self.locations.keys())
        for i, loc_id in enumerate(location_list):
            # Connect to nearby locations (within 150 units)
            for j, other_loc_id in enumerate(location_list):
                if i != j:
                    loc = self.locations[loc_id]
                    other_loc = self.locations[other_loc_id]
                    distance = np.sqrt((loc['x'] - other_loc['x'])**2 + (loc['y'] - other_loc['y'])**2)
                    
                    if distance < 150:
                        self.graph[loc_id].append((other_loc_id, distance))
        
        # Save data
        buildings_df = pd.DataFrame(self.buildings).T
        buildings_df.to_csv('/home/ubuntu/campus_buildings.csv')
        
        locations_df = pd.DataFrame(self.locations).T
        locations_df.to_csv('/home/ubuntu/campus_locations.csv')
        
        print(f"Generated campus data: {len(self.buildings)} buildings, {len(self.locations)} locations")
        return buildings_df, locations_df
    
    def dijkstra_shortest_path(self, start, end):
        """Find shortest path using Dijkstra's algorithm"""
        distances = {node: float('inf') for node in self.locations.keys()}
        distances[start] = 0
        previous = {node: None for node in self.locations.keys()}
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node == end:
                break
            
            for neighbor, weight in self.graph[current_node]:
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path, distances[end]
    
    def generate_user_queries(self, n_queries=500):
        """Generate synthetic user navigation queries"""
        location_list = list(self.locations.keys())
        
        for _ in range(n_queries):
            start = np.random.choice(location_list)
            end = np.random.choice(location_list)
            
            if start != end:
                path, distance = self.dijkstra_shortest_path(start, end)
                
                # Skip if no path found (disconnected graph)
                if distance == float('inf'):
                    continue
                
                query = {
                    'start': start,
                    'end': end,
                    'start_name': self.locations[start]['name'],
                    'end_name': self.locations[end]['name'],
                    'path_length': len(path),
                    'distance': round(distance, 2),
                    'time_minutes': round(distance / 1.4, 2)  # Assuming 1.4 units/minute walking speed
                }
                
                self.user_queries.append(query)
                self.navigation_paths.append(path)
        
        queries_df = pd.DataFrame(self.user_queries)
        queries_df.to_csv('/home/ubuntu/navigation_queries.csv', index=False)
        
        print(f"Generated {len(self.user_queries)} user navigation queries")
        return queries_df
    
    def generate_visualizations(self):
        """Generate comprehensive campus navigation visualizations"""
        
        # 1. Campus Map with Buildings and Locations
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Plot buildings
        for building_id, building in self.buildings.items():
            color = {'Academic': '#FF6B6B', 'Laboratory': '#4ECDC4', 'Administrative': '#45B7D1',
                    'Library': '#FFA07A', 'Cafeteria': '#98D8C8', 'Sports': '#F7DC6F'}.get(building['type'], '#95E1D3')
            ax.scatter(building['x'], building['y'], s=300, c=color, marker='s', alpha=0.7, edgecolors='black', linewidth=2)
            ax.text(building['x'], building['y'], building_id, ha='center', va='center', fontsize=8, fontweight='bold')
        
        # Plot locations
        for location_id, location in self.locations.items():
            ax.scatter(location['x'], location['y'], s=50, c='#2C3E50', marker='o', alpha=0.5)
        
        ax.set_xlabel('X Coordinate (meters)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y Coordinate (meters)', fontsize=12, fontweight='bold')
        ax.set_title('Campus Map with Buildings and Locations', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#FF6B6B', label='Academic'),
            Patch(facecolor='#4ECDC4', label='Laboratory'),
            Patch(facecolor='#45B7D1', label='Administrative'),
            Patch(facecolor='#FFA07A', label='Library'),
            Patch(facecolor='#98D8C8', label='Cafeteria'),
            Patch(facecolor='#F7DC6F', label='Sports')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/campus_map.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: campus_map.png")
        
        # 2. Building Type Distribution
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        building_types = [b['type'] for b in self.buildings.values()]
        type_counts = pd.Series(building_types).value_counts()
        
        axes[0].bar(type_counts.index, type_counts.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'][:len(type_counts)])
        axes[0].set_ylabel('Number of Buildings', fontsize=11, fontweight='bold')
        axes[0].set_title('Campus Building Type Distribution', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')
        for i, v in enumerate(type_counts.values):
            axes[0].text(i, v + 0.1, str(v), ha='center', fontweight='bold')
        
        # Building accessibility
        accessibility = [b['accessibility'] for b in self.buildings.values()]
        acc_counts = pd.Series(accessibility).value_counts()
        axes[1].pie(acc_counts.values, labels=['Accessible', 'Not Accessible'], autopct='%1.1f%%',
                   colors=['#2ecc71', '#e74c3c'], startangle=90)
        axes[1].set_title('Building Accessibility Status', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/campus_buildings_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: campus_buildings_analysis.png")
        
        # 3. Navigation Query Statistics
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        queries_df = pd.DataFrame(self.user_queries)
        
        # Path length distribution
        axes[0, 0].hist(queries_df['path_length'], bins=30, color='#4ECDC4', edgecolor='black')
        axes[0, 0].set_xlabel('Path Length (number of locations)', fontsize=11, fontweight='bold')
        axes[0, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
        axes[0, 0].set_title('Navigation Path Length Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Distance distribution
        axes[0, 1].hist(queries_df['distance'], bins=30, color='#45B7D1', edgecolor='black')
        axes[0, 1].set_xlabel('Distance (meters)', fontsize=11, fontweight='bold')
        axes[0, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
        axes[0, 1].set_title('Navigation Distance Distribution', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Time distribution
        axes[1, 0].hist(queries_df['time_minutes'], bins=30, color='#FFA07A', edgecolor='black')
        axes[1, 0].set_xlabel('Estimated Time (minutes)', fontsize=11, fontweight='bold')
        axes[1, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
        axes[1, 0].set_title('Navigation Time Distribution', fontsize=12, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Statistics summary
        axes[1, 1].axis('off')
        stats_text = f"""
NAVIGATION STATISTICS

Total Queries: {len(queries_df)}
Average Path Length: {queries_df['path_length'].mean():.2f} locations
Average Distance: {queries_df['distance'].mean():.2f} meters
Average Time: {queries_df['time_minutes'].mean():.2f} minutes

Min Distance: {queries_df['distance'].min():.2f} m
Max Distance: {queries_df['distance'].max():.2f} m
Min Time: {queries_df['time_minutes'].min():.2f} min
Max Time: {queries_df['time_minutes'].max():.2f} min
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                       family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/navigation_statistics.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: navigation_statistics.png")
        
        # 4. Location Type Distribution
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        location_types = [l['type'] for l in self.locations.values()]
        type_counts = pd.Series(location_types).value_counts()
        
        axes[0].barh(type_counts.index, type_counts.values, color='#45B7D1')
        axes[0].set_xlabel('Number of Locations', fontsize=11, fontweight='bold')
        axes[0].set_title('Campus Location Type Distribution', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='x')
        for i, v in enumerate(type_counts.values):
            axes[0].text(v + 0.5, i, str(v), va='center', fontweight='bold')
        
        # Location accessibility
        accessibility = [l['accessibility'] for l in self.locations.values()]
        acc_counts = pd.Series(accessibility).value_counts()
        axes[1].pie(acc_counts.values, labels=['Accessible', 'Not Accessible'], autopct='%1.1f%%',
                   colors=['#2ecc71', '#e74c3c'], startangle=90)
        axes[1].set_title('Location Accessibility Status', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/campus_locations_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: campus_locations_analysis.png")
        
        # 5. Sample Navigation Path Visualization
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Plot all buildings
        for building_id, building in self.buildings.items():
            color = {'Academic': '#FF6B6B', 'Laboratory': '#4ECDC4', 'Administrative': '#45B7D1',
                    'Library': '#FFA07A', 'Cafeteria': '#98D8C8', 'Sports': '#F7DC6F'}.get(building['type'], '#95E1D3')
            ax.scatter(building['x'], building['y'], s=300, c=color, marker='s', alpha=0.7, edgecolors='black', linewidth=2)
        
        # Plot sample path
        if len(self.navigation_paths) > 0:
            sample_path = self.navigation_paths[0]
            path_coords = [self.locations[loc_id] for loc_id in sample_path]
            path_x = [loc['x'] for loc in path_coords]
            path_y = [loc['y'] for loc in path_coords]
            
            ax.plot(path_x, path_y, 'r-', linewidth=2, alpha=0.7, label='Navigation Path')
            ax.scatter(path_x[0], path_y[0], s=200, c='green', marker='o', edgecolors='black', linewidth=2, label='Start')
            ax.scatter(path_x[-1], path_y[-1], s=200, c='red', marker='X', edgecolors='black', linewidth=2, label='End')
        
        ax.set_xlabel('X Coordinate (meters)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y Coordinate (meters)', fontsize=12, fontweight='bold')
        ax.set_title('Sample Campus Navigation Path', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/sample_navigation_path.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: sample_navigation_path.png")

def main():
    print("="*80)
    print("AI-BASED CAMPUS NAVIGATION AND INDOOR LOCATION ASSISTANCE SYSTEM")
    print("="*80)
    
    print("\n[1] Initializing campus navigation system...")
    system = CampusNavigationSystem()
    
    print("\n[2] Generating campus data...")
    buildings_df, locations_df = system.generate_campus_data(n_buildings=25, n_locations=150)
    
    print("\n[3] Generating user navigation queries...")
    queries_df = system.generate_user_queries(n_queries=500)
    
    print("\n[4] Generating visualizations...")
    system.generate_visualizations()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - All files generated successfully")
    print("="*80)

if __name__ == "__main__":
    main()
