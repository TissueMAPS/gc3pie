# test_workflow.py
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015, 2016 S3IT, Zentrale Informatik, University of Zurich
#
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 2 of the License, or (at your
#  option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

# stdlib imports
from cStringIO import StringIO
import os
import shutil
import tempfile
import re

# nose
from nose.tools import raises, assert_equal
try:
    from nose.tools import assert_is_instance
except ImportError:
    # Python 2.6 does not support assert_is_instance()
    def assert_is_instance(obj, cls):
        assert (isinstance(obj, cls))

# GC3Pie imports
from gc3libs import Run
from gc3libs.workflow import StagedTaskCollection, StopOnError

from helpers import SuccessfulApp, UnsuccessfulApp, temporary_core


def test_staged_task_collection_progress():
    class ThreeStageCollection(StagedTaskCollection):
        def stage0(self):
            return SuccessfulApp()
        def stage1(self):
            return SuccessfulApp()
        def stage2(self):
            return UnsuccessfulApp()

    with temporary_core() as core:
        coll = ThreeStageCollection()
        coll.attach(core)
        coll.submit()
        assert_equal(coll.execution.state, Run.State.SUBMITTED)

        # first task is successful
        while coll.tasks[0].execution.state != Run.State.TERMINATED:
            coll.progress()
        assert_equal(coll.execution.state, Run.State.SUBMITTED)
        #assert_equal(coll.execution.exitcode, 0)

        # second task is successful
        while coll.tasks[1].execution.state != Run.State.TERMINATED:
            coll.progress()
        #assert_equal(coll.execution.state, Run.State.RUNNING)
        #assert_equal(coll.execution.exitcode, 0)

        # third task is unsuccessful
        while coll.tasks[2].execution.state != Run.State.TERMINATED:
            coll.progress()
        assert_equal(coll.execution.state, Run.State.TERMINATED)
        assert_equal(coll.execution.exitcode, 1)
