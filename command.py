import re


def get_pattern_indexes(pattern, usr_input):  # returns first occurrence of pattern in input
    matches = pattern.finditer(usr_input)
    start_index = None
    end_index = None
    for match in matches:
        start_index = match.start()
        end_index = match.end()
        if start_index is not None:
            break
    return start_index, end_index


def get_command(command_body):
    # command body is the the command part without sed statement - 's/a/b/g' for example
    indexes = [m.start() for m in re.finditer(r'\\/', command_body)]  # indexes of separator with backslash before them
    indexes2 = [m.start() for m in re.finditer(r'[^\\]/', command_body)]  # indexes of regular separators
    combine = sorted(indexes2+indexes)  # combine and sort the indexes to get all separators indexes
    # create list of tuples, every tuple containing (old,new,flag)
    # will pass the commands into Command constructor
    num_commands = len(combine)
    if num_commands % 3 == 0:
        my_commands = [(command_body[combine[i]+2:combine[i+1] + 1],
                        command_body[combine[i+1] + 2:combine[i+2] + 1].lstrip("/"),
                        command_body[combine[i+2] + 2:combine[i+2] + 4]) for i in range(0, num_commands, 3)]
        # old string found from (0,3..) index of separator +2 until (1,4..) index +1
        # new string found from (1,4..) index of separator +2 until (2,5..) index +1
        # flag found found from (2,5) index of separator +2 until same separator +4, flag can only have 2 chars
        return my_commands

    else:
        return  # return None for incorrect formatting


class Command:
    def __init__(self, command_body):
        self.body = get_command(command_body) # body of the command is a list of command tuples
        self.changed_lines = ""
        self.flag = ""

    def __repr__(self):
        return " body{}".format(self.body)

    def execute_command(self, content):
        if self.body is None:  # handle incorrect backslash format
            return

        for command in self.body:
            # assigns new variable here for chained command scenarios, new content needs to be deleted
            # creates duplicated lines otherwise
            new_content = ""
            flag = command[2].strip("/").strip("\'").strip("\"")
            self.flag = flag  # sets flag here for run_sed
            old = command[0]
            new = str(bytes(command[1], "utf-8").decode("unicode_escape"))  # makes sure escape chars handled
            pattern = re.compile(r"{}".format(old))  # user pattern to replace, accepting regex
            if flag in ("g", "pg", "gp"):  # handle g flag, replace all occurrences
                new_content = ""
                for line in content:
                    if re.findall(pattern, line):
                        change = None
                        change = re.sub(pattern, new, line)
                        if flag in ("pg", "gp"):  # create change for every occurrence and double the line
                            new_content += change * 2  # sub pattern for new input
                        else:  # create change without doubling
                            new_content += change
                        self.changed_lines += change  # add changes for any flag option
                    else:
                        new_content += line  # no changes, add line as is
            elif flag == "p":  # handle p flag, print every replacement again inside the output
                for line in content:
                    matches = pattern.finditer(line)  # finding all matches in file
                    # find first occurrence to make a replacement
                    start_index = None
                    for match in matches:
                        start_index, end_index = match.start(), match.end()
                        break  # only first occurrence is needed
                    # remove old string,replace with new one
                    if start_index is not None:  # if there's a match
                        new_line = line[:start_index] + new + line[end_index:]
                        self.changed_lines += new_line
                        new_content += new_line * 2
                    else:
                        new_content += line

            elif flag == "w":  # handle w flag, append edited lines to file
                for line in content:
                    matches = pattern.finditer(line)  # finding all matches in file
                    # find first occurrence to make a replacement
                    start_index = None
                    for match in matches:
                        start_index, end_index = match.start(), match.end()
                        break  # only first occurrence is needed
                    # remove old string,replace with new one
                    if start_index is not None:  # if there's a match
                        new_line = line[:start_index] + new + line[end_index:]
                        new_content += new_line

            elif flag.isnumeric():  # handle number flag, replace n'th occurrence of string to replace
                n = int(flag)
                count = 0
                for line in content:
                    if re.findall(pattern, line):
                        matches = pattern.finditer(line)  # finding all matches in file
                        # find first occurrence to make a replacement
                        start_index = None
                        added_flag = False
                        for match in matches:
                            count += 1  # increment match count if
                            start_index, end_index = match.start(), match.end()
                            if count == n and start_index is not None:
                                new_content += line[:start_index] + new + line[end_index:]
                                added_flag = True
                                count = 0  # reset counter, move to next line
                                break  # found and replaced the n th occurrence in a line , one occurrence for every row
                        # if there was a match in the line but not the n'th occurrence in any of them
                        if not added_flag:
                            new_content += line

                    else:
                        new_content += line
            else:  # no flag specified
                for line in content:
                    matches = pattern.finditer(line)  # finding all matches in file
                    # find first occurrence to make a replacement
                    start_index = None
                    for match in matches:
                        start_index, end_index = match.start(), match.end()
                        break  # only first occurrence is needed
                    # remove old string,replace with new one
                    if start_index is not None:  # if there's a match
                        new_line = line[:start_index] + new + line[end_index:]
                        new_content += new_line
                    else:
                        new_content += line
            if len(self.body) > 1:  # in case of chained commands save changed file to content
                content = new_content.split("\n")  # new content is a single line, split to elements by \n
                content = [line+"\n" for line in content][:-1]  # for every line add \n back, drop last empty element

        return new_content

if __name__ == "__main__":
    print(Command('s/unix/linux/p'))