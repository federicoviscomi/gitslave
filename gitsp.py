#!/usr/bin/env python
import argparse
import os
import string
import subprocess
import sys
import signal
import sys

from urllib.parse import urlparse

ENCODING = 'utf-8'


def populate(git_slave_dir_path, git_slave_list, git_command_arguments):
    remote_origin_url = subprocess.check_output('git remote get-url origin'.split()).decode(ENCODING)
    parse_result = urlparse(remote_origin_url)
    remote_repo_base_path = (parse_result.path.strip())
    remote_repo_base_path = remote_repo_base_path[:remote_repo_base_path.rfind('/') + 1]
    with open('populate.sh', 'w') as out_file_writer:
        out_file_writer.write("#!/bin/bash")
        out_file_writer.write('\n')
        for remote_repo_resource_relative_path, local_relative_path in git_slave_list:
            out_file_writer.write('echo\n')
            out_file_writer.write('echo\n')
            assert '../' in remote_repo_resource_relative_path
            slave_repo = parse_result.scheme + '://' + \
                         parse_result.netloc + remote_repo_base_path + \
                         remote_repo_resource_relative_path[len('../'):]
            command = 'git clone {}'.format(slave_repo)
            out_file_writer.write('echo "{}"'.format(command))
            out_file_writer.write('\n')
            out_file_writer.write(command)
            out_file_writer.write('\n')
    print('run script populate.sh')


def empty(git_slave_dir_path, git_slave_list):
    file_name = 'empty.sh'
    print('to empty this gitslave repo, run the command {}'.format(file_name))
    with open(file_name, 'w') as out_file_writer:
        out_file_writer.write("#!/bin/bash")
        for remote_repo_resource_relative_path, local_relative_path in git_slave_list:
            out_file_writer.write("\n")
            slave_dir = git_slave_dir_path + '/' + local_relative_path
            rm_command = 'rm -Rf {}'.format(slave_dir)
            echo_command = 'echo "{}"'.format(rm_command)
            out_file_writer.write(echo_command)
            out_file_writer.write("\n")
            out_file_writer.write(rm_command)
            out_file_writer.write("\n")
            sys.stdout.flush()


def execute_shell_command(slave_path_list, git_slave_dir_path, command, full_shell_command):
    assert command == 'exec'
    output_script_file_name = "{}.sh" \
        .format(full_shell_command.replace(' ', '_').replace('|', '_PIPE_').replace('/', '_SLASH_'))
    print(output_script_file_name)
    print("writing to {}".format(output_script_file_name))
    with open(output_script_file_name, 'w') as out_file_writer:
        out_file_writer.write("\n#!/bin/bash\n")
        for relative_path in slave_path_list:
            try:
                absolute_path = "{}/{}".format(git_slave_dir_path, relative_path)
                os.chdir(absolute_path)
                out_file_writer.write('\n\n\necho -e "\\n\\n\\n" ')
                out_file_writer.write("\ncd " + os.getcwd().replace('\\', '\\\\'))
                out_file_writer.write("\npwd")
                out_file_writer.write('\necho "{}"'.format(full_shell_command))
                out_file_writer.write("\n{}".format(full_shell_command))
                sys.stdout.flush()
            except subprocess.CalledProcessError as e:
                print(e)
    print("done")


def execute_git_command(slave_path_list, git_slave_dir_path, command, arguments):
    for relative_path in slave_path_list:
        try:
            absolute_path = "{}/{}".format(git_slave_dir_path, relative_path)
            os.chdir(absolute_path)
            full_git_command = "git {} {}".format(command, arguments)
            print("")
            print("$ cd " + os.getcwd())
            print("$ " + full_git_command)
            sys.stdout.flush()
            result = subprocess.check_output(full_git_command.split())
            # print(result)
            print(result.decode(ENCODING, errors='ignore'))
            sys.stdout.flush()
        except subprocess.CalledProcessError as e:
            print(e)
        except UnicodeDecodeError as e:
            print(e)


def track_all(slave_path_list, git_slave_dir_path, arguments):
    for relative_path in slave_path_list:
        try:
            absolute_path = "{}/{}".format(git_slave_dir_path, relative_path)
            os.chdir(absolute_path)
            full_command = """
                git branch --all {}
            """.format(arguments)
            # print("$ " + full_command)
            sys.stdout.flush()
            result = subprocess.check_output(full_command.split()).decode(ENCODING)
            branches = []
            for branch in result.split():
                if '->' not in branch and 'HEAD' not in branch and 'master' not in branch and 'remotes' in branch:
                    branches.append(branch)
            sys.stdout.flush()
            for branch in branches:
                try:
                    full_command = """
                        git branch --track {local_branch} {remote_branch}
                    """.format(local_branch=branch[branch.rfind('/') + 1:], remote_branch=branch)
                    print("")
                    print("$ cwd " + os.getcwd())
                    print(full_command)
                    result = subprocess.check_output(full_command.split()).decode(ENCODING)
                    print(result)
                except subprocess.CalledProcessError as e:
                    print(e)
        except ValueError as e:
            print(e)


def checkout_pull_all(slave_path_list, git_slave_dir_path, arguments):
    for relative_path in slave_path_list:
        try:
            absolute_path = "{}/{}".format(git_slave_dir_path, relative_path)
            os.chdir(absolute_path)
            full_command = """
                git branch --all {}
            """.format(arguments)
            # print("$ " + full_command)
            sys.stdout.flush()
            result = subprocess.check_output(full_command.split()).decode(ENCODING)
            branches = []
            for branch in result.split():
                if '->' not in branch and 'HEAD' not in branch and 'master' not in branch and 'remotes' in branch:
                    branches.append(branch)
            sys.stdout.flush()
            for branch in branches:
                try:
                    full_command = """
                        git checkout {local_branch}
                    """.format(local_branch=branch[branch.rfind('/') + 1:])
                    print("")
                    print("$ cwd " + os.getcwd())
                    print(full_command)
                    result = subprocess.check_output(full_command.split()).decode(ENCODING)
                    print(result)

                    full_command = """
                        git pull
                    """
                    print("")
                    print("$ cwd " + os.getcwd())
                    print(full_command)
                    result = subprocess.check_output(full_command.split()).decode(ENCODING)
                    print(result)
                except subprocess.CalledProcessError as e:
                    print(e)
        except ValueError as e:
            print(e)


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.stdout.flush()
    sys.exit(0)
    # doesn't work!


def look_for_slaves_file():
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
    return git_slave_dir_path, slave_repo_list, slave_path_list


def parse_arguments():
    arguments = ' '.join(sys.argv[2:])
    # parser = argparse.ArgumentParser()
    # parser.add_argument('command', type=str)
    # parser.add_argument('arguments', nargs='*')
    # args = parser.parse_args()
    # print(args)
    # command = args.command
    # return command, arguments
    return sys.argv[1], arguments


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print("""
        Gitslave clone in python.
    """)
    git_slave_dir_path, slave_repo_list, slave_path_list = look_for_slaves_file()
    command, arguments = parse_arguments()
    if command == 'populate':
        populate(git_slave_dir_path, slave_repo_list, arguments)
    elif command == 'track_all':
        track_all(slave_path_list, git_slave_dir_path, arguments)
    elif command == 'checkout_pull_all':
        checkout_pull_all(slave_path_list, git_slave_dir_path, arguments)
    elif command == 'exec':
        execute_shell_command(slave_path_list, git_slave_dir_path, command, arguments)
    elif command == 'empty':
        empty(git_slave_dir_path, slave_repo_list)
    else:
        execute_git_command(slave_path_list, git_slave_dir_path, command, arguments)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(e)
