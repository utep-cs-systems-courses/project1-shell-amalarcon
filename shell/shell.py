# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 14:20:12 2020

@author: Aaron
"""

import os, sys, time, re

#execves a command you have to fork since doing exeve will stop your process
def do_command(commands, processwait = False):
    #fork
    pid = os.fork()
    
    #bad fork
    if pid < 0: 
        os.write(2, ("fork failed, returning %d\n" % (pid)).encode())
        sys.exit(1)
        
    #child
    if pid == 0:
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, commands[0])
            try:
                os.execve(program, commands, os.environ)
            except FileNotFoundError:
                pass
            except NotADirectoryError:
                pass
        #error
        os.write(2, ("\"{}\" command not found.\n".format(commands[0])).encode())
        sys.exit(1)
    #parent
    else: 
        if processwait:
            os.wait()
        return None
    
    #function that determines output file, input file, and command given a string
def parse2(cmdString):
    outFile = None
    inFile = None
    cmd = ''
 
    cmdString = re.sub(' +', ' ', cmdString)
 
    if '>' in cmdString:
        [cmd, outFile] = cmdString.split('>',1)
        outFile = outFile.strip()
 
    if '<' in cmd:
        [cmd, inFile] = cmd.split('<', 1)
        inFile = inFile.strip()
    
    elif outFile != None and '<' in outFile:
        [outFile, inFile] = outFile.split('<', 1)
        
        outFile = outFile.strip()
        inFile = inFile.strip()
        
    return cmd.split(), outFile, inFile

#prompt indefinetly
while (1):
    #could not figure out ps1, but current working directory is similar
    user_in = input(os.getcwd() + " $ ")
    
    #if there's no input or exit was typed
    if not user_in:
        continue
    if user_in.strip() == "exit":
        sys.exit(1)
    
    #change directory commands
    temp_command = user_in.split()
    if temp_command[0] == "cd":
        if len(temp_command) == 1:
            os.write(1, "cd is the command for changing directories\n".encode())
            continue
        try:
            os.chdir(temp_command[1])
        except FileNotFoundError:
            os.write(2, "{} is not a recognized directory or path\n".format(temp_command[1]).encode())
        continue
        
    #Create child processes to do the dirty work while you wait to prompt
    pid = os.fork()
    if pid < 0:
        os.write(2, ("fork failed, returning %d\n" % (pid)).encode())
        sys.exit(1)
    elif pid == 0:
        
        #pipe input
        if "|" in user_in:
            
            #setup file descriptors/pipe
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
            
            #restore standard input and close the copies
            os.dup2(sin_copy, 0)
            os.close(sin_copy)
            os.close(sout_copy)
            os.close(fr)
            os.close(fw)
        
        
        elif ('<' in user_in) or ('>' in user_in):
            #parse the file information
            command, out_file, in_file = parse2(user_in) 
            #save standard out
            sout_copy = os.dup(1) 
            #open file and route output to it
            fd_fout = os.open(out_file, os.O_WRONLY | os.O_CREAT) 
            os.dup2(fd_fout, 1) 
            
            #do commands and restore everything
            do_command(commands) 
            os.dup2(sout_copy, 1) 
            os.close(fd_fout)
            
         #normal command with nothing special  
        else: 
            do_command(user_in.strip().split())
        #close any child processes that are still active here
        sys.exit(1)
    #parent waits for child
    else:
        os.wait()