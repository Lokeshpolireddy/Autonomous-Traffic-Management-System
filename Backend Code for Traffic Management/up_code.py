import traci
import numpy as np
import csv
import matplotlib.pyplot as plt
import os

# Assumed fixed-duration wait time for conventional traffic lights
FIXED_LIGHT_WAIT_TIME = 40  # seconds (average estimated delay in a traditional system)

# Define results folder path
RESULTS_FOLDER = r"C:\Users\lokes\OneDrive\Desktop\Gearvit\Osm2files\results"

# Ensure the folder exists
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

def density_based_traffic_manager():
    """SUMO Traffic Manager that dynamically adjusts signals based on vehicle density and records efficiency metrics."""
    
    print("🚦 Starting SUMO Simulation...")

    try:
        # Start the SUMO simulation
        traci.start(["sumo-gui", "-c", "rjy_simulation.sumocfg"])
        
        MONITORING_RANGE = 10  # Monitoring distance in meters
        MAX_SIMULATION_STEPS = 100  # Set the max steps
        step = 0  # Step counter

        # Data collection
        vehicle_wait_times = {}  # Tracks waiting time for each vehicle
        lane_congestion = {}  # Stores congestion data per lane

        # Initialize real-time visualization
        plt.ion()  # Interactive mode ON

        while step < MAX_SIMULATION_STEPS - 1:  # Stop before last step
            if traci.simulation.getMinExpectedNumber() == 0:
                print("\n✅ SUMO reported no more vehicles. Stopping simulation early...")
                break

            traci.simulationStep()  # Advance the simulation by 1 second
            print(f"🔄 Step: {step}")  # Print step count in CMD
            step += 1

            # Track vehicle waiting times
            for veh_id in traci.vehicle.getIDList():
                wait_time = traci.vehicle.getWaitingTime(veh_id)
                vehicle_wait_times[veh_id] = wait_time

            for tl_id in traci.trafficlight.getIDList():  # Process each traffic light
                try:
                    # Retrieve traffic light program
                    program_logic = traci.trafficlight.getCompleteRedYellowGreenDefinition(tl_id)
                    if not program_logic:
                        continue

                    num_phases = len(program_logic[0].phases)
                    controlled_links = traci.trafficlight.getControlledLinks(tl_id)

                    if not controlled_links:
                        continue

                    # Monitor vehicle density per phase
                    lane_densities = {}
                    for i, link in enumerate(controlled_links):
                        if link:
                            lane_id = link[0][0]  # Extract the lane ID
                            vehicles = traci.lane.getLastStepVehicleIDs(lane_id)

                            # Count vehicles within the monitoring range
                            vehicle_count = sum(
                                1 for vehicle_id in vehicles if traci.vehicle.getLanePosition(vehicle_id) <= MONITORING_RANGE
                            )
                            lane_densities[i] = vehicle_count  # Map phase index to vehicle count

                            # Store congestion data
                            if lane_id not in lane_congestion:
                                lane_congestion[lane_id] = []
                            lane_congestion[lane_id].append(vehicle_count)

                    # Determine the phase with the highest density
                    max_phase_index = max(lane_densities, key=lane_densities.get, default=None)

                    if max_phase_index is not None and lane_densities[max_phase_index] > 0:
                        if 0 <= max_phase_index < num_phases:
                            traci.trafficlight.setPhase(tl_id, max_phase_index)

                except Exception as e:
                    print(f"⚠️ Error processing traffic light {tl_id}: {e}")

        print("\n📊 Generating Traffic Summary Before Ending Simulation...")
        generate_traffic_summary(vehicle_wait_times, lane_congestion)
        save_final_heatmap(lane_congestion)

    except traci.exceptions.TraCIException as e:
        print(f"\n❌ SUMO TraCI Exception: {e}")

    finally:
        # Ensure TraCI closes properly
        try:
            traci.close()
        except traci.exceptions.FatalTraCIError:
            print("⚠️ TraCI was already closed or not connected.")

        print("\n✅ SUMO Simulation Ended. All reports saved successfully!")

def save_final_heatmap(lane_congestion):
    """Save final congestion heatmap before simulation ends."""
    plt.clf()  # Clear previous figure
    lanes = list(lane_congestion.keys())
    congestion_levels = [np.mean(values) for values in lane_congestion.values()]

    # Plot final congestion heatmap
    plt.bar(lanes, congestion_levels, color='red')
    plt.xlabel("Lane ID")
    plt.ylabel("Average Number of Waiting Vehicles")
    plt.title("Final Traffic Congestion Heatmap")

    # Save to results folder
    heatmap_path = os.path.join(RESULTS_FOLDER, "congestion_heatmap.png")
    plt.savefig(heatmap_path)
    print(f"\n📊 Final congestion heatmap saved at: {heatmap_path}")

def generate_traffic_summary(vehicle_wait_times, lane_congestion):
    """Analyzes collected traffic data and generates insights."""
    
    total_vehicles = len(vehicle_wait_times)
    avg_wait_time = np.mean(list(vehicle_wait_times.values())) if vehicle_wait_times else 0
    max_wait_time = max(vehicle_wait_times.values(), default=0)

    # Calculate efficiency compared to conventional traffic lights
    efficiency_percentage = ((FIXED_LIGHT_WAIT_TIME - avg_wait_time) / FIXED_LIGHT_WAIT_TIME) * 100

    # Identify bottleneck lanes (top 3 congested lanes)
    bottleneck_lanes = sorted(lane_congestion.items(), key=lambda x: np.mean(x[1]), reverse=True)[:3]

    print("\n--- Traffic Efficiency Summary ---")
    print(f"Total Vehicles Processed: {total_vehicles}")
    print(f"Average Wait Time per Vehicle: {avg_wait_time:.2f} seconds")
    print(f"Maximum Wait Time: {max_wait_time:.2f} seconds")
    print(f"Efficiency Compared to Fixed Traffic Lights: {efficiency_percentage:.2f}% time saved")

    # Save to CSV in results folder
    csv_path = os.path.join(RESULTS_FOLDER, "traffic_summary.csv")
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        
        # Write header
        writer.writerow(["Metric", "Value"])
        
        # Write general stats
        writer.writerow(["Total Vehicles Processed", total_vehicles])
        writer.writerow(["Average Wait Time (seconds)", round(avg_wait_time, 2)])
        writer.writerow(["Maximum Wait Time (seconds)", round(max_wait_time, 2)])
        writer.writerow(["Efficiency (%)", round(efficiency_percentage, 2)])
        
        # Write bottleneck lanes
        writer.writerow([])
        writer.writerow(["Bottleneck Lanes", "Avg Vehicles Waiting"])
        for lane, congestion in bottleneck_lanes:
            writer.writerow([lane, round(np.mean(congestion), 2)])

    print(f"\n🚀 Traffic summary saved at: {csv_path}")

if __name__ == "__main__":
    density_based_traffic_manager()
