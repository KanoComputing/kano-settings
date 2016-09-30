/*
 * syncfs
 *
 * Copyright (C) 2014 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
 *
 * Sync filesystem containing a file
 * Usage: syncfs </path/to/file
 */
#include <unistd.h>
int main(int argc, char *argv[]){
    return syncfs(STDIN_FILENO);
}


