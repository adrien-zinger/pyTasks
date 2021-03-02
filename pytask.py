import threading
import time
import sys


class task():

    class task_thread (threading.Thread):
        def __init__(self, fct, datas):
            threading.Thread.__init__(self)
            self.fct_list = [[fct, task.status.waiting]]
            self.task_killed = False
            self.running = True
            self.datas = datas
            self.error_raised = False
            self.catch = None

        def __del__(self):
            if self.error_raised and self.catch == None:
                print("task: Warning an exception may have not been treated")

        def run(self):
            while self.should_continue():
                self.exec_if()
            sys.exit()

        def should_continue(self):
            return self.running and (not self.task_killed or not self.get_next() == None)

        def exec_if(self):
            if not self.error_raised:
                fct_exec = self.get_next()
                if not fct_exec == None:
                    try:
                        self.datas = fct_exec[0](self.datas)
                        fct_exec[1] = task.status.done
                    except ValueError as err:
                        fct_exec[1] = task.status.failed
                        self.error_raised = True
                        self.datas = err
                    except:
                        fct_exec[1] = task.status.failed
                        self.error_raised = True
                if self.error_raised and not self.catch == None:
                    self.catch(self.datas)

        def get_next(self):
            for fct in self.fct_list:
                if fct[1] == task.status.waiting:
                    return fct
                if fct[1] == task.status.failed:
                    break
            return None

        def add_foo(self, fct):
            self.fct_list.append([fct, task.status.waiting])

    class status():
        failed = "Failed"
        waiting = "Waiting"
        done = "Done"

    def __init__(self, fct, datas = None):
        self.task_thread = task.task_thread(fct, datas)
        self.task_thread.start()

    def __del__(self):
        self.task_thread.task_killed = True

    def then(self, fct):
        self.task_thread.add_foo(fct)
        return self

    def catch(self, fct):
        self.task_thread.catch = fct
        return self

    def wait(self):
        self.task_thread.task_killed = True
        self.task_thread.join()

    def stop(self):
        self.task_thread.running = False
        self.task_thread.join()
