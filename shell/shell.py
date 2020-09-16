# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 14:20:12 2020

@author: Aaron
"""

import os, sys, time, re


def do_command(commands, processwait = False):
    pid = os.fork()
    if pid < 0: 
        os.write(2, ("fork failed, returning %d\n" % (pid)).encode())
        sys.exit(1)
    if pid == 0:
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, commands[0])
            try:
                os.execve(program, commands, os.environ)
            except FileNotFoundError:
                pass
            except NotADirectoryError:
                pass
        os.write(2, ("\"{}\" command not found.\n".format(commands[0])).encode())
        sys.exit(1)
    else: 
        if processwait:
            os.wait()
        return None
while (1):
    user_in = input(os.getcwd() + " $ ")
    
    if not user_in:
        continue
    if user_in.strip() == "exit":
        sys.exit(1)
    
    temp_command = user_in.split()
    if temp_command[0] == "cd":
        try:
            os.chdir(temp_command[1])
        except FileNotFoundError:
            os.write(2, "{} is not a recognized directory or path\n".format(temp_command[1]).encode())
        continue
        
    pid = os.fork()
    if pid < 0:
        os.write(2, ("fork failed, returning %d\n" % (pid)).encode())
        sys.exit(1)
    elif pid == 0:
        if "|" in user_in:
            #setup file descriptors
            sin_copy = os.dup(0)
            sout_copy = os.dup(1)
            fr, fw = os.pipe()
            for f in (fr,fw):
                os.set_inheritable(f, True)
                
            #get commands   
            pipes = user_in.split("|")
            commands = list()
            for i in range(len(pipes)):
                commands.append(pipes[i].strip().split())

            #set up writing and exec first process
            os.close(1)
            os.dup2(fw,1)
            do_command(commands[0], processwait = True)
            
            #set up reading and exec second proces
            os.dup2(fr,0)
            os.dup2(sout_copy, 1)
          
            
            do_command(commands[1])
            os.dup2(sin_copy, 0)
        
            os.close(sin_copy)
            os.close(sout_copy)
            os.close(fr)
            os.close(fw)
            
            
        else: 
            do_command(user_in.strip().split())
        sys.exit(1)
    else:
        os.wait()