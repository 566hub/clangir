"""
Test that breakpoint works correctly in the presence of dead-code stripping.
"""

import os, time
import unittest2
import lldb
from lldbtest import *
import lldbutil

class DeadStripTestCase(TestBase):

    mydir = TestBase.compute_mydir(__file__)

    @expectedFailureWindows("llvm.org/pr24778")
    @skipIfFreeBSD # The -dead_strip linker option isn't supported on FreeBSD versions of ld.
    def test(self):
        """Test breakpoint works correctly with dead-code stripping."""
        self.build()
        exe = os.path.join(os.getcwd(), "a.out")
        self.runCmd("file " + exe, CURRENT_EXECUTABLE_SET)

        # Break by function name f1 (live code).
        lldbutil.run_break_set_by_symbol (self, "f1", num_expected_locations=1, module_name="a.out")

        # Break by function name f2 (dead code).
        lldbutil.run_break_set_by_symbol (self, "f2", num_expected_locations=0, module_name="a.out")

        # Break by function name f3 (live code).
        lldbutil.run_break_set_by_symbol (self, "f3", num_expected_locations=1, module_name="a.out")

        self.runCmd("run", RUN_SUCCEEDED)

        # The stop reason of the thread should be breakpoint (breakpoint #1).
        self.expect("thread list", STOPPED_DUE_TO_BREAKPOINT,
            substrs = ['stopped',
                       'a.out`f1',
                       'stop reason = breakpoint'])

        # The breakpoint should have a hit count of 1.
        self.expect("breakpoint list -f 1", BREAKPOINT_HIT_ONCE,
            substrs = [' resolved, hit count = 1'])

        self.runCmd("continue")

        # The stop reason of the thread should be breakpoint (breakpoint #3).
        self.expect("thread list", STOPPED_DUE_TO_BREAKPOINT,
            substrs = ['stopped',
                       'a.out`f3',
                       'stop reason = breakpoint'])

        # The breakpoint should have a hit count of 1.
        self.expect("breakpoint list -f 3", BREAKPOINT_HIT_ONCE,
            substrs = [' resolved, hit count = 1'])


if __name__ == '__main__':
    import atexit
    lldb.SBDebugger.Initialize()
    atexit.register(lambda: lldb.SBDebugger.Terminate())
    unittest2.main()
