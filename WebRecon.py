#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pip
import pip._internal
import importlib
import datetime
import json

# get config
from conf.config import *

# check pid file
pidPath = "./run.pid"
if os.path.isfile(pidPath):
	print(R + '[-]' + C + ' One instance of WebRecon is already running!' + W)
	with open(pidPath, 'r') as pidfile:
		pid = pidfile.read()
	print(G + '[+]' + C + ' PID : ' + W + str(pid))
	print(G + '[>]' + C + ' If WebRecon crashed, execute : ' + W + 'rm {}'.format(pidPath))
	sys.exit()
else:
	os.makedirs(os.path.dirname(pidPath), exist_ok=True)
	with open(pidPath, 'w') as pidfile:
		pidfile.write(str(os.getpid()))

# get required modules
with open('./requirements.txt', 'r') as f:
    pkgList = f.readlines()
    pkgList = [x.strip() for x in pkgList]
# install required modules
def install(package_name):
    if hasattr(pip, 'main'):
        pip.main(['install', package_name])
    else:
        pip._internal.main(['install', package_name])
# install nessessary modules
print(G + '[+]' + C + ' Installing required packages...' + W)
for pkg in pkgList:
    spec = importlib.util.find_spec(pkg)
    if spec is None:
        print(R + '[-]' + C + ' Package {} not found!'.format(pkg) + W)
        install(pkg)
        print(G + '[+]' + C + ' Package {} installed!'.format(pkg) + W)
print(G + '[+]' + C + ' Required packages installed!' + W)        

# get modules(tools)
moduleDir =  os.listdir("./modules")
moduleList = [module.split(".")[0] for module in moduleDir]
# remove not used modules(tools)
for fileName in ignoreFiles:
    if fileName.split(".")[0] in moduleList:
    	moduleList.remove(fileName.split(".")[0])
moduleName = ""
module = None

# conmmands
firstLevelCommands = {
	"help": "Print this help",
	"modules": "List all available modules",
	"use": "Use a module",
	"exit": "Exit WebRecon"
}
secondLevelCommands = {
	"help": "Print this help",
	"show": "Show module information",
	"set": "Set module options",
	"run": "Run module",
	"exit": "Exit module"
}
commands = {
	1: firstLevelCommands,
	2: secondLevelCommands
}
level = 1

# tab completion
import readline
lastCommand = ""
def complete(text, state):
	global level, lastCommand
	line = readline.get_line_buffer().split(" ")
	line = [x for x in line if x != ""]
	lastCommand = line[0]
	if "use" == lastCommand:
		return [x for x in moduleList if x.startswith(text)][state]
	elif "set" == lastCommand:
		return [x for x in module.options.keys() if x.startswith(text)][state]
	else:
		return [x for x in commands[level].keys() if x.startswith(text.strip())][state]
readline.set_completer(complete)
readline.parse_and_bind("tab: complete")

# print help
def printHelp(level):
	printCommands = commands[level]
	for cmd in printCommands:
		print(G + '[+]' + C + ' ' + cmd + ':\t' + W + printCommands[cmd])
	print("")

# print modules(tools)
def modules(args):
	print(G + '[>]' + C + ' Available modules : ' + W)
	for module in moduleList:
		print(G + '[+]' + C + ' ' + module + W)
	print("")

# use module(tool)
def use(args):
	global level, moduleName, module
	# check module name
	if len(args) == 0:
		print(Y + '[!]' + C + ' Module name is required!' + W)
		print("")
		return
	moduleName = args[0]
	if moduleName in moduleList:
		level = 2
		module = importlib.import_module("modules."+moduleName).Tool()
		print(G + '[+]' + C + ' Using module : ' + W + moduleName)
		print(G + '[>]' + C + ' Type ' + G + 'help' + C + ' to get help' + W)
		print("")
	else:
		print(R + '[-]' + C + ' Module not found!' + W)
		print("")

# show module(tool) info
def show(args):
	global module, moduleName
	print(G + '[>]' + C + ' Module name : ' + W + moduleName)
	print(G + '[>]' + C + ' Module description : ' + W + module.description)
	print(G + '[>]' + C + ' Module options : ' + W)
	for option in module.options:
		# check the option is required or not
		request = R+"required"+W if module.options[option]['required'] else G+"optional"+W
		value = request if module.options[option]['value'] == "" else module.options[option]['value']
		description = module.options[option]['description']
		print(G + '[+]' + C + ' ' + option + ' : ' + W + value + '\t- ' + description)
	print("")

