#!/usr/bin/env python
import os
import subprocess
import sys

from urllib.parse import urlparse


def init(gitslave_dir_path, git_slave_list, git_command_arguments):
    remote_origin_url = subprocess.check_output('git remote get-url origin'.split()).decode('utf-8')
    parse_result = urlparse(remote_origin_url)
    for remote_repo_resource_relative_path, local_relative_path in git_slave_list:
        print()
        # mkdir first!
        os.chdir(gitslave_dir_path + '/' + local_relative_path)
        print(os.getcwd())
        print((parse_result.path.strip()) + '/' + remote_repo_resource_relative_path)  # git init!


def main():
    git_command = sys.argv[1]
    git_command_arguments = ' '.join(sys.argv[2:])

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
        init(gitslave_dir_path, gitslave_list, git_command_arguments)
    else:
        for relative_path in path_list:
            absolute_path = "{}/{}".format(gitslave_dir_path, relative_path)
            os.chdir(absolute_path)
            command = "git {} {}".format(git_command, git_command_arguments)
            print("")
            print("$ cd " + os.getcwd())
            print("$ " + command)
            sys.stdout.flush()
            result = subprocess.check_output(command.split())
            print(result.decode('utf-8'))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
