# Pytask

This python project is for anybody who wants to do asynchronous tasks with an easy format. This is clearly inspired by the system of *Promise* in JS. There are not all the Promise functionalities and the realisation is not the same but you will find some similarities in the usage.

## Why using it

Ok now you want to create an asynch task for some reason. You may want to call an API, to execute a program in background or to divide your algorythm. All reasons are goods.

But we are using python so you have to create a thread or use an other better library (of course you should). Then, you want to execute your task... So, you're asking yourself "how do I know when it ends? Callback!... hmm ok how can I do that..."

And you are just a beginner in python and the following syntax is good enough for you.

## How to use it

Simply use this folder as a thirdpartie.

## Run the tests

Install pipenv with python 3.8.2 then..

```bash
python -m pip install pipenv
pipenv shell
pipenv install -d
python -m pytest
```

### The basic
```python
#Declare the functions that will be executed asynchronously
def call_something():
    return "the result (can be any objects)"
def receive_the_response(data):
    print(data)
    return ['ok', 'not ok']
def finaly_do_this(data):
    print(data) # will print -> ['ok', 'not ok']

#Run tasks asynchrnously
task(lambda data: call_something()
).then(lambda data: receive_the_response(data)
).then(lambda data: finaly_do_this(data))

#continue the main thread
```

The output
```python
the result (can be any objects)
['ok', 'not ok']
```

### Catch exeption

Of course you want to do something in case an error occurs

```python
def call_something():
    raise ValueError("oups I can't do that")
def receive_the_response(data):
    print(data)
    return ['ok', 'not ok']
def finaly_do_this(data):
    print(data) # will print -> ['ok', 'not ok']
def error_raised(err):
    print(err)
#Run tasks asynchrnously
task(lambda data: call_something()
).then(lambda data: receive_the_response(data)
).then(lambda data: finaly_do_this(data)
).catch(lambda err: error_raised(err))

#continue the main thread
```
The output
```
oups I can't do that
```

Two things :
 - While the tasks are running well we don't stop the thread.
 - If the thread cought an error without a *catch* function assigned before the destruction of the task object, it will dump a warning

### Wait

You want to work with asynch tasks and eventually, you also want to wait for a response or being sure that everything has been done, call the *wait* function !

```python
t = task(lambda data: call_something()
).then(lambda data: receive_the_response(data)
).then(lambda data: finaly_do_this(data)

doing_something_else()

t.wait()

continue_my_script()
```

### Delete the task object

There is no *auto-delete* in the task thread. You have to delete the object yourself if you keep it in a global variable. If you don't delete it, your program will continue to process with the task thread.

So don't do this:

```python
my_beautifull_task = task(lambda data: call_something()
).then(lambda data: receive_the_response(data)
).then(lambda data: finaly_do_this(data).wait()

#End of file... what ? why my script are still alive.... hoooooo yes I have to delete the task

del(my_beautifull_task)
# or my_beautifull_task.wait()
#End of file.... finally true !
```

### Stop all

You can stop the task with the *stop* function

```python
my_beautifull_task = task(lambda data: call_something()
).then(lambda data: receive_the_response(data)
).then(lambda data: finaly_do_this(data).wait()

my_beautifull_task.stop() # will stop the execution after the end of the current task 
```

### Multi-threading

You can eventually use statics data or globals depending of your needs. But I highly recommand you to give a lot of attention in case you want to do it to avoid any problem.
Dont forget that the data are used by multiple threads. Please use *thread safe* objects as Queue if you really need to share objects.

Here is an example of loading some wikipedia's pages and writing those in the local storage:

```python
from pytask import task
from urllib import request
import os

def create_file():
    i = 0
    while os.path.exists(f'writing_siteweb{i}.html'):
        i += 1
    open(f'writing_siteweb{i}.html', 'w').close()
    return f'writing_siteweb{i}.html'

def write_in_local(resp):
    filename = task.lock("creating a file", lambda: create_file())
    with open(filename, 'wb') as f:
        f.write(resp)

website_list = [
    "https://www.wikipedia.org/",
    "https://nl.wikipedia.org/",
    "https://fr.wikipedia.org/",
    "https://de.wikipedia.org/",
    "https://ru.wikipedia.org/",
    "https://it.wikipedia.org/"
]

for _url in website_list:
    task(lambda url: request.urlopen(url).read(), _url
    ).then(lambda resp: write_in_local(resp)
    ).catch(lambda data: print("oups"))
```

#### Lock your access

If you are ok with the concept of locking in threads, you don't really need to use the static method **lock**. When you see you'll need to access a component that is not thread safe, you have to lock your variables. You can see what the lock function does, this is very simple. I encourage you to understand how to do it without my lock method.

Although, I'm going to tell you how it works.

```python
task.lock(key, lambda: do_it())
```

The key, this is the lock key that the current thread will take if he needs to do something solo. If the current thread has the key, the others need to wait the release.

The lambda is the function that will be executed solo by the current thread.

You can call this method in every thread, even the main one.

#### Create an observer

In the previous example, we have seen how to load websites. Now you probably want to wait for an input? Or to observe a variable? Here is an example of an observer.

```python
from pytask import task
from queue import Queue
from urllib import request
import os
import time

def create_file():
    i = 0
    while os.path.exists(f'writing_siteweb{i}.html'):
        i += 1
    open(f'writing_siteweb{i}.html', 'w').close()
    return f'writing_siteweb{i}.html'

def write_in_local(resp):
    filename = task.lock("creating a file", lambda: create_file())
    with open(filename, 'wb') as f:
        f.write(resp)

def create_downloader_task(_url):
    task(lambda url: request.urlopen(url).read(), _url
    ).then(lambda resp: write_in_local(resp)
    ).catch(lambda err: print(f"error: failed to load {url}"))
    return True

website_queue = Queue()

observer = task(lambda data: website_queue.get(), loop = True
).then(lambda url: create_downloader_task(url))

time.sleep(1)
website_queue.put("https://www.wikipedia.org/")
website_queue.put("https://fr.wikipedia.org/")
time.sleep(1)
website_queue.put(None)
observer.stop()
```

You can see there is a new parameter in the constructor, **loop = True**.
This means the task will loop while lambdas return something. You can eventually stop the observer manually, but in this case we are using a Queue object and its **get** method. As you know, this method will wait until the **get** finds something, and, I need to feed the website_queue with *None* to close my observer. For the same reason the function **create_downloader_task** returns a True value, otherwise the observer will stop itself.
