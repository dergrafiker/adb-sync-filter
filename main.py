import os
import re
import subprocess
import sys


def dry_run_and_count_pulls_matching_ignore_pattern(phone_root, target, ignore_pattern):
    # sync without copying (dry-run)
    dry_run_output = subprocess.getoutput("adbsync --dry-run pull " + phone_root + " " + target).splitlines()

    print("double check for missing files:")
    lines_filtered_because_of_pattern = 0
    all_lines_with_pull = 0
    for line in dry_run_output:
        if line.startswith("INFO:root:Pull:"):
            all_lines_with_pull += 1
            if ignore_pattern.search(line) is None:
                print(line)  # line does not match pattern and must be reported to user
            else:
                lines_filtered_because_of_pattern += 1  # line matches pattern and will be ignored

    print("pull lines containing pattern (" + ignore_pattern.pattern + ") " +
          str(lines_filtered_because_of_pattern) + "/" + str(all_lines_with_pull))


def collect_toplevel_directories_not_matching_pattern(paths_to_sync, phone_root, ignore_pattern):
    skip = []
    # find top-level directories in root that will be synced
    for line in subprocess.getoutput(
            "adb shell find " + phone_root + " -mindepth 1 -maxdepth 1 -type d | sort").splitlines():
        if ignore_pattern.search(line) is None:
            paths_to_sync.append(line)
        else:
            skip.append(line)  # when pattern matches directory will be skipped
    print('skipping [%s]' % ', '.join(map(str, skip)))


def collect_files_in_root(paths_to_sync, phone_root):
    # find files in root that will be synced - pattern will not be used to filter
    for line in subprocess.getoutput(
            "adb shell find " + phone_root + " -mindepth 1 -maxdepth 1 -type f | sort").splitlines():
        paths_to_sync.append(line)


def main():
    ignore_pattern = re.compile("Android|Music|newpipe|ebooks")
    target = os.path.join(sys.argv[1], "sdcard")  # files will be copied here
    phone_root = "/sdcard/"

    paths_to_sync = []
    collect_files_in_root(paths_to_sync, phone_root)
    collect_toplevel_directories_not_matching_pattern(paths_to_sync, phone_root, ignore_pattern)

    for path in paths_to_sync:
        command = "adbsync pull " + path + " " + target
        print(command)
        subprocess.run(command, shell=True, check=True)
        print()

    dry_run_and_count_pulls_matching_ignore_pattern(phone_root, target, ignore_pattern)


main()
