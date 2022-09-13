import os
import re
import subprocess
import sys


def dry_run_and_count_pulls_matching_ignore_pattern():
    # sync without copying (dry-run)
    dry_run_output = subprocess.getoutput("adb-sync --dry-run -R -t /sdcard/ " + target).splitlines()

    print("double check for missing files:")
    lines_filtered_because_of_pattern = 0
    all_lines_with_pull = 0
    for line in dry_run_output:
        if line.startswith("INFO:root:Pull:"):
            all_lines_with_pull += 1
            if ignorePattern.search(line) is None:
                print(line)  # line does not match pattern and must be reported to user
            else:
                lines_filtered_because_of_pattern += 1  # line matches pattern and will be ignored

    print("pull lines containing pattern (" + ignorePattern.pattern + ") " +
          str(lines_filtered_because_of_pattern) + "/" + str(all_lines_with_pull))


def collect_toplevel_directories_not_matching_pattern(paths_to_sync):
    skip = []
    # find top-level directories in root that will be synced
    for line in subprocess.getoutput("adb shell find /sdcard/ -mindepth 1 -maxdepth 1 -type d | sort").splitlines():
        if ignorePattern.search(line) is None:
            paths_to_sync.append(line)
        else:
            skip.append(line)  # when pattern matches directory will be skipped
    print('skipping [%s]' % ', '.join(map(str, skip)))


def collect_files_in_root(paths_to_sync):
    # find files in root that will be synced - pattern will not be used to filter
    for line in subprocess.getoutput("adb shell find /sdcard/ -mindepth 1 -maxdepth 1 -type f | sort").splitlines():
        paths_to_sync.append(line)


if __name__ == '__main__':
    ignorePattern = re.compile("Android")
    targetRoot = sys.argv[1]  # directory to which files and folders from android phone will be copied
    target = os.path.join(targetRoot, "sdcard")

    paths_to_sync = []
    collect_files_in_root(paths_to_sync)
    collect_toplevel_directories_not_matching_pattern(paths_to_sync)

    for path in paths_to_sync:
        command = "adb-sync -R -t " + path + " " + target
        print(command)
        subprocess.run(command, shell=True, check=True)
        print()

    dry_run_and_count_pulls_matching_ignore_pattern()
