# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""Local serial workflow execution
"""
import os

from .base import (PluginBase, logger, report_crash, report_nodes_not_run)
from ..utils import (nx, dfs_preorder, config)

class LinearPlugin(PluginBase):
    """Execute workflow in series
    """

    def run(self, graph, updatehash=False):
        """Executes a pre-defined pipeline in a serial order.

        Parameters
        ----------

        graph : networkx digraph
            defines order of execution          
        """

        if not isinstance(graph, nx.DiGraph):
            raise ValueError('Input must be a networkx digraph object')
        logger.info("Running serially.")
        old_wd = os.getcwd()
        notrun = []
        donotrun = []
        for node in nx.topological_sort(graph):
            try:
                if node in donotrun:
                    continue
                node.run(updatehash=updatehash)
            except:
                os.chdir(old_wd)
                if config.getboolean('execution', 'stop_on_first_crash'):
                    raise
                # bare except, but i really don't know where a
                # node might fail
                crashfile = report_crash(node)
                # remove dependencies from queue
                subnodes = [s for s in dfs_preorder(graph, node)]
                notrun.append(dict(node = node,
                                   dependents = subnodes,
                                   crashfile = crashfile))
                donotrun.extend(subnodes)
        report_nodes_not_run(notrun)

