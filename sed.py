import os
from command import Command
import re


class FormatError(Exception):
    pass


class BadQuotesException(Exception):
    pass


class NoFileInput(Exception):
    pass


# input is sed command entered by user
# output is Command, Parameter - Optional : Filename
# process sed command
# gets called only if input passes validation

def read_sed(usr_input):
    if not check_quotes(usr_input):  # check for quotes match in command part
        raise BadQuotesException
    command_pattern = re.compile(r"sed\s(-e|-f|-n|-i)\s[\"\']s/.+/.*/(pg|gp|w|g|p|\d+)?[\"\']")
    start_index, end_index = get_pattern_indexes(command_pattern, usr_input)
    if start_index is not None:  # parameter was given, pattern match
        command_body = usr_input[start_index + 5:end_index]  # parameter was specified, drop sed
        parameter = command_body[0:1].strip()
        command_body = command_body[2:].strip().strip("\"").strip("\'")
    else:  # no parameter, will get a match because user command passed initial format check
        command_pattern = re.compile(r"sed\s[\"\']s/.+/.*/(pg|gp|w|g|p|\d+)?[\"\']")  # no parameter
        parameter = None
        start_index, end_index = get_pattern_indexes(command_pattern, usr_input)
        command_body = usr_input[start_index + 4:end_index].strip("\'").strip("\"")  # no parameter, drop sed
    # split on pattern found, left part is sed, right is file name
    raw_command = usr_input.strip("\"").strip("\'").split(command_body)
    file_name = raw_command[1].strip("\"").strip("\'").strip(" ")  # extract file name
    # command body is the the command part without sed statement - 's/a/b/g' for example
    command = Command(command_body)  # build command object
    if command is None:
        return None, None
    if file_name == "":  # for literal string input cases
        return command, parameter
    else:
        return command, parameter, file_name


# returns first occurrence of pattern in input
def get_pattern_indexes(pattern, usr_input):
    matches = pattern.finditer(usr_input)
    start_index = None
    end_index = None
    for match in matches:
        start_index = match.start()
        end_index = match.end()
        if start_index is not None:
            break
    return start_index, end_index

# ending part of bash and echo command formats
# creates the output from the command and content, output depends on parameter given
def end_bash_echo(parameter, content, command):
    new_content = command.execute_command(content)  # result to be printed
    if new_content is None:
        raise FormatError
    if parameter == "i":  # invalid parameter in this format
        raise NoFileInput
    if command.flag == "w":
        raise IOError
    if parameter == "n" and command.flag in ("p", "pg", "gp"):
        print(command.changed_lines)
    elif parameter == "n" and command.flag != "p":
        pass  # doesn't print anything
        return
    else:
        print(new_content)


# function to check for proper command quotation
def check_quotes(usr_input):
    quotes1 = bool(re.match(r"^sed\s(-e|-f|-n|-i)?\s?[\"]s/.+/.*/(pg|gp|w|g|p|\d+)?[\"].*",
                            usr_input))
    quotes2 = bool(re.match(r"^sed\s(-e|-f|-n|-i)?\s?[\']s/.+/.*/(pg|gp|w|g|p|\d+)?[\'].*",
                            usr_input))
    return quotes1 or quotes2


# function to validate and return command type
def check_command(usr_command):
    # makes sure command is in either correct format
    # only accepts s command
    string_format = bool(
        re.match(r"^echo\s[\"\'].+[\"\']\s[|]\ssed\s(-e|-f|-n|-i)?\s?[\"\']s/.+/.*/(pg|gp|w|g|p|\d+)?[\"\']$",
                 usr_command))
    file_format = bool(re.match(r"^sed\s(-e|-f|-n|-i)?\s?[\"\']s/.+/.*/(pg|gp|w|g|p|\d+)?[\"\']\s[^\s]+$",
                                usr_command))
    bash_format = bool(re.match(r"^sed\s(-e|-f|-n|-i)?\s?[\"\']s/.+/.*/(pg|gp|w|g|p|\d+)?[\"\']\s<<<\s[\"\'].+[\"\']$",
                                usr_command))

    if file_format:
        return 0  # return 0 if format is file
    if string_format:  # command in a replace literal string format
        return 1  # return 1 if format is string
    if bash_format:  # return 2 if format is bash
        return 2


# main function,  input is sed command as entered by user
# function prints sed command output

def run_sed(usr_input):
    try:
        # variable to store command type if it's valid, avoid calling check_command twice
        is_valid = check_command(usr_input)
        if is_valid is None:  # command not in a valid format
            raise FormatError

        if is_valid == 0:  # file format
            command, parameter, file_name = read_sed(usr_input)
            flag = command.flag
            if os.path.isfile(file_name):  # checks if file exists in current directory
                with open(file_name, "r") as file:
                    content = file.readlines()
                new_content = command.execute_command(content)
                if new_content is None:
                    raise FormatError

                if parameter == "n" and command.flag in ("p", "pg", "gp"):
                    print(command.changed_lines)

                elif parameter == "n" and command.flag != "p":
                    pass  # doesn't print anything
                else:
                    print(new_content)

                # ## writing to file scenarios ## #
                if flag == "w" and parameter == "i":  # append changes to file
                    with open(file_name, "w") as file:
                        origin = ""
                        for line in content:
                            origin += line
                        file.write(origin + new_content)

                if flag != "w" and parameter == "i":  # write changes to file
                    with open(file_name, "w") as file:
                        file.write(new_content)

            else:
                raise IOError

        if is_valid == 1:  # string format
            pattern = re.compile(r"^echo\s[\"\'].+[\"\']\s[|]")
            start_index, end_index = get_pattern_indexes(pattern, usr_input)
            command_body = usr_input[end_index + 1:]  # finds the beginning of sed statement
            command, parameter = read_sed(command_body)
            content = [usr_input[6:end_index - 3] + "\n"]  # puts string in a list to match function iteration
            end_bash_echo(parameter, content, command)

        if is_valid == 2:  # bash format
            # with parameter
            pattern = re.compile(r"\s<<<\s[\"\'].+[\"\']$")
            start_index, end_index = get_pattern_indexes(pattern, usr_input)
            command_body = usr_input[:start_index]
            command, parameter = read_sed(command_body)
            content = [usr_input[start_index + 4:].strip().strip("\'").strip("\"") + "\n"]
            end_bash_echo(parameter, content, command)

    except FormatError:
        print("Incorrect syntax")
    except IOError:
        print("File not found")
    except BadQuotesException:
        print("Make sure to close statement with the correct quotes!")
    except NoFileInput:
        print("No Input Files")


if __name__ == "__main__":
    run_sed(input("Please Enter a sed command\n"))
