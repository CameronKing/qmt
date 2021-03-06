#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from qmt.basic_tasks import GeometryTask
from qmt.ms_tasks import PoissonTask

geo_dict = {"part1": {"side length": 5.0}, "part2": {"side length": 10.0}}
geo_task = GeometryTask(options=geo_dict)


poisson_dict = {"part1": {"voltage": 2.0}, "part2": {"voltage": 1.0}}
poisson_task = PoissonTask(geo_task, options=poisson_dict)

poisson_task.run()
print(poisson_task.result)
