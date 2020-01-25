#!/usr/bin/python3

"""
    Class 'SSHCommand' used to send commands through the instantiated SSH connection.
    SSH connection is instantiated on the constructor for 'SSHCommand' as the 'SSH' subclass.
    Utilizes paramiko (underlying functionality is socket programming) to send valid PS/Terminal 
    commands to the hosting device connection..
"""

import paramiko

class SSHCommand:
    #Determines whether an SSH object has already been instantiated
    _instance = None

    def __init__(self, ip, user, password):
        """
        Creates an SSH instance to open a connection if it has not already been instantiated.
        """
        self.stdin = None
        self.stdout = None
        self.stderr = None
        
        if not SSHCommand._instance:
            SSHCommand._instance = SSHCommand.SSH(ip, user, password)

    def __getattr__(self, name):
        """
        Passes attributes to the subclass.
        """
        return getattr(self._instance, name)

    def Open_SSH_Connection(self):
        """
        Calls the subclass function to open the specified SSH connection.
        """
        self.connect()

    def Close_SSH_Connection(self):
        """
        Closes the SSH connection.

        Raises:
            Exception if the server or pipes could not be closed.
        """
        try:
            self.stdout.close()
            self.stdin.close()
            self.stderr.close()
        except:
            raise Exception("You instantiated an SSH connection yet sent no commands")

        try:
            self.ssh.close()
        except:
            raise Exception("You did not instantiate an SSH connection")

    def Run_Executable(self, command):
        """
        Writes a command to the open SSH connection.
        Defaulted to running python scripts as this was the purpose at my institution.

        Args:
            command: The script to run on the remote server.

        Raises:
            Exception if the executable failed during its execution
            Exception if an unexpected result was returned
        """
        self.stdin, self.stdout, self.stderr = self.ssh.exec_command(
            "python {}".format(command))
        self.stdout.channel.shutdown_write()
        while not self.stdout.channel.eof_received:
            result = self.stdout.readline().strip()
            if result == "PASS":
                print("Success! {} returned: {}".format(command, result))
                return
            elif "FAIL" in result:
                raise Exception("Failed! {} returned: {}".format(command, result))
        raise Exception("Receieved unexpected result: {}".format(result))


    class SSH:
        def __init__(self, ip, user, password):
            self.ip = ip
            self.user = user
            self.password = password
            self.ssh = None
        
        def connect(self):
            """
            Opens the specified SSH connection.

            Raises:
                Exception if the attempted connection could not be authenticated.
                Exception if the attempted connection had an other general error.
            """
            print("Opening an SSH Connection to {}".format(self.ip))
            self.ssh = paramiko.SSHClient()
            self.ssh.load_system_host_keys()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                self.ssh.connect(self.ip, username=self.user, password=self.password)
            except paramiko.AuthenticationException:
                raise Exception("Authentication failed, verify your credentials")
            except paramiko.SSHException as sshException:
                raise Exception("Unable to establish connection to {}: {}".format(self.ip,sshException))
