import asyncio
from threading import Thread, Lock

class Task:
    class __AsyncLoop():
        def __init__(self):
            self.loop = asyncio.new_event_loop()
            self.start()
        def __run(self, loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        def start(self):
            self.__t = Thread(target=self.__run, args=(self.loop,))
            self.__t.start()
        def stop(self):
            if self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
                self.__t.join()
        def join(self):
            self.__t.join()
        def is_thread_alive(self):
            return self.__t.is_alive()

    def __init__(self, coro = None):
        self.data = None
        self.error = None
        self.__parent = None
        self.__cff = None
        self.__pending = None
        self.__pending_error = None
        self.__childs = []
        self.__lock = Lock()
        if coro != None:
            async def exec_coro(coro, resolve, reject):
                try:
                    await coro(resolve, reject)
                except Exception as err:
                    reject(err)
                finally:
                    self.__aloop.stop()
            self.__aloop = Task.__AsyncLoop()
            self.__cff = asyncio.run_coroutine_threadsafe(
                exec_coro(coro, self.resolve, self.reject),
                self.__aloop.loop)

    def __exec_pending(self):
        async def exec_coro(coro, coro_error, data, error):
            try:
                if error == None:
                    print("exec pending then")
                    resolve(await coro(data))
                elif coro_error != None:
                    await coro_error(error)
            except Exception as err:
                reject(err)
            finally:
                self.__aloop.stop()
        self.__aloop = Task.__AsyncLoop()
        self.__cff = asyncio.run_coroutine_threadsafe(
            exec_coro(self.__pending, self.__pending_error, self.data, self.error),
            self.__aloop.loop)

    def __ret_task(self, task):
        task.wait()
        self.data = task.data
        self.error = task.error

    def resolve(self, data = None):
        print(f"resolve{data}")
        self.__lock.acquire()
        if isinstance(data, Task):
            self.__ret_task(data)
        else: self.data = data
        for child in self.__childs:
            child.__exec_pending()
        self.__lock.release()

    def reject(self, error):
        self.__lock.acquire()
        if isinstance(error, Task):
            self.__ret_task(error)
        else: self.error = error
        for child in self.__childs:
            child.__exec_pending()
        # here can I loss an important error ? need to find a unit test
        self.__lock.release()

    def wait(self):
        if self.__parent != None:
            self.__parent.wait()
        if self.__aloop:
            self.__aloop.join()

    def then(self, coro, err_coro = None):
        print("push a then")
        ret = Task()
        ret.__parent = self
        ret.__pending = coro
        ret.__pending_error = err_coro
        self.__childs.append(ret)
        return ret

    def cancel(self):
        if self.__cff:
            self.__cff.cancel()
            try:
                self.__cff.result()
            except Exception:
                pass
            self.__aloop.stop()
