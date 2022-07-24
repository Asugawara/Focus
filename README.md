# Focus
**Focus** is a CLI tool to focus on your business by preventing you from viewing the website that breaks your concentration via `/etc/hosts`.<br/>
Good to use when you want to focus on a specific time.<br/>
It works well with Pomodoro.

# Installation
```bash
$ pip install -e git+ssh://git@github.com/Asugawara/Focus.git#egg=focus

# or
$ git clone git@github.com:Asugawara/Focus.git
$ cd Focus
$ pip install -e .
```

Add **Focus** bin directory to your PATH environment variable.
If you need to know **Focus** bin directory's location, you should use pip's `-v, --verbose` option.


# Usage
```bash
# forbid `instagram` and `youtube` for 10 seconds
$ sudo focus instagram.com youtube.com -t 10s

# forbid `instagram` and `youtube` for 25 minutes without countdown and logs
$ sudo focus instagram.com youtube.com -t 25m -q

# forbid all the time
$ sudo focus instagram.com youtube.com -n

# restore
$ sudo focus restore ${BACKUP_FILE_HASH}
```

# Versioning
This repo uses [Semantic Versioning](https://semver.org/).

# License
**Focus** is released under the MIT License. See [LICENSE](/LICENSE) for additional details.