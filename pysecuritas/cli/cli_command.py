# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import argparse
import json
import textwrap
from typing import List

from pysecuritas.__version__ import __description__
from pysecuritas.api.pysecuritas import pysecuritas
from pysecuritas.core.commands import get_available_commands


class CLICommand:
    """
    Class responsible for creating a cli parser and execute a single command
    """

    def __init__(self):
        """
        Class initialization
        """

        self.parser = None
        self.args = None
        self.result = None

    def parse(self, args: List[str]) -> None:
        """
        Creates a parser for the cli entrypoint and parses the provided arguments
        against the newly created parser

        :param args a list of arguments to be parsed
        """

        parser = argparse.ArgumentParser(usage="%(prog)s [options]",
                                         description=__description__, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('-u',
                            '--username',
                            help='Username used in the web page/mobile app.',
                            required=True)
        parser.add_argument('-p',
                            '--password',
                            help='Password used in the web page/mobile app.',
                            required=True)
        parser.add_argument('-i',
                            '--installation',
                            help='Installation/Facility number (appears on the website).',
                            required=True)
        parser.add_argument('-c',
                            '--country',
                            help='Your country: ES, IT, FR, GB, PT ...',
                            required=True)
        parser.add_argument('-l',
                            '--language',
                            help='Your language: es, it, fr, en, pt ...',
                            required=True)
        parser.add_argument('-s',
                            '--sensor',
                            help='The sensor ID (to take a picture using IMG)',
                            required=False)
        commands = get_available_commands()
        parser.add_argument("command",
                            help=textwrap.dedent('\n'.join([': '.join(i) for i in commands.items()])),
                            type=str)

        self.args = parser.parse_args(args)

    def run(self) -> None:
        """
        Runs a the command provided on cli arguments

        :return: the result from the operation
        """

        client = pysecuritas(self.args)
        self.result = client.operate_alarm(self.args.command)

    def pretty_print(self) -> None:
        """
        Prints the result from the executed operation
        """

        print(json.dumps(self.result, indent=2))