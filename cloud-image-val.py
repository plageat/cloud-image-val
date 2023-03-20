import os
import json

from argparse import ArgumentParser, RawTextHelpFormatter
from main.cloud_image_validator import CloudImageValidator
from lib.config_lib import CIVConfig

parser = ArgumentParser(formatter_class=RawTextHelpFormatter)

parser.add_argument('-r', '--resources-file',
                    help='Path to the resources JSON file that contains the Cloud provider and the images to use.\n'
                         'See cloud/sample/resources_<cloud>.json to know about the expected file structure.')
parser.add_argument('-o', '--output-file',
                    help='Output file path of the resultant Junit XML test report and others')
parser.add_argument('-t', '--test-filter',
                    help='Use this option to filter tests execution by test name')
parser.add_argument('-m', '--include-markers',
                    help='Use this option to specify which tests to run that match a pytest markers expression.\n'
                         'The only marker currently supported is "pub" (see pytest.ini for more details)\n'
                         'Example:\n'
                         '\t-m "pub" --> run tests marked as "pub", which is for images are already published\n'
                         '\t-m "not pub" --> exclude "pub" tests\n'
                         'More information about pytest markers:\n'
                         '--> https://doc.pytest.org/en/latest/example/markers.html',
                    default=None)
parser.add_argument('-p', '--parallel',
                    help='Use this option to enable parallel test execution mode. Default is DISABLED',
                    default=False,
                    action='store_true')
parser.add_argument('-d', '--debug',
                    help='Use this option to enable debugging mode. Default is DISABLED',
                    default=False,
                    action='store_true')
parser.add_argument('-s', '--stop-cleanup',
                    help='Use this option to enable stop cleanup process until a key is pressed. \n'
                         'Helpful when you need to connect through ssh to an instance. Default is DISABLED',
                    default=False,
                    action='store_true')
parser.add_argument('-c', '--config-file',
                    help='Use this option to pass CLI options through a config file.\n'
                         'This config should be in yaml format, examples can be found in the README',
                    default=None)
parser.add_argument('--tags',
                    help='Use this option to add tags to created cloud resources and modify CIV behaviour.\n'
                         'This tags should be passed in json format as in this example:\n'
                         '--tags \'{"key1": "value1", "key2": "value2"}\'',
                    default=None)

if __name__ == '__main__':
    args = parser.parse_args()

    # Add current dir abspath to PYTHONPATH to avoid issues when importing modules
    if 'PYTHONPATH' not in os.environ:
        os.environ['PYTHONPATH'] = ''
    os.environ['PYTHONPATH'] = ':'.join(
        [f'{os.path.dirname(__file__)}', os.environ['PYTHONPATH']])

    if args.config_file:
        civ_config = CIVConfig(args.config_file)
        civ_config.validate()
        config = civ_config.get_config()
    else:
        assert (args.resources_file is not None), 'ERROR: Please provide a resources file'
        assert (args.output_file is not None), 'ERROR: Please provide an output path'

        if args.tags:
            args.tags = json.loads(args.tags)

        civ_config = CIVConfig()
        args.config_file = civ_config.config_path
        civ_config.write_config(args)
        config = civ_config.get_config()

    cloud_image_validator = CloudImageValidator(config=config)
    exit(cloud_image_validator.main())
