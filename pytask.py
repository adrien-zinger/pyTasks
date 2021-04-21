import threading
import time
import sys


class task():

    class func_iterator ():
        def __init__(self, data):
            self.func_list = []
            self.data = data
            self.error = None
        def add_func(self, func):
            self.func_list.append(func)
        def __iter__(self):
            self.index = 0
            return self
        def __next__(self):
            if self.error:
                return StopIteration
            try:
                if len(self.func_list) > 
                self.data = self.func_list[self.index](self.data)
                self.index = self.index + 1
            except ValueError as err:
                self.error  = err
            except:
                raise
    #Iterator
    class task_thread (threading.Thread):
        def __init__(self, fct, data):
            threading.Thread.__init__(self)
            self.fct_list = [[fct, task.status.waiting]]
            self.task_killed = False
            self.running = True
            self.data = data
            self.error_raised = False
            self.catch = None
            self.loop = False

        def __del__(self):
            if self.error_raised and self.catch == None:
                print("task: Warning an exception may have not been treated")

        def run(self):
            while self.should_continue():
                self.exec_if()

        def should_continue(self):
            return self.running and (not self.task_killed or not self.get_next() == None)

        def exec_if(self):
            if not self.error_raised:
                fct_exec = self.get_next()
                if not fct_exec == None:
                    try:
                        self.data = fct_exec[0](self.data)
                        if not isinstance(self.data, dict) or not 'repeat' in self.data or not self.data['repeat']:
                            fct_exec[1] = task.status.done
                        if self.loop and self.data == None:
                            self.running = False
                    except ValueError as err:
                        fct_exec[1] = task.status.failed
                        self.error_raised = True
                        self.data = err
                    except:
                        fct_exec[1] = task.status.failed
                        self.error_raised = True
                        self.data = sys.exc_info()[0]
                if self.error_raised and not self.catch == None:
                    print("call catch")
                    self.catch(self.data)

        def add_foo(self, fct):
            self.fct_list.append([fct, task.status.waiting])

    class status():
        failed = "Failed"
        waiting = "Waiting"
        done = "Done"

    def __init__(self, fct, data = None, loop=False):
        self.task_thread = task.task_thread(fct, data)
        self.task_thread.loop = loop
        self.task_thread.start()

    def __del__(self):
        if self.task_thread.loop:
            self.stop()
        else:
            self.task_thread.task_killed = True

    def then(self, fct):
        self.task_thread.add_foo(fct)
        return self

    def catch(self, fct):
        self.task_thread.catch = fct
        return self

    def wait(self):
        if self.task_thread.loop:
            self.stop()
        else:
            self.task_thread.task_killed = True
            self.task_thread.join()

    def stop(self):
        self.task_thread.running = False
        self.task_thread.join()

    _lock = {}
    @staticmethod
    def lock(key, do):
        if not key in task._lock:
            task._lock[key] = threading.Lock()
        with task._lock[key]:
            return do()
