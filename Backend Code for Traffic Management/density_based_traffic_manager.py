import traci

def density_based_traffic_manager():
    # Start the SUMO simulation
    traci.start(["sumo-gui", "-c", "rjy_simulation.sumocfg"])
    MONITORING_RANGE = 10  # Monitoring distance in meters

    while traci.simulation.getMinExpectedNumber() > 0:  # Run while vehicles are in the simulation
        traci.simulationStep()  # Advance the simulation by 1 second

        for tl_id in traci.trafficlight.getIDList():  # Process each traffic light
            # Retrieve traffic light program
            program_logic = traci.trafficlight.getCompleteRedYellowGreenDefinition(tl_id)
            if not program_logic:
                print(f"No program logic found for traffic light {tl_id}")
                continue

            num_phases = len(program_logic[0].phases)  # Number of valid phases
            print(f"Traffic light {tl_id} has {num_phases} phases")

            # Get controlled lanes
            controlled_links = traci.trafficlight.getControlledLinks(tl_id)
            if not controlled_links:
                print(f"No controlled links for traffic light {tl_id}")
                continue

            # Monitor vehicles near each lane
            lane_densities = {}
            for i, link in enumerate(controlled_links):
                if link:
                    lane_id = link[0][0]
                    vehicles = traci.lane.getLastStepVehicleIDs(lane_id)
                    vehicle_count = sum(
                        1 for vehicle_id in vehicles if traci.vehicle.getLanePosition(vehicle_id) <= MONITORING_RANGE
                    )
                    lane_densities[i] = vehicle_count  # Map phase index to vehicle count

            print(f"Lane densities for {tl_id}: {lane_densities}")

            # Determine the phase with the highest density
            max_phase_index = max(lane_densities, key=lane_densities.get, default=None)
            if max_phase_index is not None and lane_densities[max_phase_index] > 0:
                if 0 <= max_phase_index < num_phases:
                    traci.trafficlight.setPhase(tl_id, max_phase_index)
                    print(f"[{tl_id}] Green for phase {max_phase_index} with {lane_densities[max_phase_index]} vehicles")
                else:
                    print(f"[{tl_id}] Invalid phase index {max_phase_index}")
            else:
                print(f"[{tl_id}] No vehicles detected, keeping current phase")

    # Close the simulation
    traci.close()

if __name__ == "__main__":
    density_based_traffic_manager()
