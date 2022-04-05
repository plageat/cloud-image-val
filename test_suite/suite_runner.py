import os


class SuiteRunner:
    max_processes = 40  # based on the number of threads used by ami-val

    def __init__(self,
                 cloud_provider,
                 instances,
                 ssh_config,
                 parallel=True,
                 debug=False):
        self.cloud_provider = cloud_provider
        self.instances = instances
        self.ssh_config = ssh_config
        self.parallel = parallel
        self.debug = debug

    def run_tests(self, output_filepath):
        if os.path.exists(output_filepath):
            os.remove(output_filepath)

        os.system(self.compose_testinfra_command(output_filepath))

    def compose_testinfra_command(self, output_filepath):
        all_hosts = self.get_all_instances_hosts_with_users()
        test_suite_paths = self.get_test_suite_paths()

        command_with_args = [
            'py.test',
            ' '.join(test_suite_paths),
            f'--hosts={all_hosts}',
            f'--ssh-config {self.ssh_config}',
            f'--junit-xml {output_filepath}',
            '--connection=ssh'
        ]

        if self.parallel:
            command_with_args.append(f'--numprocesses={len(self.instances)}')
            command_with_args.append(f'--maxprocesses={self.max_processes}')

            # rerun failed tests in case ssh times out or connection is refused by host
            command_with_args.append('--only-rerun="refused|timeout"')
            command_with_args.append('--reruns 3')
            command_with_args.append('--reruns-delay 5')

        if self.debug:
            command_with_args.append('-v')

        return ' '.join(command_with_args)

    def get_all_instances_hosts_with_users(self):
        """
        :return: A string with comma-separated items in the form of '<user1>@<host1>,<user2>@<host2>'
        """
        return ','.join(['{0}@{1}'.format(inst['username'], inst['public_dns']) for inst in self.instances.values()])

    def get_test_suite_paths(self):
        """
        :return: A String array of test file absolute paths that will be executed in the cloud instances
        """
        test_suites_to_run = ['generic/test_generic.py']

        if self.cloud_provider == 'aws':
            test_suites_to_run.append('cloud/test_aws.py')

        return [os.path.join(os.path.dirname(__file__), p) for p in test_suites_to_run]
