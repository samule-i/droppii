import argparse
import json

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
    parser.add_argument("-o", "--output", metavar="filepath",
                        type=str, required=True, help="Output filename")
    parser.add_argument("-k", "--keys", type=str,
                        nargs='+', help='Keys to censor')

    args = parser.parse_args()
    print(args)

    output_file = args.output

    json_arguments = json.dumps({
        "s3_uri": args.input,
        "private_keys": args.keys
    })

    censor_output = censor(json_arguments)

    with open(output_file, "wb") as f:
        f.write(censor_output)
