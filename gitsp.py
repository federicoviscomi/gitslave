#!/usr/bin/env python
import urllib
import os
import subprocess
import argparse
import sys

# a remote repo has a protocol, a host address and a resource path such as
#   ssh://git@git.bbp.ch/git/inuc/core/master.git
# where ssh is the protocol
#       git@git.bbp.ch is the host address
#       /git/inuc/core/master.git is the resource path
# a .gitslave files stores a list of pairs such that:
# the first element is a resource path relative to the remote repo path
# of the git repo that stores the .gitslave file
# and the second element is a local path ... TODO
from urllib.parse import urlparse


def init(gitslave_dir_path, git_slave_list):
    remore_origin_url = subprocess.check_output('git remote get-url origin'.split()).decode('utf-8')
    parse_result = urlparse(remore_origin_url)
    # ParseResult(scheme='ssh', netloc='git@git.bbp.ch', path='/git/inuc/core/master.git\n', params='', query='', fragment='')
    for remote_repo_resource_relative_path, local_relative_path in git_slave_list:
        print()
        os.chdir(gitslave_dir_path + '/' + local_relative_path)
        print(os.getcwd()) # mkdir!
        print((parse_result.path.strip()) + '/' + remote_repo_resource_relative_path) #git init!


def main():
    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument("git_command", help="An integer will be increased by 1 and printed.")
    args = parser.parse_args()
    git_command = args.git_command

    gitslave_file_name = '.gitslave'
    while not os.path.isfile(gitslave_file_name):
        os.chdir(os.path.dirname(os.getcwd()))
        if os.getcwd() == os.path.dirname(os.getcwd()):
            print("no .gitslave file found")
            exit(-1)

    gitslave_dir_path = os.getcwd().replace('\\', '/')
    print(".gitslave file found in {}".format(gitslave_dir_path))

    path_list = []
    gitslave_list = []
    with open(gitslave_file_name) as gitslave_config_fdin:
        for line in gitslave_config_fdin:
            remote_repo_resource_relative_path, local_relative_path = line.split()
            local_relative_path = local_relative_path.replace("\"", "")
            remote_repo_resource_relative_path = remote_repo_resource_relative_path.replace("\"", "")
            path_list.append(local_relative_path)
            gitslave_list.append((remote_repo_resource_relative_path, local_relative_path))

    if git_command == 'init':
        init(gitslave_dir_path, gitslave_list)
    else:
        for relative_path in path_list:
            absolute_path = "{}/{}".format(gitslave_dir_path, relative_path)
            os.chdir(absolute_path)
            command = "git {}".format(git_command)
            print("")
            print("$ cd " + os.getcwd())
            print("$ " + command)
            sys.stdout.flush()
            result = subprocess.check_output(command.split())
            print(result.decode('utf-8'))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
