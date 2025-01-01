import random
import os
import sys
import subprocess
from typing import Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from collections import deque
import json

def print_rainbow(text: str):
    """Print text through lolcat for rainbow effect."""
    try:
        import subprocess
        subprocess.run(['lolcat', '-F', '0.3'], input=text.encode('utf-8'), check=True)
    except FileNotFoundError:
        print(text)

# ANSI escape codes for colors
CYAN = '\033[96m'
ROSE = '\033[91m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
LIGHT_PURPLE = '\033[38;5;147m'
YELLOW = '\033[93m'
ORANGE = '\033[38;5;208m'
SOFT_GOLD = '\033[38;5;178m'
PEACH = '\033[38;5;216m'
LAVENDER = '\033[38;5;183m'
SAGE = '\033[38;5;151m'
SKY_BLUE = '\033[38;5;153m'
RESET = '\033[0m'

# Score constants
CORRECT_POINTS = 1
INCORRECT_POINTS = -5
CASE_MISMATCH_POINTS = -2

class Mode(Enum):
    BEGINNER = 'b'
    INTERMEDIATE = 'i'
    ADVANCED = 'a'
    UNDERSTANDING = 'u'
    VARIABLES = 'v'
    SCRIPTING = 's'
    API = 'p'
    GIT = 'g'

@dataclass
class Command:
    command: str
    explanation: str
    example: str
    output: str = "" # Optional output for demonstration
    
@dataclass
class Variable:
    name: str
    explanation: str
    example: str
    output: str = "" # Optional oputput for the example

