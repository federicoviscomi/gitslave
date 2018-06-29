#!/usr/bin/env python
import os
import subprocess
import sys

from urllib.parse import urlparse


def populate(git_slave_dir_path, git_slave_list, git_command_arguments):
    remote_origin_url = subprocess.check_output('git remote get-url origin'.split()).decode('utf-8')
    parse_result = urlparse(remote_origin_url)
    remote_repo_base_path = (parse_result.path.strip())
    remote_repo_base_path = remote_repo_base_path[:len(remote_repo_base_path) - len('master.git')]
    for remote_repo_resource_relative_path, local_relative_path in git_slave_list:
        print('\n')
        slave_dir = git_slave_dir_path + '/' + local_relative_path
        try:
            os.mkdir(slave_dir)
        except FileExistsError:
            print('folder already exists')
        os.chdir(slave_dir)
        print(os.getcwd())
        assert '../' in remote_repo_resource_relative_path
        slave_repo = parse_result.scheme + '://' + \
                     parse_result.netloc + remote_repo_base_path + \
                     remote_repo_resource_relative_path[len('../'):]
        command = 'git clone -b dev {}'.format(slave_repo)
        sys.stdout.flush()
        print(subprocess.call(command.split()))
        sys.stdout.flush()
        os.chdir(git_slave_dir_path)


def execute_git_command(slave_path_list, git_slave_dir_path, command, arguments):
    for relative_path in slave_path_list:
        absolute_path = "{}/{}".format(git_slave_dir_path, relative_path)
        os.chdir(absolute_path)
        full_git_command = "git {} {}".format(command, arguments)
        print("")
        print("$ cd " + os.getcwd())
        print("$ " + full_git_command)
        sys.stdout.flush()
        result = subprocess.check_output(full_git_command.split())
        print(result.decode('utf-8'))
        sys.stdout.flush()


def main():
    command = sys.argv[1]
    arguments = ' '.join(sys.argv[2:])
    slave_list_file_name = '.gitslave'
    while not os.path.isfile(slave_list_file_name):
        os.chdir(os.path.dirname(os.getcwd()))
        if os.getcwd() == os.path.dirname(os.getcwd()):
            print("no .gitslave file found")
            exit(-1)
    git_slave_dir_path = os.getcwd().replace('\\', '/')
    print(".gitslave file found in {}".format(git_slave_dir_path))
    slave_path_list = []
    slave_repo_list = []
    with open(slave_list_file_name) as slave_list_file_reader:
        for slave_list_file_line in slave_list_file_reader:
            remote_repo_resource_relative_path, local_relative_path = slave_list_file_line.split()
            local_relative_path = local_relative_path.replace("\"", "")
            remote_repo_resource_relative_path = remote_repo_resource_relative_path.replace("\"", "")
            slave_path_list.append(local_relative_path)
            slave_repo_list.append((remote_repo_resource_relative_path, local_relative_path))

    if command == 'populate':
        populate(git_slave_dir_path, slave_repo_list, arguments)
    else:
        execute_git_command(slave_path_list, git_slave_dir_path, command, arguments)


if __name__ == "__main__":
    main()
