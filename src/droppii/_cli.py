import argparse
import json
import sys

from .censor import censor


def main():
    parser = argparse.ArgumentParser(
        prog="droppii",
        description="""Python module to process data from an AWS (S3) bucket
    and anonymize personally
    identifiable information, returning data in the same format as provided."""
    )

    parser.add_argument("-i", "--input", metavar="s3 uri", type=str,
                        required=True, help="s3 uri of file to be converted")
    parser.add_argument("-k", "--keys", type=str,
                        nargs='+', help='Keys to censor')

    args = parser.parse_args()

    json_arguments = json.dumps({
        "s3_uri": args.input,
        "private_keys": args.keys
    })

    censor_output = censor(json_arguments)
    sys.stdout.buffer.write(censor_output)
