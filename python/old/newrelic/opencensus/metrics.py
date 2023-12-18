#!/usr/bin/env python

import random
import time

from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import view as view_module
from opencensus.stats import stats as stats_module
from opencensus.tags import tag_key as tag_key_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.tags import tag_value as tag_value_module

from ocnewrelic import NewRelicStatsExporter

stats_recorder = stats_module.stats.stats_recorder

float_measure = measure_module.MeasureFloat(
        "float_measure",
        "a measure that is a float",
        "ms",
)

key_status = tag_key_module.TagKey("status")
key_error = tag_key_module.TagKey("error")

count_view = view_module.View(
        "count_view",
        "The count view",
        [key_status, key_error],
        float_measure,
        aggregation_module.CountAggregation(),
)
last_value_view = view_module.View(
        "last_value_view",
        "The last value view",
        [key_status, key_error],
        float_measure,
        aggregation_module.LastValueAggregation(),
)
sum_view = view_module.View(
        "sum_view",
        "The sum view",
        [key_status, key_error],
        float_measure,
        aggregation_module.SumAggregation(),
)
distribution_view = view_module.View(
        "distribution_view",
        "The distribution view",
        [key_status, key_error],
        float_measure,
        aggregation_module.DistributionAggregation([0, 25, 50, 75, 100]),
)


def setup_opencensus():
    stats = stats_module.stats
    view_manager = stats.view_manager

    exporter = NewRelicStatsExporter(
            insert_key='4SqUr_n3qMzTjEnxwp_VG_Myl-m09tjG',
            host='staging-metric-api.newrelic.com',
    )

    view_manager.register_exporter(exporter)

    view_manager.register_view(count_view)
    view_manager.register_view(last_value_view)
    view_manager.register_view(sum_view)
    view_manager.register_view(distribution_view)


def record_stats(val_status, val_error):
    mmap = stats_recorder.new_measurement_map()
    mmap.measure_float_put(float_measure, random.random())

    tmap = tag_map_module.TagMap()
    tmap.insert(key_status, tag_value_module.TagValue(str(val_status)))
    tmap.insert(key_error, tag_value_module.TagValue(str(val_error)))

    mmap.record(tmap)


def main():
    setup_opencensus()

    while True:
        record_stats("OK", False)
        record_stats("OK", True)
        time.sleep(1)


if __name__ == "__main__":
    main()
