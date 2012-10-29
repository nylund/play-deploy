import sys
import os

MODULE = 'deploy'

# Commands that are specific to your module

COMMANDS = ['deploy:hello', 'deploy:update', 'deploy:start', 'deploy:stop', 'deploy:restart']

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def getArg(args, findThis):
    for a in args:
        p = a.find('--' + findThis)
        if p == 0:
            return a[3 + len(findThis):]
    return None

def getParameters(app, args):
    host = app.readConf('deploy.default.host')
    path = app.readConf('deploy.default.path')
    port = app.readConf('deploy.default.port')
    login = app.readConf('deploy.default.login')
    excludes = app.readConf('deploy.default.excludes')
    play_path = app.readConf('deploy.default.play_path')

    instance = getArg(args, 'instance')
    if instance != None:
        host = app.readConf('deploy.' + instance + '.host')
        path = app.readConf('deploy.' + instance + '.path')
        port = app.readConf('deploy.' + instance + '.port')
        login = app.readConf('deploy.' + instance + '.login')
        excludes = app.readConf('deploy.' + instance + '.excludes')
        play_path = app.readConf('deploy.' + instance + '.play_path')

    if getArg(args, 'host') != None:
        host = getArg(args, 'host')
    if getArg(args, 'path') != None:
        path = getArg(args, 'path')
    if getArg(args, 'port') != None:
        port = getArg(args, 'port')
    if getArg(args, 'login') != None:
        login = getArg(args, 'login')
    if getArg(args, 'excludes') != None:
        excludes = getArg(args, 'excludes')
    if getArg(args, 'play_path') != None:
        play_path = getArg(args, 'play_path')

    if host == "":
        print "deploy: No host specified"
        sys.exit(-1) 
    if path == "":
        print "deploy: No path specified"
        sys.exit(-1) 
    if port == "":
        print "deploy: No port specified"
        sys.exit(-1) 
    if login == "":
        print "deploy: No login specified"
        sys.exit(-1) 
    if play_path == "":
        print "~ play_path not specified! Assuming that ./play exists in path on target host"
        play_path = "./play"

    cmd = login + "@" + host + ":" + path

    parameters = {}
    parameters["host"] = host
    parameters["path"] = path
    parameters["port"] = port 
    parameters["login"] = login
    parameters["excludes"] = excludes
    parameters["play_path"] = play_path
    parameters["cmd"] = cmd
    parameters["ssh"] = "ssh " + login + "@" + host

    return parameters


def cmdUpdate(app, args):
    parameters = getParameters(app, args)

    excludesList = ["server.pid", "application.log"]
    if parameters["excludes"] != "":
        excludesList.extend(parameters["excludes"].split(","))
    def excludePaths(path) : return "--exclude '" + path.strip() + "'"
    exclude = " ".join(map(excludePaths, excludesList))

    print "~ Updating files for " + parameters["cmd"] + ". port=" + parameters["port"]
    print "~ Skipping " + ", ".join(excludesList)

    return os.system("rsync -avzrc " + exclude + " " + app.path + " " + parameters["cmd"])

def cmdStart(app, args):
    parameters = getParameters(app, args)
    play_path = parameters["play_path"]

    remoteCmd = " \"cd " + parameters["path"] + ";"
    remoteCmd += "nice -n 19 " + play_path + " dependencies " + app.name() + ";"
    remoteCmd += "nice -n 19 " + play_path + " precompile " + app.name() + ";"
    #remoteCmd += "rm -f " + app.name() + "/server.pid;"
    remoteCmd += play_path + " start " + app.name() + " -Dprecompiled=true\""

    return os.system(parameters["ssh"] + remoteCmd)


def cmdStop(app, args):
    parameters = getParameters(app, args)
    play_path = parameters["play_path"]

    remoteCmd = " \"cd " + parameters["path"] + ";"
    remoteCmd += play_path + " stop " + app.name() + "\""

    return os.system(parameters["ssh"] + remoteCmd)


def cmdRestart(app, args):
    parameters = getParameters(app, args)
    play_path = parameters["play_path"]

    remoteCmd = " \"cd " + parameters["path"] + ";"
    remoteCmd += "nice -n 19 " + play_path + " precompile " + app.name() + ";"
    remoteCmd += play_path + " restart " + app.name() + " -Dprecompiled=true\""

    return os.system(parameters["ssh"] + remoteCmd)


def execute(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")

    if which("rsync") == None:
        print "~ rsync needed!"
        sys.exit(-1)
    
    if which("ssh") == None:
        print "~ ssh needed!"
        sys.exit(-1)

    if command == "deploy:hello":
        print "~ Hello"

    if command == "deploy:update":
        sys.exit(cmdUpdate(app, args))

    if command == "deploy:start":
        sys.exit(cmdStart(app, args))

    if command == "deploy:stop":
        sys.exit(cmdStop(app, args))

    if command == "deploy:restart":
        sys.exit(cmdRestart(app, args))

# This will be executed before any command (new, run...)
def before(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")


# This will be executed after any command (new, run...)
def after(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")

    if command == "new":
        pass
