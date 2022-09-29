def process_telmetery(queue):
    while not queue.empty():
        print ("[telmetry_processor] Process telemetry data")
        batch = queue.get_nowait()

        # Modify the below line to dispatch/send the telemetry data to the desired choice of observability tool.
        print(f"BATCH RECEIVED: {batch}", flush=True)
