import os as _os

import six as _six
from pyspark import SparkConf, SparkContext

from flytekit.common.types.helpers import \
    pack_python_std_map_to_literal_map as _packer
from flytekit.contrib.notebook.supported_types import \
    notebook_types_map as _notebook_types_map


def record_outputs(outputs=None):
    """
    Converts/Records outputs generated by users in their Notebook as Flyte Types.
    """
    if outputs is None:
        return _packer({}, {})
    tm = {}
    for k, v in _six.iteritems(outputs):
        t = type(v)
        if t not in _notebook_types_map:
            raise ValueError(
                "Currently only primitive types {} are supported for recording from notebook".format(
                    _notebook_types_map
                )
            )
        tm[k] = _notebook_types_map[t]
    return _packer(outputs, tm).to_flyte_idl()


# TODO: Support Client Mode
def get_spark_context(spark_conf):
    """
       outputs: SparkContext
       Returns appropriate SparkContext based on whether invoked via a Notebook or a Flyte workflow.
    """
    # We run in cluster-mode in Flyte.
    # Ref https://github.com/lyft/flyteplugins/blob/master/go/tasks/v1/flytek8s/k8s_resource_adds.go#L46
    if "FLYTE_INTERNAL_EXECUTION_ID" in _os.environ:
        return SparkContext()

    # Add system spark-conf for local/notebook based execution.
    spark_conf.add(("spark.master", "local"))
    conf = SparkConf().setAll(spark_conf)
    return SparkContext(conf=conf)