class BashTutor:
    def __init__ (self):
        self.questions = {  
            Mode.BEGINNER: {
                "What command creates a new file?": Command(
                    "touch filename",
                    "Creates a new empty file or updates the access/modification times of an existing file",
                    "touch document.txt",
                    "# Creates empty file 'document.txt' in current directory\n# No output is shown if successful"
                ),

                "How do you list all text files in current directory?": Command(
                    "ls *.txt",
                    "Lists all files ending in .txt using the * wildcard. The * matches any number of any characters before '.txt'",
                    "ls *.txt  # List all .txt files\nls test*.txt  # List .txt files starting with 'test'\nls *2023*.txt  # List .txt files containing '2023'",
                    "notes.txt\nreadme.txt\ntest.txt\ntodo.txt"
                ),

                "How do you copy from a parallel directory to your current directory?": Command(
                    "cp ../parallel_dir/* ./",
                    "Copies files from a directory at the same level using relative paths. '../' means up one directory, './' means current directory",
                    "cp ../project1/*.txt ./  # Copy all txt files from parallel directory\ncp ../old_project/config.json ./  # Copy specific file\ncp -r ../source_code/ ./  # Copy entire directory recursively",
                    "# No output shown if successful\n# Contents from ../parallel_dir/ appear in current directory"
                ),

                "What command can you use to locally compress and backup a project with date?": Command(
                    "tar -czvf project_backup_$DATE.tar.gz project_folder/",
                    "Makes a compressed archieve of the project folder with the current date in the filename",
                    "tar -czvf bash-tutor_backup_$(date +%F).tar.gz projects/"
                ),
                
                "How do you list all files in the current directory?": Command(
                    "ls",
                    "Lists files and directories in the current directory. Shows names by default",
                    "ls\nls -l  # For detailed list\nls -a  # To show hidden files",
                    "documents/  downloads/  example.txt  pictures/"
                ),
                
                "How do you change directories?": Command(
                    "cd directory",
                    "Changes current working directory to specified directory path",
                    "cd Documents\ncd ..  # Go up one directory\ncd ~  # Go to home directory",
                    "# No output is shown if successful"
                ),
                
                "How do you remove a file?": Command(
                    "rm filename",
                    "Permanently deletes a file. Be careful as this cannot be undone!",
                    "rm old_file.txt\nrm -i file.txt  # Ask for confirmation",
                    "# No output is shown if successful\n# With -i flag: remove file.txt? y"
                ),
                
                "How do you copy a file?": Command(
                    "cp source destination",
                    "Creates a copy of a file at the specified destination",
                    "cp document.txt backup.txt\ncp -r folder1 folder2  # Copy directory",
                    "# No output is shown if successful"
                ),
                
                "How do you move or rename a file?": Command(
                    "mv source destination",
                    "Moves a file to new location or renames it if destination is in same directory",
                    "mv old.txt new.txt  # Rename file\nmv file.txt ../docs/  # Move to docs directory",
                    "# No output is shown if successful"
                ),
                
                "How do you display file contents?": Command(
                    "cat filename",
                    "Displays entire contents of a file in the terminal",
                    "cat notes.txt\ncat -n file.txt  # Show line numbers",
                    "This is the content of notes.txt\nIt shows all lines at once"
                ),
                
                "How do you create a new directory?": Command(
                    "mkdir directory",
                    "Creates a new empty directory with specified name",
                    "mkdir projects\nmkdir -p path/to/directory  # Create parent directories if needed",
                    "# No output is shown if successful"
                ),
                
                "How do you show the current directory?": Command(
                    "pwd",
                    "Print Working Directory - shows full path of current directory",
                    "pwd",
                    "/home/username/documents"
                ),
                
                "How do you view file permissions?": Command(
                    "ls -l filename",
                    "Shows detailed file information including permissions, owner, size, and modification time",
                    "ls -l document.txt",
                    "-rw-r--r-- 1 user group 4096 Dec 29 10:00 document.txt"
                ),
                
                "How do you exit an operation?": Command(
                    "ctrl + c",
                    "Sends interrupt signal to current process, typically stopping it immediately",
                    "# Press Ctrl + C while running a command or stuck in an operation",
                    "^C\nOperation terminated"
                ),
                
                "How do you exit the terminal?": Command(
                    "exit",
                    "Closes the current terminal session or shell",
                    "exit",
                    "# Terminal window will close"
                ),
                
                "How do you shut down the system?": Command(
                    "shutdown",
                    "Safely shuts down the system, with options for timing and reboot",
                    "shutdown now  # Immediate shutdown\nshutdown -r now  # Immediate reboot\nshutdown +10  # Shutdown in 10 minutes",
                    "Shutdown scheduled for Thu 2024-12-29 10:00:00"
                ),
                
                "How do you reboot the system?": Command(
                    "reboot",
                    "Restarts the system immediately (requires sudo privileges)",
                    "sudo reboot",
                    "# System will restart immediately"
                ),
                
                "How do you list all processes?": Command(
                    "ps",
                    "Shows currently running processes. By default shows only current user's processes",
                    "ps\nps aux  # Show all processes from all users",
                    "  PID TTY          TIME CMD\n 1234 pts/0    00:00:01 bash\n 5678 pts/0    00:00:00 ps"
                ),
                
                "How do you display a message or string in the terminal?": Command(
                    'echo "string"',
                    "Prints text to the terminal. Can include variables and escape characters",
                    'echo "Hello, World!"\necho -e "Line 1\\nLine 2"  # Use newline',
                    "Hello, World!"
                ),
                
                "How do you search for a file on the local database?": Command(
                    "locate filename",
                    "Quickly searches the system's file database for matching filenames",
                    "locate readme.txt\nlocate -i README  # Case-insensitive search",
                    "/home/user/documents/readme.txt\n/usr/share/doc/readme.txt"
                ),
                
                "How do you search for a file on the local database that belongs to a package?": Command(
                    "locate filename | grep package",
                    "Searches for files and filters results to show only those matching the package name",
                    "locate README | grep nginx",
                    "/usr/share/doc/nginx/README\n/etc/nginx/README.txt"
                ),
                
                "How do you update the local search database?": Command(
                    "sudo updatedb",
                    "Updates the system's file location database used by the locate command",
                    "sudo updatedb",
                    "# No output is shown if successful"
                ),
                
                "How do you read a markdown file on the local database?": Command(
                    "cat /path/to/file.md",
                    "Displays contents of a markdown file. Note: will show raw markdown formatting",
                    "cat /usr/share/doc/package/README.md",
                    "# Project Title\n\nThis is a markdown file..."
                ),
                
                "How do you read a markdown file on the local database with scrolling?": Command(
                    "less /path/to/file.md",
                    "Views file contents with ability to scroll up/down. Press q to quit",
                    "less /usr/share/doc/package/README.md",
                    "# File contents shown with scrolling capability\n(Use arrow keys to navigate, q to quit)"
                ),
                
                "How do you search for a readme file that may not be a markdown?": Command(
                    "locate package | grep -i readme",
                    "Case-insensitive search for any readme files related to a package",
                    "locate nginx | grep -i readme",
                    "/usr/share/doc/nginx/README\n/usr/share/doc/nginx/README.md"
                ),
                
                "How do you check if a package is installed?": Command(
                    "dpkg -l | grep package",
                    "Lists installed packages and filters for specific package name",
                    "dpkg -l | grep nginx",
                    "ii  nginx  1.18.0-1  amd64  high performance web server"
                )
            
            },
            Mode.INTERMEDIATE: {
                "How do you find all files larger than 10MB in a current directory?": Command(
                    "find . -size +10M",
                    "Searches recursively through current directory for files larger than 10 megabytes",
                    "find . -size +10M -type f -ls  # Lists all files over 10MB with details\nfind . -size +10M -exec ls -lh {} \\;  # Human-readable sizes",
                    "12583 10.5M ./videos/tutorial.mp4\n15890 12.8M ./archives/backup.zip"
                ),

                "How do you find all files larger than 1GB in a current directory?": Command(
                    "find . -size +1G",
                    "Searches recursively through current directory for files larger than 1 gigabyte",
                    "find . -size +1G -type f -ls\nfind . -size +1G -exec du -h {} \\;  # Show sizes",
                    "1.2G ./videos/movie.mp4\n3.5G ./backups/system.img"
                ),

                "How do you check disk space usage of specific directories?": Command(
                    "du -sh directory",
                    "Shows total disk usage of specified directory in human-readable format (-s for summary, -h for human readable)",
                    "du -sh Documents\ndu -sh */  # Check all directories in current location",
                    "1.2G Documents\n523M Downloads\n2.1G Pictures"
                ),

                "How do you check disk space usage of current directory?": Command(
                    "du -h",
                    "Shows disk usage of current directory and all subdirectories in human-readable format",
                    "du -h\ndu -h --max-depth=1  # Only show one level deep",
                    "128K    ./config\n256M    ./data\n1.2G    ."
                ),

                "How do you monitor system resources in real-time?": Command(
                    "top",
                    "Shows real-time view of system processes, CPU usage, memory usage, and more",
                    "top\ntop -u username  # Show only user's processes",
                    "top - 14:23:56 up 7 days, 23 users\nTasks: 180 total, 1 running\n%Cpu(s): 25.3 us, 12.7 sy"
                ),

                "How do you set the date in a environment variable with standardisation?": Command(
                    "DATE=$(date +%F)",
                    "Stores current date in YYYY-MM-DD format in DATE variable",
                    "DATE=$(date +%F)\necho $DATE",
                    "2024-12-29"
                ),

                "How do you compress a directory into a tar.gz file?": Command(
                    "tar -czvf archive.tar.gz directory",
                    "Creates compressed archive (-c create, -z gzip, -v verbose, -f specify filename)",
                    "tar -czvf backup.tar.gz Documents/",
                    "Documents/file1.txt\nDocuments/file2.txt\nDocuments/subfolder/"
                ),

                "How do you compress a directory into a tar.gz file with a backup date?": Command(
                    "tar -czvf backup_$DATE.tar.gz directory",
                    "Creates dated backup archive using DATE variable set earlier",
                    "tar -czvf backup_$(date +%F).tar.gz Documents/",
                    "backup_2024-12-29.tar.gz created containing:\nDocuments/file1.txt\nDocuments/file2.txt"
                ),

                "How do you extract a tar.gz file?": Command(
                    "tar -xzvf archive.tar.gz",
                    "Extracts files from a compressed tar archive (-x extract, -z gzip, -v verbose, -f specify filename)",
                    "tar -xzvf backup.tar.gz\ntar -xzvf backup.tar.gz -C /target/directory  # Extract to specific location",
                    "Documents/file1.txt\nDocuments/file2.txt\nDocuments/subfolder/"
                ),

                "How do you search for text recursively in all files?": Command(
                    'grep -r "pattern" directory',
                    "Searches for text pattern in all files under specified directory (-r recursive)",
                    'grep -r "TODO" src/\ngrep -ri "error" logs/  # Case-insensitive search',
                    "src/main.c:// TODO: Implement error handling\nlogs/app.log:Error: Connection refused"
                ),

                "How do you check running processes?": Command(
                    "ps",
                    "Shows snapshot of current processes in simple format",
                    "ps\nps -f  # Full format listing",
                    "  PID TTY          TIME CMD\n 1234 pts/0    00:00:01 bash\n 5678 pts/0    00:00:00 ps"
                ),

                "How do you check all running processes?": Command(
                    "ps aux",
                    "Shows detailed list of all processes from all users (-a all users, -u detailed, -x includes processes without TTY)",
                    "ps aux\nps aux | grep nginx  # Filter for specific process",
                    "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\nroot      1234  0.0  0.1  2468  1234 ?        Ss   Dec29   0:00 nginx"
                ),

                "How do you display a message over two separate lines?": Command(
                    'echo -e "line1\\nline2"',
                    "Prints text with newline (-e enables interpretation of backslash escapes)",
                    'echo -e "Hello\\nWorld"\necho -e "First line\\nSecond line\\nThird line"',
                    "Hello\nWorld"
                ),

                "How do you kill a process by its process ID?": Command(
                    "kill PID",
                    "Sends termination signal to process with specified PID",
                    "kill 1234  # Normal termination\nkill -9 1234  # Force kill\nkill -l  # List all signals",
                    "# No output if successful\n# kill -l shows:\n 1) SIGHUP   2) SIGINT   3) SIGQUIT   4) SIGILL"
                ),

                "How do you download a file from the internet?": Command(
                    "wget url",
                    "Downloads file from specified URL, preserving original filename",
                    "wget https://example.com/file.zip\nwget -O custom_name.zip https://example.com/file.zip",
                    "Resolving example.com... 93.184.216.34\nConnecting to example.com... connected.\nHTTP request sent, awaiting response... 200 OK\nLength: 1234567 (1.2M) [application/zip]\nSaving to: 'file.zip'\n\nfile.zip          100%[===================>]   1.2M   1.2MB/s    in 1.0s"
                ),

                "How do you check network connections?": Command(
                    "netstat -tuln",
                    "Shows all TCP and UDP listening ports (-t TCP, -u UDP, -l listening, -n show numbers)",
                    "netstat -tuln\nnetstat -tulnp  # Also show process name (requires sudo)",
                    "Proto Recv-Q Send-Q Local Address           Foreign Address         State\ntcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN\ntcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN"
                ),

                "How do you sync directories while excluding certain files?": Command(
                    "rsync -av --exclude='pattern' source/ destination/",
                    "Synchronizes directories while excluding specified patterns. The -a preserves attributes, -v shows progress.",
                    "rsync -av --exclude='.git' --exclude='*.log' src/ dest/  # Exclude multiple patterns\nrsync -av --exclude-from='exclude.txt' src/ dest/  # Exclude from file",
                    "sending incremental file list\nfile1.txt\nfile2.txt\nsubdir/\nsubdir/file3.txt\n\nsent 1,234 bytes  received 42 bytes  2,552.00 bytes/sec\ntotal size is 10,340  speedup is 8.12"
                ),

                "How do you sync directories while showing progress?": Command(
                    "rsync -avP source/ destination/",
                    "Synchronizes with progress bar (-P) and verbose output. Useful for large transfers.",
                    "rsync -avP ~/Documents/ backup/  # Sync with progress\nrsync -avP --info=progress2 src/ dest/  # Detailed progress",
                    "sending incremental file list\nfile.txt\n    1,234,567 100%   23.45MB/s    0:00:01\ntotal size is 1,234,567  speedup is 1.00"
                ),

                "How do you do a dry run of directory synchronization?": Command(
                    "rsync -av --dry-run source/ destination/",
                    "Shows what would be transferred without actually copying files. Good for testing.",
                    "rsync -av --dry-run ~/src/ ~/backup/  # Test sync\nrsync -avn src/ dest/  # Short form",
                    "sending incremental file list\nfile1.txt\nfile2.txt\n\nNOTE: would transfer 123 bytes in 2 files"
                ),

                "How do you create a mirror backup of a directory?": Command(
                    "rsync -av --delete source/ destination/",
                    "Creates exact mirror, deleting files in destination that don't exist in source.",
                    "rsync -av --delete ~/www/ backup/  # Mirror website\nrsync -av --delete --backup src/ dest/  # Mirror with backups",
                    "deleting old_file.txt\nsending incremental file list\nnew_file.txt"
                ),

                "How do you sync files while preserving hard links?": Command(
                    "rsync -avH source/ destination/",
                    "Preserves hard links (-H) during synchronization. Useful for backup systems.",
                    "rsync -avH /etc/ backup/  # Sync preserving hard links\nrsync -avHAX root/ backup/  # Full system backup",
                    "sending incremental file list\nfile1.txt => file2.txt\nfile3.txt"
                ),

                "How do you use tar with ssh for remote backup?": Command(
                    "tar czf - directory | ssh user@host 'cat > backup.tar.gz'",
                    "Creates compressed archive and sends it directly to remote host via SSH.",
                    "tar czf - Documents | ssh server 'cat > docs.tar.gz'  # Backup to server\ntar czf - /etc | ssh user@host 'cd /backup && cat > etc.tar.gz'  # Backup to specific directory",
                    "tar: Documents: Removing leading '/' from member names\n# Data transfers without local storage"
                ),

                "How do you use dd to clone a disk?": Command(
                    "dd if=/dev/sda of=/dev/sdb bs=4M status=progress",
                    "Creates exact disk copy, useful for disk cloning and backup. Be very careful with this command.",
                    "dd if=/dev/sda of=disk.img bs=4M  # Create disk image\ndd if=/dev/zero of=/dev/sdb bs=4M  # Wipe disk",
                    "1234567+0 records in\n1234567+0 records out\n1234567890123 bytes transferred in 123.45 seconds (123.45 MB/s)"
                ),

                "How do you create a compressed file archive?": Command(
                    "tar czvf archive.tar.gz files/",
                    "Creates a compressed tar archive (-c create, -z gzip, -v verbose, -f specify file).",
                    "tar czvf backup.tar.gz ~/Documents/  # Backup Documents\ntar czvf --exclude='*.tmp' archive.tar.gz dir/  # Exclude patterns",
                    "dir/\ndir/file1.txt\ndir/file2.txt\ndir/subdir/\ndir/subdir/file3.txt"
                ),

                "How do you synchronize only newer files?": Command(
                    "rsync -avu source/ destination/",
                    "Updates only files that are newer in source (-u update only).",
                    "rsync -avu ~/src/ ~/backup/  # Update newer files\nrsync -avu --ignore-existing src/ dest/  # Skip existing",
                    "sending incremental file list\nnew_file.txt\nmodified_file.txt"
                ),

                "How do you create an incremental backup?": Command(
                    "rsync -av --link-dest=previous_backup source/ new_backup/",
                    "Creates hard links to unchanged files from previous backup, saving space.",
                    "rsync -av --link-dest=/backup/last /src/ /backup/new/  # Incremental backup\nrsync -av --link-dest=../backup.1 src/ backup.0/  # Rotating backup",
                    "sending incremental file list\nfile1.txt\nfile2.txt -> ../backup.1/file2.txt"
                )                
            },
            Mode.ADVANCED: {
                # ADVANCED Mode Commands
                "How do you redirect both stdout and stderr to a file?": Command(
                    "command &> output.log",
                    "Redirects both standard output (stdout) and standard error (stderr) to a single file",
                    "ls /existing /nonexistent &> output.log  # Captures both output and errors\necho 'test' &> output.log  # Overwrites file\necho 'append' &>> output.log  # Appends to file",
                    "# Content of output.log might look like:\nls: cannot access '/nonexistent': No such file or directory\nexisting.txt\nother_file.txt"
                ),

                "How do you find and replace text in multiple files?": Command(
                    "sed -i 's/old/new/g' *.txt",
                    "Replaces all occurrences of 'old' with 'new' in all .txt files (-i for in-place editing, g for global/multiple occurrences per line)",
                    "sed -i 's/error/warning/g' *.log  # Replace in all log files\nsed -i.bak 's/foo/bar/g' config.txt  # Create backup before replacing\nsed -i 's/cat/dog/gi' *.txt  # Case-insensitive replacement",
                    "# No output shown but files are modified\n# Use sed -i.bak to create backups of original files"
                ),

                "How do you check open file handles for a process?": Command(
                    "lsof -p pid",
                    "Lists all open files and network connections for a specific process ID",
                    "lsof -p 1234  # Check process with PID 1234\nlsof -p $(pgrep nginx)  # Check nginx process\nlsof -u username  # Check all processes for user",
                    "COMMAND  PID   USER   FD   TYPE DEVICE SIZE/OFF   NODE NAME\nnginx   1234 www-data  3u  IPv4 164928   0t0    TCP *:80 (LISTEN)\nnginx   1234 www-data  4r   REG  252,1   65536   logs/access.log"
                ),

                "How do you set up a cron job to run every hour?": Command(
                    "0 * * * * command",
                    "Schedules a command to run at the start of every hour using cron (minute hour day-of-month month day-of-week command)",
                    "0 * * * * /scripts/backup.sh  # Run backup.sh every hour\n*/30 * * * * command  # Run every 30 minutes\n0 */2 * * * command  # Run every 2 hours",
                    "# Edit crontab with: crontab -e\n# View current crontab with: crontab -l\n# Example output of crontab -l:\n0 * * * * /scripts/backup.sh"
                ),

                "How do you check disk I/O statistics?": Command(
                    "iostat -x",
                    "Shows detailed I/O statistics for devices (-x for extended statistics)",
                    "iostat -x 1  # Update every second\niostat -xk  # Show stats in kilobytes\niostat -xm 5  # Show in MB, update every 5 seconds",
                    "Linux 5.4.0 (hostname)     12/29/2024     _x86_64_    (4 CPU)\n\nDevice   r/s   w/s    rkB/s    wkB/s  avgqu-sz   await  svctm  %util\nsda    25.20  60.50  1000.40  2200.30     1.25    8.50   2.30  15.20"
                ),

                "How do you trace system calls of a process?": Command(
                    "strace -p pid",
                    "Traces system calls and signals for a running process (-p for process ID)",
                    "strace -p 1234  # Trace specific PID\nstrace -f -p 1234  # Also trace child processes\nstrace -c -p 1234  # Show summary of system calls",
                    "read(3, \"Hello\\n\", 6)                  = 6\nwrite(1, \"Hello\\n\", 6)                 = 6\nfstat(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(136, 0), ...}) = 0"
                ),

                "How do you create a symbolic link?": Command(
                    "ln -s target link_name",
                    "Creates a symbolic link (soft link) pointing to target file or directory",
                    "ln -s /path/to/file.txt link.txt  # Link to file\nln -s /var/www/html current  # Link to directory\nln -sf target link_name  # Force create/update link",
                    "# No output if successful\nls -l link.txt\nlrwxrwxrwx 1 user group 14 Dec 29 10:00 link.txt -> /path/to/file.txt"
                ),

                "How do you check CPU temperature?": Command(
                    "sensors",
                    "Shows hardware monitoring information including CPU and motherboard temperatures",
                    "sensors\nwatch sensors  # Monitor temperatures continuously\nsensors | grep 'Core'  # Show only CPU core temperatures",
                    "coretemp-isa-0000\nCore 0:  +45.0°C  (high = +80.0°C, crit = +100.0°C)\nCore 1:  +46.0°C  (high = +80.0°C, crit = +100.0°C)\nCore 2:  +44.0°C  (high = +80.0°C, crit = +100.0°C)"
                ),

                "How do you monitor network bandwidth usage?": Command(
                    "iftop -n",
                    "Shows current network bandwidth usage by process (-n prevents DNS lookups)",
                    "iftop -n  # Show numeric IP addresses\niftop -P  # Show ports\niftop -B  # Show bandwidth in bytes",
                    "                 12.5Kb          25.0Kb          37.5Kb          50.0Kb\n─────────────────────────────────────────────────────────────────\n192.168.1.100:22 => 192.168.1.200:12345     8.12Kb    10.2Kb    12.1Kb"
                ),

                "How do you find files modified in the last 24 hours?": Command(
                    "find . -mtime -1",
                    "Finds files modified in the last 24 hours (-mtime -1 means less than 1 day old)",
                    "find . -mtime -1 -type f  # Only files\nfind . -mmin -60  # Modified in last hour\nfind /home -mtime -1 -size +100M  # Large files modified recently",
                    "./documents/report.doc\n./downloads/file.zip\n./logs/system.log"
                ),

                "How do you manage system services?": Command(
                    "systemctl [command] service_name",
                    "Controls and monitors system services using systemd",
                    "systemctl status nginx  # Check service status\nsystemctl start mysql  # Start service\nsystemctl enable ssh  # Enable at boot",
                    "● nginx.service - A high performance web server\n   Loaded: loaded (/lib/systemd/system/nginx.service)\n   Active: active (running) since Thu 2024-12-29 10:00:00 UTC"
                ),

                "How do you analyze system boot time?": Command(
                    "systemd-analyze",
                    "Shows how long the system took to boot and which services took the most time",
                    "systemd-analyze\nsystemd-analyze blame  # Show service startup times\nsystemd-analyze critical-chain  # Show boot chain",
                    "Startup finished in 2.997s (kernel) + 4.299s (userspace) = 7.296s"
                ),

                "How do you check system logs in real-time?": Command(
                    "journalctl -f",
                    "Shows and follows system logs in real-time (-f for follow)",
                    "journalctl -f\njournalctl -u nginx -f  # Follow nginx logs\njournalctl --since '10 minutes ago'",
                    "Dec 29 10:00:01 hostname sshd[1234]: Accepted publickey for user from 192.168.1.100\nDec 29 10:00:05 hostname nginx[5678]: 192.168.1.200 - GET / HTTP/1.1"
                )
            },
            Mode.UNDERSTANDING: {
                "What does 'ls' stand for?": Command(
                    "list",
                    "The ls command lists directory contents. It's one of the most fundamental commands in Unix/Linux.",
                    "ls         # List files\nls -a      # List all files including hidden\nls -l      # Long format listing",
                    "documents/  downloads/  file.txt  pictures/"
                ),

                "What does 'cd' stand for?": Command(
                    "change directory",
                    "The cd command changes your current working directory. It's used for navigation in the filesystem.",
                    "cd Documents     # Go to Documents\ncd ..           # Go up one level\ncd ~            # Go to home directory",
                    "# No output shown when successful"
                ),

                "What does 'pwd' stand for?": Command(
                    "print working directory",
                    "The pwd command displays the full path of your current working directory.",
                    "pwd",
                    "/home/username/Documents"
                ),

                "What does 'rm' stand for?": Command(
                    "remove",
                    "The rm command deletes files and directories. Use with caution as deletion is permanent.",
                    "rm file.txt      # Delete file\nrm -r folder     # Delete folder and contents\nrm -i file.txt   # Interactive delete",
                    "# No output shown when successful"
                ),

                "What does 'cp' stand for?": Command(
                    "copy",
                    "The cp command creates copies of files and directories.",
                    "cp file.txt backup.txt    # Copy file\ncp -r folder1 folder2     # Copy directory",
                    "# No output shown when successful"
                ),

                "What does 'mv' stand for?": Command(
                    "move",
                    "The mv command moves files/directories or renames them if the destination is in the same directory.",
                    "mv file.txt docs/        # Move file\nmv old.txt new.txt      # Rename file",
                    "# No output shown when successful"
                ),

                "What does 'mkdir' stand for?": Command(
                    "make directory",
                    "The mkdir command creates new directories.",
                    "mkdir docs              # Create directory\nmkdir -p a/b/c          # Create parent directories as needed",
                    "# No output shown when successful"
                ),

                "What does 'chmod' stand for?": Command(
                    "change mode",
                    "The chmod command changes the permissions (mode) of files and directories.",
                    "chmod 755 file.txt      # Set specific permissions\nchmod +x script.sh      # Make file executable",
                    "# No output shown when successful"
                ),

                "What does 'chown' stand for?": Command(
                    "change owner",
                    "The chown command changes the owner and group of files/directories.",
                    "chown user:group file.txt   # Change owner and group\nchown -R user folder      # Recursive ownership change",
                    "# No output shown when successful"
                ),

                "What does 'grep' stand for?": Command(
                    "global regular expression print",
                    "The grep command searches for patterns in text using regular expressions.",
                    "grep 'pattern' file.txt     # Search in file\ngrep -r 'text' .           # Recursive search",
                    "matching line 1\nmatching line 2"
                ),

                "What does 'sudo' stand for?": Command(
                    "superuser do",
                    "The sudo command executes commands with superuser (administrator) privileges.",
                    "sudo apt update          # Run system update\nsudo -i                 # Start root shell",
                    "# Output depends on command"
                ),

                "What does 'df' stand for?": Command(
                    "disk free",
                    "The df command shows disk space usage of filesystems.",
                    "df -h           # Human readable sizes\ndf -i           # Show inode information",
                    "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1       100G   50G   50G  50% /"
                ),

                "What does 'du' stand for?": Command(
                    "disk usage",
                    "The du command shows disk space used by files and directories.",
                    "du -sh *        # Size of items in current directory\ndu -h --max-depth=1 /home    # First level usage",
                    "4.0K    file.txt\n156M    Documents"
                ),

                "What does 'ps' stand for?": Command(
                    "process status",
                    "The ps command shows information about active processes.",
                    "ps aux          # Show all processes\nps -ef          # Full format listing",
                    "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"
                ),

                "What does 'ssh' stand for?": Command(
                    "secure shell",
                    "The ssh command provides secure encrypted communication between computers.",
                    "ssh user@host           # Connect to remote host\nssh -p 2222 user@host    # Connect to specific port",
                    "Connected to user@host..."
                ),

                "What does 'scp' stand for?": Command(
                    "secure copy",
                    "The scp command copies files securely between hosts using SSH.",
                    "scp file.txt user@host:~/     # Copy to remote\nscp user@host:file.txt .      # Copy from remote",
                    "file.txt                    100%  123KB  1.1MB/s   00:01"
                ),

                "What does 'tar' stand for?": Command(
                    "tape archive",
                    "The tar command handles tape archive files (though now mostly used for general archiving).",
                    "tar -czf archive.tar.gz files/   # Create archive\ntar -xzf archive.tar.gz        # Extract archive",
                    "# No output shown when using without verbose flag"
                ),

                "What does 'wget' stand for?": Command(
                    "world wide web get",
                    "The wget command downloads files from the web.",
                    "wget https://example.com/file.zip    # Download file\nwget -c URL                      # Continue interrupted download",
                    "100%[===================>] 1,234,567   1.23M/s   in 1.0s"
                ),

                "What does 'sed' stand for?": Command(
                    "stream editor",
                    "The sed command is used for parsing and transforming text using a simple programming language.",
                    "sed 's/old/new/' file.txt     # Replace first occurrence\nsed 's/old/new/g' file.txt    # Replace all occurrences",
                    "# Modified text output"
                ),

                "What does 'awk' stand for?": Command(
                    "aho weinberger kernighan",
                    "Named after its authors, awk is a powerful text processing language.",
                    "awk '{print $1}' file.txt     # Print first column\nawk -F: '{print $1}' /etc/passwd  # Using different delimiter",
                    "column1_data\ncolumn1_data"
                ),

                # Common Flag Meanings
                "What does '-r' commonly mean as a flag?": Command(
                    "recursive",
                    "Applies the command recursively to subdirectories and their contents.",
                    "cp -r folder1 folder2     # Copy directory and contents\ngrep -r pattern /path      # Search in all files recursively",
                    "# Output varies by command"
                ),

                "What does '-f' commonly mean as a flag?": Command(
                    "force",
                    "Forces the command to execute without asking for confirmation.",
                    "rm -f file.txt         # Force delete without prompting\nln -f source target    # Force create link",
                    "# Usually no output shown"
                ),

                "What does '-v' commonly mean as a flag?": Command(
                    "verbose",
                    "Shows detailed output of what the command is doing.",
                    "cp -v file1 file2      # Show copying progress\nrm -v file.txt        # Show what's being removed",
                    "'file1' -> 'file2'\nremoved 'file.txt'"
                ),

                "What does '-h' commonly mean as a flag?": Command(
                    "human readable",
                    "Shows sizes in human readable format (K, M, G instead of bytes).",
                    "ls -lh                # Show file sizes in K/M/G\ndf -h                 # Show disk usage in K/M/G",
                    "total 1.5G\n-rw-r--r-- 1 user group 1.2M Dec 29 10:00 file.txt"
                ),

                "What does '-a' commonly mean as a flag?": Command(
                    "all",
                    "Includes all items, including hidden ones (those starting with .)",
                    "ls -a                  # Show all files including hidden\nps -ax                 # Show all processes",
                    ".hidden_file  visible_file  .config"
                ),

                "What does '-l' mean in 'ls -l'?": Command(
                    "long listing format",
                    "Shows detailed information including permissions, size, owner, and date",
                    "ls -l                  # Long listing\nls -la                 # Long listing including hidden files",
                    "-rw-r--r-- 1 user group 1234 Dec 29 10:00 file.txt"
                ),

                "What does '-p' commonly mean as a flag?": Command(
                    "preserve permissions",
                    "Maintains original file permissions, timestamps, and ownership",
                    "cp -p file1 file2      # Copy while preserving attributes\nrsync -p src dest     # Sync with preserved permissions",
                    "# No output shown when successful"
                ),

                "What does '-i' commonly mean as a flag?": Command(
                    "interactive",
                    "Prompts for confirmation before performing actions",
                    "rm -i file.txt         # Ask before deleting\ncp -i src dest         # Ask before overwriting",
                    "rm: remove 'file.txt'? y"
                ),

                "What does '-x' commonly mean as a flag?": Command(
                    "extract",
                    "Used for extracting archives or excluding patterns",
                    "tar -x archive.tar     # Extract archive\nfind /path -x           # Don't cross filesystem boundaries",
                    "# Extraction output or no output depending on command"
                ),

                "What does '-z' commonly mean as a flag?": Command(
                    "gzip",
                    "Uses gzip compression with the command",
                    "tar -z archive.tar.gz  # Use gzip compression\ngrep -z pattern        # Search in compressed files",
                    "# No direct output for compression"
                ),

                "What does '-e' commonly mean as a flag?": Command(
                    "enable",
                    "Enables features or interprets escape sequences",
                    "echo -e \"\\n\"         # Enable interpretation of backslash escapes\nservice -e             # Show enabled services",
                    "# Output depends on specific command"
                ),

                "What does '-q' commonly mean as a flag?": Command(
                    "quiet",
                    "Suppresses normal output, showing only errors",
                    "wget -q file.txt       # Download quietly\napt-get -q update      # Quiet package update",
                    "# No output unless errors occur"
                ),

                "What does '-c' commonly mean as a flag?": Command(
                    "count",
                    "Counts occurrences or shows count of items",
                    "grep -c pattern file   # Count matching lines\nwc -c file.txt        # Count bytes in file",
                    "42  # Number of matches or items"
                ),

                "What does '-d' commonly mean as a flag?": Command(
                    "directory",
                    "Applies operation to directories or specifies directory",
                    "ls -d */              # List only directories\nrm -d emptydir        # Remove empty directory",
                    "dir1/  dir2/  dir3/"
                ),

                "What does '-s' commonly mean as a flag?": Command(
                    "silent",
                    "Similar to quiet, suppresses output and progress information",
                    "wget -s URL           # Silent mode download\ngrep -s pattern file   # Suppress error messages",
                    "# No output shown"
                ),

                "What does '-t' commonly mean as a flag?": Command(
                    "time",
                    "Related to time operations or sorting",
                    "ls -t                 # Sort by modification time\ntouch -t 202412291200 file  # Set specific timestamp",
                    "# Output shows time-sorted items"
                ),

                "What does '-u' commonly mean as a flag?": Command(
                    "update",
                    "Updates files or shows updated information",
                    "cp -u src dest        # Copy only when source is newer\napt-get -u upgrade    # Show what would be upgraded",
                    "# Shows update information"
                ),

                "What does '-w' commonly mean as a flag?": Command(
                    "width",
                    "Sets or deals with output width",
                    "pr -w 80 file.txt     # Set page width\nps -w                # Wide output format",
                    "# Output formatted to specified width"
                ),

                "What does '-y' commonly mean as a flag?": Command(
                    "yes to all prompts",
                    "Automatically answers yes to all prompts",
                    "apt-get -y install    # Install without prompting\nrm -y files          # Remove without confirmation",
                    "# Proceeds without interactive prompts"
                ),

                "What does '-n' commonly mean as a flag?": Command(
                    "line numbers",
                    "Shows line numbers in output",
                    "cat -n file.txt       # Show numbered lines\nhead -n 5 file.txt    # Show first 5 lines",
                    "     1\tFirst line\n     2\tSecond line"
                ),

                "What does '-m' commonly mean as a flag?": Command(
                    "message",
                    "Specifies a message or deals with message formatting",
                    "git commit -m \"msg\"   # Commit with message\nwrite -m user \"msg\"   # Send message to user",
                    "# Output depends on command context"
                ),

                "What does '-b' commonly mean as a flag?": Command(
                    "backup",
                    "Creates backup before performing operation",
                    "cp -b file1 file2     # Copy with backup\nsed -b -i 's/old/new/' file  # Edit with backup",
                    "# Original file backed up as file~"
                ),

                "What does '-k' commonly mean as a flag?": Command(
                    "keep files",
                    "Keeps files or maintains existing settings",
                    "rm -k                 # Keep files matching pattern\ntar -k                # Don't overwrite existing files",
                    "# No output shown when successful"
                )
            },
            Mode.VARIABLES: {
                "What is the shell variable for current user?": Command(
                    "$USER",
                    "Contains the username of the current user. Commonly used in scripts to check who is running them or customize behavior per user.",
                    "echo \"Hello $USER\"\nif [ \"$USER\" = \"root\" ]; then echo \"Running as root\"; fi",
                    "Hello john"
                ),
                
                "What is the shell variable for home directory?": Command(
                    "$HOME",
                    "Contains the path to current user's home directory. Essential for scripts that need to reference user-specific files.",
                    "echo \"Your home is $HOME\"\ncd $HOME\ntouch $HOME/.config",
                    "Your home is /home/john"
                ),

                "What is the shell variable for current working directory?": Command(
                    "$PWD",
                    "Contains the full path of current working directory. Updates automatically when you change directories.",
                    "echo \"You are in $PWD\"\nls $PWD/subdirectory",
                    "You are in /home/john/projects"
                ),

                "What is the shell variable for hostname?": Command(
                    "$HOSTNAME",
                    "Contains the system's host name. Useful for scripts that need to identify the current machine.",
                    "echo \"Running on $HOSTNAME\"\nif [ \"$HOSTNAME\" = \"server1\" ]; then echo \"Production server\"; fi",
                    "Running on server1.example.com"
                ),

                "What is the shell variable for system path?": Command(
                    "$PATH",
                    "Lists directories where shell looks for commands. Each directory is separated by colons.",
                    "echo $PATH\nPATH=$PATH:/new/bin  # Add new directory\necho $PATH | tr ':' '\\n'  # Show each path on new line",
                    "/usr/local/bin:/usr/bin:/bin:/usr/sbin"
                ),

                "What is the shell variable for current date?": Command(
                    "$DATE",
                    "Must be set manually using the date command. Often used for timestamping files and logs.",
                    "DATE=$(date +%Y-%m-%d)\necho \"Today is $DATE\"\ntouch backup_$DATE.tar.gz",
                    "Today is 2024-12-29"
                ),

                "What is the shell variable for current time?": Command(
                    "$TIME",
                    "Must be set manually using the date command. Used for precise timestamps in logs and file names.",
                    "TIME=$(date +%H:%M:%S)\necho \"Current time: $TIME\"\necho \"Log entry\" >> log_$TIME.txt",
                    "Current time: 14:30:45"
                ),

                "What is the shell variable for number of arguments?": Command(
                    "$#",
                    "Contains the number of arguments passed to a script. Essential for argument validation.",
                    "echo \"Got $# arguments\"\nif [ $# -lt 2 ]; then echo \"Need at least 2 arguments\"; exit 1; fi",
                    "Got 3 arguments"
                ),

                "What is the shell variable for all script arguments?": Command(
                    "$@",
                    "Contains all arguments passed to script as separate strings. Preserves spaces in arguments.",
                    "for arg in \"$@\"; do\n    echo \"Processing: $arg\"\ndone",
                    "Processing: file one.txt\nProcessing: file two.txt"
                ),

                "What is the shell variable for script name?": Command(
                    "$0",
                    "Contains the name of the current script as it was called. Useful for script self-reference.",
                    "echo \"Running script: $0\"\nbasename=$(basename \"$0\")",
                    "Running script: ./backup.sh"
                ),

                "What is the shell variable for current shell?": Command(
                    "$SHELL",
                    "Contains the path to current user's login shell. Used to determine which shell is running.",
                    "echo \"Using shell: $SHELL\"\nif [ \"$SHELL\" = \"/bin/bash\" ]; then echo \"Bash features available\"; fi",
                    "Using shell: /bin/bash"
                ),

                "What is the shell variable for previous working directory?": Command(
                    "$OLDPWD",
                    "Contains the previous working directory path. Updated whenever you change directories.",
                    "cd /tmp\necho \"Previous directory was $OLDPWD\"\ncd -  # Returns to previous directory",
                    "Previous directory was /home/john"
                ),

                "What is the shell variable for system type?": Command(
                    "$OSTYPE",
                    "Contains the operating system type. Useful for writing cross-platform compatible scripts.",
                    "case \"$OSTYPE\" in\n  linux*) echo \"Linux\";;\\n  darwin*) echo \"Mac\";;\\n  *) echo \"Other\";;\nesac",
                    "Linux"
                ),

                "What is the shell variable for user ID?": Command(
                    "$UID",
                    "Contains the numeric user ID of current user. Often used to check if script is running as root (UID 0).",
                    "echo \"Your UID is $UID\"\nif [ $UID -eq 0 ]; then echo \"Running as root\"; fi",
                    "Your UID is 1000"
                ),

                "What is the shell variable for exit status of last command?": Command(
                    "$?",
                    "Contains the exit status of last command (0 means success, non-zero means failure).",
                    "grep \"pattern\" file.txt\nif [ $? -ne 0 ]; then echo \"Pattern not found\"; fi",
                    "Pattern not found"
                ),

                "What is the shell variable for process ID?": Command(
                    "$PID",
                    "Contains process ID of current shell. Useful for creating unique temporary files.",
                    "echo \"Shell PID: $$\"\ntmp_file=\"/tmp/script_$$.tmp\"",
                    "Shell PID: 1234"
                ),

                "What is the shell variable for parent process ID?": Command(
                    "$PPID",
                    "Contains process ID of parent process that started this script or shell.",
                    "echo \"Parent process: $PPID\"\nps -p $PPID  # Show parent process details",
                    "Parent process: 1200"
                ),

                "What is the shell variable for random number?": Command(
                    "$RANDOM",
                    "Generates random integer between 0 and 32767. Useful for temporary files and simple randomization.",
                    "echo $RANDOM  # Random number\nrand=$((RANDOM % 100))  # Random number 0-99",
                    "12345"
                ),

                "What is the shell variable for number of seconds shell has run?": Command(
                    "$SECONDS",
                    "Contains number of seconds shell has been running. Good for timing script execution.",
                    "start=$SECONDS\nsleep 5\necho \"Took $((SECONDS - start)) seconds\"",
                    "Took 5 seconds"
                ),

                "What is the shell variable for line number in script?": Command(
                    "$LINENO",
                    "Contains current line number in script. Useful for debugging and error messages.",
                    "echo \"Error on line $LINENO\"\nfunc() { echo \"Called from line $LINENO\"; }",
                    "Error on line 42"
                ),

                "What is the shell variable for terminal type?": Command(
                    "$TERM",
                    "Specifies the terminal type being used. Important for scripts that use terminal-specific features.",
                    "echo \"Terminal: $TERM\"\nif [ \"$TERM\" = \"xterm-256color\" ]; then use_colors; fi",
                    "Terminal: xterm-256color"
                ),

                "What is the shell variable for default editor?": Command(
                    "$EDITOR",
                    "Contains path to default text editor. Used by scripts that need to open files for editing.",
                    "echo \"Editor: $EDITOR\"\n$EDITOR filename.txt  # Open file in editor",
                    "Editor: /usr/bin/vim"
                ),

                "What is the shell variable for user's language?": Command(
                    "$LANG",
                    "Specifies user's language and locale settings. Affects output formatting of many commands.",
                    "echo \"Language: $LANG\"\nif [ \"$LANG\" = \"en_US.UTF-8\" ]; then echo \"Using US English\"; fi",
                    "Language: en_US.UTF-8"
                ),

                "What is the shell variable for shell options?": Command(
                    "$SHELLOPTS",
                    "Contains a colon-separated list of enabled shell options. Useful for checking shell behavior settings.",
                    "echo $SHELLOPTS\nif [[ $SHELLOPTS =~ errexit ]]; then echo \"Exit on error is enabled\"; fi",
                    "braceexpand:errexit:hashall:interactive-comments"
                ),

                "What is the shell variable for bash version?": Command(
                    "$BASH_VERSION",
                    "Contains the version of bash being used. Helpful for version-specific feature checks.",
                    "echo \"Bash version: $BASH_VERSION\"\nif [[ \"${BASH_VERSION:0:1}\" -ge 4 ]]; then echo \"Modern bash features available\"; fi",
                    "Bash version: 5.1.16(1)-release"
                ),

                "What is the shell variable for command history file size?": Command(
                    "$HISTFILESIZE",
                    "Maximum number of lines in history file. Controls how many commands are saved between sessions.",
                    "echo \"History file can store $HISTFILESIZE commands\"\nHISTFILESIZE=10000  # Set new size",
                    "History file can store 2000 commands"
                ),

                "What is the shell variable for history timestamp format?": Command(
                    "$HISTTIMEFORMAT",
                    "Format string for timestamps in history. Must be set to enable timestamp display.",
                    "HISTTIMEFORMAT=\"%F %T \"\nhistory | head -n 1",
                    "2024-12-29 14:30:45 ls -la"
                ),

                "What is the shell variable for last argument of previous command?": Command(
                    "$_",
                    "Contains the last argument of the previous command. Updates automatically after each command.",
                    "mkdir new_directory\ncd $_  # Changes to new_directory\necho \"Last arg was: $_\"",
                    "Last arg was: new_directory"
                ),

                "What is the shell variable for number of columns in terminal?": Command(
                    "$COLUMNS",
                    "Contains the current width of terminal in columns. Updates if terminal is resized.",
                    "echo \"Terminal width: $COLUMNS columns\"\nprintf '=%.0s' $(seq 1 $COLUMNS)  # Print line across screen",
                    "Terminal width: 80 columns"
                ),

                "What is the shell variable for number of lines in terminal?": Command(
                    "$LINES",
                    "Contains the current height of terminal in lines. Updates if terminal is resized.",
                    "echo \"Terminal height: $LINES lines\"\nif [ $LINES -lt 24 ]; then echo \"Small terminal\"; fi",
                    "Terminal height: 24 lines"
                ),

                "What is the shell variable for machine hardware name?": Command(
                    "$MACHTYPE",
                    "Contains a string describing the machine architecture bash is running on.",
                    "echo \"Machine type: $MACHTYPE\"\ncase $MACHTYPE in *64*) echo \"64-bit system\";; esac",
                    "Machine type: x86_64-pc-linux-gnu"
                ),

                "What is the shell variable for prompt string?": Command(
                    "$PS1",
                    "Primary prompt string. Controls what your command prompt looks like.",
                    "echo \"Current prompt: $PS1\"\nPS1='\\u@\\h:\\w\\$ '  # Set user@host:directory$ format",
                    "Current prompt: \\u@\\h:\\w\\$"
                ),

                "What is the shell variable for secondary prompt?": Command(
                    "$PS2",
                    "Secondary prompt string, used for command continuation lines.",
                    "echo \"Continuation prompt: $PS2\"\nPS2='> '  # Set simple continuation prompt",
                    "Continuation prompt: >"
                ),

                "What is the shell variable for mail check interval?": Command(
                    "$MAILCHECK",
                    "Specifies how often (in seconds) bash checks for new mail.",
                    "echo \"Checking mail every $MAILCHECK seconds\"\nMAILCHECK=60  # Check every minute",
                    "Checking mail every 60 seconds"
                ),

                "What is the shell variable for command search path?": Command(
                    "$CDPATH",
                    "Colon-separated list of directories for the cd command to search in.",
                    "echo $CDPATH\nCDPATH=.:~:/usr/local  # Set search path for cd",
                    ".:/home/user:/usr/local"
                ),

                "What is the shell variable for input field separator?": Command(
                    "$IFS",
                    "Input Field Separator. Determines how bash splits words during expansion.",
                    "old_IFS=$IFS\nIFS=','  # Split on commas\necho \"a,b,c\" | while read -r x y z; do echo \"$x|$y|$z\"; done\nIFS=$old_IFS",
                    "a|b|c"
                ),

                "What is the shell variable for command not found handling?": Command(
                    "$COMMAND_NOT_FOUND_HANDLE",
                    "Function called when a command is not found. Can be set to provide custom behavior.",
                    "command_not_found_handle() { echo \"Custom error: command '$1' not found!\"; return 127; }",
                    "Custom error: command 'xyz' not found!"
                ),

                "What is the shell variable for debug trap?": Command(
                    "$BASH_COMMAND",
                    "Contains the command currently being executed (mainly used in DEBUG trap).",
                    "trap 'echo \"executing: $BASH_COMMAND\"' DEBUG\nls -l  # Will show command before execution",
                    "executing: ls -l"
                ),

                "What is the shell variable for subprocess count?": Command(
                    "$BASH_SUBSHELL",
                    "Indicates how many subshell levels deep you are.",
                    "echo \"Level: $BASH_SUBSHELL\"\n(echo \"Subshell level: $BASH_SUBSHELL\")",
                    "Level: 0\nSubshell level: 1"
                ),

                "What is the shell variable for temporary directory?": Command(
                    "$TMPDIR",
                    "Directory for temporary files. Used by many programs to store temporary data.",
                    "echo \"Temp dir: $TMPDIR\"\ntemp_file=\"$TMPDIR/myapp.$$.tmp\"",
                    "Temp dir: /tmp"
                ),

                "What is the shell variable for system load average?": Command(
                    "$LOADAVG",
                    "Contains system load averages (if your shell supports it).",
                    "echo \"System load: $LOADAVG\"  # May need to enable shell option",
                    "System load: 0.15 0.10 0.05"
                ),

                "What is the shell variable for process substitution count?": Command(
                    "$BASHPID",
                    "Process ID of current bash process. Different from $$ in subshells.",
                    "echo \"Main PID: $$\"\necho \"Actual PID: $BASHPID\"\n(echo \"Subshell BASHPID: $BASHPID\")",
                    "Main PID: 1234\nActual PID: 1234\nSubshell BASHPID: 1235"
                )
            },
            Mode.SCRIPTING: {
                "How do you write a shebang line for a bash script?": Command(
                    "#!/bin/bash",
                    "The shebang line tells the system which interpreter to use for the script. Always should be the first line.",
                    "#!/bin/bash\n\necho \"Hello, World!\"",
                    "# Creates an executable bash script"
                ),

                "How do you create an if statement checking if a file exists?": Command(
                    "if [ -f filename ]; then commands; fi",
                    "Checks if a regular file exists before performing operations on it.",
                    "if [ -f \"config.txt\" ]; then\n    echo \"Config exists\"\nelse\n    echo \"No config found\"\nfi",
                    "No config found"
                ),

                "How do you write a for loop iterating over a list of files?": Command(
                    "for file in *; do commands; done",
                    "Loops over files in current directory. The * wildcard can be replaced with specific patterns.",
                    "for file in *.txt; do\n    echo \"Processing $file\"\n    cat \"$file\"\ndone",
                    "Processing doc1.txt\nProcessing doc2.txt"
                ),

                "How do you define a function in a bash script?": Command(
                    "function_name() { commands; }",
                    "Creates a reusable function. Can also be written as 'function function_name { commands; }'",
                    "backup_file() {\n    cp \"$1\" \"${1}.bak\"\n    echo \"Backed up $1\"\n}",
                    "# Function can then be called: backup_file myfile.txt"
                ),

                "How do you read input from the user?": Command(
                    'read variable_name',
                    "Reads user input into a variable. Can include a prompt with -p flag.",
                    'read -p "Enter your name: " username\necho "Hello, $username!"',
                    "Enter your name: John\nHello, John!"
                ),

                "How do you check if a command was successful?": Command(
                    'if [ $? -eq 0 ]; then commands; fi',
                    "Checks the exit status of the last command. 0 means success, non-zero means failure.",
                    'grep "pattern" file.txt\nif [ $? -eq 0 ]; then\n    echo "Pattern found"\nelse\n    echo "Pattern not found"\nfi',
                    "Pattern not found"
                ),

                "How do you write a while loop reading a file line by line?": Command(
                    'while read -r line; do commands; done < file',
                    "Reads file content line by line. The -r prevents backslash interpretation.",
                    'while read -r line; do\n    echo "Line: $line"\ndone < input.txt',
                    "Line: First line\nLine: Second line"
                ),

                "How do you check if required arguments are provided?": Command(
                    'if [ $# -lt required_number ]; then commands; fi',
                    "Checks if script received enough command-line arguments.",
                    'if [ $# -lt 2 ]; then\n    echo "Usage: $0 arg1 arg2"\n    exit 1\nfi',
                    "Usage: ./script.sh arg1 arg2"
                ),

                "How do you handle script errors?": Command(
                    'set -e',
                    "Makes script exit immediately if any command fails. Often combined with -u for undefined variables.",
                    'set -e\nset -u\n\ncommand1\ncommand2  # Script stops if either fails',
                    "# Script exits on first error"
                ),

                "How do you create a case statement?": Command(
                    'case $variable in pattern) commands;; esac',
                    "Creates a switch-like statement to handle multiple conditions.",
                    'case "$answer" in\n  yes|Y) echo "Proceeding";;\\n  no|N) echo "Aborting";;\\n  *) echo "Invalid input";;\\nesac',
                    "Proceeding"
                ),

                "How do you create a select menu?": Command(
                    'select choice in options; do commands; done',
                    "Creates an interactive numbered menu for user selection.",
                    'select opt in "Option 1" "Option 2" "Exit"; do\n    case $opt in\n        "Exit") break;;\n        *) echo "Selected: $opt";;\n    esac\ndone',
                    "1) Option 1\n2) Option 2\n3) Exit\n#? "
                ),

                "How do you trap signals in a script?": Command(
                    'trap command_or_function SIGNALS',
                    "Sets up signal handlers for script interruption or termination.",
                    'trap "echo Cleaning up...; rm -f temp_file" EXIT\ntrap "echo Interrupted; exit 1" INT TERM',
                    "Cleaning up...\n# When script exits"
                ),

                "How do you parse command line options?": Command(
                    'while getopts "options" var; do case $var in ...; esac done',
                    "Processes command-line flags and options using getopts.",
                    'while getopts "f:v" opt; do\n    case $opt in\n        f) file="$OPTARG";;\\n        v) verbose=true;;\n    esac\ndone',
                    "# Script can now handle -f file -v"
                ),

                "How do you implement a countdown timer?": Command(
                    'for ((i=number; i>0; i--)); do commands; done',
                    "Creates a countdown loop with sleep for timing.",
                    'for ((i=5; i>0; i--)); do\n    echo "$i..."\n    sleep 1\ndone\necho "Go!"',
                    "5...\n4...\n3...\n2...\n1...\nGo!"
                ),

                "How do you check if a directory is empty?": Command(
                    'if [ -z "$(ls -A directory)" ]; then commands; fi',
                    "Checks if a directory contains any files or subdirectories.",
                    'if [ -z "$(ls -A /path/to/dir)" ]; then\n    echo "Directory is empty"\nelse\n    echo "Directory contains files"\nfi',
                    "Directory is empty"
                ),

                "How do you create a temporary file safely?": Command(
                    'mktemp',
                    "Creates a unique temporary file and returns its name.",
                    'temp_file=$(mktemp)\necho "Data" > "$temp_file"\n# Process file\nrm "$temp_file"',
                    "/tmp/tmp.XXXXXXXXXX"
                ),

                "How do you handle script cleanup on exit?": Command(
                    'trap cleanup_function EXIT',
                    "Ensures cleanup code runs when script exits for any reason.",
                    'cleanup() {\n    rm -f "$temp_file"\n    echo "Cleaned up"\n}\ntrap cleanup EXIT',
                    "Cleaned up\n# When script exits"
                ),

                "How do you process files in parallel?": Command(
                    'parallel command ::: arguments',
                    "Uses GNU parallel to process multiple items simultaneously.",
                    'ls *.jpg | parallel convert {} {.}.png\n# Or\nparallel gzip ::: *.txt',
                    "# Processes all files in parallel"
                ),

                "How do you validate numeric input?": Command(
                    'if [[ $var =~ ^[0-9]+$ ]]; then commands; fi',
                    "Uses regex to check if a variable contains only numbers.",
                    'read -p "Enter a number: " num\nif [[ $num =~ ^[0-9]+$ ]]; then\n    echo "Valid number"\nelse\n    echo "Not a number"\nfi',
                    "Enter a number: 42\nValid number"
                ),

                "How do you create a log file with timestamps?": Command(
                    'exec 1> >(while read -r line; do echo "$(date): $line"; done) > logfile',
                    "Redirects all output to a log file with timestamps.",
                    'exec 1> >(while read -r line; do\n    echo "$(date +"%Y-%m-%d %H:%M:%S"): $line"\ndone) > script.log',
                    "2024-12-29 14:30:45: Script started"
                )
            },
            Mode.API: {
                "How do you make a basic GET request to an API endpoint?": Command(
                    "curl https://api.example.com/data",
                    "Makes a simple GET request to fetch data from an API endpoint",
                    "curl https://api.example.com/data\ncurl -i https://api.example.com/data  # Show headers",
                    '{"status": "success", "data": {"id": 1, "name": "example"}}'
                ),

                "How do you handle URL parameters in a GET request?": Command(
                    'curl "https://api.example.com/search?query=term&page=1"',
                    "Sends GET request with URL parameters (note the quotes around URL)",
                    'curl "https://api.example.com/products?category=electronics&sort=price"\ncurl -G --data-urlencode "query=search term" https://api.example.com/search',
                    '{"results": [...], "page": 1, "total": 100}'
                ),

                "How do you show response headers in a GET request?": Command(
                    "curl -I https://api.example.com",
                    "Shows only the response headers from the server (-I for headers only)",
                    "curl -I https://api.github.com\ncurl -i https://api.github.com  # Show headers and content",
                    "HTTP/2 200\nserver: GitHub.com\ncontent-type: application/json\nx-ratelimit-limit: 60"
                ),

                "How do you make a PUT request to update data?": Command(
                    'curl -X PUT -H "Content-Type: application/json" -d \'{"key":"updated_value"}\' https://api.example.com/resource/1',
                    "Sends PUT request to update existing resource",
                    'curl -X PUT \\\n  -H "Content-Type: application/json" \\\n  -d \'{\n    "title": "Updated Title"\n  }\' \\\n  https://api.example.com/posts/1',
                    '{"id": 1, "title": "Updated Title", "message": "Resource updated"}'
                ),

                "How do you delete a resource using curl?": Command(
                    "curl -X DELETE https://api.example.com/resource/1",
                    "Sends DELETE request to remove a resource",
                    "curl -X DELETE https://api.example.com/posts/1\ncurl -v -X DELETE https://api.example.com/comments/5  # Verbose output",
                    '{"status": "success", "message": "Resource deleted"}'
                ),

                "How do you make a POST request with JSON data?": Command(
                    'curl -X POST -H "Content-Type: application/json" -d \'{"key":"value"}\' https://api.example.com/create',
                    "Sends POST request with JSON data (-X specify method, -H add header, -d specify data)",
                    'curl -X POST \\\n  -H "Content-Type: application/json" \\\n  -d \'{"username":"john","password":"secret"}\' \\\n  https://api.example.com/login',
                    '{"status": "success", "token": "eyJhbG..."}'
                ),

                "How do you make an authenticated API request?": Command(
                    'curl -H "Authorization: Bearer YOUR_TOKEN" https://api.example.com/secure',
                    "Makes API request with authentication token in header",
                    'curl -H "Authorization: Bearer eyJhbG..." https://api.example.com/user/profile\n\n# Save token in variable:\nTOKEN="eyJhbG..."\ncurl -H "Authorization: Bearer $TOKEN" https://api.example.com/data',
                    '{"user": "john_doe", "email": "john@example.com"}'
                ),

                "How do you see detailed request/response information?": Command(
                    "curl -v https://api.example.com",
                    "Shows verbose output including request/response headers and SSL details",
                    "curl -v -X POST -d 'data' https://api.example.com\ncurl --trace-ascii debug.txt https://api.example.com  # Even more detail",
                    "* Connected to api.example.com\n> GET / HTTP/1.1\n> Host: api.example.com\n< HTTP/1.1 200 OK\n< Content-Type: application/json"
                ),

                "How do you retry failed requests?": Command(
                    "curl --retry n https://api.example.com",
                    "Retries failed requests up to specified number of times",
                    "curl --retry 5 --retry-delay 2 https://api.example.com  # Wait 2 seconds between retries\ncurl --retry 3 --retry-connrefused https://api.example.com",
                    "# Will retry up to 3 times on failure"
                ),

                "How do you query OpenRouter's API for a chat completion?": Command(
                    'curl -X POST https://openrouter.ai/api/v1/chat/completions \\\n  -H "Authorization: Bearer $OPENROUTER_KEY" \\\n  -H "Content-Type: application/json" \\\n  -d \'{"model": "MODEL_NAME", "messages": [{"role": "user", "content": "Hello"}]}\'',
                    "Sends a chat completion request to OpenRouter API with necessary headers and JSON payload",
                    'curl -X POST https://openrouter.ai/api/v1/chat/completions \\\n  -H "Authorization: Bearer $OPENROUTER_KEY" \\\n  -H "HTTP-Referer: Your approved site" \\\n  -H "Content-Type: application/json" \\\n  -d \'{\n    "model": "mistralai/mistral-7b-instruct",\n    "messages": [{"role": "user", "content": "Tell me a joke"}]\n  }\'',
                    '{\n  "id": "gen-123abc",\n  "choices": [{\n    "message": {\n      "role": "assistant",\n      "content": "Why did the developer go broke? Because he used up all his cache!"\n    }\n  }]\n}'
                ),

                "How do you upload a file using curl?": Command(
                    'curl -F "file=@filename.txt" https://api.example.com/upload',
                    "Uploads file using multipart/form-data (-F for form data, @ to specify file)",
                    'curl -F "image=@photo.jpg" https://api.example.com/upload\ncurl -F "file=@document.pdf" -F "type=report" https://api.example.com/upload',
                    '{"status": "success", "url": "https://example.com/uploads/filename.txt"}'
                ),

                "How do you download and save a file using curl?": Command(
                    "curl -o filename.txt https://example.com/path/to/file",
                    "Downloads file and saves it with specified name (-o output to file)",
                    "curl -o program.zip https://example.com/downloads/program.zip\ncurl -O https://example.com/file.txt  # Keep original filename",
                    "  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\n                                 Dload  Upload   Total   Spent    Left  Speed\n100 1234k  100 1234k    0     0   102k      0  0:00:12  0:00:12  --:--:-- 125k"
                ),

                "How do you save API response to a file?": Command(
                    "curl -o response.json https://api.example.com/data",
                    "Saves API response to specified file (-o output to file)",
                    "curl -o users.json https://api.example.com/users\ncurl https://api.example.com/data > response.json  # Alternative method",
                    "# File saved as response.json containing API response"
                ),

                "How do you make a request with custom timeout?": Command(
                    "curl --connect-timeout 10 --max-time 30 https://api.example.com",
                    "Sets connection and total transfer timeouts in seconds",
                    "curl --connect-timeout 5 --max-time 20 https://slow-api.example.com\ncurl --max-time 10 https://api.example.com/large-file",
                    "# Will timeout if connection takes >10s or total time >30s"
                ),

                "How do you make a request with client certificate authentication?": Command(
                    "curl --cert client.pem --key client.key https://api.example.com/secure",
                    "Makes request using client certificate authentication",
                    "curl --cert client.pem --key client.key --cacert ca.pem https://api.example.com\ncurl --cert client.p12:password -X POST https://api.example.com/secure",
                    '{"status": "authenticated", "client": "verified"}'
                ),

                "How do you follow redirects with curl?": Command(
                    "curl -L https://example.com/redirecting-url",
                    "Follows HTTP redirects to final destination (-L location)",
                    "curl -L https://git.io/shortened-url\ncurl -IL https://example.com  # Show headers and follow redirects",
                    "HTTP/1.1 302 Found\nLocation: https://final-destination.com\n\nHTTP/1.1 200 OK\n<html>Final content</html>"
                )
            },
            Mode.GIT: {
                "How do you initialize a new Git repository?": Command(
                    "git init",
                    "Creates a new Git repository in the current directory, initializing the .git folder",
                    "git init\ngit init project_name  # Initialize in new directory",
                    "Initialized empty Git repository in /path/to/project/.git/"
                ),

                "How do you clone a remote repository?": Command(
                    "git clone repository_url",
                    "Creates a copy of a remote repository on your local machine",
                    "git clone https://github.com/username/repo.git\ngit clone git@github.com:username/repo.git  # Using SSH",
                    "Cloning into 'repo'...\nremote: Counting objects: 100, done.\nReceiving objects: 100%"
                ),

                "How do you add all changes to staging?": Command(
                    "git add .",
                    "Adds all modified and new files in the current directory to the staging area",
                    "git add .\ngit add -A  # Add all changes including deletions\ngit add '*.py'  # Add all Python files",
                    "# No output if successful"
                ),

                "How do you commit staged changes with a message?": Command(
                    'git commit -m "message"',
                    "Creates a new commit with the staged changes and a descriptive message",
                    'git commit -m "Add new feature"\ngit commit -am "Fix bug"  # Add and commit in one step',
                    "[main 5d6d8f9] Add new feature\n 2 files changed, 35 insertions(+)"
                ),

                "How do you check the status of your working directory?": Command(
                    "git status",
                    "Shows the state of your working directory and staging area",
                    "git status\ngit status -s  # Short format",
                    "On branch main\nYour branch is up to date with 'origin/main'\nChanges not staged for commit:\n  modified: file.txt"
                ),

                "How do you view commit history?": Command(
                    "git log",
                    "Shows a log of all commits in the current branch",
                    "git log\ngit log --oneline  # Compact format\ngit log --graph  # Show branch structure",
                    "commit 5d6d8f9...\nAuthor: John Doe\nDate: Thu Dec 29 10:00:00 2024\n\n    Add new feature"
                ),

                "How do you create and switch to a new branch?": Command(
                    "git checkout -b branch_name",
                    "Creates a new branch and switches to it immediately",
                    "git checkout -b feature/login\ngit checkout -b bugfix/issue-123 main  # Branch from main",
                    "Switched to a new branch 'feature/login'"
                ),

                "How do you merge a branch into current branch?": Command(
                    "git merge branch_name",
                    "Merges specified branch into the current branch",
                    "git merge feature/login\ngit merge --no-ff feature/login  # Create merge commit always",
                    "Fast-forward\n file.txt | 2 +-"
                ),

                "How do you fetch updates from remote?": Command(
                    "git fetch origin",
                    "Downloads objects and refs from remote repository",
                    "git fetch origin\ngit fetch --all  # Fetch from all remotes",
                    "remote: Counting objects: 5, done.\nUnpacking objects: 100%"
                ),

                "How do you pull changes from remote branch?": Command(
                    "git pull origin branch_name",
                    "Fetches and merges changes from remote branch",
                    "git pull origin main\ngit pull --rebase origin main  # Rebase instead of merge",
                    "Updating 5d6d8f9..123abc\nFast-forward"
                ),

                "How do you push changes to remote?": Command(
                    "git push origin branch_name",
                    "Uploads local branch commits to remote repository",
                    "git push origin main\ngit push -u origin feature/login  # Set upstream",
                    "To github.com:username/repo.git\n   5d6d8f9..123abc  main -> main"
                ),

                "How do you discard local changes in a file?": Command(
                    "git checkout -- filename",
                    "Discards changes in working directory, reverting file to last commit",
                    "git checkout -- file.txt\ngit checkout -- .  # Discard all changes",
                    "# No output if successful"
                ),

                "How do you remove a file from staging?": Command(
                    "git reset HEAD filename",
                    "Unstages a file while preserving its contents",
                    "git reset HEAD file.txt\ngit reset HEAD .  # Unstage all changes",
                    "Unstaged changes after reset:\nM       file.txt"
                ),

                "How do you view changes in a file?": Command(
                    "git diff filename",
                    "Shows changes between working directory and staging area",
                    "git diff file.txt\ngit diff --staged  # View staged changes\ngit diff HEAD  # All changes",
                    "diff --git a/file.txt b/file.txt\n--- a/file.txt\n+++ b/file.txt\n@@ -1,3 +1,3 @@"
                ),

                "How do you list all branches?": Command(
                    "git branch",
                    "Shows all local branches, with current branch marked with asterisk",
                    "git branch\ngit branch -a  # Show all branches including remote\ngit branch -v  # Show last commit on each branch",
                    "* main\n  feature/login\n  bugfix/issue-123"
                ),

                "How do you undo the last commit?": Command(
                    "git reset HEAD~1",
                    "Moves HEAD and branch pointer back one commit, preserving changes as unstaged",
                    "git reset HEAD~1\ngit reset --hard HEAD~1  # Discard changes completely",
                    "Unstaged changes after reset:\nM       file.txt"
                ),
                "How do you view all remote repositories?": Command(
                    "git remote -v",
                    "Shows all remote repositories with their URLs (fetch and push)",
                    "git remote -v\ngit remote show origin  # Detailed info about 'origin'",
                    "origin  https://github.com/username/repo.git (fetch)\norigin  https://github.com/username/repo.git (push)"
                ),

                "How do you add a new remote repository?": Command(
                    "git remote add name url",
                    "Adds a new remote repository with specified name and URL",
                    "git remote add upstream https://github.com/original/repo.git\ngit remote add origin git@github.com:username/repo.git",
                    "# No output if successful"
                ),

                "How do you change a remote repository URL?": Command(
                    "git remote set-url name new_url",
                    "Updates the URL of an existing remote repository",
                    "git remote set-url origin https://github.com/username/new-repo.git\ngit remote set-url origin git@github.com:username/repo.git  # Switch to SSH",
                    "# No output if successful"
                ),

                "How do you remove a remote repository?": Command(
                    "git remote remove name",
                    "Removes a remote repository from local configuration",
                    "git remote remove upstream\ngit remote rm origin  # Alternative syntax",
                    "# No output if successful"
                ),

                "How do you configure your Git username globally?": Command(
                    'git config --global user.name "Your Name"',
                    "Sets your name for all Git repositories on this system",
                    'git config --global user.name "John Doe"\ngit config user.name  # Check current setting',
                    "John Doe"
                ),

                "How do you configure your Git email globally?": Command(
                    'git config --global user.email "email@example.com"',
                    "Sets your email for all Git repositories on this system",
                    'git config --global user.email "john@example.com"\ngit config user.email  # Check current setting',
                    "john@example.com"
                ),

                "How do you set up a global Git ignore file?": Command(
                    'git config --global core.excludesfile ~/.gitignore_global',
                    "Specifies a global ignore file for all Git repositories",
                    'git config --global core.excludesfile ~/.gitignore_global\necho ".DS_Store" >> ~/.gitignore_global',
                    "# No output if successful"
                ),

                "How do you rename a remote branch?": Command(
                    "git branch -m old_name new_name",
                    "Renames a local branch, must push with new name to affect remote",
                    "git branch -m feature/old feature/new\ngit push origin :feature/old feature/new  # Delete old, push new",
                    "# No output for rename, push shows progress"
                ),

                "How do you track a remote branch?": Command(
                    "git branch --track branch_name origin/branch_name",
                    "Creates a local branch that tracks a remote branch",
                    "git branch --track develop origin/develop\ngit checkout --track origin/feature  # Create and switch",
                    "Branch 'develop' set up to track remote branch 'develop' from 'origin'"
                ),

                "How do you update remote tracking branches?": Command(
                    "git remote update",
                    "Updates all remote tracking branches in local repository",
                    "git remote update\ngit remote update origin  # Update specific remote\ngit remote update --prune  # Remove deleted branches",
                    "Fetching origin\nremoving remote/deleted-branch"
                )
            }
        }
        self.current_mode: Optional[Mode] = None
        self.current_question = None
        self.current_answer: str = ""
        self.question_history = deque(maxlen=6) # Keeps last 6 questions
        self.score = 0
        self.high_score = self.load_high_score()

    def load_high_score(self) -> int:
        """Load high score from file, create if doesn't exist."""
        try:
            if os.path.exists('bash-tutor-score.json'):
                with open('bash-tutor-score.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except Exception as e:
            print(f"Error loading high score: {e}")
        return 0

    def save_high_score(self):
        """Save current high score to file."""
        try:
            with open('bash-tutor-score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except Exception as e:
            print(f"Error saving high score: {e}")

    def update_score(self, points: int):
        """Update current score and high score if necessary."""
        self.score += points
        if self.score < 0:
            self.score = 0

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            print(f"{SAGE}New High Score: {self.high_score}!{RESET}")

    def display_score(self):
        """Display current score and high score."""
        if self.score == self.high_score:
            print(f"\n{SAGE}Current Score: {self.score}")
            print(f"High Score: {self.high_score}{RESET}")
        else:
            print(f"\n{BLUE}Current Score: {self.score}")  
            print(f"High Score: {self.high_score}{RESET}")

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def get_mode(self) -> Mode:
        """Get the user's selected mode."""
        while True:
            self.display_score() # Show scores when selecting mode
            print("\nSelect a mode:")
            print(f"{LIGHT_PURPLE}b - Beginner (basic file operations, navigation)")
            print("i - Intermediate (file searching, system monitoring, processes, networking)")
            print("a - Advanced (system administration, performance tuning)")
            print("u - Understanding (understanding of commands and flags)")
            print("v - Variables (shell variables and their meanings)")
            print("s - Scripting (bash scripting concepts)")
            print("p - API (using curl to interact with APIs)")
            print(f"g - Git (basic git commands){RESET}")
            try:
                choice = input("\nEnter mode (b/i/a/u/v/s/p/g): ").lower()
                if choice == 'exit':
                    print(f"{BLUE}Final Score: {self.score}")
                    print(f"High Score: {self.high_score}")
                    print(f"Thanks for learning! Goodbye!{RESET}")
                    sys.exit(0)
                if choice in [m.value for m in Mode]:
                    return Mode(choice)
                print("Invalid choice. Please select b, i, a, u, v, s, p or g.")
            except (KeyboardInterrupt, EOFError):
                print(f"\n{BLUE}Final Score: {self.score}")
                print(f"High Score: {self.high_score}")
                print(f"Thanks for learning! Goodbye!{RESET}")
                sys.exit(0)

    def get_random_question(self) -> Tuple[str, Command]:
        """Get a random question and its answer for the current mode."""
        questions = self.questions[self.current_mode]
        available_questions = [q for q in questions.keys() 
                             if q not in self.question_history]
        
        # If all recent questions have been used, reset history
        if not available_questions:
            available_questions = list(questions.keys())
            self.question_history.clear()
            
        self.current_question = random.choice(available_questions)
        self.current_answer = questions[self.current_question]
        self.question_history.append(self.current_question)
        return self.current_question, self.current_answer

    def display_explanation(self, command: Command, is_correct: bool = True, is_case_mismatch: bool = False) -> None:
        """Display detailed explanation of a command."""
        if is_case_mismatch:
            color = PEACH
            self.update_score(CASE_MISMATCH_POINTS)
            print(f"{color}[{CASE_MISMATCH_POINTS} points]{RESET}")
        else:
            if is_correct:
                color = CYAN
                self.update_score(CORRECT_POINTS)
                print(f"{color}[+{CORRECT_POINTS} points]{RESET}")
            else:
                color = ROSE
                self.update_score(INCORRECT_POINTS)
                print(f"{color}[{INCORRECT_POINTS} points]{RESET}")
            
        print(f"\n{color}{'=' * 50}{RESET}")
        print(f"{color}Command:{RESET}     {command.command}")
        print(f"{color}Purpose:{RESET}     {command.explanation}")
        print(f"{color}Example:{RESET}     {command.example}")
        if command.output:
            print(f"{color}Sample Output:{RESET}\n{command.output}")
        print(f"{color}{'=' * 50}{RESET}")
        self.display_score()

    def check_answer(self, user_answer: str) -> (bool, bool):
        """Check if the user's answer matches the correct answer."""
        user_answer = user_answer.strip()
        correct_answer = self.current_answer.command.strip()
        
        # Check if answer matches ignoring case
        if user_answer.lower() == correct_answer.lower():
            # If it matches ignoring case but doesn't match exactly,
            # it's a case mismatch
            if user_answer != correct_answer:
                return False, True  # False for incorrect, True for case mismatch
            return True, False  # True for correct, False for case mismatch
        return False, False  # False for incorrect, False for case mismatch

    def provide_hint(self) -> str:
        """Provide a hint for the current question."""
        return f"Hint: The answer starts with '{self.current_answer.command[0]}'"

    def run(self):
        """Main program loop."""
        self.clear_screen()
        print_rainbow('=' * 50)
        print("\nWelcome to bash-tutor!")        
        print("Type 'exit' to quit, 'hint' for a hint,\n'skip' to skip question, or 'mode' to change mode")
        print_rainbow('=' * 50)
        print(f"\n{BLUE}If you wish to reset the current score, type 'clears'{RESET}")
        print(f"{BLUE}If you wish to reset the high score, type 'clearh'{RESET}")
        print(f"{BLUE}If you wish to reset both scores, type 'clearb'{RESET}")
        print(f"\n{SOFT_GOLD}Scoring System:")
        print(f"{CYAN}✓ Correct Answer: +{CORRECT_POINTS} point")
        print(f"{PEACH}~ Case Mismatch: {CASE_MISMATCH_POINTS} points")
        print(f"{ROSE}✗ Incorrect Answer: {INCORRECT_POINTS} points{RESET}")        
        print("-" * 40)

        # Get initial mode
        self.current_mode = self.get_mode()

        while True:
            if not hasattr(self, 'current_question') or self.current_question is None:
                question, _ = self.get_random_question()
            else:
                question = self.current_question

            print(f"\n{PURPLE}{question}{RESET}")

            try:
                user_input = input("> ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nThanks for learning! Goodbye!")
                sys.exit(0)

            if user_input.lower() == 'exit':
                # Check if we're on the "exit terminal" question
                if question == "How do you exit the terminal?":
                    is_correct, is_case_mismatch = self.check_answer(user_input)
                    if is_correct:
                        print(f"{CYAN}Correct! Well done!{RESET}")
                        self.display_explanation(self.current_answer, True, False)
                        self.current_question = None
                        continue  # Skip the normal answer handling below
                    else:
                        if is_case_mismatch:
                            print(f"{PEACH}Wrong capitalisation. Please check your casing.{RESET}")
                            self.display_explanation(self.current_answer, False, True)
                        else:
                            print(f"{ROSE}Incorrect. The correct answer is: {self.current_answer.command}{RESET}")
                            self.display_explanation(self.current_answer, False, False)
                        self.current_question = None
                        continue  # Skip the normal answer handling below
                else:
                    print(f"\n{BLUE}Final Score: {self.score}")
                    print(f"High Score: {self.high_score}")
                    print(f"Thanks for learning! Goodbye!{RESET}")
                    break
            elif user_input.lower() == 'hint':
                print(f"{YELLOW}{self.provide_hint()}{RESET}")
                continue  # Keep same question
            elif user_input.lower() == 'mode':
                self.current_mode = self.get_mode()
                self.current_question = None  # Reset question for new mode
                continue
            elif user_input.lower() == 'skip':
                print(f"The answer is: {CYAN}{self.current_answer.command}{RESET}")
                self.display_explanation(self.current_answer, False)
                self.current_question = None  # Get new question next time
                continue
            elif user_input.lower() == 'clearh':
                self.high_score = 0
                self.high_score = self.score
                self.save_high_score()
                print(f"{BLUE}High score has been reset to 0!{RESET}")
                continue
            elif user_input.lower() == 'clears':
                self.score = 0
                print(f"{BLUE}Score has been reset to 0!{RESET}")
                continue
            elif user_input.lower() == 'clearb':
                self.current_score = 0
                self.high_score = 0                
                self.save_high_score()
                print(f"{BLUE}Scores have been reset to 0!{RESET}")
                continue

            is_correct, is_case_mismatch = self.check_answer(user_input)
            if is_correct:
                print(f"{CYAN}Correct! Well done!{RESET}")
                self.display_explanation(self.current_answer, True, False)
                self.current_question = None  # Get new question next time
            else:
                if is_case_mismatch:
                    print(f"{PEACH}Wrong capitalisation. Please check your casing.{RESET}")
                    self.display_explanation(self.current_answer, False, True)  # Note the True for is_case_mismatch
                else:
                    print(f"{ROSE}Incorrect. The correct answer is: {self.current_answer.command}{RESET}")
                    self.display_explanation(self.current_answer, False, False)
                self.current_question = None  # Get new question next time

def main():
    tutor = BashTutor()
    tutor.run()

if __name__ == '__main__':
    main()