# set module(tool) options
def set(args):
	global module
	# check module name
	if len(args) == 0:
		print(Y + '[!]' + C + ' Option name is required!' + W)
		print("")
		return
	option = args[0]
	# check value
	if len(args) > 1:
		value = args[1]
	else:
		value = ""
	
	if option not in module.options:
		print(R + '[-]' + C + ' Option ' + W + option + W + C + ' not found!' + W)
		print("")
	else:
		module.options[option]['value'] = value
		print(G + '[+]' + C + ' Option ' + W + option + W + C + ' set to ' + W + value)
		print("")
    
# check module(tool) options
def checkOption():
	global module
	faile = False
	for option in module.options:
		# check the option is required or not and the value is set or not
		if module.options[option]['required'] and module.options[option]['value'] == "":
			print(R + '[-]' + C + ' Option ' + W + option + W + C + ' is required!' + W)
			faile = True
	if faile:
		print("")
		return False
	else:
		return True
    
# run module(tool)
def run(args):
	global module
	# check the required options are set or not
	if checkOption():
		module.run()
		if module.output['status'] == "success":
			print(G + '[+]' + C + ' Module ' + W + moduleName + C + ' executed successfully!' + W)
			# if save option is True then save the output
			if module.output['save']:
				save(module.output['data'])
			print("")
		else:
			print(R + '[-]' + C + ' Module ' + W + moduleName + C + ' execution failed!' + W)
			print("")
	else:
		print(R + '[-]' + C + ' Module ' + W + moduleName + C + ' failed!' + W)
		print("")

# save module(tool) output
def save(data):
	global moduleName
	# check folder existance
	if not os.path.exists("output"):
		os.makedirs("output")
	# check module folder existance
	if not os.path.exists("output/"+moduleName):
		os.makedirs("output/"+moduleName)
	# get date and time as the file name
	date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	savePath = "output/"+moduleName+"/"+date+".txt"
	# if data is a dict then save it as json
	if isinstance(data, dict):
		with open(savePath, "w") as f:
			json.dump(data, f, indent=4)
	# if data is not dict then save it as text
	else:
		with open(savePath, "w") as f:
			f.write(str(data))
	print("\n" + G + '[+]' + C + ' Saved to ' + W + savePath)

    
# print banner
def printBanner():
    # print banner
	banner = r"""
     ___       __   _______   ________                 
    |\  \     |\  \|\  ___ \ |\   __  \                
    \ \  \    \ \  \ \   __/|\ \  \|\ /_               
     \ \  \  __\ \  \ \  \_|/_\ \   __  \              
      \ \  \|\__\_\  \ \  \_|\ \ \  \|\  \             
       \ \____________\ \_______\ \_______\            
        \|____________|\|_______|\|_______|                                                   
 ________  _______   ________  ________  ________      
|\   __  \|\  ___ \ |\   ____\|\   __  \|\   ___  \    
\ \  \|\  \ \   __/|\ \  \___|\ \  \|\  \ \  \\ \  \   
 \ \   _  _\ \  \_|/_\ \  \    \ \  \\\  \ \  \\ \  \  
  \ \  \\  \\ \  \_|\ \ \  \____\ \  \\\  \ \  \\ \  \ 
   \ \__\\ _\\ \_______\ \_______\ \_______\ \__\\ \__\
    \|__|\|__|\|_______|\|_______|\|_______|\|__| \|__|"""
	print(G + banner + W + '\n')
	print(G + '[>]' + C + ' Created By : ' + W + 'Cirno9-dev')
	print(G + '[>]' + C + ' Github     : ' + W + 'https://github.com/Cirno9-dev/WebRecon')
	print(G + '[>]' + C + ' Blog       : ' + W + 'https://blog-ljx.site')
	print(G + '[>]' + C + ' Version    : ' + W + version + '\n')

    
def main():
	global level, module, moduleName
 
	printBanner()
	
	try:
		while True:
			if level == 1:
				command = input(G + '[>]' + C + ' WebRecon > ' + W).strip()
			else:
				command = input(G + '[>]' + C + ' WebRecon/' + moduleName + ' > ' + W).strip()
			command = command.split(" ")
			command = [x for x in command if x != ""]
			# check command
			if command[0] not in commands[level]:
				print(R + '[-]' + C + ' Command not found!' + W)
				print("")
				continue
			# help
			if command[0] == "help":
				printHelp(level)
				continue
			# exit
			if command[0] == "exit":
				if level == 1:
					break
				else:
					level = 1
					printBanner()
					continue
			# other commands
			eval(command[0])(command[1:])
		os.remove(pidPath)
	# keyboard interrupt
	except KeyboardInterrupt:
		print (R + '[-]' + C + ' Keyboard Interrupt.' + W + '\n')
		os.remove(pidPath)
		sys.exit()
 
if __name__ == '__main__':
	main()