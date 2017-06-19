# Pywatchdog
**Inotify** is a Linux kernel subsystem that provides a mechanism for monitoring filesystem events. It was merged into the Linux kernel mainline in the kernel version 2.6.13 released on August 28, 2005. 

**inotify-tools** is a set of command-line programs for Linux providing a simple interface to inotify and consists of two utilities:

* **inotifywait** simply blocks for inotify events, making it appropriate for use in shell scripts.

* **inotifywatch** collects filesystem usage statistics and outputs counts of each inotify event.

##### Pywatchdog is a simple python script that uses **inotifywait** for monitoring filesystem events from a python application in a easy way. #####

## Installation
```sh
$ apt-get install inotify-tools
```

The installation as pip package not available yet.

## Usage
```python
def run():
    watch_dog = FileSystemWatchDog(['/home/myuser/Documents/myfolder_01','/home/myuser/Documents/myfolder_02'])
    
    # It starts to monitoring the given paths
    watch_dog.release_the_watch_dog()
    input('Press to see the events...')
    
    # show the current caught events without stop it the monitoring task
    print(watch_dog.get_caught_dams())
    
    # it kills the process and subprocess released, otherwise they will be running until computer is turned off
    watch_dog.hold_on_to_the_watch_dog()

if __name__ == "__main__":
    run()

```

## Contributing

It could be great to get feedback and coding improvements from you! 
