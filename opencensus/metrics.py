#!/usr/bin/env python

import sys
import time

from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import view as view_module
from opencensus.stats import stats as stats_module
from opencensus.tags import tag_key as tag_key_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.tags import tag_value as tag_value_module

from ocnewrelic import NewRelicStatsExporter

# Create the measures
# The latency in milliseconds
m_latency_ms = measure_module.MeasureFloat("repl_latency", "The latency in milliseconds per REPL loop", "ms")

# Counts/groups the lengths of lines read in.
m_line_lengths = measure_module.MeasureInt("repl_line_lengths", "The distribution of line lengths", "By")

# The stats recorder
stats_recorder = stats_module.stats.stats_recorder

# Create the tag key
key_method = tag_key_module.TagKey("method")
# Create the status key
key_status = tag_key_module.TagKey("status")
# Create the error key
key_error = tag_key_module.TagKey("error")

latency_view = view_module.View("demo_latency", "The distribution of the latencies",
    [key_method, key_status, key_error],
    m_latency_ms,
    # Latency in buckets:
    # [>=0ms, >=25ms, >=50ms, >=75ms, >=100ms, >=200ms, >=400ms, >=600ms, >=800ms, >=1s, >=2s, >=4s, >=6s]
    aggregation_module.DistributionAggregation([0, 25, 50, 75, 100, 200, 400, 600, 800, 1000, 2000, 4000, 6000]))

line_count_view = view_module.View("demo_lines_in", "The number of lines from standard input",
    [key_method, key_status, key_error],
    m_line_lengths,
    aggregation_module.CountAggregation())

line_length_view = view_module.View("demo_line_lengths", "Groups the lengths of keys in buckets",
    [key_method, key_status, key_error],
    m_line_lengths,
    # Lengths: [>=0B, >=5B, >=10B, >=15B, >=20B, >=40B, >=60B, >=80, >=100B, >=200B, >=400, >=600, >=800, >=1000]
    aggregation_module.DistributionAggregation([0, 5, 10, 15, 20, 40, 60, 80, 100, 200, 400, 600, 800, 1000]))

def main():
    # In a REPL:
    # 1. Read input
    # 2. process input
    setupOpenCensusAndPrometheusExporter()

    while True:
        readEvaluateProcessLine()


def registerAllViews(view_manager):
    view_manager.register_view(latency_view)
    view_manager.register_view(line_count_view)
    view_manager.register_view(line_length_view)


def setupOpenCensusAndPrometheusExporter():
    stats = stats_module.stats
    view_manager = stats.view_manager

    exporter = NewRelicStatsExporter(
            insert_key='4SqUr_n3qMzTjEnxwp_VG_Myl-m09tjG',
            host='staging-metric-api.newrelic.com',
    )

    view_manager.register_exporter(exporter)
    registerAllViews(view_manager)


def readEvaluateProcessLine():
    line = sys.stdin.readline()
    start = time.time()
    print(line.upper())

    # Now record the stats
    # Create the measure_map into which we'll insert the measurements
    mmap = stats_recorder.new_measurement_map()
    end_ms = (time.time() - start) * 1000.0 # Seconds to milliseconds

    # Record the latency
    mmap.measure_float_put(m_latency_ms, end_ms)

    # Record the line length
    mmap.measure_int_put(m_line_lengths, len(line))

    tmap = tag_map_module.TagMap()
    tmap.insert(key_method, tag_value_module.TagValue("repl"))
    tmap.insert(key_status, tag_value_module.TagValue("OK"))

    # Insert the tag map finally
    mmap.record(tmap)

if __name__ == "__main__":
    main()
