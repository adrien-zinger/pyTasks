import pytest
from task import Task
import asyncio
import threading

def test_run_coroutine():
    async def coro(resolve, reject):
        await asyncio.sleep(0.2)
        resolve("hello world")
    task = Task(coro)
    assert threading.active_count() is 2
    task.wait()
    assert task.data == "hello world"
    assert threading.active_count() is 1

def test_run_coroutine_reject():
    async def coro(resolve, reject):
        await asyncio.sleep(0.2)
        reject("bad hello world")
    task = Task(coro)
    assert threading.active_count() is 2
    task.wait()
    assert task.error == "bad hello world"
    assert threading.active_count() is 1

def test_run_coroutine_raise():
    async def coro(resolve, reject):
        raise Exception("exception world")
    task = Task(coro)
    task.wait()
    assert type(task.error) == Exception
    assert threading.active_count() is 1

def test_run_coroutine_raise2():
    async def coro(resolve, reject):
        raise ValueError("exception world")
    task = Task(coro)
    task.wait()
    assert type(task.error) == ValueError
    assert threading.active_count() is 1

def _test_force_manual_cancel_resolve():
    # This will dump a warning because of the never awaited call of coro execution
    async def coro(resolve, reject):
        await asyncio.sleep(1)
        resolve("2")
    task = Task(coro)
    assert threading.active_count() is 2
    task.cancel()
    task.resolve("hello world")
    task.wait()
    assert task.data == "hello world"
    assert threading.active_count() is 1

def test_resolve_with_data():
    task = Task()
    task.resolve("hello world")
    assert threading.active_count() is 1
    assert task.data == "hello world"

def test_resolve_with_coro():
    async def coro(resolve, reject):
        await asyncio.sleep(1)
        resolve("hello world")
    task = Task()
    task.resolve(Task(coro))
    assert threading.active_count() is 1
    assert task.data == "hello world"

def test_then(): #todo
    async def coro():
        print("will return")
        await asyncio.sleep(1)
        return "test then"
    task = Task()
    task2 = task.then(coro)
    assert threading.active_count() is 1
    task.resolve("go")
    assert threading.active_count() is 2
    task2.wait()
    assert threading.active_count() is 1
    assert task.data == None
    assert task2.data == "test then"
    assert not task is task2
